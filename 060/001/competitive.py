#!/usr/bin/env python3
"""
关卡 2-4 · 竞争式 Multi-Agent（生成 + judge）（完整版）

核心：竞争式（Competitive）——多个 agent 独立生成答案，一个 judge 评出最优。
和协作式的区别：协作式是「一起讨论」，竞争式是「各做各的，最后挑最好的」。

执行流程图（python3 competitive.py）：

[任务]
  ├─ candidate(风格1) ─┐
  ├─ candidate(风格2) ─┼─ 独立生成（temperature 高，方案有差异）
  └─ candidate(风格3) ─┘
  └─ judge（LLM）评估所有方案 → 选出最优 + 理由

方法调用关系：
  candidate() ──> llm()（用不同风格生成方案）
  judge() ──> llm()（评估选优）

面试怎么讲（30 秒）：
  "竞争式是多个 agent 独立生成、judge 选最优，适合「答案有客观好坏」的场景
  （写文案、解题、生成代码）。代价是并行生成 + 评判，成本是单 agent 的 N+1 倍。"
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
        temperature=0.7,   # 竞争式用更高温度，让多个方案有差异
    )
    return resp.choices[0].message.content.strip()


def candidate(task, style):
    """候选 agent：用不同风格生成方案"""
    return llm(f"你是一个{style}，为下面的任务提供一个方案。", f"任务：{task}")


def judge(task, candidates):
    """judge：评估所有方案，选最优"""
    numbered = "\n\n".join(f"方案{i+1}：\n{c}" for i, c in enumerate(candidates))
    return llm(
        "你是评委。评估下面所有方案，选出最优的一个，说明编号和理由。",
        f"任务：{task}\n\n{numbered}\n\n请选出最优方案：",
    )


if __name__ == "__main__":
    task = "给一家新开的咖啡店写一句宣传 slogan"
    print("=" * 55)
    print("  竞争式 Multi-Agent：多个方案 + judge 选最优")
    print("=" * 55)

    styles = ["文艺风格的文案", "简洁有力的文案", "幽默风格的文案"]
    candidates = [candidate(task, s) for s in styles]

    for i, c in enumerate(candidates, 1):
        print(f"\n方案{i}（{styles[i-1]}）：{c}")

    result = judge(task, candidates)
    print(f"\n🏆 Judge 评审：\n{result}")
