package main

/*
关卡 2-17 · Go 版 · 人机协同 human-in-the-loop（对比 Python 版 035.py）

核心：多 agent 跑流程时，关键节点（发信、改库这类高风险动作）必须停下来等人确认，
不能全自动一路到底。这就是 human-in-the-loop。

执行流程（go run 035.go）：
  步骤列表 → 逐个执行 → 遇到关键节点 → askHuman 停下来等人确认
       → 人批准（approve）继续 → 人拒绝（reject）立即中止整个流程

Go 和 Python 最大的不同：
  Python 的步骤用 (名称, 是否关键) 元组，step[0]/step[1] 取值；Go 用 struct{name, critical}。
  Python 的 HUMAN_REPLIES 用 list.pop(0) 弹队首；Go 里用 slice 切片 humanReplies[1:] 模拟。
  Python 的 ask_human 里 `if HUMAN_REPLIES:` 判队列非空；Go 用 len(humanReplies) > 0。
*/

import "fmt"

// step：一个流程步骤 = 名称 + 是否关键节点
type step struct {
	name     string
	critical bool
}

// humanReplies：模拟人类预先排好的回答队列（离线演示，不用真等人点按钮）
var humanReplies = []string{"approve", "reject"}

// isCritical：判断这个步骤是不是「必须等人确认」的关键节点
func isCritical(s step) bool {
	return s.critical
}

// askHuman：从队列弹出一个回答；队列弹空了就默认批准（approve）
func askHuman(question string) string {
	if len(humanReplies) > 0 {
		reply := humanReplies[0]
		humanReplies = humanReplies[1:]
		return reply
	}
	return "approve"
}

// runStep：模拟执行一个普通步骤（离线，不真调工具）
func runStep(name string) string {
	return fmt.Sprintf("已完成「%s」", name)
}

func main() {
	// (步骤名, 是否关键节点)。关键节点 = 高风险、出错代价大、必须人拍板的动作
	steps := []step{
		{"收集用户需求", false},
		{"生成方案草稿", false},
		{"自动保存草稿", false},
		{"对外发送营销邮件", true}, // 高风险：乱发会出事故
		{"更新生产数据库", true},  // 高风险：误改数据难恢复
		{"生成总结报告", false},
	}

	fmt.Println("=======================================================")
	fmt.Println("  人机协同 human-in-the-loop 演示")
	fmt.Println("=======================================================")

	for _, s := range steps {
		fmt.Printf("\n▶ %s\n", runStep(s.name))

		if isCritical(s) {
			decision := askHuman(fmt.Sprintf("关键步骤「%s」需要人工确认：批准还是拒绝？", s.name))
			fmt.Printf("  ⏸ 关键节点「%s」→ 人工决定：%s\n", s.name, decision)
			// 关键节点等人确认：批准才继续，拒绝就立即中止
			if decision != "approve" {
				fmt.Println("  🛑 人工拒绝，流程中止")
				break
			}
		}
	}

	fmt.Println("\n=======================================================")
	fmt.Println("  流程结束")
	fmt.Println("=======================================================")
}
