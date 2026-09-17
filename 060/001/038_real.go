package main

/*
038_real.go · 真实版工具调用 Agent（Go 版，对照 038_real.py / 038.go）

Python 版三件套在 Go 里的对应：
  langchain_openai.ChatOpenAI   →  chat() 函数：net/http 真调 DeepSeek
  langchain_core.tools 的 @tool →  Tool 结构体 + tools 切片（name+description+参数schema+run）
  langchain.agents 的 create_agent → agentRun() 手写 ReAct 循环

和 038.go 手写模拟版的区别：这里不硬编码调用计划，而是真调 DeepSeek，
LLM 实时输出 tool_calls，我们按它给的名字/参数去分发执行——这才是真实流程。

跑法：
  export DEEPSEEK_API_KEY=sk-你的key   # 或改下面 apiKey 常量
  go run 038_real.go
*/

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
)

const deepseekBase = "https://api.deepseek.com"

// 从环境变量读 key，读不到就用占位符
func apiKey() string {
	if k := os.Getenv("DEEPSEEK_API_KEY"); k != "" {
		return k
	}
	return "sk-换成你自己的key"
}

// ============ 工具定义（对应 Python 的 @tool）============

// Tool：一个工具 = 名字 + 描述 + 参数 schema + 执行函数
type Tool struct {
	Name        string
	Description string
	Parameters  map[string]any // JSON Schema 的 properties（name -> {type, description}）
	Run         func(args map[string]any) (string, error)
}

// 天气工具：真调 Open-Meteo（免费、无需 key）
func getWeather(args map[string]any) (string, error) {
	city, _ := args["city"].(string)

	gURL := "https://geocoding-api.open-meteo.com/v1/search?" + url.Values{
		"name": {city}, "count": {"1"}, "language": {"zh"}, "format": {"json"},
	}.Encode()
	resp, err := http.Get(gURL)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	var geo struct {
		Results []struct {
			Name      string  `json:"name"`
			Latitude  float64 `json:"latitude"`
			Longitude float64 `json:"longitude"`
		} `json:"results"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&geo); err != nil {
		return "", err
	}
	if len(geo.Results) == 0 {
		return fmt.Sprintf("没找到城市「%s」", city), nil
	}
	loc := geo.Results[0]

	wURL := "https://api.open-meteo.com/v1/forecast?" + url.Values{
		"latitude":  {strconv.FormatFloat(loc.Latitude, 'f', -1, 64)},
		"longitude": {strconv.FormatFloat(loc.Longitude, 'f', -1, 64)},
		"current":   {"temperature_2m,weather_code"},
	}.Encode()
	resp2, err := http.Get(wURL)
	if err != nil {
		return "", err
	}
	defer resp2.Body.Close()
	var w struct {
		Current struct {
			Temperature float64 `json:"temperature_2m"`
			WeatherCode int     `json:"weather_code"`
		} `json:"current"`
	}
	if err := json.NewDecoder(resp2.Body).Decode(&w); err != nil {
		return "", err
	}

	codes := map[int]string{0: "晴", 1: "多云", 2: "阴", 3: "阴", 45: "雾",
		51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
		61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 95: "雷雨"}
	desc := codes[w.Current.WeatherCode]
	if desc == "" {
		desc = fmt.Sprintf("天气码%d", w.Current.WeatherCode)
	}
	return fmt.Sprintf("%s 当前%s，气温 %.1f°C", loc.Name, desc, w.Current.Temperature), nil
}

// 计算工具：Go 里没有 eval，用递归下降求值（这里允许 + - * / ( ) 和数字）
func calcRun(args map[string]any) (string, error) {
	expr, _ := args["expr"].(string)
	v, err := evalExpr(expr)
	if err != nil {
		return "表达式错误：" + err.Error(), nil
	}
	return strconv.FormatFloat(v, 'f', -1, 64), nil
}

// tools 切片 + 按名索引（对应 @tool 生成的工具表 + findTool 分发）
var tools = []Tool{
	{
		Name:        "get_weather",
		Description: "查询某个城市的实时天气",
		Parameters: map[string]any{
			"city": map[string]any{"type": "string", "description": "中文城市名，如 北京"},
		},
		Run: getWeather,
	},
	{
		Name:        "calc",
		Description: "计算数学表达式，如 3*(5+2)，支持 + - * / 和括号",
		Parameters: map[string]any{
			"expr": map[string]any{"type": "string", "description": "数学表达式"},
		},
		Run: calcRun,
	},
}

var toolMap = func() map[string]Tool {
	m := map[string]Tool{}
	for _, t := range tools {
		m[t.Name] = t
	}
	return m
}()

// ============ DeepSeek OpenAI 兼容接口（对应 ChatOpenAI）============

type Message struct {
	Role       string     `json:"role"`
	Content    string     `json:"content,omitempty"`
	ToolCalls  []ToolCall `json:"tool_calls,omitempty"`
	ToolCallID string     `json:"tool_call_id,omitempty"`
}

type ToolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function FunctionCall `json:"function"`
}

type FunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"` // JSON 字符串，需要自己解析
}

type functionSchema struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Parameters  map[string]any `json:"parameters"`
}

