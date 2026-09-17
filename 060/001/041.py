#!/usr/bin/env python3
"""
关卡 3-4 · 评估 eval harness（填空版）

核心：建一个小 eval 集 + LLM-as-Judge，跑出通过率。这是「agent 写完了怎么知道好不好」
的工程答案——不能凭感觉，要量化。比 1-19 更进一步：固定 eval 集 + judge 结构化判定 + 通过率统计。

执行流程图（python3 041.py）：

[EVAL_SET 测试集]
  └─ for 每个 (question, expected)：
       ├─ agent(question)  → 调被测 agent/LLM 拿实际答案
       ├─ judge(...)       → 用另一个 LLM 当「阅卷老师」判对错
       └─ 记录 ✓/✗ + 答案
  └─ 汇总：通过率 = 答对数 / 总数

核心概念（面试 30 秒）：
  1. eval 集 =（问题, 期望关键点）的列表，固定住，每次改代码后重跑对比
  2. LLM-as-Judge = 用一个 LLM 判另一个 LLM 的答案，比字符串完全匹配宽容（语义对就给对）
  3. 通过率 = 量化指标；没有它，改一版代码不知道变好还是变坏

依赖：pip3 install openai

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-038-042.md（关卡 3-4 那节）。
  3. 跑通：打印出「通过率：N/5」那一行。
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-你的key",               # ← 换成你自己的 key
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
    """被测的 agent：直接问 LLM"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": question}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def judge(question, answer, expected):
    """LLM-as-Judge：判断答案是否正确，返回 True/False"""
    # ── 填空 1 ──────────────────────────────────
    # 写 judge 的 system prompt：严格的阅卷老师，只输出「对」或「错」
    # 提示：要点 = 角色（严格阅卷）、只看关键点是否满足、忽略措辞差异、只输出对/错
    system = ________                    # ← 填空 1
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content":
             f"问题：{question}\n标准答案关键点：{expected}\n学生答案：{answer}\n请判断对错："},
        ],
        temperature=0,
    )
    # ── 填空 2 ──────────────────────────────────
    # 从 judge 的输出里提取「对/错」判定，转成布尔值
    # 提示：judge 输出里只要包含「对」字就算对
    verdict = resp.choices[0].message.content
    return ________                      # ← 填空 2：布尔判定


if __name__ == "__main__":
    correct = 0
    print("=" * 50)
    print("  eval harness（LLM-as-Judge）")
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
    # ── 填空 3 ──────────────────────────────────
    # 算通过率（百分比，保留整数）
    # 提示：答对数 / 总数 * 100，用 round 取整
    rate = ________                       # ← 填空 3：通过率百分比
    print("\n" + "=" * 50)
    print(f"  通过率：{correct}/{total} = {rate}%")
    print("=" * 50)
