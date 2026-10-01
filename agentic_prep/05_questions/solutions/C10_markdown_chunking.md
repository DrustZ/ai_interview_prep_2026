# [C10] Markdown 按 header 层级分块（size limit + 父 header 重复）· 参考实现

⏱ 读完 12 min ｜ 建议先盲写 40 min（base 25 min + 两个 follow-up 15 min）再对照——Sierra 是 multi-part 递进，结构比速度重要。题库原文见 [../C_live_ai_coding.md](../C_live_ai_coding.md) [C10]。

## 题目还原 + 验收标准

**原始问法**：实现 `split_markdown(markdown: str, max_size: int) -> list[str]`，把 markdown 切成有序 chunks，每个 ≤ `max_size`。Header = 行首 1–6 个 `#` + 空格；非 header 行属于当前层级。**关键规则**：chunk 在某 section 中间开始时，必须在首个内容行前重复所有 active 父 headers（重复的 header 计入 size limit）；遇到 level-L header 时清空 level L–6 的 active headers。`len(markdown) ≤ 200,000`；base 版保证「任意单行 + 所需父 headers」能放进 `max_size`。

**验收标准**（开场复述给面试官，写在 CoderPad 注释里）：
1. 每个 chunk `len ≤ max_size`——含注入的父 headers（follow-up 里还含 fence 闭合标记）
2. 行序与内容保持原样，除注入的重复 header / fence 标记外不丢不改
3. 在 section 中间开始的 chunk，首内容行前有完整父 header 路径（浅→深）
4. level-L header 出现即清空 L..6 的栈；`("", 10) -> []`；整篇装得下 → 单 chunk 原样返回
5. 单遍 O(n)，200k 输入毫秒级

**开场必澄清 3 个假设**（说出口再写码）：size 按字符数还是 token（按 `len()`，说明换 tokenizer 的改法在 follow-up）；行分隔符只有 `\n`（`split("\n")` + `"\n".join` 可精确还原，空行是长度为 0 的行、原样保留，文末 `\n` 变成末 chunk 的尾部空行）；code fence 里的 `#` 不算 header（base 版先不管 fence，声明为 follow-up）。

## 解题主线（60 min CoderPad 时间分配）

- **0–5**：复述验收标准 + 三个澄清 + 手推小例子 `("# Title\nHello\n## Section\nWorld", 100)` → 单 chunk。
- **5–12**：先立骨架——四个 helper 的签名和一个长度不变式：`cur_len == len("\n".join(cur))`（追加一行的成本 = `len(line) + (1 if cur else 0)`，先写对这个就不会 off-by-one）。helpers：`append` / `flush` / `open_chunk`（开新 chunk 时注入父 header 前缀，**抽成函数**——后面 fence 重开也挂在这）/ `place`（放不下就开新 chunk）。
- **12–25**：base 版：header 栈（`dict[int, str]`，level→原始行）+ 贪心逐行追加。写完立刻跑三个边界：空文档、整篇单 chunk、中途开新 chunk 重复父 headers。
- **25–35**：follow-up 1 超长行二次切分（`place` 里加 while 循环，词边界优先、硬切兜底）。
- **35–48**：follow-up 2 code fence（fence 内 `#` 不算 header；被迫切开时闭合再重开，reserve 闭合标记的预算）。
- **48–60**：补 assert 测试 + 主动讲 trade-offs（dangling header、空 fence 块、word-boundary 丢空格）。

**可以砍的**（时间紧就口头声明）：词边界切分（硬切也满足验收）、`~~~` fence、fence reserve 的精确预算（先写对 `\n```` 的 4 字符 reserve 最稳，来不及就口头指出）。

## 参考实现

```python
import re

HEADER_RE = re.compile(r"^(#{1,6}) ")   # 行首 1-6 个 # + 空格 = header
FENCE_RE = re.compile(r"^(```|~~~)")    # code fence 开/闭标记


