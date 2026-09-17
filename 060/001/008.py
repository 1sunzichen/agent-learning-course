"""
关卡 1-8 · 工具设计进阶（填空版）

核心：真实世界的工具调用不可靠——会超时、会偶发失败、会重复提交。
生产级 agent 要给工具包四层防护：
  1. 重试 retry       —— 偶发失败自动重试几次
  2. 超时 timeout     —— 工具卡住不无限等
  3. 幂等 idempotent  —— 重复请求不重复生效
  4. 降级 fallback    —— 彻底失败给个兜底，保证可用

执行流程图（python3 008.py）：

call_weather(城市)
  ① 幂等：查缓存，命中直接返回          ← 填空 1
  ② 重试循环（最多 3 次）：
       每次调 get_weather 套超时          ← 填空 2
  ③ 降级：3 次都失败 → 返回兜底          ← 填空 3

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-8 那节）。
  3. 跑通：能看到工具失败时自动重试、卡死时超时、彻底失败时降级返回。
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
    # ── 填空 1 ──────────────────────────────
    # 幂等：同一城市查过就返回缓存，不重复打后端
    # 提示：查 _cache，命中就返回缓存结果
    if city in _cache:                                      # ← 填空 1
        return _cache[city] + "（缓存）"

    # ② 重试 + 超时
    for attempt in range(1, max_retry + 1):
        fut = _executor.submit(get_weather, city)
        try:
            # ── 填空 2 ──────────────────────────────
            # 给工具调用套一个超时上限，超时就抛 TimeoutError 进入重试
            # 提示：用 fut.result 带 timeout 参数
            result = fut.result(timeout=timeout)            # ← 填空 2
            _cache[city] = result
            return f"第 {attempt} 次成功：{result}"
        except TimeoutError:
            print(f"  第 {attempt} 次超时（>{timeout}s），重试...")
        except Exception as e:
            print(f"  第 {attempt} 次失败（{e}），重试...")
        time.sleep(0.5 * attempt)   # 退避：越重试等越久

    # ── 填空 3 ──────────────────────────────
    # 降级：重试耗尽，不能崩，给个「还能用」的兜底
    # 提示：返回一个默认值，说明服务不可用
    return f"{city} 天气服务不可用，降级返回默认值"        # ← 填空 3


if __name__ == "__main__":
    print("=== 包了四层防护的天气工具 ===")
    for i in range(3):
        print(f"\n第 {i+1} 次查北京：", call_weather("北京"))
    print("\n=== 幂等验证：再查一次北京，应走缓存 ===")
    print(" ", call_weather("北京"))
