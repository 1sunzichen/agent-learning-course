#!/usr/bin/env python3
"""
关卡 1-19 · 单 agent 评测（填空版）

核心：建 eval 集（问题+标准答案），跑一遍，用 LLM-as-Judge 判对错，算出通过率。

执行流程图（python3 019.py）：

EVAL_SET → for 每道题：agent 作答 → judge 判对错 → 统计通过率

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-19 那节）。
  3. 跑通：看到 5 道题的作答结果和最终通过率。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# ── 填空 1 ──────────────────────────────
# eval 集：(问题, 期望答案的关键点)
# 提示：放 5 个有标准答案的简单问题，元组格式 (问题, 关键点)
EVAL_SET = [
    ("中国有多少个生肖","12"),
    ("中国的首都是哪里？", "北京"),
    ("水的化学式是什么？", "H2O"),
    ("一年有几个季度？", "4"),
    ("太阳系最大的行星是哪个？", "木星"),

]   # ← 填空 1：补全 5 道测试题


def agent(question):
    # ── 填空 2 ──────────────────────────────
    # 被测的 agent：直接问 LLM 得到答案
    # 提示：client.chat.completions.create，messages 只有 user 一条，temperature=0
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role":"user","content":question}
        ],
        temperature=0,
    )   # ← 填空 2：补全 LLM 调用
    return resp.choices[0].message.content.strip()


def judge(question, answer, expected):
    # ── 填空 3 ──────────────────────────────
    # LLM-as-Judge：判断答案是否正确
    # 提示：system 说「你是阅卷老师，只输出对或错」，user 带上问题/标准/学生答案
    resp =  client.chat.completions.create(
        model="deepseek-chat",
        messages=[
           {"role": "system", "content": "「你是阅卷老师，只输出对或错」"},
           {"role": "user","content":f"这个是问题{question},标准是{expected},答案是{answer}"},
        ],
        temperature=0,
    )    # ← 填空 3：补全 LLM 调用，并 return 判断结果（"对" in 结果）
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
