#!/usr/bin/env python3
"""
关卡 2-3 · 协作式 Multi-Agent（对话/辩论）（填空版）

核心：两个 agent 多轮对话，互相质疑补充，直到达成一致。

执行流程图（python3 022.py）：

agent_a 提方案 → agent_b 回应 → agree 判是否一致 → 不一致 A 继续 → 循环直到一致

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-3 那节）。
  3. 跑通：看到 A、B 两位专家就微服务 vs 单体展开辩论，最终达成一致或到轮数上限。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
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
    # ── 填空 1 ──────────────────────────────
    # agent A：提出方案
    # 提示：system 说「你是技术专家 A，提出简洁可行的方案」，user 带上 context
    return llm("你是技术专家 A，提出简洁可行的方案", context)   # ← 填空 1：补全 system 和 user


def agent_b(context, a_says):
    # ── 填空 2 ──────────────────────────────
    # agent B：回应 A，补充或质疑
    # 提示：system 说「你是技术专家 B，审视 A 的方案」，user 带上 context 和 a_says
    return llm("你是技术专家 B，审视 A 的方案", f"专家A说:{a_says},这是我的建议{context}")   # ← 填空 2：补全 system 和 user


def agree(a_says, b_says):
    # ── 填空 3 ──────────────────────────────
    # 判断两位专家是否达成一致
    # 提示：system 说「只输出 一致 或 不一致」，user 带上 A 和 B 的话，
    #       最后 return 判断结果里是否含「一致」
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "只输出 一致 或 不一致"},
            {"role": "user", "content": f"A:{a_says},B:{b_says}"},
        ],
        temperature=0,
    )   # ← 填空 3：补全 messages，并 return 判断结果
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
        a_says = llm(
            "你是技术专家 A，回应 B 的质疑，调整或坚持你的方案。",
            f"讨论背景：{context}\n\nB 的观点：{b_says}",
        )
        print(f"\n🤖 A：{a_says}")
    else:
        print("\n⚠️ 达到轮数上限，未完全一致")
