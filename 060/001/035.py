#!/usr/bin/env python3
"""
关卡 2-17 · 人机协同 human-in-the-loop（填空版）

核心：多 agent 跑流程时，关键节点（发信、改库这类高风险动作）必须停下来等人确认，
不能全自动一路到底。这就是 human-in-the-loop。

执行流程图（python3 035.py）：

步骤列表 → 逐个执行 → 遇到关键节点（critical）→ ask_human 停下来等人确认
       → 人批准（approve）继续 → 人拒绝（reject）立即中止整个流程

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-034-037.md（关卡 2-17 那节）。
  3. 跑通：看到普通步骤自动执行，关键步骤停下来等确认，被拒绝时流程中止。
"""

# 模拟人类预先排好的回答队列（离线演示：不用真等人点按钮）
HUMAN_REPLIES = ["approve", "reject"]


def is_critical(step):
    """判断这个步骤是不是「必须等人确认」的关键节点。
    step 是 (步骤名, 是否关键) 的元组。"""
    # ── 填空 1 ──────────────────────────────
    # 从元组里取出「是否关键」这个布尔字段返回
    # 提示：step[1] 就是第二项（是否关键），直接 return step[1]
    return False   # ← 填空 1：把 False 换成取元组第二项


def ask_human(question):
    """模拟停下来等人确认：从 HUMAN_REPLIES 弹出一个回答。
    真实系统里，这里是发通知给人、挂起任务等人点「批准/拒绝」。"""
    # ── 填空 2 ──────────────────────────────
    # 从队列弹出一个回答；队列弹空了就默认批准（approve）
    # 提示：if HUMAN_REPLIES: return HUMAN_REPLIES.pop(0)，否则 return "approve"
    return "approve"   # ← 填空 2：补全「弹队列 + 空则默认批准」


def run_step(name):
    """模拟执行一个普通步骤（离线，不真调工具）。"""
    return f"已完成「{name}」"


def main():
    # (步骤名, 是否关键节点)。关键节点 = 高风险、出错代价大、必须人拍板的动作
    steps = [
        ("收集用户需求", False),
        ("生成方案草稿", False),
        ("自动保存草稿", False),
        ("对外发送营销邮件", True),   # 高风险：乱发会出事故
        ("更新生产数据库", True),      # 高风险：误改数据难恢复
        ("生成总结报告", False),
    ]

    print("=" * 55)
    print("  人机协同 human-in-the-loop 演示")
    print("=" * 55)

    for step in steps:
        name = step[0]
        print(f"\n▶ {run_step(name)}")

        if is_critical(step):
            decision = ask_human(f"关键步骤「{name}」需要人工确认：批准还是拒绝？")
            print(f"  ⏸ 关键节点「{name}」→ 人工决定：{decision}")

            # ── 填空 3 ──────────────────────────────
            # 关键节点等人确认：批准才继续，拒绝就立即中止
            # 提示：if decision != "approve": 打印中止信息 + break
            # ← 填空 3：补全「拒绝即中止」

    print("\n" + "=" * 55)
    print("  流程结束")
    print("=" * 55)


if __name__ == "__main__":
    main()
