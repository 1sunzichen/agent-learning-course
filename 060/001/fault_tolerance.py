#!/usr/bin/env python3
"""
关卡 2-7 · 容错与降级（完整版）

核心：多 agent 里某个 worker 挂了，整体不能崩。三种手段：
  1. try/except 捕获单个 worker 的异常（本关）
  2. 降级：失败的任务给个兜底结果
  3. 超时：卡死的 worker 强制中断（1-8 讲过）

和 1-8 的区别：1-8 是「单个工具」的四层防护，本关是「整个 worker」级别的容错——
一个 worker 挂掉，不影响其他 worker，orchestrator 照样汇总出结果。

执行流程图（python3 fault_tolerance.py）：

[任务列表]
  └─ for 每个任务：
       ├─ try worker(task)
       │    ├─ 成功 → 记录结果
       │    └─ 失败 → 捕获异常 → 记录「失败」+ 降级兜底
  └─ 汇总：成功的结果 + 失败的降级标记，整体不崩

方法调用关系：
  worker() ──> 模拟执行（30% 概率抛异常）
  run_with_fallback() ──> try/except 包住 worker，失败降级

面试怎么讲（30 秒）：
  "多 agent 容错靠三层：单个 worker 用 try/except 隔离异常，失败用降级兜底，
  卡死用超时。核心原则是「一个 worker 挂掉，不影响其他 worker，整体照常出结果」。"
"""

import random


def worker(task):
    """模拟一个可能失败的 worker"""
    if random.random() < 0.3:   # 30% 概率失败
        raise RuntimeError(f"任务「{task}」执行失败")
    return f"「{task}」完成"


def run_with_fallback(task):
    """带容错的执行：失败就降级兜底，返回 (结果, 状态)"""
    try:
        return worker(task), "成功"
    except Exception as e:
        return f"「{task}」降级兜底（{e}）", "失败"


if __name__ == "__main__":
    tasks = ["查天气", "查股价", "查新闻", "算数学", "查地图"]
    print("=" * 55)
    print("  多 agent 容错与降级演示（每个 worker 30% 概率挂）")
    print("=" * 55)

    results = []
    for t in tasks:
        result, status = run_with_fallback(t)
        mark = "✓" if status == "成功" else "✗"
        print(f"  {mark} {result}")
        results.append((t, status))

    ok = sum(1 for _, s in results if s == "成功")
    print(f"\n  结果：{ok}/{len(tasks)} 成功，{len(tasks)-ok} 个降级兜底，整体不崩")
