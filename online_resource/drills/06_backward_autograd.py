"""
06_backward_autograd.py -- 手推 backward + 标量 micro-autograd 冷写训练

对应真题:
    OpenAI Research Scientist 轨 "AI coding I": 手写 autograd / matmul backward
    原题 (2026-04 PracHub / 1p3a 多帖)。Anthropic / GDM ML coding 轮也常考
    "给定 forward 写出 backward" 与 micrograd 风格的标量自动微分。

冷写清单 (函数签名):
    1. matmul_backward(A: np.ndarray, B: np.ndarray, dC: np.ndarray)
           -> tuple[np.ndarray, np.ndarray]
       约定 C = A @ B, A:(m,k) B:(k,n) dC:(m,n)。返回 (dA, dB)。
    2. linear_backward(x: np.ndarray, W: np.ndarray, b: np.ndarray,
                       dY: np.ndarray)
           -> tuple[np.ndarray, np.ndarray, np.ndarray]
       约定 Y = x @ W + b, x:(batch,in) W:(in,out) b:(out,)。
       返回 (dx, dW, db)。
    3. class Value:  # ~80 行标量 autograd, Karpathy micrograd 风格
       支持 __add__ / __mul__ (含 int/float 混算与 __radd__/__rmul__)、
       tanh()、backward() (拓扑排序反向回传, grad 累加)。
    4. mlp_forward_backward(x, W1, b1, W2, b2, y_target)
           -> tuple[float, dict[str, np.ndarray]]
       两层 MLP: h = tanh(x@W1+b1); yhat = h@W2+b2;
       loss = mean((yhat - y_target)**2)  # 对所有元素取 mean
       返回 (loss, {"dx","dW1","db1","dW2","db2"})。

核心记忆点:
    C = A @ B  =>  dA = dC @ B.T,  dB = A.T @ dC   (形状对得上就是对的)
    bias 广播  =>  db = dY.sum(axis=0)
    tanh'(z) = 1 - tanh(z)**2  (用 forward 存下来的激活值, 不要重算 z)
    mean 的梯度 = 上游梯度 / 元素总数

建议 timebox: 共 45 分钟
    matmul_backward 5min | linear_backward 5min | Value 类 20min | MLP 15min
"""

from __future__ import annotations

import math

import numpy as np

# ========================= COLD-WRITE ZONE =========================


