package main

/*
关卡 3-9 · Go 版 · LangGraph 进阶：checkpoint + 人审节点（对比 Python 版 044.py）

核心：图状态用 checkpoint 持久化，人审节点用 interrupt() 暂停 + Command(resume=...) 恢复。
Go 没有 LangGraph，这里用一个极简「图引擎」模拟：状态 struct + 落盘 JSON checkpoint +
两阶段调用（第一次在 review 暂停、第二次带 resume 值恢复），跑出和 Python 一样的效果。

执行流程（go run 044.go）：
  第一次 run ──▶ generate 节点（产出草稿）──▶ review 节点 ──▶ interrupt() 暂停 ──▶ 状态落盘
  第二次 run(resume="approve") ──▶ review 恢复 ──▶ 走到 END

Go 和 Python 最大的不同：
  Python 的 interrupt() 会真的挂起函数执行（框架/协程能力），Go 没有这个原语，
  用「第一次 run 停在 review 前并落盘、第二次 run 带 resume 值继续」等价表达。
  Python 的 SqliteSaver 存 sqlite 文件；Go 用 encoding/json 落盘到 checkpoints.json。
  Python 的 config thread_id 标识「同一次会话」，Go 这里隐式靠「同一个 checkpoint 文件」衔接两次 run。
*/

import (
	"encoding/json"
	"fmt"
	"os"
)

// State：图的状态（节点之间共享，checkpoint 落盘存的就是它）
type State struct {
	Content  string `json:"content"`  // 生成的草稿
	Approved bool   `json:"approved"` // 人审结果
}

const checkpointFile = "checkpoints.json"

// Graph：极简图引擎（模拟 LangGraph 的 StateGraph + checkpointer）
type Graph struct{}

func (g *Graph) load() State {
	b, err := os.ReadFile(checkpointFile)
	if err != nil {
		return State{}
	}
	var s State
	json.Unmarshal(b, &s)
	return s
}

func (g *Graph) save(s State) {
	b, _ := json.Marshal(s)
	os.WriteFile(checkpointFile, b, 0o644)
}

// generateNode：节点 1 —— 生成内容（简化版，不真调 LLM）
func generateNode(s State) State {
	s.Content = "这是 AI 生成的营销文案草稿（请人工审核）。"
	return s
}

// reviewNode：节点 2 —— 人审。decision = interrupt(...) 的返回值 = 恢复时 resume 传进来的值
func reviewNode(s State, decision string) State {
	s.Approved = decision == "approve"
	return s
}

// run：跑图。resume=="" 表示第一次（在 review 前 interrupt 暂停，返回 false=没跑完）；
// resume 带决定时从 checkpoint 恢复、走完 review 到 END（返回 true=跑完）。
func (g *Graph) run(initial State, resume string) (State, bool) {
	if resume == "" {
		s := generateNode(initial)
		g.save(s) // checkpoint 落盘：状态已持久化
		return s, false
	}
	s := g.load()
	s = reviewNode(s, resume)
	g.save(s)
	return s, true
}

func main() {
	_ = os.Remove(checkpointFile) // 清理旧 checkpoint
	g := &Graph{}

	fmt.Println("=======================================================")
	fmt.Println("  LangGraph 进阶：checkpoint + 人审节点")
	fmt.Println("=======================================================")

	fmt.Println("\n第一次调用：跑到 review 节点会 interrupt 暂停……")
	s, _ := g.run(State{}, "")
	fmt.Printf("  [图已暂停] 当前状态: {content=%q, approved=%v}\n", s.Content, s.Approved)

	fmt.Println("\n人类审完，用 Command(resume=\"approve\") 恢复……")
	s, _ = g.run(s, "approve")
	fmt.Printf("\n  [图已恢复并结束] 最终状态: {content=%q, approved=%v}\n", s.Content, s.Approved)
	fmt.Printf("  ✅ approved = %v（人审通过）\n", s.Approved)

	fmt.Println("\n（checkpoint 是「记忆」存状态，interrupt+resume 是「刹车和油门」停和继续）")
}
