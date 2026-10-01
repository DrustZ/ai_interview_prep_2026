"""Design Durable Function Call Cache — 题目与 Python 解法。

题目说明
========
用 LRU cache 包装一个昂贵函数：相同输入再次调用时直接返回缓存结果。

Part 1：create_cache_key
------------------------
题目已经提供缓存查询、插入、hit/miss 统计和 LRU 淘汰，缺少的部分是
``create_cache_key(*args, **kwargs)``。它必须：

1. 对相同函数调用生成相同 key；
2. key 必须可哈希；
3. kwargs 的传入顺序不能影响 key；
4. 嵌套 list/dict 等 JSON 数据必须被递归、稳定地表示；
5. 不同函数不能因为参数相同而共用错误的缓存项。

本实现先用函数签名绑定参数，因此 ``f(1, b=2)``、``f(a=1, b=2)``
和省略/显式传入相同默认值会得到同一个 key。之后使用 ``sort_keys=True``
的 canonical JSON；字符串本身就是可哈希对象。

基础版本约定参数是 JSON-compatible 数据。自定义对象需要额外定义稳定的
序列化协议，不能直接依赖可能包含内存地址的 ``repr(obj)``。

Part 2：崩溃恢复
----------------
把缓存操作写入 append-only write-ahead log（WAL），重启时顺序重放：

* ``put`` 记录 key 和 value；
* ``touch`` 记录一次 cache hit，因为 hit 也会改变 LRU 顺序；
* 重放已有 key 时必须把它移动到 MRU 端；
* 超过 capacity 时从 LRU 端淘汰；
* 日志末尾可能因崩溃而截断或损坏：保留此前的完整前缀并停止重放；

这里用“checksum + base64(pickle(record)) + 换行”保存记录。checksum 用于发现
损坏记录；pickle 允许缓存一般 Python 返回值，但日志必须是自己生成的可信文件，
绝对不能加载不可信 pickle。每次写入默认执行 flush + fsync，安全但较慢。

下面给出了完整可运行类；如果面试 skeleton 只要求 Part 1，复制
``create_cache_key`` 即可。
"""

import base64
import hashlib
import hmac
import inspect
import json
import os
import pickle
from collections import OrderedDict
from functools import update_wrapper
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Dict, Optional


class FunctionCallCache:
    """In-memory LRU function cache."""

    def __init__(self, func: Callable[..., Any], capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.func = func
        self.capacity = capacity
        self.cache: "OrderedDict[str, Any]" = OrderedDict()
        self.hits = 0
        self.misses = 0
        self._signature = inspect.signature(func)
        self._function_id = f"{func.__module__}.{func.__qualname__}"
        self._lock = RLock()
        update_wrapper(self, func)

    def create_cache_key(self, *args: Any, **kwargs: Any) -> str:
        """Return one deterministic, hashable key for an equivalent call."""
        bound = self._signature.bind(*args, **kwargs)
        bound.apply_defaults()

        payload = {
            "function": self._function_id,
            # Bound arguments are ordered by the function's parameter order.
            "arguments": list(bound.arguments.items()),
        }
        try:
            return json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "cache arguments must be JSON-compatible and contain no NaN/Infinity"
            ) from exc

    def _put(self, key: str, value: Any) -> None:
        if key in self.cache:
            del self.cache[key]
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        key = self.create_cache_key(*args, **kwargs)

        # A coarse lock is intentionally simple. A production implementation
        # can use one lock/future per key so different misses run concurrently.
        with self._lock:
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                return self.cache[key]

            self.misses += 1
            value = self.func(*args, **kwargs)
            self._put(key, value)
            return value


class DurableFunctionCallCache(FunctionCallCache):
    """FunctionCallCache with append-only WAL recovery."""

    def __init__(
        self,
        func: Callable[..., Any],
        capacity: int,
        log_path: str,
        *,
        fsync: bool = True,
    ):
        super().__init__(func, capacity)
        self.log_path = Path(log_path)
        self.fsync = fsync
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._recover()

    def _append_record(self, record: Dict[str, Any]) -> None:
        payload = pickle.dumps(record, protocol=pickle.HIGHEST_PROTOCOL)
        checksum = hashlib.sha256(payload).hexdigest().encode("ascii")
        line = checksum + b" " + base64.b64encode(payload) + b"\n"

        with self.log_path.open("ab") as log:
            log.write(line)
            log.flush()
            if self.fsync:
                os.fsync(log.fileno())

    @staticmethod
    def _decode_record(line: bytes) -> Optional[Dict[str, Any]]:
        try:
            expected, encoded = line.strip().split(b" ", 1)
            payload = base64.b64decode(encoded, validate=True)
            actual = hashlib.sha256(payload).hexdigest().encode("ascii")
            if not hmac.compare_digest(expected, actual):
                return None
            record = pickle.loads(payload)
            return record if isinstance(record, dict) else None
        except (ValueError, TypeError, pickle.PickleError, EOFError):
            return None

    def _recover(self) -> None:
        if not self.log_path.exists():
            return

        with self.log_path.open("rb") as log:
            for line in log:
                # No newline means the final append did not complete.
                if not line.endswith(b"\n"):
                    break

                record = self._decode_record(line)
                if record is None:
                    # WAL is an ordered prefix: never trust records after a gap.
                    break

                key = record.get("key")
                if not isinstance(key, str):
                    break

                if record.get("op") == "put" and "value" in record:
                    self._put(key, record["value"])
                elif record.get("op") == "touch" and key in self.cache:
                    self.cache.move_to_end(key)
                else:
                    break

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        key = self.create_cache_key(*args, **kwargs)

        with self._lock:
            if key in self.cache:
                self.hits += 1
                # Persist recency changes as well as new values.
                self._append_record({"op": "touch", "key": key})
                self.cache.move_to_end(key)
                return self.cache[key]

            self.misses += 1
            value = self.func(*args, **kwargs)
            # Write first, then expose the value in memory.
            self._append_record({"op": "put", "key": key, "value": value})
            self._put(key, value)
            return value
