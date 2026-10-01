"""Drill C · PyTorch 手写 InfoNCE / 对比学习(第二轮 PyTorch 题主力)

⏱ timebox 25 分钟  ｜  概率评级:★★★★★(ML Research/Evals 第二轮)

为什么是这道题:Exa 自己预训练+微调 embedding 模型。「手写 contrastive loss」
是 embedding 训练最核心的一块,也是最容易在细节上翻车的一块。

冷写协议:
    cp drill_c_infonce_pytorch.py scratch.py -> 删实现体 -> 计时 25 分钟

五个必须记住的坑(面试官八成会挑其中一个问):
    1. **忘记归一化** -> 点积不是 cosine,温度的含义全变,训练不稳
    2. **温度是除不是乘**: logits = sim / T。T 越小分布越尖、对 hard negative
       越敏感;T 太小会梯度饱和
    3. **labels 是 arange(B)** —— 第 i 个 query 的正例是第 i 个 doc(对角线)
    4. **对称损失**: query->doc 和 doc->query 两个方向都要算(CLIP 的做法),
       只算一个方向会让两侧编码器学得不对称
    5. **batch 内重复正例 = 假负例**:同一篇文档出现两次,或两个 query 指向
       同一文档时,它会被当成别人的负例 -> 必须 mask 掉
"""

import torch
import torch.nn.functional as F

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def info_nce_in_batch(q: torch.Tensor, d: torch.Tensor,
                      temperature: float = 0.05,
                      symmetric: bool = True) -> torch.Tensor:
    """标准 in-batch negatives 版 InfoNCE。

    q: (B, dim) query 向量   d: (B, dim) 正例文档向量,d[i] 是 q[i] 的正例
    其余 B-1 个文档充当负例。

    返回标量 loss。
    """
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    logits = q @ d.t() / temperature          # (B, B),对角线是正例
    labels = torch.arange(q.size(0), device=q.device)
    loss = F.cross_entropy(logits, labels)
    if symmetric:
        # 反方向:每个 doc 找回自己的 query
        loss = 0.5 * (loss + F.cross_entropy(logits.t(), labels))
    return loss


def info_nce_with_hard_negatives(q: torch.Tensor, pos: torch.Tensor,
                                 negs: torch.Tensor,
                                 temperature: float = 0.05) -> torch.Tensor:
    """显式负例版:每个 query 自带一组挖来的 hard negatives。

    q:    (B, dim)
    pos:  (B, dim)
    negs: (B, N, dim)

    做法:把正例拼到负例前面 -> (B, 1+N),标签恒为 0。
    """
    q = F.normalize(q, dim=-1)
    pos = F.normalize(pos, dim=-1)
    negs = F.normalize(negs, dim=-1)

    pos_logit = (q * pos).sum(-1, keepdim=True)            # (B, 1)
    neg_logits = torch.bmm(negs, q.unsqueeze(-1)).squeeze(-1)  # (B, N)
    logits = torch.cat([pos_logit, neg_logits], dim=1) / temperature
    labels = torch.zeros(q.size(0), dtype=torch.long, device=q.device)
    return F.cross_entropy(logits, labels)


def build_false_negative_mask(doc_ids: torch.Tensor) -> torch.Tensor:
    """batch 内同一篇文档出现多次时,把「非自己位置的同一文档」标记出来。

    doc_ids: (B,) 每个位置对应的文档 id
    返回 (B, B) 的 bool mask,True = 需要屏蔽的假负例(不含对角线)。
    """
    same = doc_ids.unsqueeze(0) == doc_ids.unsqueeze(1)     # (B, B)
    eye = torch.eye(len(doc_ids), dtype=torch.bool, device=doc_ids.device)
    return same & ~eye


