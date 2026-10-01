# 05 · Case Study：OCR / Signature Recognition ML System Design

⏱ 精读约 35 分钟 ｜ 面试前重点背：**任务消歧、数据切分、双阈值、人审、cost cascade、10 分钟口述稿**

> **三档阅读入口**（别从头读到尾，按你的时间预算选）
> - **面试前 3 分钟** → §0 五种任务表 + §13 面试前一页速记
> - **只有 15 分钟** → §0 + §2 数据（这题真正的核心）+ §7 production 与 cost + §10 10 分钟口述稿
> - **完整（Day 1 傍晚）** → 先闭卷限时 30 min 答题，再读 §0/§2/§3/§7/§10/§11
>
> 这题的两个题眼：**§0 五种任务必须先拆开**（detect / verify / identify / quality / OCR，数据模型指标全不同）、**§2+§3 场景采集矩阵**（不能只说"做 augmentation"）。你上一次被问的正是这两点。

> 高分开场：`signature recognition` 不是一个任务。我会先确认我们要做的是 **detect（有没有/在哪）**、**verify（是不是声称的这个人，1:1）**、**identify（是谁，1:N）**、**quality/type（能否处理、湿签还是电子签）**，还是 OCR 签名旁边的姓名。它们的数据、模型、指标和风险完全不同。签名图像通常也不是可以逐字符转录的普通 OCR 文本。

---

## 0. 先把题目钉死：五种任务不能混在一起

| 任务 | 输入 → 输出 | 典型用途 | 主要指标 | 主要风险 |
|---|---|---|---|---|
| Signature detection | 文档页 → bbox / polygon / absent | 检查表单是否签名、定位 ROI | Recall、mAP、漏检率 | 把印刷线条、手写备注、印章当签名 |
| Quality/type classification | 签名 crop → usable / blur / clipped；wet / typed / e-sign | 决定是否重拍、走哪条 pipeline | Macro-F1、per-class recall、coverage | 低质量图被错误放行 |
| Signature verification（1:1） | 当前签名 + 声称身份的 reference → genuine / reject / review | 银行、保险、合同核验 | TAR@FAR、FMR/FNMR、校准 | 欺诈者被接受，或合法用户被拒绝 |
| Signature identification（1:N） | 当前签名 + gallery → top-k signer / unknown | 档案归属、法证辅助 | Recall@k、open-set FAR | gallery 大、相似签名、隐私风险更高 |
| OCR / field association | 文档 → signer name/date/title + source span | 抽取“谁、何时、以什么身份签署” | Field F1、CER/WER、link accuracy | 把邻近字段错误地关联给签名 |

**必须再问一句**：是离线图像（offline signature image），还是触控笔产生的在线轨迹（online signature）？后者有坐标、压力、速度、笔画顺序，验证信号强得多；前者不能假装拥有这些 liveness/dynamics 信号。

### 面试中建议提出的 8 个澄清问题

1. **业务动作**：结果只是预填/排序，还是会自动拒绝付款、合同或身份？错误成本差几个数量级。
2. **任务范围**：只判断“签过了”，还是要和 reference 做 1:1 verification？是否需要 1:N identification？
3. **输入分布**：PDF 原件、扫描仪、手机照片、传真、截图分别占多少？每份多少页？
4. **reference 条件**：每个 signer 有几张可信 enrollment signatures？多久以前采集？reference 本身是否可能被污染？
5. **对手模型**：只处理自然质量问题，还是要抵抗 copy-paste、trace、skilled forgery、生成式伪造？
6. **SLO 与规模**：QPS、P95 latency、日文档量、允许的人工审核率和单文档成本？
7. **风险目标**：可以接受多大的 false match rate？不同交易金额是否应使用不同 threshold？
8. **隐私/地域**：是否把签名视为 biometric / sensitive personal data？consent、retention、deletion、region 有什么约束？

下面用一个具体假设回答：

> 为保险/金融文档做离线签名处理。输入是 PDF 或手机照片；先检测签名、判断质量，再用 1–5 张可信 reference 做 1:1 verification，同时 OCR 姓名/日期并关联到签名。低风险文档 P95 < 1 秒，高风险允许异步；不自动做最终法律/欺诈裁决，灰区进入人工审核。日均 1,000 万页，峰值约均值 5 倍。

---

## 1. 需求、输出合同与系统边界

### 1.1 成功定义

系统不应只返回一个无解释的 `0.87`，而应返回一个可审计的 decision artifact：

```json
{
  "document_id": "doc_123",
  "model_version": "sig-v17",
  "policy_version": "claims-high-value-v4",
  "signatures": [{
    "bbox": [0.14, 0.72, 0.46, 0.83],
    "detection_confidence": 0.995,
    "type": "wet_ink",
    "quality": {"usable": true, "issues": []},
    "linked_fields": {
      "signer_name": {"value": "Jane Doe", "source_bbox": [0.10, 0.63, 0.43, 0.69]},
      "signed_date": {"value": "2026-07-21", "source_bbox": [0.53, 0.72, 0.72, 0.78]}
    },
    "verification": {
      "reference_set_id": "ref_jane_v3",
      "score": 0.78,
      "calibrated_p_genuine": 0.94,
      "decision": "REVIEW",
      "reason_codes": ["single_reference", "cross_device_shift"]
    }
  }]
}
```

关键原则：

- **score 不是 probability**；只有经过 held-out calibration 后才能叫概率。
- `model_version` 与 `policy_version` 分开。模型产生证据/分数，业务 policy 根据风险、金额、客户决定阈值。
- detection、quality、verification 各自保留分数，避免只看到最终 decision 而无法归因。
- OCR 字段必须带 `source_bbox`；签名验证结果不应被表述为法律上的“真实性证明”。

### 1.2 Non-goals（主动讲很加分）

v1 不做：

- 仅凭静态图像宣称绝对检测所有 sophisticated forgery；
- 用签名字形猜测性格、健康、性别等没有业务依据的属性；
- 在 reference 不可信或只有严重裁剪的一张样本时给高置信自动通过；
- 把 cryptographic digital signature validation 和手写图像相似度混为一谈；
- 让一个通用 VLM 直接输出“真/假”并作为高风险最终裁决。

