#!/usr/bin/env python3
"""
关卡 2-19 · 多 agent 安全与权限隔离（填空版）

核心：每个 agent 只给完成本职工作所需的最小权限（最小权限原则），
调用工具前先过权限门，越权直接拒绝，敏感操作再加一道管理员门槛，全程留审计日志。

执行流程图（python3 037.py）：

agent 请求调工具 → 第一层 has_permission 查白名单 → 无权限 → 拒绝 + 审计日志
             └→ 有权限 → 第二层 敏感操作检查 → 非管理员碰敏感工具 → 拒绝 + 审计日志
                                    └→ 通过 → 执行

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-034-037.md（关卡 2-19 那节）。
  3. 跑通：看到有权限的 agent 正常执行，越权和敏感操作越权都被拒绝并留审计记录。
"""

# 每个 agent 的角色 → 允许调用的工具白名单（最小权限：只给够用的，不给多余的）
ROLES = {
    "检索员": ["search", "read"],
    "写手": ["read", "write"],
    "审核员": ["read", "review"],
    "运维": ["read", "write", "delete"],        # 运维有 delete 权，但 delete 仍属敏感操作
    "管理员": ["read", "write", "delete", "grant"],
}

# 敏感操作：即使白名单里有，也要求是管理员才能执行（纵深防御）
SENSITIVE = {"delete", "grant"}

# 审计日志：记录所有被拒绝的越权尝试 (agent, tool, 拒绝原因)
audit_log = []


def has_permission(agent, tool):
    """查该 agent 的角色白名单里有没有 tool。"""
    # ── 填空 1 ──────────────────────────────
    # 取 agent 的白名单（缺省空列表），判断 tool 是否在里面
    # 提示：return tool in ROLES.get(agent, [])
    return False   # ← 填空 1：把 False 换成白名单查询


def execute(agent, tool):
    """执行工具调用，先过两道权限门。越权就拒绝并记审计日志。"""
    # 第一层：白名单权限门
    if not has_permission(agent, tool):
        # ── 填空 2 ──────────────────────────────
        # 越权：记审计日志 + 返回拒绝信息
        # 提示：audit_log.append((agent, tool, "无权限"))，然后 return 拒绝信息
        return ""   # ← 填空 2：补全「记审计 + 拒绝」

    # 第二层：敏感操作额外门槛（纵深防御）
    # ── 填空 3 ──────────────────────────────
    # 敏感工具（delete/grant）必须是管理员才能碰
    # 提示：if tool in SENSITIVE and agent != "管理员": 记审计 + return 拒绝信息
    # ← 填空 3：补全「敏感操作仅限管理员」

    return f"✅ {agent} 调用了 {tool}"


def main():
    print("=" * 55)
    print("  多 agent 安全与权限隔离演示")
    print("=" * 55)

    requests = [
        ("检索员", "search"),    # ✅ 白名单内
        ("检索员", "write"),     # ⛔ 越权
        ("写手", "write"),       # ✅ 白名单内
        ("写手", "delete"),      # ⛔ 越权（不在白名单）
        ("运维", "delete"),      # ⛔ 敏感操作非管理员（白名单有，但第二层拦）
        ("管理员", "delete"),    # ✅ 管理员
        ("管理员", "grant"),     # ✅ 管理员
    ]

    for agent, tool in requests:
        print(f"  {execute(agent, tool)}")

    print("\n" + "=" * 55)
    print(f"  审计日志：共 {len(audit_log)} 次越权/敏感操作被拦截")
    for agent, tool, reason in audit_log:
        print(f"    ⚠️ {agent} 试图调用 {tool} → 原因：{reason}")
    print("=" * 55)


if __name__ == "__main__":
    main()