def info_nce_masked(q: torch.Tensor, d: torch.Tensor, doc_ids: torch.Tensor,
                    temperature: float = 0.05) -> torch.Tensor:
    """带假负例屏蔽的 InfoNCE。

    屏蔽方式是把对应 logit 设成 -inf,让它在 softmax 里权重为 0。
    注意:要在**除以温度之后**再填 -inf,顺序不影响结果但别写成 -1e9 加在
    归一化前(数值上不干净)。
    """
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    logits = q @ d.t() / temperature
    mask = build_false_negative_mask(doc_ids)
    logits = logits.masked_fill(mask, float("-inf"))
    labels = torch.arange(q.size(0), device=q.device)
    return F.cross_entropy(logits, labels)


def retrieval_accuracy(q: torch.Tensor, d: torch.Tensor) -> float:
    """batch 内 top-1 检索准确率,训练时最直观的健康指标。"""
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    pred = (q @ d.t()).argmax(dim=1)
    labels = torch.arange(q.size(0), device=q.device)
    return (pred == labels).float().mean().item()


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    torch.manual_seed(0)
    B, DIM = 8, 16

    # --- 完美对齐时 loss 应当接近 0 ---
    d = F.normalize(torch.randn(B, DIM), dim=-1)
    loss_perfect = info_nce_in_batch(d.clone(), d.clone(), temperature=0.05)
    assert loss_perfect.item() < 1e-3, loss_perfect.item()

    # --- 随机时 loss 应当接近 ln(B) ---
    q_rand, d_rand = torch.randn(B, DIM), torch.randn(B, DIM)
    loss_rand = info_nce_in_batch(q_rand, d_rand, temperature=1.0)
    import math
    assert abs(loss_rand.item() - math.log(B)) < 0.6, loss_rand.item()

    # --- 与手算 cross entropy 一致(非对称版) ---
    qn, dn = F.normalize(q_rand, dim=-1), F.normalize(d_rand, dim=-1)
    logits = qn @ dn.t() / 0.05
    manual = -torch.log_softmax(logits, dim=1).diag().mean()
    got = info_nce_in_batch(q_rand, d_rand, 0.05, symmetric=False)
    assert torch.allclose(manual, got, atol=1e-6)

    # --- 对称版 = 两个方向的平均 ---
    rev = -torch.log_softmax(logits.t(), dim=1).diag().mean()
    sym = info_nce_in_batch(q_rand, d_rand, 0.05, symmetric=True)
    assert torch.allclose(0.5 * (manual + rev), sym, atol=1e-6)

    # --- 忘记归一化会改变结果(证明这一步不是可选的) ---
    raw_logits = q_rand @ d_rand.t() / 0.05
    raw_loss = F.cross_entropy(raw_logits, torch.arange(B))
    assert not torch.allclose(raw_loss, got, atol=1e-3), "归一化必须影响结果"

    # --- 温度效应:更小的温度让同样的排序产生更极端的 loss ---
    l_hot = info_nce_in_batch(q_rand, d_rand, 0.02, symmetric=False)
    l_cold = info_nce_in_batch(q_rand, d_rand, 1.0, symmetric=False)
    assert l_hot.item() > l_cold.item(), "随机初始化下,低温会放大惩罚"

    # --- hard negative 版 ---
    q = F.normalize(torch.randn(B, DIM), dim=-1)
    pos = F.normalize(q + 0.1 * torch.randn(B, DIM), dim=-1)     # 与 q 很像
    easy = F.normalize(torch.randn(B, 4, DIM), dim=-1)
    hard = F.normalize(q.unsqueeze(1) + 0.5 * torch.randn(B, 4, DIM), dim=-1)
    l_easy = info_nce_with_hard_negatives(q, pos, easy)
    l_hard = info_nce_with_hard_negatives(q, pos, hard)
    assert l_hard.item() > l_easy.item(), "hard negative 的 loss 必须更大"

    # --- 假负例屏蔽 ---
    doc_ids = torch.tensor([0, 1, 2, 2, 4, 5, 6, 7])   # 位置 2、3 是同一篇文档
    mask = build_false_negative_mask(doc_ids)
    assert mask[2, 3] and mask[3, 2]
    assert not mask[2, 2] and not mask[0, 1]
    assert mask.sum().item() == 2

    l_plain = info_nce_in_batch(q_rand, d_rand, 0.05, symmetric=False)
    l_masked = info_nce_masked(q_rand, d_rand, doc_ids, 0.05)
    assert l_masked.item() <= l_plain.item() + 1e-6, \
        "屏蔽掉一个负例后 loss 不应变大"
    assert torch.isfinite(l_masked), "-inf 屏蔽后仍须是有限值"

    # --- 梯度确实回传 ---
    p = torch.randn(B, DIM, requires_grad=True)
    info_nce_in_batch(p, d_rand).backward()
    assert p.grad is not None and torch.isfinite(p.grad).all()
    assert p.grad.abs().sum() > 0

    # --- 真训一小步,loss 必须下降、batch 内 top-1 必须上升 ---
    torch.manual_seed(1)
    docs = F.normalize(torch.randn(B, DIM), dim=-1)
    qv = torch.randn(B, DIM, requires_grad=True)
    opt = torch.optim.Adam([qv], lr=0.1)
    first = info_nce_in_batch(qv, docs).item()
    acc0 = retrieval_accuracy(qv.detach(), docs)
    for _ in range(120):
        opt.zero_grad()
        loss = info_nce_in_batch(qv, docs)
        loss.backward()
        opt.step()
    last = info_nce_in_batch(qv, docs).item()
    acc1 = retrieval_accuracy(qv.detach(), docs)
    assert last < first, (first, last)
    assert acc1 >= acc0

    print("  全部断言通过")
    print("  完美对齐 loss = {:.6f}   随机 loss ≈ ln(B) = {:.4f}".format(
        loss_perfect.item(), math.log(B)))
    print("  easy negatives loss = {:.4f}   hard negatives loss = {:.4f}".format(
        l_easy.item(), l_hard.item()))
    print("  训练 120 步: loss {:.4f} -> {:.4f}   batch top-1 {:.2f} -> {:.2f}".format(
        first, last, acc0, acc1))