---

## 2. 数据：这道题真正的核心

> 面试高分句：我不会先问“用 ViT 还是 CNN”，而会先定义 **deployment distribution × error cost × label contract**。现实场景覆盖不足，换更大的模型也只会更自信地错。

### 2.1 数据从哪里来

按真实性与成本分层：

1. **历史生产数据（最高价值）**
   - 已取得合法处理依据的历史表单、支票、合同、理赔文件；
   - 真实设备、压缩、模板、用户行为和失败模式；
   - 需要从人工复核、争议结果或后续业务 outcome 获得可靠 label；
   - 不能把“旧模型通过”直接当 genuine gold label，否则会复制旧模型偏差。
2. **受控 enrollment / collection campaign**
   - 经明确 consent，请参与者在不同笔、纸、姿势、速度、时间和设备下多次签名；
   - genuine 样本应跨天采集，不能只在 10 分钟内连签 20 次；
   - 收集 random forgery、simple forgery、skilled imitation、traced/copy-paste 等不同负例；
   - 适合建立干净、可解释的 verification benchmark。
3. **客户/合作方数据**
   - 通过 data-use agreement 获取某行业或模板覆盖；
   - tenant 数据默认隔离，除非合同和 consent 允许，不能默认为全局训练材料；
   - 必须记录 provenance、许可范围、retention 和 deletion obligation。
4. **公开或商业许可数据集**
   - 用于初始 representation learning 和 sanity check；
   - 多为干净 crop、签署人少、设备单一，不能代表生产；
   - license 必须允许训练与商业使用。
5. **合成/增强数据**
   - 适合扩充图像退化、背景、布局、签名位置；
   - 只能补 coverage，不能替代真实 adversarial forgery 与真实 prevalence。

### 2.2 场景矩阵：不要只说“多收一些 diverse data”

采样计划应显式覆盖以下 axes，并统计每个 cell 的数量与错误：

| Axis | 需要覆盖的 slice |
|---|---|
| Capture | native PDF、flatbed scan、mobile photo、fax、screenshot、复印再扫描 |
| Image | 72–600 DPI、blur、noise、JPEG artifacts、shadow、glare、perspective、rotation |
| Signature | full/partial/clipped、浅色笔、粗/细笔、多行、initials、简写、极简签名 |
| Background | 纯白、签名线、表格线、印章重叠、文字穿过、logo、水印、复杂纹理 |
| Document | 合同、支票、保险表、医疗表、税表、多语言、不同客户 template |
| Placement | 固定 ROI、任意位置、多签名、签名跨框、签名贴在错误 field |
| Signer variation | 同人跨天/跨年、受伤/年龄变化、惯用手变化、不同书写工具 |
| Attack | random、simple、skilled、trace、copy-paste、print-scan、synthetic generation |
| Operational | 新设备、新 scanner firmware、新压缩 pipeline、新国家/客户/季度 |

**不要平均采样生产 prevalence 就结束。** rare but costly 的 fraud 在自然流量中太少：训练和压力测试应过采样，最终校准与业务指标则要按真实 base rate 重加权。

### 2.3 Label schema：标签必须和决策相匹配

```text
DocumentLabel
  document_type, template_id, capture_type, device_family, quality_tags

SignatureInstance
  polygon, is_signature, signature_type
  target_field_id, claimed_signer_id
  clipped, occluded, blur_level, contrast_level, reviewer_confidence

VerificationPair / Episode
  query_signature_id, reference_set_id
  same_signer: true|false|unknown
  negative_type: random|simple|skilled|trace|copy_paste|synthetic
  acquisition_time_gap, device_pair, adjudication_status
```

Labeling 流程：

- detection 用 polygon/bbox 标注；难例允许 `ambiguous`，不要逼标注员猜；
- verification 的“同一签署人”需要可信身份 provenance，不能靠两个 annotators 看起来像就当事实；
- 欺诈标签应来自调查/专家 adjudication，普通众包只适合定位和质量标签；
- 每批加入 gold checks、重复标注和 adjudication；按 label type 报 inter-annotator agreement；
- 保留 raw label、annotator、指南版本、adjudication 过程，不只保留最终数字；
- OCR 姓名/日期分开标 `value + source span`，另标 signature-to-field link。

### 2.4 最容易犯的 leakage：按图片随机切分

错误做法：把同一个人的 20 张签名随机分到 train/test。模型可能记住 signer identity，而不是学到可迁移的 genuine-vs-imposter relation；相同模板背景、重复扫描件也会泄漏。

至少建立四个测试层：

| Split | 验证什么 |
|---|---|
| Unseen sample / seen signer | 同一已知 signer 的日常变化 |
| Unseen signer | writer-independent generalization，是主 benchmark |
| Unseen template/device/customer | domain generalization，排除背景捷径 |
| Forward time split | 上线后未来分布、设备与攻击变化 |

切分单位优先级：`signer_id → source_document_id → acquisition_session → template/device`。近重复图用 perceptual hash / embedding dedup，且 dedup 必须在 split 前做。最终保留一个长期冻结的 **gold test**；active learning 数据不能偷偷流进去。

### 2.5 隐私、consent 与治理

签名可能同时是 PII、身份验证因子和某些法域下的 biometric/sensitive data。设计时应说：具体义务让 privacy/legal 确认，但技术上先按高敏感数据处理。

- data minimization：尽早裁出 ROI；不需要整份文件就不要把整页送入训练系统；
- consent / purpose limitation：用于完成业务不自动等于允许训练通用模型；
- encrypt in transit/at rest；raw image、identity mapping、embedding 分开存并最小权限访问；
- tenant/region isolation；训练导出有 lineage、审批和 immutable audit log；
- retention + user deletion：必须能由 `signer_id/document_id` 找到 raw、crop、embedding、cache 和派生训练版本；
- 日志不记录 raw signatures；debug UI 默认遮蔽其他 PII；
- vendor/VLM API 只有在合同、region、no-training guarantee 满足时使用；
- embedding 不是“匿名数据”：它仍可能被 link、窃取或用于 membership inference。

