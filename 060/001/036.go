package main

/*
关卡 2-18 · Go 版 · 多 agent 评测（对比 Python 版 036.py）

核心：单 agent 评测看「答对没」，多 agent 评测还要看「协作得怎么样」——
任务完成率、共识效率、产出质量、成本，几个维度一起量化。

执行流程（go run 036.go）：
  若干次协作 run（模拟数据）→ completionRate 算完成率 → efficiencyScore 算效率
      → overall 加权综合 → 汇总多次 run → 出平均协作质量报告

Go 和 Python 最大的不同：
  Python 的 run 是 dict，run["completed"] 取值；Go 用 struct 字段。
  Python 的 f"{cr:.0%}" 百分比格式，Go 没有等价 verb，用 fmt.Printf("%.0f%%", cr*100)。
  Python 的 enumerate(RUNS, 1) 从 1 起编号，Go 的 range 从 0 起，打印时 i+1。
*/

import "fmt"

// run：一次协作评测的模拟数据
// completed/total = 完成的子任务 / 总子任务；rounds = 达成共识用的对话轮数（越少越好）
// quality = 产出质量（0~1，真实系统由 LLM-as-Judge 或 golden 答案比对得出）；cost = 花费（元）
type run struct {
	completed int
	total     int
	rounds    int
	quality   float64
	cost      float64
}

var runs = []run{
	{3, 3, 2, 0.9, 0.0012},
	{2, 3, 4, 0.7, 0.0025},
	{3, 3, 5, 0.85, 0.0031},
}

// completionRate：任务完成率 = 完成的子任务数 / 总子任务数（0~1）
func completionRate(r run) float64 {
	return float64(r.completed) / float64(r.total)
}

// efficiencyScore：效率分 = 1 / 共识轮数（轮数越少越高效，轮数 1 得满分 1.0）
func efficiencyScore(r run) float64 {
	return 1.0 / float64(r.rounds)
}

// qualityScore：产出质量分，直接读 run 的 quality
func qualityScore(r run) float64 {
	return r.quality
}

// overall：综合协作质量 = 完成率 0.4 + 效率 0.3 + 质量 0.3 加权求和
func overall(r run) float64 {
	return 0.4*completionRate(r) + 0.3*efficiencyScore(r) + 0.3*qualityScore(r)
}

func main() {
	fmt.Println("=======================================================")
	fmt.Println("  多 agent 评测：协作质量量化")
	fmt.Println("=======================================================")

	total := 0.0
	for i, r := range runs {
		cr := completionRate(r)
		eff := efficiencyScore(r)
		q := qualityScore(r)
		ov := overall(r)
		total += ov
		fmt.Printf("\n  run%d：完成 %d/%d，共识轮数 %d，成本 ¥%.4f\n", i+1, r.completed, r.total, r.rounds, r.cost)
		fmt.Printf("    完成率 %.0f%%  效率 %.2f  质量 %.2f  → 综合 %.2f\n", cr*100, eff, q, ov)
	}

	avg := total / float64(len(runs))
	fmt.Println("\n=======================================================")
	fmt.Printf("  平均协作质量：%.2f\n", avg)
	fmt.Println("  结论：多 agent 评测 = 完成率 + 效率 + 质量 + 成本，多维度一起看")
	fmt.Println("=======================================================")
}
