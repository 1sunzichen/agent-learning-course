package main

/*
关卡 2-14 · Go 版 · 死锁与循环检测（对比 Python 版 032.py）

核心：多 agent 系统两大「卡死」——死锁（互相等）和无限循环（停不下来）。
  死锁检测：等待图找环（DFS 三色标记法）
  循环检测：状态去重 + 步数上限

执行流程（go run 032.go）：
  等待关系图 → DFS 三色标记找环 → 有环 = 死锁
  agent 状态序列 → 检测重复状态 / 超步数 → 有 = 无限循环

Go 和 Python 最大的不同（看不懂 hasCycle 看这里）：
  三色标记：0=白(未访问) 1=灰(访问中) 2=黑(已完成)。
  遍历图时，如果走到一个「灰色」节点，说明绕回了正在访问的路径上 = 有环 = 死锁。
  Go 里写「递归匿名函数」要两步：先 var dfs func(...) 声明，再 dfs = func(...) {...} 赋值，
  因为匿名函数要引用自己，必须先声明变量名。
*/

import "fmt"

// hasCycle：等待图找环。waitsFor = {agent: [它正在等待的 agent...]}
func hasCycle(waitsFor map[string][]string) bool {
	color := map[string]int{}

	var dfs func(string) bool
	dfs = func(node string) bool {
		color[node] = 1 // 灰：正在访问
		for _, nxt := range waitsFor[node] {
			if color[nxt] == 1 { // 撞到灰色节点 = 绕回来了 = 有环 = 死锁
				return true
			}
			if color[nxt] == 0 && dfs(nxt) {
				return true
			}
		}
		color[node] = 2 // 黑：已完成
		return false
	}

	for node := range waitsFor {
		if color[node] == 0 && dfs(node) {
			return true
		}
	}
	return false
}

// detectLoop：返回 (是否循环, 原因)。
// 两种循环：① 状态重复出现（原地打转）② 步数超上限（一直不停）。
func detectLoop(states []string, maxSteps int) (bool, string) {
	seen := map[string]bool{}
	for _, s := range states {
		if seen[s] {
			return true, "状态重复：原地打转"
		}
		seen[s] = true
	}
	if len(states) > maxSteps {
		return true, "步数超限：停不下来"
	}
	return false, "正常结束"
}

func main() {
	fmt.Println("【场景 1】死锁检测（A 等 B，B 等 C，C 等 A）")
	waits := map[string][]string{
		"agent_A": {"agent_B"},
		"agent_B": {"agent_C"},
		"agent_C": {"agent_A"}, // 环：A→B→C→A
	}
	if hasCycle(waits) {
		fmt.Println("  ⚠️  检测到死锁：A→B→C→A 互相等待")
	} else {
		fmt.Println("  无死锁")
	}

	fmt.Println("\n【场景 2】循环检测（原地打转）")
	states := []string{"思考", "调工具", "思考", "调工具"}
	if isLoop, reason := detectLoop(states, 10); isLoop {
		fmt.Printf("  ⚠️ 循环（%s）\n", reason)
	} else {
		fmt.Printf("  ✓ 正常（%s）\n", reason)
	}

	fmt.Println("\n【场景 3】循环检测（步数超限）")
	longStates := make([]string, 0, 12)
	for i := 0; i < 12; i++ {
		longStates = append(longStates, fmt.Sprintf("步骤%d", i))
	}
	if isLoop, reason := detectLoop(longStates, 10); isLoop {
		fmt.Printf("  ⚠️ 循环（%s）\n", reason)
	} else {
		fmt.Printf("  ✓ 正常（%s）\n", reason)
	}
}
