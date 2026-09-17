#!/usr/bin/env python3
"""
关卡 2-1 · 层级式 Multi-Agent：Orchestrator + Workers（完整版）

核心：层级式（Hierarchical）——一个主 agent（orchestrator）把大任务拆成子任务，
分派给多个 worker 各自执行，最后汇总。主 agent 管「拆」和「合」，worker 管「干」。

执行流程图（python3 orchestrator.py）：

[大任务]
  └─ orchestrator_plan（LLM）拆成 3 个子任务
       ├─ worker(子任务1) ─┐
       ├─ worker(子任务2) ─┼─ 各干各的（互相独立）
       └─ worker(子任务3) ─┘
  └─ orchestrator_summarize（LLM）汇总 → 最终答案

方法调用关系：
  orchestrator_plan() ──> llm()（拆任务）
  worker() ──> llm()（执行单个子任务）
  orchestrator_summarize() ──> llm()（汇总）

面试怎么讲（30 秒）：
  "层级式是主 agent 拆任务、分派给 worker、再汇总。控制流清晰、易扩展，
  适合「任务可分解、子任务独立」的场景。缺点是 orchestrator 是单点，拆错了全错。"
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
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def orchestrator_plan(task):
    """主 agent：把大任务拆成子任务"""
    return llm(
        "你是任务规划师。把用户的任务拆成 3 个独立的子任务，每行一个，不要编号。",
        f"任务：{task}\n请拆成 3 个子任务：",
    )


def worker(subtask):
    """worker：执行单个子任务"""
    return llm("你是一个执行者，简洁完成交给你的子任务。", f"子任务：{subtask}")


def orchestrator_summarize(task, results):
    """主 agent：汇总所有 worker 的结果"""
    joined = "\n".join(f"- {r}" for r in results)
    return llm(
        "你是一个总结者，把各子任务的结果整合成一段完整回答。",
        f"任务：{task}\n各子任务结果：\n{joined}\n请整合：",
    )


if __name__ == "__main__":
    task = "介绍北京：包括地理位置、著名景点、特色美食三个方面"
    print("=" * 55)
    print("  层级式 Multi-Agent：Orchestrator + Workers")
    print("=" * 55)

    # 1. orchestrator 拆任务
    plan = orchestrator_plan(task)
    subtasks = [line.strip("- ").strip() for line in plan.split("\n") if line.strip()]
    print("\n📋 Orchestrator 拆出的子任务：")
    for i, s in enumerate(subtasks, 1):
        print(f"  {i}. {s}")

    # 2. worker 各自执行
    results = [worker(s) for s in subtasks]
    print("\n🔧 Workers 执行结果：")
    for i, r in enumerate(results, 1):
        print(f"  worker{i}: {r[:60]}...")

    # 3. orchestrator 汇总
    final = orchestrator_summarize(task, results)
    print(f"\n📦 最终汇总：\n{final}")
