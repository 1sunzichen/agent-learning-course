"""
关卡 1-15 · 缓存策略（填空版）

核心：相同请求不重复花钱。两种缓存：
  结果缓存    —— 相同问题直接返回上次答案（本地做）
  prompt 缓存 —— 相同前缀输入 token 打折（服务端做）

执行流程图（python3 015.py）：

问题 → 查本地结果缓存
  ├─ 命中 → 直接返回（0 成本）        ← 填空 1
  └─ 未命中 → 调 LLM → 存进缓存 → 返回  ← 填空 2、3

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-15 那节）。
  3. 跑通：第二次问同样的问题，直接走缓存、几乎 0 耗时。
"""

import time
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

_cache = {}   # 结果缓存：问题 → 答案


def ask(question):
    """带结果缓存的提问：相同问题直接复用"""
    # ── 填空 1 ──────────────────────────────
    # 查结果缓存：如果这个问题问过，直接返回缓存答案，不调 LLM
    # 提示：判断 question 在不在 _cache 里，命中就返回缓存值
    if question in _cache:                                  # ← 填空 1
        return _cache[question] + "（缓存，0 成本）"
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": "你是一个助手，简洁回答。"},
                  {"role": "user", "content": question}],
        temperature=0,
    )
    answer = resp.choices[0].message.content
    # ── 填空 2 ──────────────────────────────
    # 把这次的真实答案存进缓存，下次同样的问题就能直接复用
    # 提示：_cache[question] = answer
    _cache[question] = answer                               # ← 填空 2
    # ── 填空 3 ──────────────────────────────
    # 返回答案，并标注「真实调用」（区分于缓存的「0 成本」）
    return answer + "（真实调用）"                           # ← 填空 3


if __name__ == "__main__":
    q = "什么是 Python 的装饰器？用一句话回答。"
    print("=" * 55)
    print("  缓存策略演示")
    print("=" * 55)

    print("\n第 1 次问：")
    t0 = time.time()
    print(" ", ask(q))
    print(f"   耗时 {time.time() - t0:.2f}s")

    print("\n第 2 次问（相同问题）：")
    t0 = time.time()
    print(" ", ask(q))
    print(f"   耗时 {time.time() - t0:.4f}s  ← 走缓存，几乎 0 耗时 0 成本")
