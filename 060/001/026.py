#!/usr/bin/env python3
"""
关卡 2-7 · 容错与降级（填空版）

核心：某个 worker 挂了，整体不崩。用 try/except 隔离 + 降级兜底。

执行流程图（python3 026.py）：

任务列表 → 每个 worker try/except → 失败降级兜底 → 统计整体不崩

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-7 那节）。
  3. 跑通：看到部分 worker 失败但降级兜底，整体照常出结果。
"""

import random


def worker(task):
    # ── 填空 1 ──────────────────────────────
    # 模拟一个可能失败的 worker
    # 提示：random.random() < 0.3 时 raise RuntimeError，否则 return 完成
    # ← 填空 1：补全失败和成功两个分支
    if random.random() < 0.3:   # 30% 概率失败
           raise RuntimeError(f"任务「{task}」执行失败")
    return f"「{task}」完成"



def run_with_fallback(task):
    # ── 填空 2 ──────────────────────────────
    # 带容错：try 执行 worker，except 捕获异常降级兜底
    # 提示：成功 return (结果, "成功")，失败 return (降级结果, "失败")
    """带容错的执行：失败就降级兜底，返回 (结果, 状态)"""
    try:
        return worker(task), "成功"   # ← 填空 2：补全 try 成功分支
    except Exception as e:
        return f"「{task}」降级兜底（{e}）", "失败"   # ← 填空 2：补全 except 降级分支


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

    # ── 填空 3 ──────────────────────────────
    # 统计成功数量
    # 提示：sum(1 for _, s in results if s == "成功")
    # ← 填空 3：补全统计

    ok = sum(1 for _, s in results if s == "成功")
    print(f"\n  结果：{ok}/{len(tasks)} 成功，{len(tasks)-ok} 个降级兜底，整体不崩")
