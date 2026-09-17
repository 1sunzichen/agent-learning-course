#!/usr/bin/env python3
"""
关卡 2-10 · Multi-Agent 综合项目（完整版）

核心：把 Phase 2 学的东西串起来——层级式拆任务 + asyncio 并发 + 容错降级，
跑通一个完整的多 agent 协作任务。

场景：orchestrator 把「写一份北京旅游攻略」拆成 3 个子任务，
3 个 worker 并发执行，其中某个可能失败（容错降级），最后汇总成完整攻略。

执行流程图（python3 multi_agent_project.py）：

[大任务「北京旅游攻略」]
  ├─ worker1（美食）┐
  ├─ worker2（景点）├─ asyncio.gather 并发执行
  └─ worker3（交通）┘
  └─ safe_worker 容错：谁失败就降级标记
  └─ 汇总打印完整攻略

方法调用关系：
  worker() ──> aclient（AsyncOpenAI 调 LLM）
  safe_worker() ──> try/except 包住 worker（容错）
  main() ──> asyncio.gather（并发）

面试怎么讲（30 秒）：
  "综合项目把层级式拆任务、asyncio 并发、容错降级串起来，
  演示了一个完整的多 agent 协作流程：拆解 → 并行执行 → 容错 → 汇总。"
"""

import asyncio
from openai import AsyncOpenAI

aclient = AsyncOpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)


async def worker(subtask):
    """worker：执行单个子任务（调 LLM）"""
    resp = await aclient.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": subtask}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


async def safe_worker(subtask):
    """带容错的 worker：失败就降级标记，不影响其他 worker"""
    try:
        return await worker(subtask)
    except Exception as e:
        return f"（降级）本子任务执行失败：{e}"


async def main():
    subtasks = [
        "用两句话介绍北京必吃的美食",
        "用两句话介绍北京必玩的景点",
        "用两句话介绍北京交通出行的注意事项",
    ]

    print("=" * 55)
    print("  Multi-Agent 综合项目：北京旅游攻略")
    print("=" * 55)
    print("  3 个 worker 并发执行（层级式拆任务 + 并发 + 容错）\n")

    # 并发执行 3 个子任务，每个都带容错
    results = await asyncio.gather(*[safe_worker(s) for s in subtasks])

    for i, r in enumerate(results, 1):
        print(f"  子任务{i}：{r}")

    print("\n" + "=" * 55)
    print("  ✅ 攻略汇总完成（上面 3 段拼起来就是完整攻略）")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