if __name__ == "__main__":
    print("Drill C · PyTorch InfoNCE")
    _tests()
    print("""
面试追问预演:
  Q batch size 为什么对 contrastive 这么重要?
  A in-batch negatives 的数量就是 B-1。B 越大,softmax 的分母里负例越多,
    梯度信号越强、估计的对比分布越接近全库。所以业界会用很大的 batch
    (几万级),工程上靠 gradient cache / 跨卡收集 in-batch negatives 实现。

  Q 温度怎么选?
  A 太小 -> softmax 饱和,梯度消失,而且对标注噪声极敏感;太大 -> 区分不出
    hard 和 easy。常见 0.01–0.1,要在 dev set 上扫。有些实现把它做成可学习
    参数(CLIP 就是,用 log 参数化并做上限裁剪)。

  Q 为什么要对称 loss?
  A 只算 query->doc 时,doc 侧编码器只通过负例得到梯度,两侧会学得不对称。
    CLIP 式对称损失让两个方向都有正例梯度。

  Q in-batch negatives 有什么隐患?
  A 假负例。batch 里可能混进对当前 query 也相关的文档,却被当成负例。
    两种处理:① 按文档 id 去重并 mask(本 drill 的 build_false_negative_mask);
    ② 更狠的做法是用 cross-encoder 给候选打分,过滤掉与正例太像的。
    这也是 Exa 放弃 MS Marco 式稀疏标注评测的同一个病根。

  Q 显存不够放大 batch 怎么办?
  A GradCache:先不建图跑一遍拿到所有 embedding 和对比矩阵的梯度,
    再分块重跑带图的前向把梯度接上。用两遍前向换 O(B) 显存。
""")
