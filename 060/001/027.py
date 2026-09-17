#!/usr/bin/env python3
"""
关卡 2-8 · 并发与限流（填空版）

核心：并行派发 + Semaphore 限流，防止并发过高打爆 API。

执行流程图（python3 027.py）：

10 任务 → Semaphore(3) 限流 → 最多 3 并发 → gather 全部完成

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-8 那节）。
  3. 跑通：看到 10 个任务完成，但受信号量限制最多 3 个同时跑。
"""

import asyncio
import random


async def worker(i, sem):
    # ── 填空 1 ──────────────────────────────
    # 用信号量限流：async with sem 拿到通行证才执行
    # 提示：async with sem: 里面 await asyncio.sleep
    # ← 填空 1：补全限流逻辑，return f"任务{i} 完成"
    async with sem: 
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return f"任务{i} 完成"


async def main():
    # ── 填空 2 ──────────────────────────────
    # 信号量：最多 3 个并发
    # 提示：asyncio.Semaphore(3)
    sem = asyncio.Semaphore(3)   
    # ← 填空 2：补全信号量

    # ── 填空 3 ──────────────────────────────
    # 并发派发：10 个 worker 任务，gather 一起跑
    # 提示：[worker(i, sem) for i in range(10)]，然后 asyncio.gather(*tasks)
    tasks = [worker(i, sem) for i in range(10)]   
    # ← 填空 3：补全任务列表
    results = await asyncio.gather(*tasks)
    for r in results:
        print(f"  {r}")


if __name__ == "__main__":
    print("=" * 55)
    print("  并发与限流演示（10 任务，最多 3 并发）")
    print("=" * 55)
    asyncio.run(main())
    print("  （如果去掉 Semaphore，10 个会一次性全并发）")
