package main

/*
关卡 2-16 · Go 版 · 成本分摊与预算控制（对比 Python 版 034.py）

核心：多 agent 里每个 agent 的 token 都要记账、按 agent 分摊成本，总成本超预算就止损停派。

执行流程（go run 034.go）：
  任务列表 → mockRun 模拟各 agent 消耗 token → costOf 算钱 → allocate 记到各 agent 台账
          → 累计总成本 → 每步检查预算 → 超预算触发止损，不再派新任务

Go 和 Python 最大的不同：
  Python 里 tasks 是 (agent, work) 元组列表，for agent_name, work in tasks 直接解包；
  Go 里元组用 struct{agent, work} 表示，for _, tk := range tasks 后 tk.agent / tk.work 取值。
  Python 排序用 sorted(ledger.items(), key=lambda kv: -kv[1])，Go 用 sort.Slice 手写比较。
  Python 的 len(work) 按字符数（code point），Go 的 len() 按字节数——中文要换成 []rune 才等价。
*/

import (
	"fmt"
	"sort"
)

// deepseek-chat 单价（元 / 百万 token），这里演示计算逻辑，实际以官网为准
const (
	priceInput  = 1.0 // 输入 1 元 / 百万 token
	priceOutput = 2.0 // 输出 2 元 / 百万 token
	budget      = 0.00012
)

type task struct {
	agent string
	work  string
}

// costOf：算一次调用的成本（元）。输入、输出单价不同，要分开乘，再除以 1_000_000。
func costOf(promptTokens, completionTokens int) float64 {
	return (float64(promptTokens)*priceInput + float64(completionTokens)*priceOutput) / 1_000_000
}

// mockRun：模拟一个 agent 执行任务，返回 (prompt_tokens, completion_tokens)。
// 用 work 的字符长度近似 token 数，离线可跑，不真调 LLM。
func mockRun(work string) (int, int) {
	promptTokens := len([]rune(work))
	completionTokens := promptTokens / 2
	return promptTokens, completionTokens
}

// allocate：成本分摊，把本次 cost 累加到 agent_name 名下
func allocate(ledger map[string]float64, agentName string, cost float64) {
	ledger[agentName] += cost
}

// firstN：取字符串前 n 个字符（按 rune，对应 Python 的 s[:n]）
func firstN(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[:n])
}

func main() {
	// 任务队列：(负责的 agent, 要处理的文本)。文本长度近似 token 消耗
	tasks := []task{
		{"规划师", "把用户需求拆成三个子任务并分配给合适的执行者"},
		{"研究员", "搜集与主题相关的背景资料并整理成要点"},
		{"写手", "基于素材写一段通顺的介绍"},
		{"审核员", "检查文章是否有事实错误并给出修改建议"},
		{"规划师", "汇总所有结果产出最终交付物"},
	}

	ledger := map[string]float64{} // 各 agent 的累计成本台账
	total := 0.0                   // 总成本
	stopped := false

	fmt.Println("==========================================================")
	fmt.Printf("  成本分摊与预算控制（总预算 ¥%.6f）\n", budget)
	fmt.Println("==========================================================")

	for _, tk := range tasks {
		pt, ct := mockRun(tk.work)
		c := costOf(pt, ct)
		allocate(ledger, tk.agent, c)
		total += c
		fmt.Printf("  %s：%s… prompt %dt + completion %dt → ¥%.6f\n", tk.agent, firstN(tk.work, 10), pt, ct, c)

		// 预算止损：累计成本超过预算就停下，不再派新任务
		if total > budget {
			fmt.Println("  ⛔ 触发预算止损，停止派发新任务")
			stopped = true
			break
		}
	}

	fmt.Println("\n==========================================================")
	fmt.Println("  各 agent 成本分摊台账（按花费排序）：")
	type kv struct {
		name string
		cost float64
	}
	var pairs []kv
	for name, c := range ledger {
		pairs = append(pairs, kv{name, c})
	}
	sort.Slice(pairs, func(i, j int) bool { return pairs[i].cost > pairs[j].cost })
	for _, p := range pairs {
		fmt.Printf("    %s: ¥%.6f\n", p.name, p.cost)
	}
	fmt.Printf("  总成本：¥%.6f\n", total)
	if stopped {
		fmt.Printf("  ⛔ 已触发预算止损：累计超过 ¥%.6f，停止派发\n", budget)
	} else {
		fmt.Println("  ✅ 未超预算，全部任务完成")
	}
	fmt.Println("==========================================================")
}
