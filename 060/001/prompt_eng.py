#!/usr/bin/env python3
"""
关卡 1-13 · Prompt 工程（完整版）

核心：同一个任务，换个问法，结果天差地别。四种经典技巧：
  零样本 zero-shot   —— 直接问，不给例子
  few-shot           —— 给几个例子，让模型照着学
  CoT (思维链)       —— 加一句「一步步想」，逼模型展示推理
  角色设定           —— 给一个身份，改变回答风格/严谨度

执行流程图（python3 prompt_eng.py）：

同一个任务 → 用四种 prompt 分别调 LLM → 对比四个答案

方法调用关系：
  zero_shot()/few_shot()/cot()/role_play() ──> call() ──> client.chat.completions.create

面试怎么讲（30 秒）：
  "Prompt 工程核心是换问法。零样本直接问，few-shot 给例子，CoT 加『一步步想』
  逼出推理过程（能显著提正确率），角色设定改风格。实际常用 few-shot + CoT 组合。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 一道容易答错的题（很多人会直觉算错）
TASK = "一个水池，进水管单独注满要 3 小时，排水管单独排空要 4 小时。同时开两根，几小时注满？"

# 给 few-shot 用的类似例题（已解好，让模型照着这个套路走）
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
    """直接问，不给任何提示"""
    return call("你是助手。", f"请解答：{TASK}")


def few_shot():
    """先给一个解好的例题，让模型照着学"""
    return call("你是助手。", f"先看这个例题：\n{EXAMPLE}\n\n现在用同样的方法解答：{TASK}")


def cot():
    """加一句「一步步思考」，逼模型展示推理过程"""
    return call("你是助手。", f"请一步步思考，展示每一步计算过程，最后给出答案：{TASK}")


def role_play():
    """给一个角色身份，改变严谨度和风格"""
    return call("你是一位严谨的小学数学老师，批改过上千道应用题。",
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