type toolDef struct {
	Type     string         `json:"type"`
	Function functionSchema `json:"function"`
}

type chatRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
	Tools    []toolDef `json:"tools"`
}

type chatResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

// chat：真调 DeepSeek 的 /chat/completions，把工具 schema 一起发过去
func chat(messages []Message) (Message, error) {
	defs := make([]toolDef, 0, len(tools))
	for _, t := range tools {
		defs = append(defs, toolDef{
			Type: "function",
			Function: functionSchema{
				Name:        t.Name,
				Description: t.Description,
				Parameters: map[string]any{
					"type":       "object",
					"properties": t.Parameters,
				},
			},
		})
	}
	body, _ := json.Marshal(chatRequest{Model: "deepseek-chat", Messages: messages, Tools: defs})

	req, err := http.NewRequest("POST", deepseekBase+"/chat/completions", bytes.NewReader(body))
	if err != nil {
		return Message{}, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey())

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return Message{}, err
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return Message{}, fmt.Errorf("DeepSeek 返回 %d: %s", resp.StatusCode, string(raw))
	}
	var cr chatResponse
	if err := json.Unmarshal(raw, &cr); err != nil {
		return Message{}, err
	}
	if len(cr.Choices) == 0 {
		return Message{}, fmt.Errorf("空响应")
	}
	return cr.Choices[0].Message, nil
}

// ============ ReAct 循环（对应 create_agent）============

func agentRun(question string) string {
	messages := []Message{{Role: "user", Content: question}}

	for round := 0; round < 10; round++ {
		msg, err := chat(messages)
		if err != nil {
			return "LLM 调用失败：" + err.Error()
		}

		// 没有 tool_calls → 就是最终答案
		if len(msg.ToolCalls) == 0 {
			return msg.Content
		}

		// 有 tool_calls → 把 assistant 消息原样留下，逐个执行工具并回填结果
		messages = append(messages, msg)
		for _, tc := range msg.ToolCalls {
			var args map[string]any
			if err := json.Unmarshal([]byte(tc.Function.Arguments), &args); err != nil {
				args = map[string]any{}
			}
			t, ok := toolMap[tc.Function.Name]
			var out string
			if !ok {
				out = "未知工具 " + tc.Function.Name
			} else if r, err := t.Run(args); err != nil {
				out = "工具执行出错：" + err.Error()
			} else {
				out = r
			}
			fmt.Printf("  🔧 调用 %s(%s) → %s\n", tc.Function.Name, tc.Function.Arguments, out)
			messages = append(messages, Message{Role: "tool", ToolCallID: tc.ID, Content: out})
		}
	}
	return "超过最大轮数仍未得出答案"
}

func main() {
	fmt.Println("=======================================================")
	fmt.Println("  真实版工具调用 Agent（Go 真调 DeepSeek + 真天气 API）")
	fmt.Println("=======================================================")
	q := "北京天气怎么样？顺便算一下 3*(5+2) 等于多少"
	fmt.Printf("\n用户问题：%s\n\n", q)
	fmt.Printf("\n🎯 最终答案: %s\n", agentRun(q))
}

// ============ 表达式求值器（对应 Python 的 calc 工具）============

type parser struct {
	s   string
	pos int
}

func (p *parser) parseExpr() (float64, error) {
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

func (p *parser) parseTerm() (float64, error) {
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

func (p *parser) parseFactor() (float64, error) {
	if p.pos >= len(p.s) {
		return 0, fmt.Errorf("表达式不完整")
	}
	// 一元正负号：-3、-(2+3)
	if p.s[p.pos] == '-' {
		p.pos++
		v, err := p.parseFactor()
		if err != nil {
			return 0, err
		}
		return -v, nil
	}
	if p.s[p.pos] == '+' {
		p.pos++
		return p.parseFactor()
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
	// 去空格
	b := make([]byte, 0, len(s))
	for i := 0; i < len(s); i++ {
		if s[i] != ' ' {
			b = append(b, s[i])
		}
	}
	p := &parser{s: string(b)}
	v, err := p.parseExpr()
	if err != nil {
		return 0, err
	}
	if p.pos != len(p.s) {
		return 0, fmt.Errorf("表达式尾部有多余字符")
	}
	return v, nil
}
