#!/usr/bin/env python3
"""
关卡 2-12 · 消息路由与事件总线（填空版）

核心：发布/订阅模式——发布者发消息，总线只把消息路由给「订阅了该主题」的订阅者，不串台。

执行流程图（python3 030.py）：

发布者 publish(topic, msg) → 总线按 topic 查订阅者 → 只投递给订阅该 topic 的 agent

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-029-033.md（关卡 2-12 那节）。
  3. 跑通：看到「天气」只被天气 agent 收到、「新闻」只被新闻 agent 收到，没人订阅的 topic 没人收到。
"""


class EventBus:
    """事件总线：按 topic 把消息路由给订阅者"""
    def __init__(self):
        self._subs = {}  # topic -> [handler, ...]

    def subscribe(self, topic, handler):
        # ── 填空 1 ──────────────────────────────
        # 把 handler 登记到该 topic 的订阅者列表里（topic 第一次出现时先建空列表）
        # 提示：self._subs.setdefault(topic, []).append(handler)
        result = None   # ← 填空 1：登记订阅者

    def publish(self, topic, message):
        # ── 填空 2 ──────────────────────────────
        # 只把消息投递给「订阅了该 topic」的 handler；没人订阅就一个都不投（不串台）
        # 提示：for h in self._subs.get(topic, []): h(message)
        result = None   # ← 填空 2：按 topic 投递消息


def weather_agent(msg):
    print(f"    [天气agent] 收到：{msg}")


def news_agent(msg):
    print(f"    [新闻agent] 收到：{msg}")


def stock_agent(msg):
    print(f"    [股票agent] 收到：{msg}")


def main():
    bus = EventBus()
    # ── 填空 3 ──────────────────────────────
    # 让天气/新闻/股票 agent 各自订阅自己的 topic（三行 subscribe）
    # 提示：bus.subscribe("weather", weather_agent) 等
    result = None   # ← 填空 3：完成三个订阅

    print("发布 weather 消息「北京明天晴」：")
    bus.publish("weather", "北京明天晴")
    print("发布 news 消息「AI 大会开幕」：")
    bus.publish("news", "AI 大会开幕")
    print("发布 stock 消息「某股大涨」：")
    bus.publish("stock", "某股大涨")
    print("发布 sport 消息「足球比赛结果」（没人订阅）：")
    bus.publish("sport", "足球比赛结果")


if __name__ == "__main__":
    print("=" * 55)
    print("  消息路由与事件总线演示")
    print("=" * 55)
    main()
    print("  （sport 消息没人订阅，所以没有任何 agent 收到——这就是路由不串台）")
