package main

/*
关卡 2-19 · Go 版 · 多 agent 安全与权限隔离（对比 Python 版 037.py）

核心：每个 agent 只给完成本职工作所需的最小权限（最小权限原则），
调用工具前先过权限门，越权直接拒绝，敏感操作再加一道管理员门槛，全程留审计日志。

执行流程（go run 037.go）：
  agent 请求调工具 → 第一层 hasPermission 查白名单 → 无权限 → 拒绝 + 审计日志
             └→ 有权限 → 第二层 敏感操作检查 → 非管理员碰敏感工具 → 拒绝 + 审计日志
                                    └→ 通过 → 执行

Go 和 Python 最大的不同：
  Python 的 ROLES 是 dict[str, list]，判断 tool 在不在白名单用 `tool in list`；
  Go 用 map[string][]string + 手写 contains 辅助函数（Go 没有 `in` 语法）。
  Python 的 SENSITIVE 是 set（O(1) 查询）；Go 用 map[string]bool 等价。
  Python 的 audit_log 是元组列表；Go 用 struct 切片。
*/

import "fmt"

// 每个 agent 的角色 → 允许调用的工具白名单（最小权限：只给够用的，不给多余的）
var roles = map[string][]string{
	"检索员": {"search", "read"},
	"写手":  {"read", "write"},
	"审核员": {"read", "review"},
	"运维":  {"read", "write", "delete"}, // 运维有 delete 权，但 delete 仍属敏感操作
	"管理员": {"read", "write", "delete", "grant"},
}

// 敏感操作：即使白名单里有，也要求是管理员才能执行（纵深防御）
var sensitive = map[string]bool{"delete": true, "grant": true}

// 审计日志条目：(agent, tool, 拒绝原因)
type auditEntry struct {
	agent  string
	tool   string
	reason string
}

var auditLog []auditEntry

// contains：判断白名单里有没有 tool（Go 没有 `in` 语法，手写一个）
func contains(list []string, tool string) bool {
	for _, t := range list {
		if t == tool {
			return true
		}
	}
	return false
}

// hasPermission：查该 agent 的角色白名单里有没有 tool（未注册 agent 兜底空列表 → 默认无权）
func hasPermission(agent, tool string) bool {
	return contains(roles[agent], tool)
}

// execute：执行工具调用，先过两道权限门。越权就拒绝并记审计日志。
func execute(agent, tool string) string {
	// 第一层：白名单权限门
	if !hasPermission(agent, tool) {
		auditLog = append(auditLog, auditEntry{agent, tool, "无权限"})
		return fmt.Sprintf("⛔ 拒绝：%s 无权限调用 %s", agent, tool)
	}
	// 第二层：敏感操作额外门槛（纵深防御）
	if sensitive[tool] && agent != "管理员" {
		auditLog = append(auditLog, auditEntry{agent, tool, "敏感操作仅限管理员"})
		return fmt.Sprintf("⛔ 拒绝：敏感操作 %s 仅限管理员", tool)
	}
	return fmt.Sprintf("✅ %s 调用了 %s", agent, tool)
}

func main() {
	fmt.Println("=======================================================")
	fmt.Println("  多 agent 安全与权限隔离演示")
	fmt.Println("=======================================================")

	requests := [][2]string{
		{"检索员", "search"}, // ✅ 白名单内
		{"检索员", "write"},  // ⛔ 越权
		{"写手", "write"},   // ✅ 白名单内
		{"写手", "delete"},  // ⛔ 越权（不在白名单）
		{"运维", "delete"},  // ⛔ 敏感操作非管理员（白名单有，但第二层拦）
		{"管理员", "delete"}, // ✅ 管理员
		{"管理员", "grant"},  // ✅ 管理员
	}

	for _, r := range requests {
		fmt.Printf("  %s\n", execute(r[0], r[1]))
	}

	fmt.Println("\n=======================================================")
	fmt.Printf("  审计日志：共 %d 次越权/敏感操作被拦截\n", len(auditLog))
	for _, e := range auditLog {
		fmt.Printf("    ⚠️ %s 试图调用 %s → 原因：%s\n", e.agent, e.tool, e.reason)
	}
	fmt.Println("=======================================================")
}
