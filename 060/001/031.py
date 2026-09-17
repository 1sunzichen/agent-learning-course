#!/usr/bin/env python3
"""
关卡 2-13 · 黑板模式/共享记忆（填空版）

核心：多个 agent 不直接通信，都往一块「黑板」上读写；谁看到缺什么就补什么，逐步拼出完整答案。

执行流程图（python3 031.py）：

黑板(共享 dict) → 天气agent写weather → 交通agent写traffic → 美食agent读weather写food → 顾问agent读全部拼最终建议

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-029-033.md（关卡 2-13 那节）。
  3. 跑通：看到 4 个 agent 依次往黑板写东西，最后黑板拼出一条完整出行建议。
"""


class Blackboard:
    """共享黑板：所有 agent 通过它读写中间结果"""
    def __init__(self):
        self.data = {}

    def write(self, key, value):
        # ── 填空 1 ──────────────────────────────
        # 把 value 写到黑板（以 key 为键）
        # 提示：self.data[key] = value
        result = None   # ← 填空 1：写黑板

    def read(self, key):
        # ── 填空 2 ──────────────────────────────
        # 读黑板上的 key，没有就返回 None
        # 提示：self.data.get(key)
        result = None   # ← 填空 2：读黑板
        return result


def weather_agent(bb):
    bb.write("weather", "晴 25度")
    return "天气agent：查到了天气，写进黑板"


def traffic_agent(bb):
    bb.write("traffic", "二环轻微拥堵")
    return "交通agent：查到了路况，写进黑板"


def food_agent(bb):
    w = bb.read("weather")
    bb.write("food", f"天气「{w}」，推荐清淡的淮扬菜")
    return "美食agent：读了天气，推荐了餐厅"


def advisor_agent(bb):
    # ── 填空 3 ──────────────────────────────
    # 读黑板上的 weather/traffic/food，拼成一条最终出行建议写到 "advice"
    # 提示：w = bb.read("weather")；t = bb.read("traffic")；f = bb.read("food")；bb.write("advice", ...)
    result = None   # ← 填空 3：读三个结果拼最终建议并写回黑板
    return "顾问agent：读了黑板全部结果，生成了最终建议"


def main():
    bb = Blackboard()
    for agent in [weather_agent, traffic_agent, food_agent, advisor_agent]:
        print(f"  {agent(bb)}")

    print("\n黑板最终内容：")
    for k, v in bb.data.items():
        print(f"    {k}: {v}")

    print(f"\n最终建议：{bb.read('advice')}")


if __name__ == "__main__":
    print("=" * 55)
    print("  黑板模式 / 共享记忆演示")
    print("=" * 55)
    main()
    print("  （agent 之间不直接说话，全靠黑板协作）")
