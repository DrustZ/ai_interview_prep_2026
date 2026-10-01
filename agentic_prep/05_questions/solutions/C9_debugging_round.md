# [C9] Sierra onsite debugging round：TS/React buggy 代码库找 bug（禁 AI）· 完整解答

⏱ 读完 10 min ｜ 建议先自己限时（60 min）在任一 React 练习 repo 上跑一遍流程再看
题库原文：[../C_live_ai_coding.md#c9](../C_live_ai_coding.md#c9) ｜ 姊妹篇（带 agent 的对照轮）：[C13](C13_draft_pr_round.md)

## 题目还原 + 验收标准

TS+React 应用（典型：客服 bot 聊天界面），埋 4–6 个 bug，60 分钟，**明确禁 AI 工具**。多位候选人称这轮是 "the real gate"，且 "Do not believe the language-agnostic framing"——只会 Python 会直接挂。

验收标准（面试官在看的）：
1. 复现 → 定位 → 假设 → 验证的**系统化流程**，不是乱改碰运气
2. 修复**不破坏其他功能**（每修一个要回归）
3. **UX/产品意识**：只让测试通过不够，要说清用户看到什么
4. 全程 narration：每个动作说出"我在验证什么假设"

## 解题主线（60 分钟节奏）

| 时间 | 动作 |
|---|---|
| 0–5 | 跑起来 + 读结构：`npm run dev`、`npm test`；看 package.json scripts、目录结构、核心组件树。**先看 bug 清单/症状描述有没有给** |
| 5–10 | 把每个症状变成可复现步骤，按"影响用户程度"排优先级 |
| 10–45 | 逐个 bug：复现 → 二分定位 → 一句话假设 → 最小修复 → 回归。每个 bug 预算约 7 分钟，卡 10 分钟就先跳下一个 |
| 45–55 | 全量回归（手点主流程 + 跑测试），review 自己的 diff |
| 55–60 | 总结：修了哪些、各自根因、没修的和风险、有时间会优化什么 |

**二分定位三板斧**（narration 时点名用哪个）：
1. **数据流二分**：症状在 UI → 检查 props → state → API response → request payload，逐层 `console.log`/React DevTools 确认"数据在哪一层开始变错"
2. **时间二分**：初次渲染就错（初始化/props 传递）vs 交互后才错（handler/effect/竞态）
3. **注释二分**：怀疑某段 effect/handler，先注释掉看症状是否消失，确认再细看

**开场澄清（1 分钟内问完）**：能不能装依赖/跑测试？bug 是功能性的还是含性能/类型？可以查 MDN/React 官方文档吗（题面说可查资源时）？修复以"用户可见行为正确"为准还是以测试为准？

## React/TS 五大类 bug 清单（识别特征 → 修法）

### 1. Stale closure（旧闭包捕获旧 state）

识别：interval/timeout/事件订阅/异步回调里读到的 state 永远是初始值；"计数器只加到 1"。

```tsx
// BUG：count 被闭包捕获，永远是 0
useEffect(() => {
  const id = setInterval(() => setCount(count + 1), 1000);
  return () => clearInterval(id);
}, []); // 依赖数组空，闭包不更新

// FIX：函数式更新，不依赖闭包里的值
useEffect(() => {
  const id = setInterval(() => setCount(c => c + 1), 1000);
  return () => clearInterval(id);
}, []);
// 若回调要读多个 state：用 useRef 存最新值，或把依赖加进数组并清理重建
```

### 2. useEffect 依赖数组错误

识别：数据不刷新（依赖缺失）/ 无限循环、请求风暴（依赖了每次渲染都新建的对象/函数）。

```tsx
// BUG A：缺依赖——切换 userId 不重新拉数据
useEffect(() => { fetchUser(userId).then(setUser); }, []);
// FIX A：补上 [userId]

// BUG B：依赖每次都是新引用——无限循环
const options = { id: userId };           // 每次渲染新对象
useEffect(() => { fetch(url, options); }, [options]);
// FIX B：依赖原始值 [userId]，或 useMemo 包住 options
```

narration 高分句："依赖数组的原则是 effect 里读到的所有响应式值都要列出；如果列出后循环，说明该值不该每次渲染重建。"

### 3. 列表 key 错误

识别：删除/插入列表项后，**输入框内容或选中态"串行"到别的项上**；用 index 作 key。

```tsx
// BUG：index 作 key，删除第 0 项后各行 state 错位
{messages.map((m, i) => <MessageRow key={i} msg={m} />)}
// FIX：用稳定唯一 id
{messages.map(m => <MessageRow key={m.id} msg={m} />)}
```

### 4. 异步竞态（旧请求覆盖新结果）

识别：快速切换 tab/连续搜索后，界面显示的是**上一个**查询的结果；慢网络下必现。聊天界面变体：旧会话的回复渲染进新会话。

```tsx
// BUG：无取消/无守卫，慢的旧请求后到，覆盖新结果
useEffect(() => {
  fetchResults(query).then(setResults);
}, [query]);

// FIX：cleanup 标记 + AbortController
useEffect(() => {
  const ctrl = new AbortController();
  let alive = true;
  fetchResults(query, { signal: ctrl.signal })
    .then(r => { if (alive) setResults(r); })
    .catch(e => { if (e.name !== "AbortError") setError(e); });
  return () => { alive = false; ctrl.abort(); };
}, [query]);
```

### 5. 直接突变 state（mutation）

识别：数据明明变了但 UI 不刷新——因为引用没变，React 认为无变化。

```tsx
// BUG：原地 push，引用不变，不触发重渲染
messages.push(newMsg); setMessages(messages);
items[0].done = true; setItems(items);
// FIX：不可变更新
setMessages(prev => [...prev, newMsg]);
setItems(prev => prev.map((it, i) => i === 0 ? { ...it, done: true } : it));
```

### 附：TS/异步层高频陪跑 bug（快速扫一眼就能捡分）

- **未 await 的 promise**：`const data = fetchX()` 拿到 Promise 当值用；或 `try/catch` 包了没 await 的调用捕不到异常。修：补 await，确认函数签名 async。
- **吞异常**：`catch (e) {}` 空块，或 fetch 只查网络错不查 `res.ok`。修：`if (!res.ok) throw new Error(...)` + 把 error 送进 UI 的 error state。
- **可选链缺失/类型断言掩盖 null**：`data!.user.name` 崩在 undefined。修：可选链 + 类型窄化（`if (!data) return <Spinner/>`）。
- **setState 异步误用**：`setX(v); use(x)` 读到旧值。修：用刚计算的局部值，或放进 effect 依赖 x。
- **loading/error 状态缺失**：请求失败 UI 静默空白——这是 UX 分，主动补三态（loading/error/empty）。

## 边界与测试要点

- 每个修复后必须做两件事并 narration："跑相关测试" + "手动走一遍相邻功能"（比如修了消息列表 key，要验证发送/删除/滚动都正常）
- 修复求**最小 diff**：面试官会问"这个修复会不会影响别的功能"——最小 diff 让你能用"改动面只有 X"回答
- 如果测试本身有断言错误（Sierra 会埋），说出"测试锁的是错误行为"，先改测试再修代码

## 高频 follow-up 与应对

**Q1「这个修复会不会影响别的功能？」**
答法三层：(1) diff 范围——"我只改了 X 组件的 Y 逻辑，调用方是 A/B 两处，我都手测过"；(2) 语义——"函数式更新/AbortController 是行为等价的加固，不改变 happy path 输出"；(3) 证据——"回归测试全绿 + 我手动走了发送/切换/删除三条路径"。

**Q2「还有时间你会优化什么？」**
按 UX → 正确性 → 性能排序说：(1) 补 loading/error/empty 三态和请求 abort；(2) 给竞态和列表 key 写回归测试，防止复发；(3) 性能——大列表虚拟化、`useMemo`/`useCallback` 只在量过 profiler 后加（"先测量再优化"是加分句）；(4) 类型加固——把 API response 从 `any` 收紧成显式接口，让下一类 bug 编译期就挂。

**Q3「为什么先修这个 bug？」**
"按用户影响排序：崩溃 > 数据错误 > 状态不刷新 > 视觉问题。竞态导致用户看到错误数据，比样式问题严重。"

## 如果这轮允许 AI

本轮**禁 AI**——这正是 Sierra 的设计意图：与 [C13 带 agent 的 PR review 轮](C13_draft_pr_round.md) 形成对照，验证你没有 AI 时的原生 debug 能力。上面的五类 bug 清单要练到"看症状 10 秒内说出假设"。允许 AI 的轮次驾驶法见 [../../02_playbook.md](../../02_playbook.md) 第八节。
