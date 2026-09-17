#!/usr/bin/env python3
"""
关卡 2-10 · Multi-Agent 综合项目（填空版）

核心：层级式拆任务 + asyncio 并发 + 容错降级，串成一个完整的多 agent 任务。

执行流程图（python3 028.py）：

3 个子任务 → safe_worker（容错）→ gather 并发 → 打印完整攻略

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-10 那节）。
  3. 跑通：看到 3 个子任务并发执行，最终拼成完整攻略。
"""

import asyncio
from openai import AsyncOpenAI

aclient = AsyncOpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)


async def worker(subtask):
    # ── 填空 1 ──────────────────────────────
    # worker：调 LLM 执行单个子任务
    # 提示：await aclient.chat.completions.create(...)，返回 content.strip()
    resp = await aclient.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": subtask}],
    )
    return resp.choices[0].message.content.strip()



async def safe_worker(subtask):
    # ── 填空 2 ──────────────────────────────
    # 容错：try 执行 worker，except 降级标记
    # 提示：try return await worker(subtask)，except return 降级信息
    try:
        return await worker(subtask)
    except Exception as e:
        return f"[降级] {subtask} 执行失败：{e}"


async def main():
    
    subtasks = [
        "用两句话介绍北京必吃的美食",
        "用两句话介绍北京必玩的景点",
        "用两句话介绍北京交通出行的注意事项",
    ]

    print("=" * 55)
    print("  Multi-Agent 综合项目：北京旅游攻略")
    print("=" * 55)

    # ── 填空 3 ──────────────────────────────
    # 并发执行 3 个子任务（每个都包了 safe_worker 容错）
    # 提示：asyncio.gather(*[safe_worker(s) for s in subtasks]) 
    # ← 填空 3：补全并发调用  
    results = await asyncio.gather(*[safe_worker(s) for s in subtasks])
    for i, r in enumerate(results, 1):
        print(f"  子任务{i}：{r}")

    print("\n" + "=" * 55)
    print("  ✅ 攻略汇总完成")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