---

## 3. 数据短缺与长尾：不是一句“做 augmentation”

### 3.1 数据短缺的类型与对应策略

| 缺什么 | 有效策略 | 不够好的捷径 |
|---|---|---|
| 每个 signer 样本少 | writer-independent metric learning；reference-set aggregation；好的 enrollment UX | 给每个 signer 单独训练 classifier |
| 新 template | layout-agnostic detector + 少量 template calibration；hard negative mining | 只记固定坐标 |
| skilled forgery 少 | 专门采集 red-team 数据；专家/调查结果；高风险默认 review | 把随机他人签名当作所有 forgery |
| 低质手机图少 | 可解释的 camera degradation augmentation + 真实 mobile shadow set | 任意强 blur，破坏真实结构 |
| 新语言/书写系统 | 分层采样、targeted collection、per-script slice eval | 假设拉丁签名模型自然迁移 |
| 标注预算少 | weak supervision、teacher prelabel + 人工确认、active learning | 用模型预测直接当 gold |

### 3.2 Augmentation 要保持 label semantics

适合 detection/quality 的增强：

- rotation/perspective、crop/partial occlusion；
- blur、sensor noise、JPEG/fax compression、contrast/illumination；
- ink color/width variation、background texture、table line/stamp overlay；
- 把真实签名 alpha-blend 到不同**合法许可**的表单背景，生成 bbox/polygon 免费标签；
- print → scan 模拟，但参数应由真实设备统计拟合。

对 verification 要更保守：轻微几何/光学变化通常保持 identity，但过度 elastic deformation 可能改变人的书写特征。增强策略要在真实 held-out 上做 ablation；`augmentation severity` 也记录进训练 trace。

### 3.3 Synthetic data 的正确位置

生成模型可以：

- 生成 layout/background/quality 长尾；
- 产生候选难负例，用于 adversarial training；
- 作为 pretraining/curriculum 的一部分。

但不能直接宣称“synthetic forgery 上 99% = 真实防伪 99%”。生成器留下的 artifact 会成为捷径，真实攻击者也不遵循生成器分布。上线 gate 必须由真实、隔离、时间外推的 forgery set 决定，并单独报告 synthetic→real transfer。

### 3.4 Weak supervision、self-supervision 与 active learning

- Weak labels：已知模板的 signature box、PDF digital-signature annotation、人工 workflow 的“要求重签”、表单 field anchor；先估计各规则的噪声，不把规则当真值。
- Self-supervised pretraining：对大量许可的未标注文档 crop 做 masked-image / contrastive learning，再用少量精标微调。
- Teacher-student：较大 detector/VLM 只做 prelabel 或离线 fallback，人确认后再进入训练；student 为生产小模型。
- Active learning：选 uncertainty、ensemble disagreement、novel embedding clusters、new template、high-loss slice 和疑似 fraud；同时保留 **随机审计样本**，否则只标灰区会失去生产 prevalence 和 calibration。

一个健康的采样 batch 可以是：

```text
40% uncertainty / gray-zone
20% detector-verifier-human disagreement
15% novel cluster / new device / new template
15% high-risk or confirmed downstream error
10% uniform random production sample  ← 用来估计真实质量，不能删
```

人工 correction 进入候选池后先做 QA、dedup、consent check；训练集 append，新一代 test set 仍冻结。

---

## 4. 模型设计：默认选择可诊断的 cascade

### 4.1 推荐架构

```text
PDF / Image
   │
   ├─► Secure decode + page render + malware/input checks
   │
   ├─► Native PDF / cryptographic e-sign path ─► 独立验证证书与文档完整性
   │
   ▼
Preflight quality + document/template router
   │                └─ unusable ─► recapture / review
   ▼
Signature detector / segmenter ─► zero / one / many ROI
   │
   ├─► OCR + layout graph ─► signer name/date/title + signature-field linking
   │
   ├─► type / quality / tamper classifiers
   │
   ▼
Signature normalization ─► writer-independent embedding model
                               │
Reference gallery ─► quality-weighted reference aggregation
                               │
                         similarity + auxiliary evidence
                               ▼
                  calibrated score + risk policy
                     /            |            \
                  ACCEPT        REVIEW        REJECT
```

为什么先用 pipeline 而不是一个 end-to-end VLM：

- 每段有独立 labels/metrics，能定位是 detector、OCR link、quality 还是 verifier 错；
- 可按文档走不同成本路径；只对 crop 跑贵模型；
- verification threshold 可独立校准和审计；
- 更容易替换 detector 或 verifier，不必重训全部；
- 高风险场景需要 evidence 和 reason code，而不是自然语言“感觉相似”。

缺点是 error propagation：若 detector recall 是 99%、field linking 98%、verifier TAR 97%，理想化端到端召回上限只有 `0.99 × 0.98 × 0.97 ≈ 94.1%`。因此必须同时报告 stage-level 与 end-to-end 指标，并为低置信 detector 保留 fallback。

### 4.2 各阶段模型选择

**A. Preflight / quality**

- 轻量 CNN/ViT 预测 blur、glare、clip、resolution、perspective；
- 可以优先用 deterministic features：Laplacian blur、有效 DPI、边界截断、文件损坏；
- 产出 actionable reason：“签名右侧被裁切，请重拍”，比一个 quality score 有用。

**B. Detection / segmentation**

- MVP：YOLO/RetinaNet 类单阶段 detector，低延迟；
- 复杂文档/多个重叠对象：DETR 类 detector；
- 签名与线条/文字粘连严重：instance segmentation，polygon 比 bbox 更适合后续 normalization；
- 输入可先由 template/anchor 提供 ROI，但必须有 layout-agnostic fallback，避免坐标捷径。

训练 loss 示例：

\[
L_{det}=\lambda_{cls}L_{focal}+\lambda_{box}L_{GIoU}+\lambda_{mask}L_{Dice}
\]

hard negatives 要包含：手写日期、手写备注、印章、表格线、logo、scribble、空签名线。

**C. OCR + field association**

