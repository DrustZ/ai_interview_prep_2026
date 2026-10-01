# [A8] 500GB 模型权重分发到 100–1000 GPU worker · 完整解答

⏱ 读完 14 min ｜ 建议先自己限时 50min 答一遍再看（重点：数学要能白板当场推）。题面原文见 [../A_scenario_design.md](../A_scenario_design.md#a8)，原始题解见 [../../../online_resource/1p3a-anthropic.md](../../../online_resource/1p3a-anthropic.md)（Model Distribution 一节）。

## 题目还原

把 500GB 模型权重分发到数据中心内 100–1000 台 GPU worker，总时间最短、容忍故障。约束：云端（S3/GCS）下载出口 10Gbps；每 worker 全双工 10Gbps（同时收 10Gbps + 发 10Gbps 互不挤占）。目标：100 台约 8 分钟、容忍 1–5% worker 故障、支持增量更新与回滚。**真正在考**：带宽数学（当场算三种方案）、链式 pipeline + chunk 化、故障绕接协议、以及落盘后的原子切换/回滚——又是"AI 皮、分布式系统骨"：这题的骨是受限带宽下的广播（broadcast）问题。

## 开场澄清（6 问 + 为什么问）

1. **"分发完成"定义到哪一层**：落盘校验通过就算，还是要加载进 GPU 显存开始服务？——决定要不要讲原子切换、双进程蓝绿与推理进程重载（我默认要，这是加分主场）。
2. **频率与形态**：每天一次全量新模型，还是频繁小增量（fine-tune/patch）？——决定 content-addressed chunk 去重值不值得建。
3. **网络拓扑**：单数据中心？rack 内/跨 rack 带宽一致吗（有无 oversubscription）？——决定链序要不要 rack-aware。
4. **故障模型**：1–5% 指分发期间崩溃率？慢节点（degraded NIC）算不算故障？Coordinator 允许单点吗？
5. **一致性要求**：全集群必须同时切同版本（原子），还是允许滚动混版本？回滚 SLA 多少？——混版本会导致同请求不同行为，推理集群通常要原子切。
6. **worker 本地盘**：容量够存两个版本吗（500GB×2 + 余量）？NVMe 持续写带宽 ≥1.25GB/s 吗？——否则瓶颈在盘不在网，全部数学都要重算。

## 答案主线（按 [../../02_playbook.md](../../02_playbook.md) 时间盒）

**开场 90 秒（背下来）**："这是受限带宽下的广播问题。我先算三种拓扑的时间证明链式 pipeline 最优，再给 coordinator/manifest/worker 三块的接口与状态，然后走 setup→seeding→pipeline→finalize 四阶段主流程，深挖故障绕接与原子切换，最后谈 10K 台的分层扩展和回滚。控制面归 coordinator，数据面 worker 之间自治泵 chunk——coordinator 挂了传输不停。"

### 0–10min 需求 + 带宽数学（这题要求当场算，先算再画图）

目标谓词：`给定 version V 的 manifest，所有 target worker 在 T 内本地校验通过并原子切到 V；任一 worker 故障不阻塞其余；可一步回滚到 V-1`。

```text
记 F=500GB, B=10Gbps=1.25GB/s, N=100, chunk c=1GB

下界：F/B = 500/1.25 = 400s ≈ 6.7min      # 一台收满 500GB 的物理下限
方案一 全员直连 S3：出口 10Gbps 被 N 台均分
  每台 0.1Gbps → 500GB/12.5MB/s ≈ 11 小时   # 出口是瓶颈，最差
方案二 二叉树：父节点上行带宽均分给 2 个孩子
  根下载 400s，之后每层 2F/B=800s × log2(100)≈7 层 ≈ 100 分钟
方案三 链式 pipeline（chunk 化，收到即转发）：
  T ≈ F/B + (N-1)·c/B = 400s + 99×0.8s ≈ 480s ≈ 8 分钟 ✓
  N=1000：400+799≈20min；缩 c=256MB → 400+200≈10min
关键洞察：全双工让每台同时收满 10Gbps、发满 10Gbps——
链（fan-out=1）是唯一不均分任何上行带宽的拓扑，逼近 F/B 下界。
```

主动点出：8 分钟目标 ≈ F/B + 传播项，题目的数字就是在暗示链式答案。

### 10–18min 接口与数据模型

```text
Coordinator API（control plane）:
  createDeployment {model_id, version, source_url, targets[]}
  getDeploymentStatus(deployment_id)     # 进度条 = 全体 bitmap 汇总
Worker API:
  register {worker_id, rack_id, disk_free, nic_bw}
  heartbeat {worker_id, status, chunks_bitmap(压缩), per_hop_throughput}
  fetch_chunk(chunk_idx)                 # worker 间 P2P 补缺用

Manifest（先于数据分发，数据面只认它）:
  {model_id, version, chunk_size, num_chunks,
   chunks: [{idx, sha256, size}], global_checksum}
WorkerState（存 etcd，coordinator 可故障转移）:
  {worker_id, status, bitmap, upstream, downstream, rack_id}
```

### 18–30min 架构图与主流程

```text
            Coordinator（leader election，状态在 etcd）
             │ 定链序(rack-aware) / 收 heartbeat / 指挥绕接
 control     │
─────────────┼────────────────────────────────────────────
 data        ▼
S3 ─10Gbps─► W1 ──► W2 ──► W3 ──╳──► W5 ──► ... ──► W100
   (唯一出口下载者)   每台：收 chunk → SHA256 校验 → NVMe 落盘 → 立刻转发
                      W4 挂: coordinator 指挥 W3.downstream=W5, bitmap diff 补缺
每台 worker 落盘: /models/{id}/{ver}.tmp/ → 全量校验 → rename →
                  coordinator 收齐 ready → 广播 activate → 原子 flip symlink
```

**四阶段**：① Setup：coordinator 生成 manifest（500 × 1GB chunk + 每块 SHA256 + 全局校验和），按 rack 排序定链——同 rack 相邻，跨 rack 只跳一次（cross-rack 链路少且可能 oversubscribed）。② Seeding：W1 从 S3 拉 chunk 0，落盘即转发 W2，同时继续拉 chunk 1——出口带宽只被 W1 一人用，不均分。③ Pipeline：每台跑两个循环——receive loop（收→校验→落盘）和 send loop（本地有即发下游）；校验不过的 chunk **绝不转发**，向上游重要，防止污染扩散到下游全链。④ Finalize：每台做全量 global_checksum，报 ready；coordinator 等齐后进入切换（深挖 3）。

### 30–46min 深挖与可靠性（见下）｜ 46–54min 验证与观测 ｜ 54–60min Trade-offs

**验证与观测（这题的 "eval"）**：指标 = makespan、per-hop throughput、bitmap 进度（进度条）、chunk 校验失败率、切换后健康探针。**checksum 只保证字节对，不保证模型好**——activate 前先金丝雀：5% worker 切新版本跑 golden prompts 比对输出分布，通过再全量切；权重被训练层面搞坏（如 checkpoint 导出错误）只有这层能抓到。Staging 常态化 chaos 演练：kill 链中 worker、kill coordinator、注入慢节点。

## 深挖 3 处

### 深挖 1：为什么 pipeline 优于树形（数学证明，必被追问）

面试官会反驳"树也可以 chunk 化流水线"。完整答法：树 fan-out=k 时，父节点要把**每个 chunk 发 k 份**，有效每子带宽 B/k → 流水线化的树 T ≈ **k·F/B** + log_k(N)·c/B。k=2 时第一项就是 800s，是链（k=1，400s）的两倍——瓶颈在"每字节要上传几次"，链上每台每字节恰好收一次、发一次，带宽利用率 100%。树赢的场景只有一个：N 大到链的线性传播项 (N-1)·c/B 压过 F/B——N=10K、c=1GB 时传播项 8000s 反超，这就引出分层（深挖 2 的 10K 扩展）。主动把这个反超点说出来是 senior 信号：**链不是普适最优，是"传播项 ≪ F/B"范围内最优**。

### 深挖 2：链中间 worker 挂了（协议细节）+ 10K 扩展

- **检测**：heartbeat 2s 间隔、3 次超时判死（~6s）；下游也会报"上游停发"作为旁证。
- **绕接**：coordinator 把 W4 标 failed，指令 `W3.downstream = W5`；W5 用 bitmap diff 向 W3 声明缺口，从缺的最小 chunk 续传——**已收的不重传，损失 ≈ 检测 6s + 协商 <1s**，不是重新开始。下游 W6...W100 无感知（它们本来就落后几个 chunk，气泡被吸收）。
- **特殊位置**：W1（seed）挂 → 提升 bitmap 最全的 W2 当 seed，用 HTTP Range 从 S3 断点续传；恢复的 W4 从链尾重新接入 + bitmap diff 补缺。
- **慢节点（straggler）**：链吞吐 = 最慢一跳，一台 degraded NIC 卡全链。per-hop throughput 进 heartbeat，持续 30s 低于阈值（如 6Gbps）→ 视同故障绕开、移到链尾自己补——**慢节点必须当故障处理，这是链式方案最大的软肋，主动说**。
- **10K worker**：分层——rack 内一条链（~40 台），每 rack 的 seed 组成顶层链/树；传播项变成 rack 内 40×0.8s + 顶层 250 hop，回到分钟级。或 BitTorrent 式 swarm（rarest-first、多 peer 并发拉）：无单链瓶颈、自愈强，代价是收敛时间不可预测、实现复杂度高一个量级（题库 [../A_scenario_design.md](../A_scenario_design.md#a8) 参考打法给的两条路）。

### 深挖 3：原子切换、回滚、增量更新

- **原子切换**：全程写 `/models/{id}/{version}.tmp/`，全量校验过后 rename 成正式目录（同文件系统 rename 原子）；coordinator 收齐全员 ready 再广播 activate；每台 flip `current` symlink → 推理进程双进程蓝绿：新进程 load 权重、readiness probe 通过后切流量、drain 旧进程。显存不够双载就分批滚动：每批退出服务 → 重载 → 回池，牺牲部分容量换零混版本窗口。
- **回滚**：本地保留上一版本目录（这就是澄清问盘容量 ≥2×500GB 的原因）→ 回滚 = flip symlink + 重载，**分钟级、零网络传输**。要害一句："回滚不走分发路径——如果回滚还要再传 500GB，等于没有回滚。"
- **增量更新**：chunk 按 content hash 寻址，新 manifest 与本地 bitmap diff，只传变了的 chunk——tokenizer/config/未动的 shard 免传。诚实边界：全量 retrain 几乎每字节都变，dedupe 收益≈0；增量只对 patch/局部微调有意义，别过度承诺。

## 失败模式与恢复（本题场景清单）

- **chunk 损坏**：收到即 SHA256 校验，失败向上游重要 1 次，再失败向 coordinator 要备源（换一个持有该 chunk 的 peer）；校验不过绝不转发。
- **coordinator 挂**：数据面自治——链已建好，worker 继续泵 chunk 不停；etcd leader election 秒级选出新 leader，heartbeat 重放恢复视图。lease/fencing 语义同 [../../03_gaps/scaling.md](../../03_gaps/scaling.md)：新旧 coordinator 并存时，指令带 epoch，worker 拒绝旧代指令。
- **盘慢/盘满**：部署前预检每台 free ≥ 1.2TB、NVMe 持续写 ≥1.25GB/s；不达标的机器不进链（放链尾慢慢补），防止它当 straggler 卡全链。
- **分发中新 worker 加入**：挂到链尾，bitmap 从零补；不插中间——插中间要重排两条边，尾部只加一条。
- **两个部署并发**：per-cluster 串行化（一次只跑一个全量分发），否则带宽对半、两个都超时；紧急 hotfix 用优先级抢占：暂停旧部署（bitmap 都在，可续传）先跑新的。

## Trade-offs 三条（主动说）

1. **链 vs swarm**：链确定性逼近带宽下界、实现简单，但对 straggler 敏感、绕接依赖 coordinator；swarm 自愈强、无单链瓶颈，但收敛不可预测。≤1000 台单 DC 我选 rack-aware 链 + 快速绕接，跨 region 或 10K+ 台再上分层/swarm——用规模信号触发，不提前造复杂度。
2. **chunk 大小**：太小协调元数据与请求开销大，太大流水线气泡大（下游等第一块的时间 = c/B）。约束是 `(N-1)·c/B ≪ F/B`；100–1000 台取 256MB–1GB，c=1GB 时每 hop 0.8s。
3. **push（coordinator 排链）vs pull（peer 自主拉）**：纯 push 全局最优但控制面重；纯 pull 自治容错但难保带宽最优。我混合：control plane push 定拓扑，data plane 用 bitmap diff 的 pull 补缺——正常路径吃 push 的最优性，故障路径吃 pull 的自愈性。

## 现实参照（只引本地已有链接/事实）

- **1p3a 原题解**：三方案数学（11h/100min/8min）、1GB chunk、rack awareness、heartbeat 绕接、etcd 存 coordinator 状态、常见错误清单（忘算时间、忘 checksum、把系统搞复杂）——[../../../online_resource/1p3a-anthropic.md](../../../online_resource/1p3a-anthropic.md)。
- **分层 / BitTorrent 式 swarm 作为 10K 扩展**：题库 [A8] 参考打法（[../A_scenario_design.md](../A_scenario_design.md#a8)）。
- **lease/fencing 与 leader election 的通用论证**（coordinator 故障转移、epoch 拒旧代指令）：[../../03_gaps/scaling.md](../../03_gaps/scaling.md) Lease + fencing 折叠节（Kleppmann 链接）。

> 高分句：链式 pipeline 的本质是"每字节每台只收一次、只发一次"——全双工下带宽利用率 100%，总时间逼近 F/B 物理下界；而回滚必须是本地 symlink flip，不走分发路径。
