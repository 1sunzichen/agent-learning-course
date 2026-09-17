#!/usr/bin/env python3
"""
关卡 2-4 · 竞争式 Multi-Agent（生成 + judge）（填空版）

核心：多个 agent 独立生成方案，judge 评出最优。

执行流程图（python3 023.py）：

任务 → 3 个 candidate 独立生成方案 → judge 评估选最优

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-4 那节）。
  3. 跑通：看到 3 个不同风格的 slogan，以及 judge 选出的最优。
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
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()


def candidate(task, style):
    # ── 填空 1 ──────────────────────────────
    # 候选 agent：用不同风格生成方案
    # 提示：system 用 f-string 带上 style（如「你是一个{style}」），user 带上 task
    return llm(f"你是一个{style}", task)   # ← 填空 1：补全 system 和 user


def judge(task, candidates):
    # ── 填空 2 ──────────────────────────────
    # judge：评估所有方案，选最优
    # 提示：先把 candidates 编号拼成一段（方案1/方案2/方案3），
    #       system 说「你是评委，选最优说明编号和理由」
    numbered = f"\n {task}这个是task,".join(f" 方案- {r}" for r in candidates)   # ← 填空 2：补全 numbered 拼接
    return llm("你是评委，选最优说明编号和理由", numbered)


if __name__ == "__main__":
    task = "给一家新开的咖啡店写一句宣传 slogan"
    print("=" * 55)
    print("  竞争式 Multi-Agent：多个方案 + judge 选最优")
    print("=" * 55)

    styles = ["文艺风格的文案", "简洁有力的文案", "幽默风格的文案"]
    # ── 填空 3 ──────────────────────────────
    # 生成 3 个候选方案
    # 提示：列表推导式 [candidate(task, s) for s in styles]
    candidates = [candidate(task, s) for s in styles]   # ← 填空 3：补全 candidates 列表

    for i, c in enumerate(candidates, 1):
        print(f"\n方案{i}（{styles[i-1]}）：{c}")

    result = judge(task, candidates)
    print(f"\n🏆 Judge 评审：\n{result}")
