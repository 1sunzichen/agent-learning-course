#!/usr/bin/env python3
"""
关卡 1-8 · 工具设计进阶（完整版）

核心：真实世界的工具调用不可靠——会超时、会偶发失败、会重复提交。
生产级 agent 要给工具包四层防护：
  1. 重试 retry       —— 偶发失败自动重试几次
  2. 超时 timeout     —— 工具卡住不无限等
  3. 幂等 idempotent  —— 重复请求不重复生效
  4. 降级 fallback    —— 彻底失败给个兜底，保证可用

执行流程图（python3 robust_tools.py）：

call_weather(城市)
  ① 幂等：查缓存，命中直接返回（不重复打后端）
  ② 重试循环（最多 3 次）：
       每次调 get_weather 套超时（超 2 秒判失败）
       失败/超时 → 退避 → 重试
  ③ 降级：3 次都失败 → 返回兜底结果

和前面关卡的区别：
  1-2 的工具 = 裸函数，失败就报错，agent 就崩
  1-8 的工具 = 包了四层防护，失败自动恢复

方法调用关系：
  call_weather() ──> _executor.submit(get_weather) ──> fut.result(timeout=...)
       ├─ _cache 查/写（幂等）
       └─ 循环重试（retry）+ 兜底返回（fallback）

面试怎么讲（30 秒）：
  "生产级工具不是裸函数，要包四层：重试扛偶发故障、超时防挂死、幂等防重复副作用、
  降级保证服务可用。这是 agent 稳定性的基础。"
"""

import time
import random
from concurrent.futures import ThreadPoolExecutor

# 模拟一个不稳定的天气 API：
#   30% 概率正常返回
#   40% 概率报「网络抖动」
#   30% 概率卡死（睡 5 秒，用来触发超时）
def get_weather(city):
    r = random.random()
    if r < 0.3:
        return f"{city} 晴，25度"
    elif r < 0.7:
        raise ConnectionError("网络抖动")
    else:
        time.sleep(5)
        return f"{city} 多云"

_executor = ThreadPoolExecutor(max_workers=4)  # 持久线程池，用来给调用套超时
_cache = {}                                     # 幂等缓存


def call_weather(city, max_retry=3, timeout=2.0):
    # ① 幂等：缓存命中直接返回，不重复打后端
    if city in _cache:
        return _cache[city] + "（缓存）"

    # ② 重试 + 超时
    for attempt in range(1, max_retry + 1):
        fut = _executor.submit(get_weather, city)
        try:
            result = fut.result(timeout=timeout)   # 超时抛 TimeoutError
            _cache[city] = result
            return f"第 {attempt} 次成功：{result}"
        except TimeoutError:
            print(f"  第 {attempt} 次超时（>{timeout}s），重试...")
        except Exception as e:
            print(f"  第 {attempt} 次失败（{e}），重试...")
        time.sleep(0.5 * attempt)   # 退避：越重试等越久

    # ③ 降级：重试耗尽，返回兜底
    return f"{city} 天气服务不可用，降级返回默认值"


if __name__ == "__main__":
    print("=== 包了四层防护的天气工具 ===")
    for i in range(3):
        print(f"\n第 {i+1} 次查北京：", call_weather("北京"))
    print("\n=== 幂等验证：再查一次北京，应走缓存 ===")
    print(" ", call_weather("北京"))
