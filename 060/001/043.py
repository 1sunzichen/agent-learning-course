#!/usr/bin/env python3
"""
关卡 3-8 · 检索质量评估（填空版）

核心：用 recall@k / NDCG@k / MRR 三个指标，把「检索好不好」从感觉变成数字。

执行流程图（python3 043.py）：

  ① 构造小数据集：3 个查询，每个带「相关文档集合」+「检索返回列表」
  ② 逐个指标计算：
       ├─ recall_at_k  ← 填空 1（召回率：命中了多少相关文档）
       ├─ ndcg_at_k    ← 填空 2（归一化折损累计增益：考虑排序位置）
       └─ mrr          ← 填空 3（平均倒数排名：第一个相关文档在第几名）
  ③ 打印每个查询的 recall/ndcg + 三个查询的平均 MRR

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-043-044.md（关卡 3-8 那节）。
  3. 跑通：看到每个查询的 recall@3 / ndcg@3 和整体 MRR。

（本关零第三方依赖，纯标准库，直接 python3 043.py 就能跑。）
"""
import math

# 每个查询：relevant 是「应该召回」的文档集合，retrieved 是「检索系统实际返回」的有序列表
QUERIES = [
    {"query": "向量数据库选型", "relevant": {"d1", "d2", "d3"}, "retrieved": ["d1", "d5", "d2"]},
    {"query": "embedding 中文模型", "relevant": {"d2", "d4"}, "retrieved": ["d9", "d2", "d4"]},
    {"query": "LangGraph 人审", "relevant": {"d7"}, "retrieved": ["d3", "d7", "d1"]},
]


def recall_at_k(relevant, retrieved, k):
    """召回率@k：检索返回的前 k 个里，命中了多少相关文档（占全部相关文档的比例）"""
    # ── 填空 1 ──────────────────────────────────────
    # 提示：取 retrieved 的前 k 个，和 relevant 求交集，再除以相关文档总数。
    #       前 k 个用切片 retrieved[:k]，交集用 set(...) & relevant。
    hits = len(set(retrieved[:k]) & relevant)
    return ________   # ← 填空 1


def ndcg_at_k(relevant, retrieved, k):
    """NDCG@k：考虑排序位置——相关文档排得越靠前，得分越高"""
    def dcg(rels):
        # 位置 i 从 0 起，对应排名 i+1，折扣 = 1 / log2(排名+1) = 1 / log2(i+2)
        return sum(rel / math.log2(i + 2) for i, rel in enumerate(rels))

    rels = [1 if d in relevant else 0 for d in retrieved[:k]]
    ideal_rels = sorted(rels, reverse=True)   # 理想排序：相关文档全排最前面
    dcg_val = dcg(rels)
    idcg_val = dcg(ideal_rels)
    # ── 填空 2 ──────────────────────────────────────
    # 提示：NDCG = DCG / IDCG。IDCG 为 0（一个相关都没有）时要返回 0，避免除零。
    return ________   # ← 填空 2


def mrr(list_of_pairs):
    """MRR：每个查询「第一个相关文档」出现在第几名，取倒数后求平均"""
    scores = []
    for relevant, retrieved in list_of_pairs:
        # ── 填空 3 ──────────────────────────────────────
        # 提示：遍历 retrieved，找到第一个在 relevant 里的文档，位置 rank（从 1 起），
        #       该查询贡献 1 / rank；一个都没找到就贡献 0。用 for...else 实现。
        for i, d in enumerate(retrieved):
            if d in relevant:
                scores.append(________)   # ← 填空 3
                break
        else:
            scores.append(0.0)
    return sum(scores) / len(scores)


if __name__ == "__main__":
    print("=" * 55)
    print("  检索质量评估：recall@k / NDCG@k / MRR")
    print("=" * 55)

    for q in QUERIES:
        rel, ret = q["relevant"], q["retrieved"]
        print(f"\n查询「{q['query']}」")
        print(f"  相关文档: {sorted(rel)}   检索结果: {ret}")
        print(f"  recall@3 = {recall_at_k(rel, ret, 3):.3f}")
        print(f"  ndcg@3   = {ndcg_at_k(rel, ret, 3):.3f}")

    pairs = [(q["relevant"], q["retrieved"]) for q in QUERIES]
    print(f"\nMRR（3 个查询平均）= {mrr(pairs):.3f}")
    print("\n✅ 三个指标都算出来了：recall 看「找没找全」，NDCG 看「排没排对」，MRR 看「第一条相关在哪」。")