OCR 本身也可拆为 `text detection → line recognition → layout/field linking`，模型选择由版面与语言决定：

| 子问题 | 可选模型族 | 什么时候用 |
|---|---|---|
| Text detection | DBNet/CRAFT 类、轻量 detector | 任意版面先找 word/line polygon；大量稳定模板可先用 anchor ROI |
| Printed recognition | CRNN + CTC、Transformer recognizer | 规则印刷文本；CTC 解码快且不要求字符级对齐 |
| Handwriting recognition | TrOCR/encoder-decoder 类 | 姓名、日期等短手写字段；必须在目标 script/device 上微调与评估 |
| Layout understanding | LayoutLM 类（text+bbox）或 layout graph | 已有 OCR tokens，希望抽 field/entity/link |
| OCR-free extraction | Donut/vision encoder-decoder 或 VLM | 复杂低流量文档 fallback；成本、hallucination 和 source grounding 要单独控制 |

CTC recognizer 给图像特征序列上每个 timestep 预测字符/blank，通过对所有合法 alignment 求和训练，适合没有逐字符框的 line-level transcription。对于长文本、多语言和复杂 handwriting，attention/seq2seq 更灵活，但解码慢，也更容易生成图中没有的字符。因此高风险字段仍需词典/regex/schema validation 与 source crop。

实践流程：

- 有可靠 PDF text layer 时直接解析并与渲染像素对齐；text layer 异常/隐藏文本时再 OCR，防止被恶意 PDF 欺骗；
- printed text 走便宜 production OCR；手写姓名/日期才走 handwriting recognizer 或 VLM fallback；
- layout graph 的 node 是 text/signature boxes，edge feature 用距离、方向、field anchor、reading order、同一 row/column；
- 先检测 field 与 signature，再做 link classification，不能默认“最近的名字就是 signer”；
- schema/regex/domain validator 检查日期、姓名、签署角色；无 source span 则不自动写入；
- OCR confidence 也需要用 held-out correctness calibration，原始 beam probability 不能直接当字段正确率。

OCR 训练标签通常是 line crop + transcription；字符集先 normalize（Unicode、空白、日期格式），但保留 raw text 供审计。OCR 评估不能只有“整页准确率”：

\[
CER=\frac{S+D+I}{N}
\]

其中 `S/D/I` 是从 gold 到 prediction 的字符替换、删除、插入数。业务上还要报告 signer name/date 的 exact match、normalized field F1、signature-to-field link accuracy；一个日期错一位字符可能比普通正文整段 CER 更重要。

**D. Verification embedding**

采用 writer-independent Siamese / metric-learning encoder：

```text
query crop q ─► Encoder fθ ─► zq
reference ri ─► same Encoder ─► zi
score(q, R) = aggregate_i cosine(zq, zi), weighted by reference quality
```

可用 contrastive/triplet loss，或把 signer 当训练类别使用 ArcFace/CosFace 类 angular-margin objective，再在 unseen signer 上做 verification：

\[
L_{triplet}=\max(0, d(z_a,z_p)-d(z_a,z_n)+m)
\]

训练 batch 用 `P signers × K genuine samples`，确保有足够 positive pairs，并在相似签名、同姓、同模板间做 hard-negative mining。不能让同一扫描 session 的 duplicate 充当“多样 positive”。

reference aggregation 不应盲目平均：先拒绝低质量/异常 enrollment；对剩余 embedding 做 quality-weighted centroid 或与每个 reference 分别比较后稳健聚合。只有一张 reference 时增大灰区，不是假装 certainty 不变。

**E. Forgery / tamper evidence**

- copy-paste/复用检测：跨文档 perceptual/embedding near-duplicate search；
- image forensic cues：边缘、压缩块、背景不连续、不同噪声谱；
- PDF path：检查 object/edit history，但 metadata 只能当证据，不能单独作真值；
- cryptographic e-sign：验证 certificate chain、timestamp、document hash，走完全独立规则系统；
- skilled forgery：embedding + 专项 detector + policy；静态图像无法保证捕捉所有攻击。

### 4.3 通用 VLM 应该放在哪里

适合：

- 少样本阶段快速 bootstrap labels；
- 复杂页面的低流量 fallback；
- OCR/signature-field association 的 teacher；
- reviewer UI 中生成“为什么进入人工”的摘要。

不适合直接承担：

- 高 QPS 每页 inference；
- 需要严格 TAR@FAR calibration 的 1:1 verification；
- 无 source localization 的最终高风险判断；
- 敏感签名未经合同允许发送到外部 API。

策略：frontier model 离线做 teacher / labeler → 人工 QA → distill 到小型 detector/layout model；线上只在 small-model uncertainty 和高价值文档触发。

---

## 5. Decision、calibration 与 threshold：不要只报 accuracy

### 5.1 两种错误的业务代价不同

- **FMR / FAR（False Match/Accept Rate）**：冒名/伪造被接受，通常是安全损失；
- **FNMR / FRR（False Non-Match/Reject Rate）**：真实签名被拒，通常是用户摩擦与人工成本。

在真实欺诈 base rate 很低时，普通 accuracy 会被 genuine majority 淹没。EER 只适合模型比较，不是生产 operating point。生产更应报：

- `TAR @ FAR = 10^-3 / 10^-4`；
- 不同 forgery type 的 FAR；
- 不同设备、模板、质量、时间间隔、客户的 slice metrics；
- calibration（Brier/ECE/reliability diagram）；
- review coverage 下的 selective risk。

### 5.2 双阈值 + 人工灰区

```text
score >= T_accept  → ACCEPT
score <= T_reject  → REJECT 或要求重新签署
otherwise          → REVIEW
```

阈值不应该只追求最大 F1。理想 decision 是最小化条件期望损失：

\[
a^*(x)=\arg\min_{a\in\{accept,reject,review\}}
\sum_y P(y\mid x)C(a,y)
\]

实际中按业务风险分 policy：

- $50 的低风险 claim 可以扩大自动处理 coverage；
- $500K 转账、单 reference、可疑 copy-paste 应直接 review/step-up；
- 新客户/新设备在 calibration 数据不足时使用更保守阈值；
- threshold 变更作为 versioned policy 发布，不需要重训模型。

