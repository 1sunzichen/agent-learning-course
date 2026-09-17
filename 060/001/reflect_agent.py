#!/usr/bin/env python3
"""
关卡 1-7 · Reflection 自我修正（完整版）

核心：让 agent 执行完任务后「反思」自己的结果，发现错误再重试，直到修对。
这是从 ReAct（每步想）和 Plan-and-Execute（先规划）再往前走一步：执行完还能「回头看」。

执行流程图（python3 reflect_agent.py）：

【第一轮】solve(题目) ──────────> LLM 直接作答 → answer_1
【反思】  reflect(题目, answer_1) ─> LLM 当批改老师挑错 → feedback
【第二轮】solve(题目, feedback) ─> LLM 带着反思意见重做 → answer_2
【对比】  打印两轮答案，看第二遍是否修对了

和 ReAct / Plan 的区别：
  ReAct：想一步 → 做一步 → 看结果（过程驱动）
  Plan-and-Execute：先规划 → 再执行（全局驱动）
  Reflection：执行 → 反思 → 重试（结果驱动，回头看）

方法调用关系：
  solve() ──> client.chat.completions.create（作答，可带反思意见）
  reflect() ──> client.chat.completions.create（批改，找错）

面试怎么讲（30 秒）：
  "Reflection 是让 agent 在产出结果后，把结果再喂给 LLM 让它自我批判、找错，
  带着批判意见重跑一遍。本质是用 LLM 当自己的 critic，能显著降低简单错误。
  这是 Reflexion 框架的核心思想。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 一道容易算错的题：进水管 3h 注满，排水管 4h 排空，同时开几小时注满？
# 正确做法：1 / (1/3 - 1/4) = 1 / (1/12) = 12 小时
PROBLEM = "一个水池，进水管单独注满要 3 小时，排水管单独排空要 4 小时。同时打开两根管子，几小时能注满？"


def solve(problem, feedback=None):
    """让 LLM 解一道题。feedback 是上一轮反思的意见（可选）"""
    messages = [
        {"role": "system", "content": "你是一个解题助手。请给出答案，并写清楚计算步骤。"},
    ]
    if feedback:
        # 第二轮：把反思意见喂回去，让 LLM 知道上次错在哪
        messages.append({"role": "user", "content": f"题目：{problem}\n\n你上一轮的答案可能有错，这是反思意见：\n{feedback}\n\n请重新作答："})
    else:
        messages.append({"role": "user", "content": f"题目：{problem}\n请作答："})
    resp = client.chat.completions.create(
        model="deepseek-chat", messages=messages, temperature=0,
    )
    return resp.choices[0].message.content


def reflect(problem, answer):
    """让 LLM 反思自己的答案，找出错误"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个严格的批改老师。仔细检查下面的解答，找出错误，给出改进意见。如果答案正确就说「答案正确」。"},
            {"role": "user", "content": f"题目：{problem}\n\n学生的解答：\n{answer}\n\n请批改："},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print("=" * 50)
    print("  题目：" + PROBLEM)
    print("=" * 50)

    print("\n【第一轮 · 直接作答】")
    answer_1 = solve(PROBLEM)
    print(answer_1)

    print("\n" + "=" * 50)
    print("【反思 · 让 LLM 当批改老师挑自己的错】")
    print("=" * 50)
    feedback = reflect(PROBLEM, answer_1)
    print(feedback)

    print("\n" + "=" * 50)
    print("【第二轮 · 带着反思意见重做】")
    print("=" * 50)
    answer_2 = solve(PROBLEM, feedback)
    print(answer_2)
