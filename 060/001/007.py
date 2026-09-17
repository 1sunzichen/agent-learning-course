"""
关卡 1-7 · Reflection 自我修正（填空版）

核心：让 agent 执行完任务后「反思」自己的结果，发现错误再重试，直到修对。
这是从 ReAct（每步想）和 Plan-and-Execute（先规划）再往前走一步：执行完还能「回头看」。

执行流程图（python3 007.py）：

【第一轮】solve(题目) ──────────> LLM 直接作答 → answer_1
【反思】  reflect(题目, answer_1) ─> LLM 当批改老师挑错 → feedback
【第二轮】solve(题目, feedback) ─> LLM 带着反思意见重做 → answer_2

和 ReAct / Plan 的区别：
  ReAct：想一步 → 做一步 → 看结果（过程驱动）
  Plan-and-Execute：先规划 → 再执行（全局驱动）
  Reflection：执行 → 反思 → 重试（结果驱动，回头看）

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-7 那节）。
  3. 跑通：能看到第一轮答案、反思意见、第二轮修正后的答案。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
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
        # ── 填空 1 ──────────────────────────────
        # 第二轮要把「反思意见」喂回给 LLM，它才知道上次错在哪
        # 提示：user 消息里拼上 problem 和 feedback
        messages.append({"role": "user", "content": f"题目：{problem}\n\n你上一轮的答案可能有错，这是反思意见：\n{feedback}\n\n请重新作答："})   # ← 填空 1
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
            # ── 填空 2 ──────────────────────────────
            # 批改老师要同时看到「题目」和「学生的解答」，才能判断对错
            # 提示：user 消息里拼上 problem 和 answer
            {"role": "user", "content": f"题目：{problem}\n\n学生的解答：\n{answer}\n\n请批改："},   # ← 填空 2
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
    # ── 填空 3 ──────────────────────────────
    # 反思意见不能白生成，必须传回 solve 的第二轮
    # 提示：solve 的第二个参数就是 feedback
    answer_2 = solve(PROBLEM, feedback)   # ← 填空 3
    print(answer_2)