### 5.3 Score calibration

在与生产 prevalence、quality、reference count 接近的 held-out calibration set 上做 Platt scaling、isotonic regression 或 likelihood-ratio calibration。**训练集不能同时拿来校准。** 监控 score distribution 与 observed error；模型升级后旧 threshold 不可自动沿用。

---

## 6. Evaluation：离线、端到端与线上三层

### 6.1 Stage-level 指标

| Stage | 必看指标 | 必看 slice |
|---|---|---|
| Preflight | unusable recall、false recapture rate | capture/device、blur/glare/clipping |
| Detection | Recall、precision、mAP、IoU；文档级“是否漏掉任一签名” | template、signature size/type、重叠对象 |
| Quality/type | Macro-F1、per-class recall、calibration | rare type、新设备、低 DPI |
| OCR | CER/WER、field exact match/F1 | printed vs handwriting、语言、quality |
| Field linking | signature-to-name/date link accuracy | 多签名、多姓名、复杂表格 |
| Verification | ROC/DET、TAR@FAR、FMR/FNMR、EER（诊断） | forgery type、unseen signer、reference count、time gap |
| Identification | Recall@k、open-set detection/FAR | gallery size、unseen signer、相似姓名 |

### 6.2 End-to-end / workflow 指标

- 文档“所有必需 signer 都存在且关联正确”的 exact success rate；
- straight-through processing（STP）率；
- 人工审核率、审核分钟数/文档、review overturn rate；
- fraud loss / false rejection downstream outcome（有延迟 label 时分 cohort）；
- recapture rate 与完成率；
- P50/P95/P99 latency、availability、cost per 1K pages；
- 不同金额/客户/文档类型的 expected loss；
- 模型错误 vs data-quality 错误 vs policy 阈值错误的归因。

### 6.3 Benchmark 组成

至少维护：

1. clean canonical set；
2. production-distribution random holdout；
3. hard-quality set（blur/fax/clipped/overlap）；
4. real fraud/red-team set（按 attack type）；
5. unseen signer/template/device/customer set；
6. forward-time set；
7. synthetic stress set——单独报告，不能混成主要分数；
8. privacy/security tests（跨 tenant 检索、删除、日志泄漏、malformed input）。

每次 model/policy 发布做 paired comparison；关键安全 slice 不允许被 aggregate improvement 掩盖。先 shadow，再 canary，再 gradual rollout；所有 prediction 保存 version、threshold、输入质量特征和路由原因以便重放。

---

## 7. Production architecture 与 cost-efficient serving

### 7.1 服务架构

```text
Client / Batch Upload
        │
        ▼
API Gateway + Auth + Rate Limit
        │  content hash / idempotency key
        ▼
Secure Intake ─► Object Store (encrypted, region/tenant scoped)
        │
        ▼
Job Controller / Queue ─────────────────────────────┐
        │                                            │
        ├─► CPU preflight / native PDF fast path     │
        ├─► Detector workers (dynamic batch)         │
        ├─► OCR/layout workers                       │
        ├─► Verification + calibrated policy         │
        └─► Expensive fallback only when needed      │
                                                     ▼
                                  Artifact/Decision Store + Audit Trace
                                                     │
                                    ┌────────────────┴───────────────┐
                                    ▼                                ▼
                               Callback/API                    Review Queue/UI
                                                                     │
                                            corrections + outcomes ─► Data flywheel
```

可靠性：

- `content_hash + tenant_id + config_version` 做 artifact cache；同文档重试不重复推理；
- job/state 持久化，stage worker 幂等；大 PDF 页级 fan-out，最终 fan-in；
- queue 分 online/batch/high-risk lane，避免 backfill 挤占在线 SLA；
- timeout、bounded retry、DLQ；损坏/炸弹 PDF 在隔离 decoder 处理；
- 人工修正是 immutable correction，重跑不能静默覆盖；
- model、threshold、OCR engine、preprocessing 全部 pin version。

### 7.2 粗算规模（面试必须会）

假设日均 1,000 万页：

\[
10{,}000{,}000 / 86{,}400 \approx 116\ pages/s
\]

峰值 5 倍约 `580 pages/s`。若 detector 单 GPU dynamic batching 后稳定处理 100 pages/s，理论 6 张 GPU 覆盖峰值；加 40% headroom、rolling deploy 和故障冗余，先规划约 10 张，再用压测校正。不要把这个估算说成真实 benchmark。

真正成本常由人审主导：假设 5% 文档进入 review、每次 2 分钟、人工 $30/hour，则每 1000 文档人工成本：

\[
1000\times 5\%\times(2/60)\times \$30=\$50
\]

所以把 review rate 从 5% 降到 3%，在不增加 false accept 的条件下，往往比 GPU 再快 20% 更值钱。

### 7.3 成本优化按收益排序

1. **先缩输入**：native PDF 不 OCR；template/anchor 先裁 ROI；合理 DPI/resize，不把整页原图送 verifier。
2. **级联路由**：deterministic checks → small quality model → detector → verifier；只有不确定/高价值样本走大模型。
3. **不做无意义阶段**：只查 presence 就不跑 identity verifier；没有 reference 时不伪造 verification。
4. **batch + async**：离线文档允许 dynamic batching；interactive recapture 走低延迟 lane。
5. **优化/蒸馏**：distillation、quantization、ONNX/TensorRT/CoreML；但必须按 slice 复测，细线签名可能对量化敏感。
6. **缓存与增量**：page hash、signature crop hash、reference embedding cache；reference 更新只重算 gallery，不重跑历史 OCR。
7. **autoscaling**：按 queue age + GPU utilization，不只按 CPU/QPS；预热模型避免冷启动毁掉 P99。
8. **压低人审时间**：UI 同屏展示 query、多个 reference、bbox、quality、reason code；不要只给一个分数让 reviewer 自己找页。

### 7.4 Edge / on-device 何时值得

手机端先做 blur/glare/clipping 与 recapture guidance，可以避免坏图上传、改善 conversion；最终高风险 verification 仍可在服务端做。优势是 latency/privacy，代价是设备碎片、模型更新、可被篡改和算力受限。

