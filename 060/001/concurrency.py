#!/usr/bin/env python3
"""
关卡 2-8 · 并发与限流（完整版）

核心：多 agent 并行派发能省时间（1-18），但不能无脑并发——并发太高会把 API 打爆
或触发服务端限流。限流就是用 Semaphore 控制「同时进行的任务数」，比如最多 3 个一起跑。

和 1-18 的区别：1-18 的 gather 是无脑并发（有多少并发多少），
本关加 Semaphore 信号量，把并发上限卡住。

执行流程图（python3 concurrency.py）：

[10 个任务] → Semaphore(3) 限流 → 每批最多 3 个并发 → 全部完成

方法调用关系：
  worker() ──> async with sem（拿到通行证才执行）
  main() ──> asyncio.gather（并发派发，但被 sem 卡住上限）

面试怎么讲（30 秒）：
  "多 agent 并发要限流，用 asyncio.Semaphore 控制同时进行的数量，
  防止并发过高打爆 API 或触发限流。1-18 的 gather 是无脑并发，这里加了信号量上限。"
"""

import asyncio
import random


async def worker(i, sem):
    """模拟一个 worker：受信号量限制，最多 sem 个同时执行"""
    async with sem:   # 拿到「通行证」才执行，超过上限就排队等
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return f"任务{i} 完成"


async def main():
    sem = asyncio.Semaphore(3)   # 最多 3 个并发
    tasks = [worker(i, sem) for i in range(10)]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(f"  {r}")


if __name__ == "__main__":
    print("=" * 55)
    print("  并发与限流演示（10 任务，最多 3 并发）")
    print("=" * 55)
    asyncio.run(main())
    print("  （如果去掉 Semaphore，10 个会一次性全并发）")
