#!/usr/bin/env python3
"""
关卡 2-6 · 状态与上下文共享（完整版）

核心：多个 agent 协作，中间结果怎么共享？三种方式：
  1. 消息传递（A2A，2-5 讲的）—— agent 之间发消息
  2. 共享状态（本关）—— 所有 agent 读写同一个 state 对象
  3. 黑板模式（2-13 会讲）—— 一个共享的「黑板」，大家往上写

本关演示「共享状态」：一个全局 state 字典，多个 worker 读写。

执行流程图（python3 shared_state.py）：

[共享 state 字典]
  ├─ worker_a 写入 state["weather"]
  ├─ worker_b 读 state["weather"] + 写 state["summary"]
  └─ worker_c 读 state，产出最终答案

方法调用关系：
  worker_a/b/c ──> 用 lock 加锁读写共享 state

面试怎么讲（30 秒）：
  "多 agent 共享中间结果，常见三种：消息传递、共享状态、黑板模式。
  共享状态最简单——一个全局 dict 大家都读写，但要小心并发写冲突，所以要加锁。"
"""

import threading

# 共享状态：所有 worker 读写这个 dict
state = {}
# 锁：防止并发写冲突
lock = threading.Lock()


def worker_a():
    """worker A：查天气，写入共享状态"""
    with lock:
        state["weather"] = "北京 晴 25度"
    return "A 写入了天气"


def worker_b():
    """worker B：读天气，写总结（依赖 A 的结果）"""
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