---

## 8. Security、fraud 与 abuse

### 8.1 Threat model

- replay：重复提交一张真实签名；
- copy-paste：从旧文档抠出签名贴到新文档；
- print-scan：用打印/复印抹去编辑痕迹；
- random/simple/skilled/traced forgery；
- diffusion/generative signature；
- enrollment poisoning：攻击者把假 reference 注册成可信样本；
- adversarial/malformed image/PDF，资源耗尽；
- insider/data exfiltration、gallery/embedding 泄漏；
- model probing/extraction，批量试分数找到 threshold。

### 8.2 防御是多信号系统，不是单模型

- enrollment 是根信任：身份校验、capture provenance、reference 更新需 step-up/approval；
- document hash、metadata、image forensic、near-duplicate search、business context 联合；
- high-value transaction 使用设备/账户/行为信号与 second factor；
- rate limit、score 不对外暴露过细、检测 probing pattern；
- gallery access 按 tenant/signer scoped，embedding 加密并可 rotation/version；
- adversarial red-team 持续采样，新 attack family 独立 slice；
- 低置信/异常不是强行二分类，进入 review 或重新采集；
- 人审也有安全边界：双人复核高金额、审计、role-based access、防 reviewer 被模型分数 anchoring。

> 高分句：离线签名模型只是 risk signal，不是 cryptographic proof。风险越高，越需要独立信号和 step-up authentication。

---

## 9. Monitoring、drift 与持续学习

### 9.1 实时可观测性

**系统指标**：QPS、queue age、stage latency、GPU/CPU utilization、OOM、timeout、decode failure、cost/1K pages。

**输入/数据指标**：DPI、resolution、blur、compression、capture type、template/device/customer mix、signature size/position、多签名比例。

**模型指标（无即时 gold）**：

- detector confidence/box count/box size 分布；
- quality/type 分布；
- embedding norm、distance-to-reference、accept/review/reject 分布；
- OCR null rate、validator failure、stage disagreement；
- novel-cluster rate、out-of-distribution score；
- 与 control model 的 shadow disagreement。

**延迟 gold 指标**：human overturn、重签结果、客户争议、chargeback/confirmed fraud、申诉成功率。按 prediction cohort 和 model/policy version join，不能只看当天总数。

### 9.2 Drift 不只是一个 KL 数字

先按业务可行动 slice 定位：新 scanner firmware 造成 blur，还是新 template 让 detector 漏检，还是 attacker 改变 forgery？聚合 embedding drift 只能报警，不能解释。

发现漂移后的顺序：

1. 验证 telemetry/label pipeline 没坏；
2. slice 定位 affected traffic；
3. 暂时收紧 threshold/扩大 review 或回滚；
4. targeted labeling / data collection；
5. shadow retrain，过 frozen + forward-time + attack gates；
6. canary 发布并持续看 delayed outcomes。

### 9.3 Feedback loop 风险

如果只人工检查模型送入 REVIEW 的样本，就永远不知道 ACCEPT 中的错；如果把 ACCEPT 当 genuine label，模型会强化自己的偏差。必须：

- 对 auto-accept 做稳定的随机 audit；
- 从下游 outcome 获取独立标签；
- correction 与 prediction 分开存；
- 训练 sampling 重加权回 production distribution；
- 发布前用不受线上模型选择影响的 frozen benchmark。

---

## 10. 10 分钟口述答案（可以直接练）

### 0:00–1:00｜先消歧与假设

> “我先澄清 signature recognition 的含义。检测签名、验证声称身份、从 gallery 识别人、判断质量，以及 OCR 邻近姓名，是五个不同任务。我假设这里是金融/保险的离线 PDF 或手机图：先检测和质量检查，再用 1–5 张可信 reference 做 1:1 verification，同时抽取姓名和日期。系统只提供 risk decision，灰区人审，不单凭静态图自动做法律结论。请问规模、延迟、允许的人审率和 false accept 目标是什么？”

### 1:00–2:00｜成功、输出与风险

> “输出不是一个裸分数，而是 signature bbox、质量问题、linked fields 和 source span、verification score、calibrated probability、decision/reason，以及 model/policy version。安全指标是 TAR@指定 FAR 和高风险 slice 的 false match；业务指标是端到端成功、STP、人审率、延迟和每千页成本。accept/reject/review 用两个阈值，阈值按金额与 reference 数量等风险调整。”

### 2:00–4:00｜数据计划

> “先用有合法用途的生产数据覆盖真实设备和模板，再做 consented collection：同一 signer 要跨天、不同笔纸设备收 genuine，并收 random、skilled、trace、copy-paste 等 forgery。显式建 capture、quality、background、template、signer variation、attack 的矩阵。label 包括 signature polygon、type/quality、claimed signer、reference provenance、pair genuine/forgery subtype，以及 OCR source span。验证标签需要可信身份或专家 adjudication，不能靠看起来像。”
>
> “切分是关键：按 signer、source document、session、template/device 去重切分；主 benchmark 是 unseen signer，再加 unseen customer/device 和 forward-time。否则随机图片 split 会让模型记住人或模板。数据不足时用真实退化增强、弱监督和 self-supervised pretraining；合成数据主要补 layout/quality 与产生候选 hard negatives，但上线 gate 必须是真实 held-out fraud。active learning 选 uncertainty、disagreement、novel cluster，同时保留随机 audit 估计真实质量。”

### 4:00–6:00｜模型与主流程

> “我先做可诊断 cascade。安全 decode/PDF render 后，native cryptographic e-sign 走独立验证；图像做 quality/template routing。小 detector 或 segmenter 找签名 ROI；OCR/layout graph 抽姓名日期并关联；quality/type/tamper 模型提供辅助信号。verification 用 writer-independent Siamese/metric-learning encoder，把 query 和可信 references 映射为 embedding，quality-weighted aggregation 后校准分数。训练使用 P×K signer batch、triplet 或 angular-margin loss、相似签名 hard negatives。”
>
> “一个 end-to-end VLM 可做 teacher、prelabel 和低流量 fallback，但高 QPS/high-risk 不直接依赖它：难校准、贵、隐私和 localization 都弱。pipeline 的缺点是错误传播，所以 stage 与 end-to-end 都测，低置信 detection 有 fallback。”

