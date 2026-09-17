package main

/*
关卡 3-2 · Go 版 · 状态图（对比 Python 版 039.py 的 LangGraph 状态机）

核心：把 2-1 层级式 Multi-Agent（orchestrator.py：拆任务→派 worker→汇总）重写成
状态图版。手写版靠「函数调用链」组织控制流；LangGraph 把「状态 + 节点 + 边」
显式建模成一张图，控制流变成图遍历。Go 里没有 LangGraph，这里用一个极简「图引擎」
（nodes map + edges map + 遍历）还原这套思想。

执行流程（go run 039.go）：
  START ──▶ planner 节点：拆成 3 个子任务 ──▶ workers 节点：逐个执行 ──▶ summarizer 节点：汇总 ──▶ END

三个核心概念（面试 30 秒）：
  1. State：图的「共享内存」，节点之间靠它传数据（这里是一个 struct）
  2. Node：一个函数，输入 state、改写 state（状态转移）
  3. Edge：节点间的转移关系，graph 按边决定执行顺序
Go 和 Python 最大的不同：
  Python 的 State 是 TypedDict，节点返回部分 dict 由框架 merge 回总状态；
  Go 用 struct + 指针，节点直接改 state（没有「返回增量」这一步）。
  Python 的 StateGraph.add_node/add_edge 对应 Go 的 map 注册 + 遍历。
  本演示离线可跑：planner/workers/summarizer 的 LLM 调用用硬编码结果模拟。
*/

import (
	"fmt"
	"strings"
)

// AgentState：图的「状态」，所有节点共享的数据
type AgentState struct {
	task     string
	subtasks []string
	results  []string
	final    string
}

// 节点函数：输入 state、改写 state（对应 LangGraph 的 node 函数）
type nodeFunc func(*AgentState)

// plannerNode：节点 1 —— 拆任务（真系统里调 LLM 拆，这里对演示任务硬编码）
func plannerNode(s *AgentState) {
	s.subtasks = []string{
		"北京的地理位置",
		"北京的著名景点",
		"北京特色美食",
	}
}

// workersNode：节点 2 —— 逐个执行子任务（真系统里调 LLM，这里硬编码）
func workersNode(s *AgentState) {
	mock := map[string]string{
		"北京的地理位置": "北京位于中国华北平原北部，是中国的首都。",
		"北京的著名景点": "故宫、长城、天坛、颐和园等。",
		"北京特色美食":  "北京烤鸭、炸酱面、涮羊肉、豆汁儿。",
	}
	for _, st := range s.subtasks {
		if r, ok := mock[st]; ok {
			s.results = append(s.results, r)
		} else {
			s.results = append(s.results, "（该子任务暂无结果）")
		}
	}
}

// summarizerNode：节点 3 —— 汇总（把各子任务结果整合成一段）
func summarizerNode(s *AgentState) {
	s.final = strings.Join(s.results, "\n")
}

// graph：极简图引擎 = 节点表 + 边表（对应 LangGraph 的 StateGraph）
type graph struct {
	nodes map[string]nodeFunc
	edges map[string]string // 当前节点 -> 下一个节点（"END" 结束）
	start string
}

func (g *graph) addNode(name string, fn nodeFunc) {
	g.nodes[name] = fn
}

func (g *graph) addEdge(from, to string) {
	g.edges[from] = to
}

// run：按边遍历执行（START 只是标记，真正从 g.start 开始）
func (g *graph) run(s *AgentState) {
	cur := g.start
	for cur != "END" {
		g.nodes[cur](s)
		cur = g.edges[cur]
	}
}

func main() {
	task := "介绍北京：包括地理位置、著名景点、特色美食三个方面"

	g := &graph{nodes: map[string]nodeFunc{}, edges: map[string]string{}, start: "planner"}
	g.addNode("planner", plannerNode)
	g.addNode("workers", workersNode)
	g.addNode("summarizer", summarizerNode)
	// 连边：START → planner → workers → summarizer → END
	g.addEdge("planner", "workers")
	g.addEdge("workers", "summarizer")
	g.addEdge("summarizer", "END")

	state := &AgentState{task: task}

	fmt.Println("=======================================================")
	fmt.Println("  状态图重写 2-1 层级式 Multi-Agent")
	fmt.Println("=======================================================")

	g.run(state)

	fmt.Printf("\n  子任务（planner 拆出 %d 个）：\n", len(state.subtasks))
	for i, st := range state.subtasks {
		fmt.Printf("    %d. %s\n", i+1, st)
	}
	fmt.Printf("\n📦 最终汇总：\n%s\n", state.final)
	fmt.Println("\n（控制流由「边」决定，而不是函数调用链——这就是状态图）")
}
