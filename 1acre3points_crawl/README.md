# 前沿面试资料库（本地索引）

一个零构建、零前端依赖的本地资料浏览器。它用于索引用户已有的 OpenAI / Anthropic 面试研究笔记、公开摘要、同题材料和原始链接。不同内容层级会明确标注，不把研究重构或同题资料冒充会员 canonical 原文。

## 启动

```bash
cd /Users/mingrui/Documents/codes/interview/1acre3points
python3 serve.py
```

脚本会自动选择可用端口并打开浏览器；加 `--no-open` 可只启动服务。不要直接双击 `index.html`，浏览器通常会阻止 `file://` 页面读取本地 JSON。

网站是纯静态文件，不需要 `npm install`、打包或数据库。

## 当前本地数据

- 页面当前合并去重后显示 488 条资料卡。其中 **283 条是可按官方 ID/slug 逐项识别的目录题**，其余是研究资料卡，二者不会混算成“官方题目数”。
- 官方目录覆盖为 **283 / 283**：OpenAI 184/184（45 qbank + 139 OJ），Anthropic 99/99（35 qbank + 64 OJ）。
- `data/questions.json`：上述 283 条 canonical 目录记录；每条都有真实官方 ID/slug、标题和详情 URL。80 条 qbank 保留分类、标签、岗位、轮次、频率等本地快照元数据；203 条 OJ 的公开目录接口不提供官方标签，非空标签会明确标为 `tagsSource: title-inference`。
- 当前 283/283 条都有可读准备内容，且不再有多题共用的正文。证据分层为：2 条公开 canonical qbank 正文、42 条本地保存的直接同题材料、25 条 qbank 研究重构、0 条 OJ 同题家族资料、0 条 OJ 研究清单式重构、2 条公开/外部 OJ 摘要，以及 212 条结构化原创中文准备指南（201 OJ + 11 qbank）。旧的“仅按标题生成提纲”现为 0 条。原创指南统一按“证据边界、题意、例子、解法、复杂度、边界测试”排版，并明确标出缺失条件、来源冲突或公开样例矛盾；它们不是会员原文或官方答案。逐条审计见 `data/content_coverage.json`。
- 全量语义复核修正了 20 条“标题/摘要与正文其实是不同题”的旧映射；Chatbot、Version Dependency、Stopping Time、PyTorch Refactor、Attention、Double Descent、Design Doc Review、TTL Cache、GRPO、Recipes、IPv4、Softmax 等不再显示另一道题的答案。
- 第二轮逐条审计又修复了全部 5 条 OJ 清单式重构、9 条同题家族硬错配和 10 条缺关键功能的记录，并为 LRU、Rotting Oranges、Web Crawler、IP-to-CIDR、Bootloader、TimeMap、`cd` 等补上公开同题链接。
- 重新审计 127 条“同题家族资料”后，已把 127 条全部升级成逐 UUID 的独立指南：覆盖 Stack Snapshot、allocator、snapshot social graph、NumPy 1-NN、chatbot、durable KV、label scheduler、file dedup、LRU durability、tokenizer、infection、GPU credits、SQL、crawler、image pipeline、type inference、system design 等；剩余复用型正文为 0。
- `materials.html` 对整个 `my_interview_prep` 建立了单独的论坛式分页索引：1,551 个物理文件中 1,548 个内容文件已分组为 1,880 个阅读单元，另有 3 个 `.DS_Store` 仅记入清单；包括 103 份本地论坛 HTML 和 181 个 Deep-ML 题包/仓库单元。当前有 315 个高匹配阅读单元关联到 200/283 道 canonical 题；`data/local_materials.json` 同时保留逐文件 manifest、源路径和自动匹配分数。
- 6 个 Anthropic OA 主题附带用户原有的本地 Python 练习实现；它们仅通过语法检查，未验证算法正确性，也不是官方答案。
- Anthropic 35 条 qbank 全部附有至少一个单独标注关系和置信度的来源；Image Processing 有 24 个可点击入口（官方条目、同题页、直接/相关面经及外站解法）。
- `data/supplemental.json`：207 条工作区中原有的多来源研究笔记，全部带来源 URL；这些不是“其余 207 道官方题”。展示层已去掉 `LOCKED / captured`、临时 `/tmp` 路径和“旁路”等内部采集状态，并统一标成“补充研究资料”。
- 原先缺失的 143 条公开 OJ 分页目录已经补齐：OpenAI 第 2–5 页 109 条、Anthropic 第 2–3 页 34 条。精确审计见 `data/catalog_coverage.json`。
- 会员 canonical 逐字正文仍需在官方页面按你的账户权限查看。本地详情页会保留原帖 URL；78 条会员题中 74 条已有可被用户提供工具识别的 `thread/post/pins/tid` 链接，并显示“复制原帖 URL”和工具入口。其余 4 条（Design AI Chatbot、Version Dependency、GPT-3 Playground、Mech Interp Take Home）在现有本地与公开索引中没有可可靠对应的原帖 ID，只保留题库 URL，避免拿相关帖冒充原帖。2026-07-11 实测该邀请码已使用 250/250 次，因此当前不能通过它验证受限正文。
- `data/member_content_audit.json` 对 78 条会员题逐项区分“已有可读本地准备内容”和“会员 canonical 正文已经验证”：当前前者为 78/78，后者为 0/78。该文件同时列出 74 条可供工具解析的帖子 URL 和 4 条待补 ID，避免把原创题解误报成会员原文。
- 一亩三分地条款禁止 crawler、批量复制和用站内内容建立数据库，因此这里停止在公开目录元数据、用户已有本地材料、研究摘要与官方链接层；不会继续自动抓取 203 个详情页的整段正文。需要更完整内容时，请导入你有权使用的个人导出文件。