### 6:00–7:30｜Eval 与 threshold

> “detection 看 recall/mAP，OCR 看 field exact/F1，field link 单独测；verification 不看普通 accuracy，主要看 unseen-signer TAR@FAR、FMR/FNMR、不同 forgery type、设备、质量、reference count 和 time gap，并测 calibration。维护 production-random、hard-quality、real attack、unseen-domain、forward-time、synthetic stress 七类集合，synthetic 分数不与真实主分数混在一起。阈值由 expected cost 决定；高金额、单 reference、新域扩大 review。”

### 7:30–9:00｜Production 与成本

> “架构上是 intake、object store、durable queue、页级 workers、decision store 和 review UI；content/config hash 幂等缓存，online/batch lane 分离，model/preprocess/threshold 全版本化。日均一千万页约 116 pages/s，5 倍峰值约 580。成本先通过 native-PDF fast path、ROI crop、small-model cascade、dynamic batch、quantization 和缓存优化；贵模型只处理不确定样本。人工往往更贵，所以 reviewer UI 和 calibration 对总成本比 GPU 微优化更重要。”

### 9:00–10:00｜安全、监控与收尾

> “威胁包括 replay、copy-paste、print-scan、skilled/generated forgery 和 enrollment poisoning。模型只是一个信号，要叠加 reference provenance、near-duplicate、forensic、账户/设备上下文与 step-up。线上监控输入质量、模板/device mix、score/decision 分布、novel clusters、人工 overturn 和延迟 fraud outcome；auto-accept 保留随机审计，防 feedback loop。上线 shadow→canary→gradual，漂移时先扩大 review/回滚再补数。最大的 trade-off 是 coverage、fraud risk 与人工成本；我会从保守阈值启动，用独立 outcome 数据逐步扩大自动化。”

---

## 11. 高频追问与标准回答

### Q1：每个人只有 1–3 张 reference，怎么办？

不用 per-person classifier，而用 unseen-signer 上训练的 writer-independent metric model。严格做 enrollment quality gate；多 reference 用 quality-weighted aggregation；一张 reference 时加宽 REVIEW 区间或要求 step-up。若 reference 很久以前采集，time gap 是 calibration feature，但不要未经验证就做每人阈值。

### Q2：没有足够 forgery 数据怎么办？

先区分 random negative 与 skilled forgery，它们不是同一难度。用其他 signer 的真实签名做 random negatives；专门付费收集 imitation/traced 样本、从确认案例建立受控 hard set、用生成器产生候选 adversarial negatives。模型可由 synthetic 训练，但 release gate 必须在真实隔离 forgery 和 red-team 上通过；高风险流量保持人审。

### Q3：为什么不是普通 OCR？

OCR 目标是恢复字符序列，而签名的判别信息包括整体笔形、相对结构和书写习惯，且许多签名不可读。OCR 可以抽签名旁边的 printed/handwritten name/date，但不能把转录文本等同于签名身份验证。

### Q4：为什么不直接用 GPT/VLM 判断真假？

通用 VLM 可做页面理解或 teacher，但 1:1 verification 需要稳定 embedding、成对数据、TAR@低 FAR 的评估和可校准阈值。VLM 自然语言置信度通常不是生产 probability，而且整页推理贵、隐私和定位更难。可以让它处理复杂低流量 fallback，但不能跳过独立 benchmark。

### Q5：训练集怎么构造 pairs？pair 数量不是会爆炸吗？

不预生成所有 O(N²) pairs。每个 batch 采 P 个 signer、每人 K 个样本，在线构造 positives 与 negatives；做 semi-hard/hard-negative mining，但混入随机 negatives 防止训练分布过窄。采样单位是 acquisition session，避免 duplicate positives。

### Q6：threshold 怎么定？

先在独立 calibration set 上将 similarity 校准；然后根据 `false accept loss、false reject loss、review cost` 选择 accept/reject 两阈值。高金额/单 reference/新 domain 可用更保守 policy。EER 只是模型对比点，不是生产阈值。上线后用随机审计与 delayed outcome 验证。

### Q7：不同用户使用不同 threshold 吗？

初期不要在每人样本极少时过拟合 per-user threshold。先按有足够样本的风险/质量/reference-count/domain bucket 做 calibration；只有 signer 历史足够且有严格 shrinkage/regularization 时才考虑个性化。否则以扩大 review 代替虚假精确度。

### Q8：如何处理新客户的新表单？

layout-agnostic detector 是底座；template router/anchors 只做 fast path。新客户先 shadow，抽样标 detection/field link，检查 OOD 与 score calibration；保守阈值/高 review 启动。active learning 优先 novel clusters 和 false positives，达到 slice gate 后再扩大 STP。

### Q9：如何发现模型走了 template background 捷径？

做 unseen-template/customer split；把同一签名放到不同背景、把不同签名放到同背景做 counterfactual；可视化 attribution 只是提示，真正证据是背景 randomization 后性能与跨模板 holdout。crop 应尽量保留必要 stroke、减少身份无关背景。

### Q10：如何处理同一人签名随时间变化？

采集跨月/跨年 genuine，时间切分评估 FNMR vs time gap；允许经过强身份验证的 reference refresh，旧新 reference 保留版本和 provenance。不能直接把模型判定的近期签名加入 gallery，否则一次 false accept 会污染未来。

### Q11：reference enrollment 被攻击怎么办？

enrollment 是 root of trust：必须依赖独立身份验证、设备/操作审计、双重确认或人工流程。reference update 是高风险写操作，不由 verifier 自己决定；所有版本可回滚，异常更新触发 alert。

### Q12：如何降低 production cost？

先做业务路由而不是盲目压模型：native PDF fast path、template ROI、只对检测出的 crop 跑 verifier、无 reference 不跑 verification、small-to-large cascade、batch/quantize/cache。再看人审：把灰区 probability 校准好、UI 给 evidence，常比 GPU 优化收益更大。始终报告 cost@quality，不单报 cost。