def split_markdown(markdown: str, max_size: int) -> list[str]:
    if not markdown:
        return []
    lines = markdown.split("\n")        # "\n".join 精确还原原文，长度好算
    chunks: list[str] = []
    cur: list[str] = []                 # 当前 chunk 的行
    cur_len = 0                         # 不变式: cur_len == len("\n".join(cur))
    active: dict[int, str] = {}         # header 栈: level -> 原始 header 行
    fence: str | None = None            # 未闭合 fence 的开头行（含语言标注）

    def append(line: str) -> None:
        nonlocal cur_len
        cur_len += len(line) + (1 if cur else 0)
        cur.append(line)

    def flush() -> None:
        nonlocal cur, cur_len
        if fence and cur:
            append(fence[:3])           # 补闭合标记，每个 chunk 都是合法 markdown
        if cur:
            chunks.append("\n".join(cur))
        cur, cur_len = [], 0

    def open_chunk() -> None:
        for lvl in sorted(active):      # 重复父 header 路径，浅→深（计入 size）
            append(active[lvl])
        if fence:
            append(fence)               # fence 中间被切开：新 chunk 重开 fence

    def place(line: str, reserve: int = 0) -> None:
        """放一行；放不下就 flush + 注入前缀；单行超长则二次切分。
        reserve: 若本 chunk 里 fence 未闭合，flush 时要补 "\\n```"，预留 4 字符。"""
        def room() -> int:
            return max_size - reserve - cur_len - (1 if cur else 0)
        if len(line) <= room():
            append(line)
            return
        flush(); open_chunk()
        rest = line
        while len(rest) > room():       # 超长行：按剩余空间切
            if room() <= 0:
                raise ValueError("max_size too small for header/fence prefix")
            cut = rest.rfind(" ", 1, room() + 1)   # 词边界优先
            cut = cut if cut > 0 else room()       # 无空格就硬切
            append(rest[:cut])
            rest = rest[cut:].lstrip(" ")          # 边界空格视作分隔符丢弃
            flush(); open_chunk()
        append(rest)

    for line in lines:
        m = None if fence else HEADER_RE.match(line)   # fence 内 # 不是 header
        if m:
            lvl = len(m.group(1))
            for l in [l for l in active if l >= lvl]:
                del active[l]           # level L 出现: 清空 L..6
            active[lvl] = line
            if cur_len + len(line) + (1 if cur else 0) <= max_size:
                append(line)
            else:                       # header 已入栈，随 open_chunk 前缀进新 chunk
                flush(); open_chunk()
        else:
            toggle = bool(FENCE_RE.match(line))
            open_after = (fence is not None) != toggle  # 放完这行后 fence 是否未闭合
            place(line, reserve=4 if open_after else 0)  # 4 == len("\n```")
            if toggle:
                fence = None if fence else line
    flush()
    return chunks


if __name__ == "__main__":
    assert split_markdown("", 10) == []
    doc = "# Title\nHello\n## Section\nWorld"
    assert split_markdown(doc, 100) == [doc]            # 整篇一个 chunk

    doc = "# A\n## B\n" + "\n".join(f"line{i}" for i in range(6))
    out = split_markdown(doc, 30)                       # 中途开新 chunk
    assert all(len(c) <= 30 for c in out)
    assert all(c.startswith("# A\n## B\n") for c in out)  # 父路径重复进块

    doc = "# A\n## B\nxxxx\n# C\n" + "\n".join(f"y{i}" for i in range(8))
    out = split_markdown(doc, 20)                       # level 清栈
    assert any(c.startswith("# C\n") for c in out[1:])
    assert all("## B" not in c for c in out[1:])        # # C 之后不再带 ## B

    out = split_markdown("# H\n" + "word " * 40, 30)    # 超长单行二次切分
    assert all(len(c) <= 30 for c in out)

    doc = "# H\n```python\n# not a header\nprint(1)\n```\ntail"
    out = split_markdown(doc, 25)                       # fence 保护
    assert all(c.count("```") % 2 == 0 for c in out)    # 每个 chunk fence 闭合
    assert not any("\n# not" in c and "```" not in c for c in out)
    print("all tests passed")
