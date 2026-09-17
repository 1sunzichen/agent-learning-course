package main

/*
关卡 3-1 · Go 版 · 工具调用 Agent（对比 Python 版 038.py 的 LangChain 重写）

核心：Python 里用 LangChain 把 1-10 手写的 160 行综合 agent 缩到 ~40 行——
@tool 装饰器从函数签名自动生成 schema、AgentExecutor 内置 ReAct 循环。
Go 没有 LangChain 生态，这里手写一个「极简工具调用 agent」，把 Python 里
被框架藏起来的样板（工具表 + 按名分发 + ReAct 循环）显式写出来——
正好让你看清 LangChain 到底替你省了什么。

执行流程（go run 038.go）：
  用户问题 → LLM 决定要调工具 → get_weather("北京") → calc("3*(5+2)")
           → 结果喂回 → LLM 输出最终答案

Go 和 Python 最大的不同：
  Python 的 @tool 装饰器自动生成 schema；Go 没有装饰器，工具 = struct（name + description + run 函数）。
  Python 的 eval("3*(5+2)") Go 里没有，得手写递归下降表达式求值器（evalExpr）。
  Python 的 ReAct while 循环由 AgentExecutor 内置；Go 手写（agentLoop）。
  本演示离线可跑：不真调 LLM，用「硬编码的调用计划」模拟 LLM 的决策。
*/

import (
	"fmt"
	"strconv"
	"strings"
)

// Tool：一个工具 = 名字 + 描述 + 执行函数（Go 版的 @tool）
type Tool struct {
	name        string
	description string
	run         func(args map[string]string) string
}

var tools = []Tool{
	{"get_weather", "查询某个城市的天气", func(a map[string]string) string {
		return fmt.Sprintf("%s 今天晴，25 度（模拟）", a["city"])
	}},
	{"calc", "计算数学表达式，如 3*(5+2)", func(a map[string]string) string {
		expr := a["expr"]
		if !allowedExpr(expr) {
			return "表达式含非法字符"
		}
		v, err := evalExpr(expr)
		if err != nil {
			return "表达式错误"
		}
		return strconv.FormatFloat(v, 'f', -1, 64)
	}},
}

// findTool：按名字找工具（对应 Python 里框架自动绑定的「按名分发」）
func findTool(name string) (Tool, bool) {
	for _, t := range tools {
		if t.name == name {
			return t, true
		}
	}
	return Tool{}, false
}

// agentLoop：极简 ReAct 循环 —— 模拟 LLM 的决策：先调工具，再给最终答案
// （Python 里这一步是 AgentExecutor 内置的，Go 里手写）
func agentLoop(question string) string {
	// 模拟 LLM 的决策：识别出两个工具调用（真系统里这是 LLM 输出的 function call）
	type call struct {
		tool string
		args map[string]string
	}
	calls := []call{
		{"get_weather", map[string]string{"city": "北京"}},
		{"calc", map[string]string{"expr": "3*(5+2)"}},
	}

	var results []string
	for _, c := range calls {
		t, ok := findTool(c.tool)
		if !ok {
			results = append(results, fmt.Sprintf("未知工具 %s", c.tool))
			continue
		}
		out := t.run(c.args)
		results = append(results, out)
		fmt.Printf("  🔧 调用 %s(%v) → %s\n", c.tool, c.args, out)
	}

	// 模拟 LLM 拿到工具结果后拼出最终答案
	return fmt.Sprintf("%s；3*(5+2) = %s", results[0], results[1])
}

func main() {
	fmt.Println("=======================================================")
	fmt.Println("  工具调用 Agent（对比 038.py 的 LangChain 重写）")
	fmt.Println("=======================================================")
	q := "北京天气怎么样？顺便算一下 3*(5+2) 等于多少"
	fmt.Printf("\n用户问题：%s\n\n", q)

	answer := agentLoop(q)
	fmt.Printf("\n🎯 最终答案: %s\n", answer)
	fmt.Println("\n（LangChain 在 Python 里替你省掉了：工具表 + 按名分发 + ReAct 循环，")
	fmt.Println("  Go 里这些都手写出来，正是 038.py 里框架藏起来的样板）")
}

// ============ 表达式求值器（对应 Python 的 eval）============

// allowedExpr：只允许数字和 + - * / ( ) . 空格
func allowedExpr(s string) bool {
	for _, c := range s {
		if !strings.ContainsRune("0123456789+-*/(). ", c) {
			return false
		}
	}
	return true
}

type exprParser struct {
	s   string
	pos int
}

// parseExpr：加减（最低优先级）
func (p *exprParser) parseExpr() (float64, error) {
	v, err := p.parseTerm()
	if err != nil {
		return 0, err
	}
	for p.pos < len(p.s) {
		op := p.s[p.pos]
		if op != '+' && op != '-' {
			break
		}
		p.pos++
		rhs, err := p.parseTerm()
		if err != nil {
			return 0, err
		}
		if op == '+' {
			v += rhs
		} else {
			v -= rhs
		}
	}
	return v, nil
}

// parseTerm：乘除（中优先级）
func (p *exprParser) parseTerm() (float64, error) {
	v, err := p.parseFactor()
	if err != nil {
		return 0, err
	}
	for p.pos < len(p.s) {
		op := p.s[p.pos]
		if op != '*' && op != '/' {
			break
		}
		p.pos++
		rhs, err := p.parseFactor()
		if err != nil {
			return 0, err
		}
		if op == '*' {
			v *= rhs
		} else {
			v /= rhs
		}
	}
	return v, nil
}

// parseFactor：数字或括号表达式（最高优先级）
func (p *exprParser) parseFactor() (float64, error) {
	if p.pos >= len(p.s) {
		return 0, fmt.Errorf("表达式不完整")
	}
	if p.s[p.pos] == '(' {
		p.pos++
		v, err := p.parseExpr()
		if err != nil {
			return 0, err
		}
		if p.pos >= len(p.s) || p.s[p.pos] != ')' {
			return 0, fmt.Errorf("缺少右括号")
		}
		p.pos++
		return v, nil
	}
	start := p.pos
	for p.pos < len(p.s) && p.s[p.pos] >= '0' && p.s[p.pos] <= '9' {
		p.pos++
	}
	if start == p.pos {
		return 0, fmt.Errorf("非法数字")
	}
	return strconv.ParseFloat(p.s[start:p.pos], 64)
}

func evalExpr(s string) (float64, error) {
	s = strings.ReplaceAll(s, " ", "")
	p := &exprParser{s: s}
	v, err := p.parseExpr()
	if err != nil {
		return 0, err
	}
	if p.pos != len(s) {
		return 0, fmt.Errorf("表达式尾部有多余字符")
	}
	return v, nil
}
