#!/usr/bin/env python3
"""
关卡 2-3 · 协作式 Multi-Agent（对话/辩论）（完整版）

核心：协作式（Collaborative）——两个 agent 多轮对话，互相补充/质疑，直到达成一致。
和流水线的区别：流水线是单向流动，协作式是双向对话。

执行流程图（python3 collab.py）：

[话题]
  └─ agent_a 提出方案
       └─ 循环 N 轮：
            ├─ agent_b 回应（补充/质疑）
            ├─ agree() 判断是否一致？
            │    ├─ 一致 → 结束
            │    └─ 不一致 → agent_a 继续回应 → 下一轮
  └─ 输出共识

方法调用关系：
  agent_a() ──> llm()（提方案/回应）
  agent_b() ──> llm()（补充/质疑）
  agree() ──> client.chat.completions.create（判是否一致）

面试怎么讲（30 秒）：
  "协作式是多个 agent 多轮对话，互相质疑补充直到一致，适合「需要多角度、开放式」的
  问题（方案评审、头脑风暴）。缺点是轮数不可控、成本高、可能陷入循环争论。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)


def llm(system, user):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def agent_a(context):
    """agent A：提出方案"""
    return llm("你是技术专家 A，提出简洁可行的方案。", f"讨论背景：\n{context}")


def agent_b(context, a_says):
    """agent B：回应 A，补充或质疑"""
    return llm(
        "你是技术专家 B，审视 A 的方案，补充优点或指出风险，最后给出你的看法。",
        f"讨论背景：\n{context}\n\nA 的方案：\n{a_says}",
    )


def agree(a_says, b_says):
    """判断两位专家是否达成一致"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "判断两位专家的意见是否基本达成一致，只输出「一致」或「不一致」。"},
            {"role": "user", "content": f"A: {a_says}\nB: {b_says}"},
        ],
        temperature=0,
    )
    return "一致" in resp.choices[0].message.content


if __name__ == "__main__":
    topic = "新项目应该用微服务还是单体架构？"
    print("=" * 55)
    print("  协作式 Multi-Agent：两个 agent 辩论")
    print("=" * 55)

    context = f"话题：{topic}"
    a_says = agent_a(context)
    print(f"\n🤖 A：{a_says}")

    for round_i in range(3):
        b_says = agent_b(context, a_says)
        print(f"\n🤖 B：{b_says}")
        if agree(a_says, b_says):
            print("\n✅ 两位专家达成一致！")
            break
        # 不一致，A 继续回应
        a_says = llm(
            "你是技术专家 A，回应 B 的质疑，调整或坚持你的方案。",
            f"讨论背景：{context}\n\nB 的观点：{b_says}",
        )
        print(f"\n🤖 A：{a_says}")
    else:
        print("\n⚠️ 达到轮数上限，未完全一致")
