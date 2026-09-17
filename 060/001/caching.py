#!/usr/bin/env python3
"""
关卡 1-15 · 缓存策略（完整版）

核心：相同请求不重复花钱。两种缓存：
  结果缓存    —— 相同问题直接返回上次答案，不调 LLM（本地做）
  prompt 缓存 —— 相同前缀的 prompt 命中服务端缓存，输入 token 打折（服务端做）

执行流程图（python3 caching.py）：

问题 → 查本地结果缓存
  ├─ 命中 → 直接返回（0 成本）
  └─ 未命中 → 调 LLM → 存进缓存 → 返回

方法调用关系：
  ask() ──> _cache 查/写（结果缓存）
       └─ client.chat.completions.create（未命中才调）

面试怎么讲（30 秒）：
  "缓存分两层：结果缓存（相同问题直接复用，本地做），prompt 缓存（相同前缀输入
  token 打折，服务端做）。都能显著省钱，但结果缓存要注意失效——答案会过期的不能乱缓存。"
"""

import time
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

_cache = {}   # 结果缓存：问题 → 答案


def ask(question):
    """带结果缓存的提问：相同问题直接复用"""
    if question in _cache:
        return _cache[question] + "（缓存，0 成本）"
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": "你是一个助手，简洁回答。"},
                  {"role": "user", "content": question}],
        temperature=0,
    )
    answer = resp.choices[0].message.content
    _cache[question] = answer
    return answer + "（真实调用）"


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