如需从原有本地材料重新生成数据：

```bash
python3 scripts/fetch_public_oj_catalog.py
python3 scripts/import_existing_snapshot.py
python3 scripts/import_anthropic_snapshot.py
python3 scripts/import_public_oj_catalog.py
python3 scripts/import_supplemental.py
python3 scripts/add_related_posts.py
python3 scripts/import_local_fulltext.py
python3 scripts/index_local_materials.py
python3 scripts/audit_member_content.py
```

## 数据加载顺序

页面会合并并去重以下数据：

1. `data/questions.json`：用户自行提供或导出的资料，可不存在。
2. `data/supplemental.json`：本地已有研究资料，可不存在。
3. 页面中“导入自己的 JSON”导入的数据：只写入当前浏览器的 `localStorage`，不会上传或改写磁盘文件。

如果前两个文件都不存在，页面仍可正常打开，并显示导入说明。`data/sources.json` 是可选的来源入口目录；缺失时会显示内置的 OpenAI 与 Anthropic 官方题库页链接。

## 支持的数据结构

顶层可以直接是数组，也可以使用 `questions`、`items`、`problems`、`entries` 或 `records`：

```json
{
  "metadata": {
    "generatedAt": "2026-07-10"
  },
  "questions": [
    {
      "id": "openai-example-1",
      "company": "OpenAI",
      "title": "示例题目",
      "category": "coding",
      "roles": ["software-engineer"],
      "tags": ["graph", "concurrency"],
      "access": "summary",
      "difficulty": "hard",
      "frequency": "high",
      "lastAsked": "2026-06-20",
      "durationMinutes": 60,
      "stages": ["technical-screen"],
      "summary": "用户笔记中的简短概览。",
      "content": "用户已有的研究内容。",
      "solutionHint": "可选的准备思路。",
      "sources": [
        {
          "title": "原始页面",
          "url": "https://example.com/original",
          "relationship": "direct-interview-report",
          "confidence": "high",
          "note": "可选的来源匹配说明"
        }
      ]
    }
  ]
}
```

前端同时兼容常见的 snake_case 字段，例如 `last_asked`、`duration_minutes`、`source_url`、`is_locked`。所有导入文本都作为纯文本渲染，不会执行其中的 HTML 或脚本。

可选的 `data/sources.json` 示例：

```json
{
  "sources": [
    {
      "name": "OpenAI 官方题库页",
      "url": "https://www.1point3acres.com/interview/problems/company/openai"
    }
  ]
}
```

## 功能

- 全文搜索，以及公司、分类、岗位、标签、访问状态筛选
- 论坛式高密度列表与真正的页码分页；可选每页 25、50 或 100 条，搜索和筛选会自动回到第一页
- 最近出现、频率、标题和公司排序
- 题目详情与醒目的原始来源链接
- 对带一亩三分地原始面经帖的条目，提供“复制原帖 URL”与用户给出的第三方看帖工具入口；支持识别 `thread-数字`、`/thread/数字`、`/post/数字`、`/pins/数字` 与 `?tid=数字`。工具不支持 `&q=` 深链，因此不会伪造自动预填链接
- 单独的 `materials.html` 本地资料页：搜索、公司/类型筛选、分页、源文件打开、路径复制与关联题目跳转
- 易读详情排版：标题、段落、列表、引用、表格、链接、行内代码与代码块均结构化显示；中英文单行长文会按句子、分号和编号保守分段
- 来源关系与置信度标签（官方条目、同题页、直接面经、相关面经、外站解法等）
- 收藏、完成状态及对应筛选
- JSON 浏览器内导入与清除
- 深浅色主题、移动端筛选抽屉、键盘快捷键 `⌘/Ctrl + K`
- 通过 URL hash 直接定位当前详情条目

收藏、完成状态、主题和导入内容保存在浏览器 `localStorage`。清理该站点的浏览器数据会同时清除这些状态。

补充资料导入使用 NFC 保留中文全角标点，NFKC 只用于去重键。外链题解中的 `PRE0` 等代码占位符会从对应的本地 HTML 快照恢复；页面仍然只用 DOM `textContent` 安全渲染，不执行资料中的 HTML 或脚本。

## 文件

```text
1acre3points/
├── index.html
├── materials.html
├── README.md
├── serve.py
├── assets/
│   ├── app.js
│   ├── materials.js
│   ├── favicon.svg
│   └── styles.css
├── scripts/
│   ├── fetch_public_oj_catalog.py
│   ├── import_existing_snapshot.py
│   ├── import_anthropic_snapshot.py
│   ├── import_public_oj_catalog.py
│   ├── import_local_fulltext.py
│   ├── import_supplemental.py
│   ├── index_local_materials.py
│   ├── audit_member_content.py
│   └── add_related_posts.py
├── data/
│   ├── questions.json
│   ├── questions.example.json
│   ├── catalog_coverage.json
│   ├── content_coverage.json
│   ├── local_material_links.json
│   ├── local_materials.json
│   ├── member_content_audit.json
│   ├── oj_original_guides.md
│   ├── oj_public_summaries.json
│   ├── public_oj_catalog.json
│   ├── qbank_public_bodies.json
│   ├── supplemental.json
│   └── sources.json
└── practice/
    ├── anthropic/
    └── openai/
```