```

核心约 95 行。跑法：`python c10.py` → `all tests passed`。

## 边界与测试要点

必须口头提或写进 assert 的 case：
- **空文档 / 只有空行**：`"" -> []`；`"\n\n"` → 三个空行，一个 chunk `"\n\n"`（round-trip 语义）。
- **连续 headers**（`# A\n## B\n### C\ncontent`）：全部入栈，新 chunk 前缀三行都注入。
- **同级替换**（`# A\n# B`）：`# A` 已进当前 chunk 不会丢，只是从栈里被 `# B` 顶掉。
- **chunk 恰好以 header 结尾**（dangling header）：header 进了上一个 chunk 尾部，下一个 chunk 又重复它——符合规则但难看。主动说：refinement 是 flush 前把尾部的 active header 行 pop 掉留给下一个 chunk（注意别把 chunk 弹空）。
- **closing fence 放不下**：会产生一个「空 fence 块」（上个 chunk 补 ```` ``` ````、新 chunk 重开又立刻闭合）——正确但浪费，主动指出。
- **word-boundary 切分丢边界空格**：`lstrip(" ")` 是有意的语义选择；面试官要严格保内容就改成 `cut = room()` 硬切。
- **性质测试**（有时间就写）：随机文档上验证 ① 所有 chunk ≤ max_size；② 把每个 chunk 去掉注入前缀后拼接 == 原文。

## 高频 follow-up 与应对

**Q1: code block 里的 `#` 要不要当 header？**（题库原追问，先澄清再写）
答：默认不当——```` ``` ````/`~~~` 之间是字面文本，把 `# comment` 当 header 会把 Python 注释切成 section。实现上用 `fence` 状态位：fence 内跳过 `HEADER_RE`；同时 fence 不能从中间切——被迫切开时上个 chunk 补闭合、新 chunk 重开 `fence` 原行（保留语言标注），闭合标记的 4 字符（`\n` + ```` ``` ````）要在 `reserve` 里预算，否则 flush 补标记时超限。简化假设（口头声明）：不处理 fence 嵌套、闭合标记只匹配前 3 字符。

**Q2: chunks 的顺序怎么保证？两个 chunk「起点相同」怎么排？**（题库原追问）
答：单遍扫描 + append-only，chunk 顺序天然等于文档顺序，无需排序。注入的父 header 是前缀复制品、不代表 chunk 的起点——chunk 的逻辑起点是它第一条非注入行，单调递增，不存在真正的 tie；若接口要返回 `(start_offset, text)`，start 记第一条非注入行在原文的 offset 即可。

**Q3: size 想按 token 算怎么改？**
答：把长度函数参数化：`split_markdown(md, max_size, length_fn=len)`，`append`/`room` 里的 `len(line)` 换 `length_fn(line)`，分隔符成本从 `1` 换 `length_fn("\n")`。注意 token 不可加性（`tok(a+b) != tok(a)+tok(b)`）——工程上按行级近似 + 留 5% 余量即可，超长行硬切要改成二分找最大可放 token 前缀。

**Q4: 要不要给 chunk 之间加 overlap？**
答：这题的父 header 注入本身就是「结构化 overlap」——只重复导航信息不重复正文。RAG 场景的实证结论（[../../03_gaps/rag.md](../../03_gaps/rag.md) 的 Chroma 报告：[Evaluating Chunking](https://www.trychroma.com/research/evaluating-chunking)）：去掉正文 overlap 反而提升 token 级 IoU——overlap 制造冗余 token 挤占 context 预算；框架默认参数（800 tok + 400 overlap）表现垫底。所以我默认 0 正文 overlap，只保 header 路径。

**Q5: 这个和通用 recursive splitter 什么关系？**
答：本题是 [../../03_gaps/rag.md](../../03_gaps/rag.md) 里「结构优先递归切分」的 header 专精版：`SEPS = ["\n## ", "\n### ", "\n\n", "\n", ". ", " "]` 逐级降级，我的 `place` 超长行 while 循环就是它的 `hard_split` 兜底，父 header 注入对应「标题路径写进 chunk 前缀或 metadata」。生产版把段落/句子边界（`"\n\n"`、`". "`）插进降级序列，就从行级贪心升级成通用 recursive splitter；结构化文档按标题切优于语义切分（rag.md 失败模式栏）。

**Q6: 200k 输入的性能？**
答：单遍 O(n)（字符数），`active` 最多 6 项、`sorted` 常数级；瓶颈只在字符串拼接，`"\n".join(cur)` 每 chunk 一次是线性总量。再大（流式日志）就把返回改 generator：`yield "\n".join(cur)` 替代 `chunks.append`，内存 O(max_size)。

## 如果这轮允许 AI：怎么驾驶

按 [../../02_playbook.md](../../02_playbook.md) 第八节：先声明验收标准 A（size 上限含注入前缀）/B（父路径重复）/C（fence 不裂开），让 AI 一次只做一个窄任务（如「给 place 加词边界切分，不改其他函数」），每步产出后自己跑 assert 块验证——重点检查 off-by-one（分隔符计费）和 reserve 预算，这两处是 AI 最常写错的地方。收尾解释哪些是 AI 写的、你怎么验证的。
