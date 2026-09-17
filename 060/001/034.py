#!/usr/bin/env python3
"""
关卡 2-16 · 成本分摊与预算控制（填空版）

核心：多 agent 里每个 agent 的 token 都要记账、按 agent 分摊成本，总成本超预算就止损停派。

执行流程图（python3 034.py）：

任务列表 → mock_run 模拟各 agent 消耗 token → cost_of 算钱 → allocate 记到各 agent 台账（成本分摊）
        → 累计总成本 → 每步检查预算 → 超预算触发止损，不再派新任务

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-034-037.md（关卡 2-16 那节）。
  3. 跑通：看到每个 agent 的花费、各 agent 成本分摊台账、总成本，以及超预算自动止损。
"""

# deepseek-chat 单价（元 / 百万 token），这里演示计算逻辑，实际以官网为准
PRICE_INPUT = 1.0    # 输入 1 元 / 百万 token
PRICE_OUTPUT = 2.0   # 输出 2 元 / 百万 token

# 总预算（元），累计成本超过它就止损（设成 0.00012，让最后 1 个任务被止损拦住）
BUDGET = 0.00012


def cost_of(prompt_tokens, completion_tokens):
    """算一次调用的成本（元）。输入、输出单价不同，要分开乘，再除以 1_000_000。"""
    # ── 填空 1 ──────────────────────────────
    # 成本 = 输入 token × 输入单价 + 输出 token × 输出单价，单位换算到「元」要 / 1_000_000
    # 提示：(prompt_tokens * PRICE_INPUT + completion_tokens * PRICE_OUTPUT) / 1_000_000
    return 0   # ← 填空 1：把 0 换成正确的成本公式


def mock_run(agent_name, work):
    """模拟一个 agent 执行任务，返回 (agent 名, prompt_tokens, completion_tokens)。
    用 work 的长度近似 token 数，离线可跑，不真调 LLM。"""
    prompt_tokens = len(work)
    completion_tokens = len(work) // 2
    return agent_name, prompt_tokens, completion_tokens


def allocate(ledger, agent_name, cost):
    """成本分摊：把本次 cost 累加到 agent_name 名下。"""
    # ── 填空 2 ──────────────────────────────
    # 把 cost 累加进台账；第一次出现该 agent 时用 0.0 兜底
    # 提示：ledger[agent_name] = ledger.get(agent_name, 0.0) + cost
    pass   # ← 填空 2：补全累加逻辑


def main():
    # 任务队列：(负责的 agent, 要处理的文本)。文本长度近似 token 消耗
    tasks = [
        ("规划师", "把用户需求拆成三个子任务并分配给合适的执行者"),
        ("研究员", "搜集与主题相关的背景资料并整理成要点"),
        ("写手", "基于素材写一段通顺的介绍"),
        ("审核员", "检查文章是否有事实错误并给出修改建议"),
        ("规划师", "汇总所有结果产出最终交付物"),
    ]

    ledger = {}     # 各 agent 的累计成本台账
    total = 0.0     # 总成本
    stopped = False

    print("=" * 58)
    print(f"  成本分摊与预算控制（总预算 ¥{BUDGET:.6f}）")
    print("=" * 58)

    for agent_name, work in tasks:
        agent_name, pt, ct = mock_run(agent_name, work)
        c = cost_of(pt, ct)
        allocate(ledger, agent_name, c)
        total += c
        print(f"  {agent_name}：{work[:10]}… prompt {pt}t + completion {ct}t → ¥{c:.6f}")

        # ── 填空 3 ──────────────────────────────
        # 预算止损：累计成本超过预算就停下，不再派新任务
        # 提示：if total > BUDGET: 打印止损提示，把 stopped 置 True 并 break
        # ← 填空 3：补全止损判断

    print("\n" + "=" * 58)
    print("  各 agent 成本分摊台账（按花费排序）：")
    for name, c in sorted(ledger.items(), key=lambda kv: -kv[1]):
        print(f"    {name}: ¥{c:.6f}")
    print(f"  总成本：¥{total:.6f}")
    if stopped:
        print(f"  ⛔ 已触发预算止损：累计超过 ¥{BUDGET:.6f}，停止派发")
    else:
        print("  ✅ 未超预算，全部任务完成")
    print("=" * 58)


if __name__ == "__main__":
    main()
