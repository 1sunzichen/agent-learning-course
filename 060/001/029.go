package main

/*
关卡 2-11 · Go 版 · 任务分解与子 agent 委派（对比 Python 版 029.py）

核心：复杂任务先拆成子任务，再按能力路由给最合适的子 agent，各司其职，
而不是一个 agent 硬扛。

执行流程（go run 029.go）：
  复杂任务字符串 → decompose 拆成子任务 → route 按关键词匹配 agent → 逐个执行 → 汇总

Go 和 Python 最大的不同（看不懂的地方看这里）：
  Python 用 dict + lambda 存子 agent：
      {"name": "math", "keywords": [...], "run": lambda t: f"「{t}」→ 42"}
  Go 里没有 dict 存函数那么随意，改用 struct + 函数字段：
      type Agent struct { name string; keywords []string; run func(string) string }
  这个 run func(string) string 就是「把函数当数据存起来」——Go 的函数是一等公民，
  和 Python 的 lambda 一个意思。用的时候直接 a.run(st) 调用。
*/

import (
	"fmt"
	"strings"
)

// Agent：一个子 agent = 名字 + 擅长的关键词 + 执行函数（纯模拟，离线可跑）
type Agent struct {
	name     string
	keywords []string
	run      func(task string) string
}

// 子 agent 注册表：谁擅长什么，一句话写清楚
var agents = []Agent{
	{"translator", []string{"翻译", "英文"}, func(t string) string { return "「" + t + "」→ Hello, world!" }},
	{"math", []string{"计算", "等于"}, func(t string) string { return "「" + t + "」→ 42" }},
	{"summarizer", []string{"总结", "摘要", "会议"}, func(t string) string { return "「" + t + "」→ （摘要）核心是把复杂任务拆小" }},
	{"writer", []string{"写", "文案", "推广"}, func(t string) string { return "「" + t + "」→ （文案）AI 让复杂任务更简单" }},
}

// decompose：把一整个复杂任务按换行拆成子任务，去掉空行和首尾空白
func decompose(task string) []string {
	var subtasks []string
	for _, line := range strings.Split(task, "\n") {
		line = strings.TrimSpace(line)
		if line != "" {
			subtasks = append(subtasks, line)
		}
	}
	return subtasks
}

// route：根据子任务内容，匹配最合适的子 agent。
// 返回 (agent, true) 表示找到；返回 (Agent{}, false) 表示没人认领。
func route(subtask string) (Agent, bool) {
	for _, a := range agents {
		for _, k := range a.keywords {
			if strings.Contains(subtask, k) {
				return a, true
			}
		}
	}
	return Agent{}, false
}

// execute：委派每个子任务给匹配的 agent 执行，收集结果
func execute(subtasks []string) []string {
	var results []string
	for _, st := range subtasks {
		a, ok := route(st)
		if !ok {
			results = append(results, "  [无人认领] "+st)
			continue
		}
		results = append(results, fmt.Sprintf("  [%s] %s", a.name, a.run(st)))
	}
	return results
}

func main() {
	task := "把「你好」翻译成英文\n" +
		"计算 40+2 等于几\n" +
		"总结今天的会议纪要\n" +
		"写一句产品推广文案"

	subtasks := decompose(task)
	fmt.Printf("拆解出 %d 个子任务：\n", len(subtasks))
	for _, st := range subtasks {
		fmt.Printf("  · %s\n", st)
	}
	fmt.Println("\n委派执行：")
	for _, line := range execute(subtasks) {
		fmt.Println(line)
	}
	fmt.Println("\n（每个子任务都交给了最合适的 agent，而不是一个 agent 硬扛）")
}
