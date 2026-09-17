#!/usr/bin/env python3
"""
关卡 1-8 进阶 · 接真实 API 的版本（对比模拟版 008.py）

先装依赖（如果 .venv 里没有）：
    .venv/bin/pip install requests

和模拟版的关键区别：
  模拟版 get_weather = 假函数，random 造失败、sleep 造卡死、线程池套超时
  真实版 get_weather_real = 真请求 Open-Meteo（免费天气接口，无需 key），
                            超时用 requests 自带的 timeout 参数

  为什么真实 HTTP 不用线程池套超时？
  因为 requests.get(timeout=2) 内部已经管好了「连接超时 + 读取超时」，
  你直接传 timeout 就行。线程池那套是「任意阻塞函数」的通用解法，HTTP 有更省的。

执行流程图（python3 robust_tools_real.py）：

call_weather(北京)
  ① 幂等：查缓存，命中直接返回
  ② 重试循环：requests.get(timeout=2) 真实打 Open-Meteo
       超时 / 报错 → 退避 → 重试
  ③ 降级：3 次都失败 → 返回兜底
"""

import time
import random
import requests

# 人为注入开关：0 = 纯真实；设成 0.7 则 70% 概率人为制造失败，用来观察重试/降级
CHAOS = 0


def get_weather_real(city):
    # 可选：人为注入失败（观察重试/降级用，真实环境删掉这一段）
    if CHAOS and random.random() < CHAOS:
        if random.random() < 0.5:
            raise requests.exceptions.ConnectionError("人为注入：网络抖动")
        else:
            raise requests.exceptions.Timeout("人为注入：超时")

    # 真实 HTTP 调用 Open-Meteo（北京坐标写死；生产要先「城市名→坐标」再查）
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": 39.9, "longitude": 116.4, "current_weather": "true"}
    resp = requests.get(url, params=params, timeout=2)   # ← 真实超时，requests 内置
    resp.raise_for_status()                              # 非 2xx 状态码抛异常 → 进重试
    w = resp.json()["current_weather"]
    return f"{city} 当前 {w['temperature']}°C，风速 {w['windspeed']} km/h"


_cache = {}


def call_weather(city, max_retry=3):
    # ① 幂等：缓存命中直接返回，不重复打后端
    if city in _cache:
        return _cache[city] + "（缓存）"

    # ② 重试 + 超时（超时由 requests 的 timeout 参数承担）
    for attempt in range(1, max_retry + 1):
        try:
            result = get_weather_real(city)
            _cache[city] = result
            return f"第 {attempt} 次成功：{result}"
        except requests.exceptions.Timeout:
            print(f"  第 {attempt} 次超时（>2s），重试...")
        except requests.exceptions.RequestException as e:
            print(f"  第 {attempt} 次失败（{e}），重试...")
        time.sleep(0.5 * attempt)   # 退避

    # ③ 降级：重试耗尽，返回兜底
    return f"{city} 天气服务不可用，降级返回默认值"


if __name__ == "__main__":
    print("=== 真实 API 版（CHAOS=0，纯真实网络）===")
    print("第 1 次查北京：", call_weather("北京"))
    print("第 2 次查北京：", call_weather("北京"), " ← 应走缓存（幂等）")
