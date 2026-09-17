#!/usr/bin/env python3
"""
关卡 3-5 · RAG 进阶（填空版）

核心：三个进阶技巧——chunking（切块）、混合检索（dense 向量 + sparse BM25）、
rerank（重排），并对比效果。1-3 的 RAG 只做了「整篇文档 → 向量检索」；
这关补上「文档怎么切」「怎么既召得准又召得全」「召回后怎么再精排」。

执行流程图（python3 042.py）：

长文档
  └─ chunking：按固定窗口 + 重叠切成若干块                       ← 填空 1
       └─ 对每个 chunk 建索引：
            ├─ dense 向量（字符 bigram 余弦）                    ← 填空 2
            └─ sparse 词频（简化 BM25）
       └─ 查询：dense 分 + sparse 分加权融合 → 混合检索          ← 填空 3
            └─ rerank：对 top-k 用 LLM 重排，选最相关            ← 填空 4
       └─ 对比打印：dense-only vs hybrid vs hybrid+rerank 的命中顺序

三个核心概念（面试 30 秒）：
  1. chunking：文档太长会「稀释」语义，切成小块（带重叠防切断），检索命中更精准
  2. 混合检索 = dense（语义相近）+ sparse（关键词命中），互补：dense 懂意思，sparse 不漏专有名词
  3. rerank：粗召回（快但糙）后用精排模型/LLM 对 top-k 重排，把最相关的顶上去
本文件为了零依赖，dense 用「字符 bigram 余弦」手写、sparse 用「词频」手写，思路和生产一致，
只是生产换 sentence-transformers / bge-reranker 这类真模型。

依赖：无第三方库；rerank 用 DeepSeek（pip3 install openai，没 key 可改填空 4 用 rerank_local 纯本地版）。

规则：
  1. 下面有 4 个空，填对了才能跑通。
  2. 卡住看 answers-038-042.md（关卡 3-5 那节）。
  3. 跑通：打印出三种检索方式的命中顺序对比。
"""

import re
import math
from collections import Counter
from openai import OpenAI

client = OpenAI(
    api_key="sk-你的key",               # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 长文档（关键句故意把「混合检索」和「重排序」放一起，方便验证 rerank 能顶到最前）
DOC = (
    "RAG 即检索增强生成，先检索相关文档再让 LLM 生成答案，能解决幻觉和知识过时问题。"
    "Embedding 把文本映射成高维向量，语义相近的文本向量方向接近。"
    "向量数据库如 Chroma、Milvus、pgvector 专门存储和检索高维向量。"
    "混合检索把稠密向量检索和稀疏关键词检索结合，再配合重排序 rerank 精排，召得更准更全。"
    "分块 chunking 把长文档切成小块，带重叠防止切断语义。"
)


# ── 填空 1 ──────────────────────────────────────
# 按固定窗口切块，块与块之间保留重叠
def chunk(text, size=30, overlap=8):
    chunks = []
    step = size - overlap
    for i in range(0, len(text), ________):        # ← 填空 1：步长（窗口减重叠）
        chunks.append(text[i:i + size])
    return chunks


CHUNKS = chunk(DOC)


# ── dense 向量：字符 bigram 手写（生产换成 sentence-transformers）
def bigrams(s):
    s = re.sub(r"\s+", "", s)
    return [s[i:i + 2] for i in range(len(s) - 1)]


def vec(text):
    return Counter(bigrams(text))


def cosine(a, b):
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[w] * b[w] for w in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    # ── 填空 2 ──────────────────────────────────
    # 余弦相似度 = 点积 / (|a| * |b|)
    # 提示：dot 已算好，na/nb 是两个向量的模长
    return ________                                # ← 填空 2：余弦公式


# ── sparse 检索：简化 BM25（词频 + 逆文档频率）
def tokenize(s):
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z]+", s)


IDF = Counter()
for c in CHUNKS:
    for term in set(tokenize(c)):
        IDF[term] += 1
N = len(CHUNKS)


def bm25_score(query, chunk):
    score = 0.0
    cterms = tokenize(chunk)
    for t in tokenize(query):
        if t not in cterms:
            continue
        tf = cterms.count(t)
        idf = math.log((N - IDF[t] + 0.5) / (IDF[t] + 0.5) + 1)
        score += idf * tf
    return score


# ── 混合检索：dense + sparse 加权融合
def hybrid_score(query, chunk, alpha=0.5):
    d = cosine(vec(query), vec(chunk))
    s = bm25_score(query, chunk)
    # ── 填空 3 ──────────────────────────────────
    # 加权融合：alpha 权重给 dense，(1-alpha) 给 sparse
    # 提示：dense 和 sparse 量纲不同，生产会先各自归一化，这里简化直接加权
    return ________                                # ← 填空 3：融合公式


# ── rerank：对 top-k 用 LLM 精排（生产可用 bge-reranker 交叉编码器）
def rerank_with_llm(query, candidates):
    ranked = []
    for c in candidates:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是检索相关性裁判。给「查询」和「候选文本」的相关性打分 0-10，只输出数字。"},
                {"role": "user", "content": f"查询：{query}\n候选：{c}\n请打分："},
            ],
            temperature=0,
        )
        try:
            score = float(resp.choices[0].message.content.strip())
        except ValueError:
            score = 0.0
        ranked.append((score, c))
    ranked.sort(key=lambda x: -x[0])
    return ranked


def rerank_local(query, candidates, scorer):
    """本地精排：直接用混合分重排（不调 LLM 的降级版）"""
    scored = [(scorer(query, c), c) for c in candidates]
    scored.sort(key=lambda x: -x[0])
    return scored


if __name__ == "__main__":
    query = "混合检索和重排序是什么"
    print("=" * 55)
    print("  RAG 进阶：chunking / 混合检索 / rerank 对比")
    print("=" * 55)
    print(f"\n长文档切成 {len(CHUNKS)} 块（窗口 30，重叠 8）：")
    for i, c in enumerate(CHUNKS):
        print(f"  [{i}] {c}")

    # ① dense-only：只按向量余弦
    dense_only = sorted(CHUNKS, key=lambda c: -cosine(vec(query), vec(c)))
    print("\n① dense-only 命中顺序：", [CHUNKS.index(c) for c in dense_only[:3]])

    # ② hybrid：dense + sparse 融合
    hybrid = sorted(CHUNKS, key=lambda c: -hybrid_score(query, c))
    print("② hybrid 命中顺序：   ", [CHUNKS.index(c) for c in hybrid[:3]])

    # ③ hybrid + rerank：对 top-3 再用 LLM 精排
    top3 = hybrid[:3]
    # ── 填空 4 ──────────────────────────────────
    # 调用 rerank 函数对 top3 精排，取重排后的顺序
    # 提示：rerank_with_llm 返回 [(分数, 文本), ...] 已按分数降序
    #      没有 key 可改用 rerank_local(query, top3, hybrid_score)
    reranked = ________                            # ← 填空 4：调用哪个函数精排
    print("③ hybrid+rerank 顺序：", [CHUNKS.index(c) for _, c in reranked])

    print("\n（人工看：正确答案是覆盖「混合检索」和「重排序 rerank」的块——第 5、6 块，")
    print("它们应该排到最前；这也正好演示了为什么要「带重叠」切块，避免关键词被拦腰切断）")
