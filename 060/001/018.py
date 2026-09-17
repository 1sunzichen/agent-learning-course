#!/usr/bin/env python3
"""
关卡 1-18 · 异步并发调用（填空版）

核心：多个独立工具并行调，总耗时从「累加」降到「取最慢」。asyncio + gather。

执行流程图（python3 018.py）：

串行：for → await（累加） vs 并行：gather（取最慢） → 对比耗时

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-18 那节）。
  3. 跑通：看到并行比串行快约 5 倍。
"""

import asyncio
import time


async def get_weather(city):
    # ── 填空 1 ──────────────────────────────
    # 模拟查天气要 1 秒：用 asyncio.sleep 模拟延迟
    # 提示：await asyncio.sleep(1)
    await asyncio.sleep(1)
       # ← 填空 1：补全模拟延迟，然后 return f"{city} 晴，25度"
    return f"{city} 晴，25度"


async def serial(cities):
    """串行：一个接一个"""
    results = []
    for city in cities:
        r = await get_weather(city)
        results.append(r)
    return results


async def parallel(cities):
    """并行：asyncio.gather 一起发"""
    # ── 填空 2 ──────────────────────────────
    # 生成任务列表：每个城市一个 get_weather 协程
    # 提示：列表推导式 [get_weather(city) for city in cities]
       # ← 填空 2：补全任务列表
    tasks = [get_weather(city) for city in cities]
    # ── 填空 3 ──────────────────────────────
    # 用 asyncio.gather 并行执行所有任务并返回结果
    # 提示：await asyncio.gather(*tasks)
    return await asyncio.gather(*tasks)  # ← 填空 3：补全 gather 调用


if __name__ == "__main__":
    cities = ["北京", "上海", "广州", "深圳", "成都"]

    t0 = time.time()
    asyncio.run(serial(cities))
    t_serial = time.time() - t0

    t0 = time.time()
    asyncio.run(parallel(cities))
    t_parallel = time.time() - t0

    print("=" * 50)
    print("  异步并发对比（5 个城市，每个 1 秒）")
    print("=" * 50)
    print(f"  串行耗时：{t_serial:.2f}s")
    print(f"  并行耗时：{t_parallel:.2f}s")
    print(f"  快了 {t_serial / t_parallel:.1f} 倍")