### Q13：如何衡量公平性？

签名风格与设备、身体能力、年龄变化、语言/书写系统、客户流程相关。只在合法、必要且可治理的属性上做 slice audit；重点比较 FMR/FNMR、recapture/review burden 和 calibration，且保证足够样本与置信区间。发现差异先检查采集/设备/label bias，再 targeted collection；不能简单删掉 subgroup。

### Q14：线上没有即时真值，如何监控？

实时看输入、score、decision、OOD、stage disagreement；用稳定 random audit 估计 accept error，用人工 overturn、重签、争议和 confirmed fraud 做延迟标签。所有 outcome 按原 prediction/model/policy cohort 回连。proxy 漂移只触发调查，不直接等同 accuracy 下降。

### Q15：检测和验证要不要 joint training？

先分开，数据标签、调试和替换更简单。若数据量足够，可共享视觉 backbone 或多任务训练提高效率，但仍保留 stage-specific heads、metrics 和 artifact。只有 end-to-end benchmark 证明 joint 模型在关键 slice 提升且可校准，才切换。

### Q16：什么时候应该要求用户重拍，而不是送人审？

当错误是可行动的采集问题——blur、glare、clipped、DPI 过低——且用户仍在线时，立即 recapture 通常更便宜、更可靠；当图像足够但身份分数灰区、文档复杂或疑似 fraud 时送 review。quality model 要输出具体 remediation。

### Q17：online signature 有什么不同？

可用 x/y trajectory、pressure、velocity、acceleration、pen-up/down、stroke order，模型可用 sequence Transformer/RNN/DTW + metric learning；安全性通常高于静态图，但输入设备 shift 更明显。仍需 enrollment provenance、anti-replay、设备校准和独立 threshold。

### Q18：如何做 human review UI？

同屏展示 query crop、多个 reference、原页 bbox、质量问题、近重复/forensic signals；隐藏默认总分或先让 reviewer 独立看，减少 anchoring。支持 accept/reject/recapture/uncertain 和 reason code；高风险双人复核。人工改动不可被重跑静默覆盖。

### Q19：合成数据如何证明有用？

做 controlled ablation：相同真实训练集，加入 synthetic 后比较真实 unseen-domain、hard-quality、real-forgery test，而不是在 synthetic test 上自证。检查不同 synthetic ratio，监控是否学到 generator artifact；只有真实指标和 calibration 改善才保留。

### Q20：如果只给两周做 MVP？

把 scope 限为 presence detection + quality + fixed-template ROI，不承诺身份 verification。用许可数据/生产抽样标 bbox，训练轻 detector；低置信全人工；建 unseen-template holdout、API/trace/版本和 review correction。verification 需要可信 reference、pair labels 和风险校准，作为下一阶段独立上线。

---

## 12. 三个主动 Trade-offs

1. **Pipeline vs end-to-end**：pipeline 易调试、校准、成本路由，但有 error propagation；先 pipeline，只有端到端模型在关键 holdout 显著提升且仍可审计时替换。
2. **Automation coverage vs fraud / review cost**：扩大 accept 区间降低人审但提高 false match；按 expected loss、金额和 independent signals 决策，从保守开始。
3. **Global model vs tenant/template specialization**：global model 对新域迁移好；tenant adapter/threshold 可提升已知客户，但维护、数据隔离、过拟合成本高。先 global backbone + versioned per-domain calibration，数据充分才加 adapter。

---

## 13. 面试前一页速记

```text
1. 消歧：detect / quality / verify 1:1 / identify 1:N / OCR-link；offline vs online
2. 风险：业务动作、FAR 目标、人审率、reference provenance、attack model
3. 数据：prod + consented collection + licensed + synthetic supplement
4. 矩阵：capture × quality × background × template × signer variation × attack
5. 标签：polygon + type/quality + claimed signer + pair subtype + provenance
6. 防泄漏：split by signer/document/session/template/device；forward-time；dedup
7. 稀缺：metric learning、P×K batch、hard negative、SSL、active + random audit
8. Pipeline：preflight → detect → OCR/link → quality → embed → calibrate → policy
9. 模型：detector/segmenter + layout graph + Siamese/ArcFace；VLM teacher/fallback
10. 指标：detection recall；field F1；TAR@FAR；FMR/FNMR；calibration；STP/cost
11. 决策：T_accept / T_reject；灰区 review；按 expected loss 和风险分 policy
12. 成本：native PDF、ROI、cascade、batch、quantize、cache；human cost first-class
13. 安全：replay/copy-paste/skilled/gen/enrollment poisoning；多信号 + step-up
14. 监控：input/score/OOD + random audit + delayed outcome；shadow→canary→rollback
15. 收尾：静态签名模型是 risk signal，不是 cryptographic proof
```

> 一句话收尾：高质量方案不是“找一个最强视觉模型”，而是用可信 reference 和无泄漏数据训练可校准的专用模型，在真实攻击与未来域上评估，再用双阈值、人审和多信号把错误成本管住。

---

## 14. 延伸阅读（理解方法，不背 benchmark 数字）

1. [TrOCR](https://arxiv.org/abs/2109.10282)：预训练视觉 Transformer + 文本 Transformer，并用 synthetic pretraining、human-labeled fine-tuning 处理 printed/handwritten/scene text；它支持 OCR recognizer 的选择，不代表签名验真。
2. [A writer-independent approach for offline signature verification](https://arxiv.org/abs/1807.10755)：说明 writer-independent、global/user-specific threshold 与 unseen-writer evaluation 的核心区别。
3. [OSVNet](https://arxiv.org/abs/1904.00240)：online signature 的 Siamese/metric-learning 思路；online trajectory 比静态图像多 pressure、velocity、stroke-order 等信号。
4. [Writer Independent Offline Signature Recognition Using Ensemble Learning](https://arxiv.org/abs/1901.06494)：多来源数据与 writer-independent offline verification 的一个案例；读它时重点审视 dataset split、forgery 类型和跨域外推，不把单一 benchmark 分数当生产保证。
