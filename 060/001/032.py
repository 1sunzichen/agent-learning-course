#!/usr/bin/env python3
"""
关卡 2-14 · 死锁与循环检测（填空版）

核心：多 agent 系统两大「卡死」——死锁（互相等）和无限循环（停不下来）。
用「等待图找环」检测死锁，用「状态去重 + 步数上限」检测循环。

执行流程图（python3 032.py）：

等待关系图 → DFS 三色标记找环 → 有环=死锁；
agent 状态序列 → 检测重复状态 / 超步数 → 有=无限循环

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-029-033.md（关卡 2-14 那节）。
  3. 跑通：看到一组互相等待被判为「死锁」，一组原地打转的状态被判为「无限循环」。
"""


def has_cycle(waits_for):
    """waits_for = {agent: [它正在等待的 agent...]}
    用 DFS 三色标记法找环：0=白(未访问) 1=灰(访问中) 2=黑(已完成)。
    遇到「灰色」节点 = 绕回了正在访问的路径 = 有环 = 死锁。"""
    color = {}

    def dfs(node):
        color[node] = 1  # 灰：正在访问
        for nxt in waits_for.get(node, []):
            c = color.get(nxt, 0)
            # ── 填空 1 ──────────────────────────────
            # 如果下一个节点是「灰色」（正在访问中），说明绕回来了——有环
            # 提示：if c == 1: return True（撞到灰色节点 = 有环 = 死锁）
            result = None   # ← 填空 1：灰色节点就 return True
            if c == 0 and dfs(nxt):
                return True
        color[node] = 2  # 黑：已完成
        return False

    for node in waits_for:
        if color.get(node, 0) == 0 and dfs(node):
            return True
    return False


def detect_loop(states, max_steps):
    """states = agent 依次产生的状态列表。返回 (是否循环, 原因)。
    两种循环：① 状态重复出现（原地打转）② 步数超上限（一直不停）。"""
    seen = set()
    for s in states:
        # ── 填空 2 ──────────────────────────────
        # 如果状态 s 之前出现过，就是原地打转的无限循环
        # 提示：if s in seen: return True, "状态重复：原地打转"
        result = None   # ← 填空 2：检测重复状态
        seen.add(s)
    # ── 填空 3 ──────────────────────────────
    # 如果步数超过 max_steps，即使状态不重复也是死循环（一直停不下来）
    # 提示：if len(states) > max_steps: return True, "步数超限：停不下来"
    result = None   # ← 填空 3：检测步数超限
    return False, "正常结束"


def main():
    print("【场景 1】死锁检测（A 等 B，B 等 C，C 等 A）")
    waits = {
        "agent_A": ["agent_B"],
        "agent_B": ["agent_C"],
        "agent_C": ["agent_A"],   # 环：A→B→C→A
    }
    if has_cycle(waits):
        print("  ⚠️  检测到死锁：A→B→C→A 互相等待")
    else:
        print("  无死锁")

    print("\n【场景 2】循环检测（原地打转）")
    states = ["思考", "调工具", "思考", "调工具"]
    is_loop, reason = detect_loop(states, max_steps=10)
    print(f"  结果：{'⚠️ 循环' if is_loop else '✓ 正常'}（{reason}）")

    print("\n【场景 3】循环检测（步数超限）")
    long_states = [f"步骤{i}" for i in range(12)]
    is_loop, reason = detect_loop(long_states, max_steps=10)
    print(f"  结果：{'⚠️ 循环' if is_loop else '✓ 正常'}（{reason}）")


if __name__ == "__main__":
    print("=" * 55)
    print("  死锁与循环检测演示")
    print("=" * 55)
    main()
