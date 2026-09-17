#!/usr/bin/env python3
"""
关卡 2-6 · 状态与上下文共享（填空版）

核心：多 agent 通过一个共享 state 字典交换中间结果。

执行流程图（python3 025.py）：

共享 state → worker_a 写 weather → worker_b 读写 → worker_c 读最终答案

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-6 那节）。
  3. 跑通：看到 A 写天气、B 读天气写总结、C 读总结出最终答案。
"""

import threading

# ── 填空 1 ──────────────────────────────
# 共享状态：所有 worker 读写的 dict + 防并发冲突的锁
# 提示：state 是空字典，lock 用 threading.Lock()
state = {}   # ← 填空 1：补全共享状态和锁
lock = threading.Lock()


def worker_a():
    # ── 填空 2 ──────────────────────────────
    # worker A：写入天气到共享状态
    # 提示：用 with lock 包住，写入 state["weather"]
    with lock:
            state["weather"] = "北京 晴 25度"
    return  "A 写入了天气"


def worker_b():
    # ── 填空 3 ──────────────────────────────
    # worker B：读天气，写总结（依赖 A 的结果）
    # 提示：state.get("weather", "未知") 读，然后写 state["summary"]
    # ← 填空 3：补全读写逻辑，return "B 写入了总结"
    with lock:
            weather = state.get("weather", "未知")
            state["summary"] = f"根据天气（{weather}），建议出门带伞"
    return "B 写入了总结"


def worker_c():
    """worker C：读所有状态，产出最终答案"""
    with lock:
        return f"最终结论：{state.get('summary', '（还没人写）')}"


if __name__ == "__main__":
    print("=" * 55)
    print("  多 agent 共享状态演示")
    print("=" * 55)

    print(f"\n  {worker_a()}")
    print(f"  {worker_b()}")
    print(f"\n  {worker_c()}")
    print(f"\n  共享状态里的内容：{state}")
