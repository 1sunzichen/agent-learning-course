#!/usr/bin/env python3
"""
关卡 1-18 · 异步并发调用（完整版）

核心：agent 一次要调多个「互相独立」的工具（比如同时查 5 个城市的天气）。
串行一个个等，总耗时 = 每个之和；并行一起发，总耗时 = 最慢的那个。
asyncio + gather 就是干这个的。

执行流程图（python3 async_tools.py）：

[cities 列表]
  ├─ 串行：for city → await get_weather(city)（一个等一个，耗时累加）
  └─ 并行：asyncio.gather(*tasks)（一起发，耗时取最慢）
  └─ 对比两次耗时

方法调用关系：
  get_weather()（async，模拟 1 秒延迟）
  serial() ──> for + await get_weather（串行）
  parallel() ──> asyncio.gather（并行）

面试怎么讲（30 秒）：
  "多个独立工具要并行调，用 asyncio.gather 一起发，总耗时从「累加」降到「取最慢」。
  注意：只适合没有依赖关系的调用，有依赖（B 要用 A 的结果）还是得串行。"
"""

import asyncio
import time


async def get_weather(city):
    """模拟查天气：每个城市要 1 秒（真实场景这里是调 API/LLM）"""
    await asyncio.sleep(1)
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
    tasks = [get_weather(city) for city in cities]
    return await asyncio.gather(*tasks)


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
    print(f"  串行耗时：{t_serial:.2f}s（5 × 1s 累加）")
    print(f"  并行耗时：{t_parallel:.2f}s（一起发，取最慢）")
    print(f"  快了 {t_serial / t_parallel:.1f} 倍")