def matmul_backward(
    A: np.ndarray, B: np.ndarray, dC: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """C = A @ B 的 backward。A:(m,k) B:(k,n) dC:(m,n) -> (dA, dB)."""
    dA = dC @ B.T          # (m,n) @ (n,k) -> (m,k)
    dB = A.T @ dC          # (k,m) @ (m,n) -> (k,n)
    return dA, dB


def linear_backward(
    x: np.ndarray, W: np.ndarray, b: np.ndarray, dY: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Y = x @ W + b 的 backward。x:(batch,in) W:(in,out) b:(out,)."""
    dx = dY @ W.T          # (batch,out) @ (out,in) -> (batch,in)
    dW = x.T @ dY          # (in,batch) @ (batch,out) -> (in,out)
    db = dY.sum(axis=0)    # b 被广播到每个样本 => 梯度对 batch 求和
    return dx, dW, db


class Value:
    """标量 autograd 节点 (micrograd 风格)。"""

    def __init__(
        self, data: float, _children: tuple["Value", ...] = (), _op: str = ""
    ) -> None:
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __add__(self, other: "Value | float | int") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward() -> None:
            # += 而不是 =: 同一节点被多处使用时梯度要累加
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __mul__(self, other: "Value | float | int") -> "Value":
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward() -> None:
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    __radd__ = __add__
    __rmul__ = __mul__

    def tanh(self) -> "Value":
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward() -> None:
            self.grad += (1.0 - t * t) * out.grad

        out._backward = _backward
        return out

    def backward(self) -> None:
        # 拓扑排序: 保证访问某节点时其所有下游节点已回传完毕
        topo: list[Value] = []
        visited: set[Value] = set()

        def build(v: "Value") -> None:
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build(child)
                topo.append(v)

        build(self)
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()

    def __repr__(self) -> str:
        return f"Value(data={self.data}, grad={self.grad})"


def mlp_forward_backward(
    x: np.ndarray,
    W1: np.ndarray,
    b1: np.ndarray,
    W2: np.ndarray,
    b2: np.ndarray,
    y_target: np.ndarray,
) -> tuple[float, dict[str, np.ndarray]]:
    """两层 MLP (linear-tanh-linear-MSE) 的完整 forward + backward。

    forward:  h = tanh(x @ W1 + b1);  yhat = h @ W2 + b2
    loss   :  mean((yhat - y_target)**2)  (对所有元素取平均)
    """
    # ---- forward (缓存中间量供 backward 使用) ----
    h = np.tanh(x @ W1 + b1)             # (batch, hidden)
    yhat = h @ W2 + b2                   # (batch, out)
    diff = yhat - y_target
    loss = float(np.mean(diff**2))

    # ---- backward (链式法则, 从 loss 往回推) ----
    dyhat = 2.0 * diff / diff.size       # mean => 除以元素总数
    dh, dW2, db2 = linear_backward(h, W2, b2, dyhat)
    dz1 = dh * (1.0 - h**2)              # tanh'(z) = 1 - tanh(z)^2
    dx, dW1, db1 = linear_backward(x, W1, b1, dz1)

    grads = {"dx": dx, "dW1": dW1, "db1": db1, "dW2": dW2, "db2": db2}
    return loss, grads


# ========================= TESTS =========================

import torch

RTOL, ATOL = 1e-6, 1e-8


def _t(a: np.ndarray, requires_grad: bool = True) -> torch.Tensor:
    """numpy -> float64 torch tensor (叶子节点)。"""
    return torch.tensor(a, dtype=torch.float64, requires_grad=requires_grad)


def test_matmul_backward_vs_torch() -> None:
    rng = np.random.default_rng(0)
    shapes = [(3, 4, 5), (1, 1, 1), (2, 7, 3), (6, 1, 4), (1, 5, 1)]
    for m, k, n in shapes:
        A = rng.standard_normal((m, k))
        B = rng.standard_normal((k, n))
        dC = rng.standard_normal((m, n))

        dA, dB = matmul_backward(A, B, dC)

        At, Bt = _t(A), _t(B)
        C = At @ Bt
        C.backward(gradient=torch.tensor(dC, dtype=torch.float64))

        assert dA.shape == A.shape and dB.shape == B.shape
        assert np.allclose(dA, At.grad.numpy(), rtol=RTOL, atol=ATOL)
        assert np.allclose(dB, Bt.grad.numpy(), rtol=RTOL, atol=ATOL)


def test_matmul_backward_zero_upstream() -> None:
    # 边界: 上游梯度全 0 => 下游梯度全 0
    rng = np.random.default_rng(1)
    A = rng.standard_normal((4, 3))
    B = rng.standard_normal((3, 2))
    dA, dB = matmul_backward(A, B, np.zeros((4, 2)))
    assert np.all(dA == 0.0) and np.all(dB == 0.0)


def test_linear_backward_vs_torch() -> None:
    rng = np.random.default_rng(2)
    shapes = [(5, 4, 3), (1, 6, 2), (7, 1, 1)]  # (batch, in, out), 含 batch=1
    for batch, din, dout in shapes:
        x = rng.standard_normal((batch, din))
        W = rng.standard_normal((din, dout))
        b = rng.standard_normal(dout)
        dY = rng.standard_normal((batch, dout))

        dx, dW, db = linear_backward(x, W, b, dY)

        xt, Wt, bt = _t(x), _t(W), _t(b)
        Y = xt @ Wt + bt
        Y.backward(gradient=torch.tensor(dY, dtype=torch.float64))

        assert np.allclose(dx, xt.grad.numpy(), rtol=RTOL, atol=ATOL)
        assert np.allclose(dW, Wt.grad.numpy(), rtol=RTOL, atol=ATOL)
        assert np.allclose(db, bt.grad.numpy(), rtol=RTOL, atol=ATOL)


def _expr(a, b, c):
    """同一表达式跑 Value 和 torch 标量 (两者都支持 + * tanh)。"""
    d = a * b + c
    e = (d + a).tanh()
    f = e * e + b * d
    return f.tanh() + f + 2.0 * a + 1.0  # 也覆盖 int/float 混算与 __radd__/__rmul__


def test_value_vs_torch_scalar_graph() -> None:
    vals = (0.7, -1.3, 0.25)

    a, b, c = (Value(v) for v in vals)
    out = _expr(a, b, c)
    out.backward()

    at, bt, ct = (
        torch.tensor(v, dtype=torch.float64, requires_grad=True) for v in vals
    )
    out_t = _expr(at, bt, ct)
    out_t.backward()

    assert math.isclose(out.data, out_t.item(), rel_tol=RTOL, abs_tol=ATOL)
    for node, leaf in [(a, at), (b, bt), (c, ct)]:
        assert math.isclose(node.grad, leaf.grad.item(), rel_tol=RTOL, abs_tol=ATOL)


def test_value_grad_accumulation() -> None:
    # 同一节点被使用多次: y = a*a + a => dy/da = 2a + 1 (解析解)
    a = Value(3.0)
    y = a * a + a
    y.backward()
    assert math.isclose(y.data, 12.0, rel_tol=RTOL)
    assert math.isclose(a.grad, 2 * 3.0 + 1, rel_tol=RTOL)


def test_value_tanh_saturation() -> None:
    # 边界: 极大输入 => tanh 饱和到 1, 梯度趋于 0 (不应出现 nan/inf)
    a = Value(50.0)
    y = a.tanh()
    y.backward()
    assert math.isclose(y.data, 1.0, rel_tol=0, abs_tol=1e-12)
    assert math.isfinite(a.grad) and abs(a.grad) < 1e-12


def test_mlp_vs_torch() -> None:
    rng = np.random.default_rng(3)
    for batch, din, dh, dout in [(5, 4, 8, 3), (1, 2, 3, 1)]:  # 含 batch=1
        x = rng.standard_normal((batch, din))
        W1 = rng.standard_normal((din, dh))
        b1 = rng.standard_normal(dh)
        W2 = rng.standard_normal((dh, dout))
        b2 = rng.standard_normal(dout)
        y = rng.standard_normal((batch, dout))

        loss, g = mlp_forward_backward(x, W1, b1, W2, b2, y)

        xt, W1t, b1t, W2t, b2t = _t(x), _t(W1), _t(b1), _t(W2), _t(b2)
        ht = torch.tanh(xt @ W1t + b1t)
        yhat_t = ht @ W2t + b2t
        loss_t = ((yhat_t - torch.tensor(y, dtype=torch.float64)) ** 2).mean()
        loss_t.backward()

        assert math.isclose(loss, loss_t.item(), rel_tol=RTOL, abs_tol=ATOL)
        for name, leaf in [
            ("dx", xt), ("dW1", W1t), ("db1", b1t), ("dW2", W2t), ("db2", b2t)
        ]:
            assert np.allclose(g[name], leaf.grad.numpy(), rtol=RTOL, atol=ATOL), name


def test_mlp_perfect_fit_zero_grad() -> None:
    # 边界: y_target 恰好等于网络输出 => loss=0 且所有梯度为 0
    rng = np.random.default_rng(4)
    x = rng.standard_normal((3, 2))
    W1 = rng.standard_normal((2, 4))
    b1 = rng.standard_normal(4)
    W2 = rng.standard_normal((4, 2))
    b2 = rng.standard_normal(2)

    yhat = np.tanh(x @ W1 + b1) @ W2 + b2
    loss, g = mlp_forward_backward(x, W1, b1, W2, b2, yhat)

    assert loss == 0.0
    for name, grad in g.items():
        assert np.all(grad == 0.0), name


if __name__ == "__main__":
    tests = [
        test_matmul_backward_vs_torch,
        test_matmul_backward_zero_upstream,
        test_linear_backward_vs_torch,
        test_value_vs_torch_scalar_graph,
        test_value_grad_accumulation,
        test_value_tanh_saturation,
        test_mlp_vs_torch,
        test_mlp_perfect_fit_zero_grad,
    ]
    for t in tests:
        t()
        print(f"PASSED: {t.__name__}")
    print("ALL TESTS PASSED")
