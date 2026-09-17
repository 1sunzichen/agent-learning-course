package main

/*
关卡 3-4 · Go 版 · 评估 eval harness（对比 Python 版 041.py）

核心：建一个小 eval 集 + LLM-as-Judge，跑出通过率。这是「agent 写完了怎么知道好不好」
的工程答案——不能凭感觉，要量化。

执行流程（go run 041.go）：
  [eval 集]
    └─ for 每个 (question, expected)：
         ├─ agent(question) → 调被测 agent 拿实际答案
         ├─ judge(...)      → 用另一个 LLM 当「阅卷老师」判对错
         └─ 记录 ✓/✗ + 答案
    └─ 汇总：通过率 = 答对数 / 总数

三个核心概念（面试 30 秒）：
  1. eval 集 =（问题, 期望关键点）的列表，固定住，每次改代码后重跑对比
  2. LLM-as-Judge = 用一个 LLM 判另一个 LLM 的答案，比字符串完全匹配宽容（语义对就给对）
  3. 通过率 = 量化指标；没有它，改一版代码不知道变好还是变坏

Go 和 Python 最大的不同：
  Python 里 agent 和 judge 都真调 DeepSeek（OpenAI 兼容接口）；
  Go 这里离线模拟：agent 用一张「模拟知识表」作答，judge 用「答案里是否含期望关键点」近似
  语义匹配（真系统里这是 LLM 读两段文字判对错，Go 这里用子串命中模拟，思路一致，不真发请求）。
  为了演示 ✗ 路径，模拟 agent 故意答错一题（太阳系最大行星答成地球），好让 harness 抓到。
*/

import (
	"fmt"
	"math"
	"strings"
)

// evalItem：一道题 = 问题 + 期望答案的关键点
type evalItem struct {
	question string
	expected string
}

var evalSet = []evalItem{
	{"1+1 等于几？", "2"},
	{"中国的首都是哪里？", "北京"},
	{"水的化学式是什么？", "H2O"},
	{"一年有几个季度？", "4"},
	{"太阳系最大的行星是哪个？", "木星"},
}

// agent：被测 agent —— 真系统里直接问 LLM；Go 这里用模拟知识表（并故意错一题）
func agent(question string) string {
	knowledge := map[string]string{
		"1+1 等于几？":     "1+1 等于 2。",
		"中国的首都是哪里？":    "中国的首都是北京。",
		"水的化学式是什么？":    "水的化学式是 H2O。",
		"一年有几个季度？":     "一年有 4 个季度。",
		"太阳系最大的行星是哪个？": "太阳系最大的行星是地球。", // 故意答错，演示 ✗
	}
	if a, ok := knowledge[question]; ok {
		return a
	}
	return "不知道。"
}

// judge：LLM-as-Judge —— 判断答案是否正确。
// 真系统里用 LLM 按「只看关键点是否满足、忽略措辞差异、只输出对/错」判定；
// Go 这里用「答案里是否含期望关键点」近似这个语义匹配。
func judge(question, answer, expected string) bool {
	return strings.Contains(answer, expected)
}

func main() {
	correct := 0
	fmt.Println("==================================================")
	fmt.Println("  eval harness（LLM-as-Judge）")
	fmt.Println("==================================================")

	for _, e := range evalSet {
		answer := agent(e.question)
		ok := judge(e.question, answer, e.expected)
		if ok {
			correct++
		}
		mark := "✓"
		if !ok {
			mark = "✗"
		}
		fmt.Printf("\n  %s Q: %s\n", mark, e.question)
		fmt.Printf("    答: %s\n", answer)
		fmt.Printf("    期望关键点: %s\n", e.expected)
	}

	total := len(evalSet)
	rate := int(math.Round(float64(correct) / float64(total) * 100))
	fmt.Println("\n==================================================")
	fmt.Printf("  通过率：%d/%d = %d%%\n", correct, total, rate)
	fmt.Println("==================================================")
}
