#!/usr/bin/env python3
"""
关卡 2-18 · 多 agent 评测（填空版）

核心：单 agent 评测看「答对没」，多 agent 评测还要看「协作得怎么样」——
任务完成率、共识效率、产出质量、成本，几个维度一起量化。

执行流程图（python3 036.py）：

若干次协作 run（模拟数据）→ completion_rate 算完成率 → efficiency_score 算效率
      → overall 加权综合 → 汇总多次 run → 出平均协作质量报告

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-034-037.md（关卡 2-18 那节）。
  3. 跑通：看到每次协作 run 各维度得分，以及整体平均协作质量。
"""

# 3 次协作 run 的模拟评测数据：
# completed/total = 完成的子任务 / 总子任务；rounds = 达成共识用的对话轮数（越少越好）
# quality = 产出质量（0~1，真实系统里由 LLM-as-Judge 或 golden 答案比对得出）；cost = 花费（元）
RUNS = [
    {"completed": 3, "total": 3, "rounds": 2, "quality": 0.9, "cost": 0.0012},
    {"completed": 2, "total": 3, "rounds": 4, "quality": 0.7, "cost": 0.0025},
    {"completed": 3, "total": 3, "rounds": 5, "quality": 0.85, "cost": 0.0031},
]


def completion_rate(run):
    """任务完成率：完成的子任务数 / 总子任务数（0~1）。"""
    # ── 填空 1 ──────────────────────────────
    # 完成数除以总数
    # 提示：return run["completed"] / run["total"]
    return 0   # ← 填空 1：把 0 换成完成率公式


def efficiency_score(run):
    """效率分：达成共识用的轮数越少，协作越高效。用 1/轮数，轮数 1 得满分 1.0。"""
    # ── 填空 2 ──────────────────────────────
    # 效率 = 1 / 共识轮数
    # 提示：return 1.0 / run["rounds"]
    return 0   # ← 填空 2：把 0 换成效率公式


def quality_score(run):
    """产出质量分：直接读 run 的 quality（真实系统由 LLM-as-Judge 给出）。"""
    return run["quality"]


def overall(run):
    """综合协作质量：完成率、效率、质量三维度加权求和。"""
    # ── 填空 3 ──────────────────────────────
    # 加权：完成率 0.4 + 效率 0.3 + 质量 0.3
    # 提示：0.4 * completion_rate(run) + 0.3 * efficiency_score(run) + 0.3 * quality_score(run)
    return 0   # ← 填空 3：把 0 换成加权公式


def main():
    print("=" * 55)
    print("  多 agent 评测：协作质量量化")
    print("=" * 55)

    totals = []
    for i, run in enumerate(RUNS, 1):
        cr = completion_rate(run)
        eff = efficiency_score(run)
        q = quality_score(run)
        ov = overall(run)
        totals.append(ov)
        print(f"\n  run{i}：完成 {run['completed']}/{run['total']}，共识轮数 {run['rounds']}，成本 ¥{run['cost']:.4f}")
        print(f"    完成率 {cr:.0%}  效率 {eff:.2f}  质量 {q:.2f}  → 综合 {ov:.2f}")

    avg = sum(totals) / len(totals)
    print("\n" + "=" * 55)
    print(f"  平均协作质量：{avg:.2f}")
    print("  结论：多 agent 评测 = 完成率 + 效率 + 质量 + 成本，多维度一起看")
    print("=" * 55)


if __name__ == "__main__":
    main()
