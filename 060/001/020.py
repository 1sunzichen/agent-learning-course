#!/usr/bin/env python3
"""
关卡 2-1 · 层级式 Multi-Agent：Orchestrator + Workers（填空版）

核心：主 agent 拆任务 → 分派 worker 各自执行 → 汇总。

执行流程图（python3 020.py）：

大任务 → orchestrator_plan 拆子任务 → worker 各自执行 → orchestrator_summarize 汇总

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-1 那节）。
  3. 跑通：看到 3 个子任务被拆出、3 个 worker 结果、最终汇总。
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


def orchestrator_plan(task):
    # ── 填空 1 ──────────────────────────────
    # 主 agent：把大任务拆成子任务
    # 提示：system 说「你是任务规划师，拆成 3 个独立子任务，每行一个」，
    #       user 里带上 task
    return llm("你是任务规划师，拆成 3 个独立子任务，每行一个，不要编号", task)   # ← 填空 1：补全 system 和 user


def worker(subtask):
    # ── 填空 2 ──────────────────────────────
    # worker：执行单个子任务
    # 提示：system 说「你是执行者，简洁完成子任务」，user 里带上 subtask
    return llm("你是执行者，简洁完成子任务", subtask)   # ← 填空 2：补全 system 和 user


def orchestrator_summarize(task, results):
    # ── 填空 3 ──────────────────────────────
    # 主 agent：汇总所有 worker 的结果
    # 提示：先把 results 用 "\n".join 拼成一段，system 说「你是总结者，整合成完整回答」
    joined = "\n".join(f"- {r}" for r in results)
   # ← 填空 3：补全 joined 拼接，然后 llm 汇总
    return llm("你是总结者，整合成完整回答", f"任务：{task}\n各子任务结果：\n{joined}\n请整合：",)


if __name__ == "__main__":
    task = "介绍北京：包括地理位置、著名景点、特色美食三个方面"
    print("=" * 55)
    print("  层级式 Multi-Agent：Orchestrator + Workers")
    print("=" * 55)

    plan = orchestrator_plan(task)
    subtasks = [line.strip("- ").strip() for line in plan.split("\n") if line.strip()]
    print("\n📋 Orchestrator 拆出的子任务：")
    for i, s in enumerate(subtasks, 1):
        print(f"  {i}. {s}")

    results = [worker(s) for s in subtasks]
    print("\n🔧 Workers 执行结果：")
    for i, r in enumerate(results, 1):
        print(f"  worker{i}: {r[:60]}...")

    final = orchestrator_summarize(task, results)
    print(f"\n📦 最终汇总：\n{final}")
