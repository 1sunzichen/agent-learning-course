"""
关卡 1-13 · Prompt 工程（填空版）

核心：同一个任务，换个问法，结果天差地别。四种经典技巧：
  零样本 zero-shot  —— 直接问
  few-shot          —— 给例子
  CoT (思维链)      —— 加「一步步想」
  角色设定          —— 给身份

执行流程图（python3 013.py）：

同一个任务 → 用四种 prompt 分别调 LLM → 对比四个答案

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-13 那节）。
  3. 跑通：能看到四种问法给出不同风格的答案。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

TASK = "一个水池，进水管单独注满要 3 小时，排水管单独排空要 4 小时。同时开两根，几小时注满？"

EXAMPLE = """例题：进水管 2 小时注满，排水管 6 小时排空，同时开几小时注满？
解：进水速度 1/2，排水速度 1/6，净速度 = 1/2 - 1/6 = 1/3，所以 3 小时注满。答案：3 小时。"""


def call(system, user):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0,
    )
    return resp.choices[0].message.content


def zero_shot():
    return call("你是助手。", f"请解答：{TASK}")


def few_shot():
    # ── 填空 1 ──────────────────────────────
    # few-shot：先给一个解好的例题，再让模型用同样的方法解本题
    # 提示：把 EXAMPLE（例题）和 TASK（本题）拼进 user 消息
    return call("你是助手。", f"先看这个例题：\n{EXAMPLE}\n\n现在用同样的方法解答：{TASK}")   # ← 填空 1


def cot():
    # ── 填空 2 ──────────────────────────────
    # CoT：加一句「一步步思考」，逼模型展示推理过程（而不是直接蹦答案）
    # 提示：在 user 消息里明确要求「一步步思考、展示每一步、最后给答案」
    return call("你是助手。", f"请一步步思考，展示每一步计算过程，最后给出答案：{TASK}")   # ← 填空 2


def role_play():
    # ── 填空 3 ──────────────────────────────
    # 角色设定：给 system 一个具体身份，改变回答的严谨度和风格
    # 提示：system 写成一个具体的角色（如「严谨的小学数学老师」）
    return call("你是一位严谨的小学数学老师，批改过上千道应用题。",   # ← 填空 3
                f"请以老师的口吻解答：{TASK}")


if __name__ == "__main__":
    print("=" * 55)
    print("  题目：" + TASK)
    print("=" * 55)

    print("\n【零样本 zero-shot】直接问")
    print(zero_shot())

    print("\n" + "=" * 55)
    print("【few-shot 给例题】")
    print(few_shot())

    print("\n" + "=" * 55)
    print("【CoT 思维链】")
    print(cot())

    print("\n" + "=" * 55)
    print("【角色设定 数学老师】")
    print(role_play())
