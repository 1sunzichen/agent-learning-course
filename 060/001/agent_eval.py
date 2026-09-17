#!/usr/bin/env python3
"""
关卡 1-19 · 单 agent 评测（完整版）

核心：agent 写完了，怎么知道它好不好？不能凭感觉，要建一个 eval 集——
一组（问题 + 标准答案），跑一遍，看通过率。这里用 LLM-as-Judge 判对错。

执行流程图（python3 agent_eval.py）：

[EVAL_SET 测试集]
  └─ for 每个 (question, expected)：
       ├─ 调 agent（LLM）得到实际答案
       ├─ 调 judge（LLM）判断「实际答案是否满足 expected」
       └─ 记录对/错
  └─ 统计通过率 = 答对数 / 总数

方法调用关系：
  agent() ──> client.chat.completions.create（被测 agent）
  judge() ──> client.chat.completions.create（LLM-as-Judge 判对错）

面试怎么讲（30 秒）：
  "评测 agent 要建 eval 集，用 LLM-as-Judge 判对错，量化成通过率。
  没有 eval，改一版代码不知道是变好了还是变坏了。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# eval 集：(问题, 期望答案的关键点)
EVAL_SET = [
    ("1+1 等于几？", "2"),
    ("中国的首都是哪里？", "北京"),
    ("水的化学式是什么？", "H2O"),
    ("一年有几个季度？", "4"),
    ("太阳系最大的行星是哪个？", "木星"),
]


def agent(question):
    """被测的 agent：就是直接问 LLM"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": question}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def judge(question, answer, expected):
    """LLM-as-Judge：判断答案是否正确"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是严格的阅卷老师。判断答案是否正确，只输出「对」或「错」。"},
            {"role": "user", "content": f"问题：{question}\n标准答案关键点：{expected}\n学生答案：{answer}\n请判断对错："},
        ],
        temperature=0,
    )
    return "对" in resp.choices[0].message.content


if __name__ == "__main__":
    correct = 0
    print("=" * 50)
    print("  单 agent 评测（LLM-as-Judge）")
    print("=" * 50)

    for question, expected in EVAL_SET:
        answer = agent(question)
        ok = judge(question, answer, expected)
        if ok:
            correct += 1
        mark = "✓" if ok else "✗"
        print(f"\n  {mark} Q: {question}")
        print(f"    答: {answer}")
        print(f"    期望关键点: {expected}")

    total = len(EVAL_SET)
    print("\n" + "=" * 50)
    print(f"  通过率：{correct}/{total} = {correct/total*100:.0f}%")
    print("=" * 50)
