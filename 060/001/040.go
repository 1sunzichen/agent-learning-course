package main

/*
关卡 3-3 · Go 版 · 手写 MCP（对比 Python 版 040.py）

核心：手写一个极简 MCP（Model Context Protocol）server + client，理解协议本质。
MCP = 「JSON-RPC 2.0」+「三个方法」+「stdio 传输」。别被"协议"吓到，本质就是：
客户端往 server 的 stdin 写一行 JSON 请求，server 从 stdout 回一行 JSON 响应。

执行流程（go run 040.go）：
  client（主进程）
    ├─ 启动 server 子进程（stdio 管道相连）
    ├─ ① initialize  → 握手，拿 server 的协议版本和能力
    ├─ ② tools/list  → 发现 server 暴露了哪些工具（name + JSON schema）
    ├─ ③ tools/call  → 按名字 + 参数调用工具，拿回结果
    └─ 打印全过程，看到真实往返的 JSON 报文

三个核心方法（面试 30 秒）：
  1. initialize ：握手 + 版本协商
  2. tools/list ：服务发现
  3. tools/call ：真正执行
JSON-RPC 2.0 报文格式：请求 {jsonrpc, id, method, params}；响应 {jsonrpc, id, result|error}

Go 和 Python 最大的不同：
  Python 用 subprocess.Popen 起子进程 + stdin/stdout 管道读写；
  Go 用 os/exec.Command + StdinPipe/StdoutPipe，配 bufio.Reader 逐行读。
  Python 的 eval(args["expr"]) 在 Go 里手写表达式求值器（evalExpr）。
  一个二进制两种角色：带 --server 参数就是 server（读 stdin），否则是 client（起子进程）。
*/

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

// ================= MCP Server 端 =================

// toolSpec：MCP 规定每个工具是 {name, description, inputSchema} 三件套
type toolSpec struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	InputSchema map[string]interface{} `json:"inputSchema"`
}

var tools = []toolSpec{
	{
		Name:        "get_weather",
		Description: "查询城市天气",
		InputSchema: map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"city": map[string]interface{}{"type": "string"},
			},
			"required": []string{"city"},
		},
	},
	{
		Name:        "calc",
		Description: "计算数学表达式",
		InputSchema: map[string]interface{}{
			"type": "object",
			"properties": map[string]interface{}{
				"expr": map[string]interface{}{"type": "string"},
			},
			"required": []string{"expr"},
		},
	},
}

// callTool：真正执行工具（这是 server 的核心逻辑）
func callTool(name string, args map[string]interface{}) string {
	switch name {
	case "get_weather":
		city, _ := args["city"].(string)
		return fmt.Sprintf("%s 今天晴，25 度（MCP 模拟）", city)
	case "calc":
		expr, _ := args["expr"].(string)
		if !allowedExpr(expr) {
			return "表达式含非法字符"
		}
		v, err := evalExpr(expr)
		if err != nil {
			return "表达式错误"
		}
		return strconv.FormatFloat(v, 'f', -1, 64)
	}
	return fmt.Sprintf("未知工具：%s", name)
}

// handleRequest：按 method 分发，返回 result（这就是 MCP 的「协议处理」）
func handleRequest(req map[string]interface{}) map[string]interface{} {
	method, _ := req["method"].(string)
	switch method {
	case "initialize":
		return map[string]interface{}{
			"protocolVersion": "2024-11-05",
			"capabilities":    map[string]interface{}{"tools": map[string]interface{}{}},
			"serverInfo":      map[string]interface{}{"name": "my-mini-mcp", "version": "0.1.0"},
		}
	case "tools/list":
		return map[string]interface{}{"tools": tools}
	case "tools/call":
		params, _ := req["params"].(map[string]interface{})
		name, _ := params["name"].(string)
		args, _ := params["arguments"].(map[string]interface{})
		text := callTool(name, args)
		return map[string]interface{}{
			"content": []map[string]interface{}{{"type": "text", "text": text}},
			"isError": false,
		}
	}
	return map[string]interface{}{"error": fmt.Sprintf("未知 method: %s", method)}
}

// serverMain：server 主循环，从 stdin 逐行读 JSON 请求，往 stdout 逐行写 JSON 响应
func serverMain() {
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		var req map[string]interface{}
		if err := json.Unmarshal([]byte(line), &req); err != nil {
			continue
		}
		result := handleRequest(req)
		resp := map[string]interface{}{"jsonrpc": "2.0", "id": req["id"]}
		if errMsg, ok := result["error"]; ok {
			resp["error"] = errMsg
		} else {
			resp["result"] = result
		}
		b, _ := json.Marshal(resp)
		fmt.Println(string(b))
	}
}

// ================= MCP Client 端 =================

// rpc：发一个 JSON-RPC 请求，收一个响应
func rpc(stdin *bufio.Writer, reader *bufio.Reader, method string, params map[string]interface{}) map[string]interface{} {
	req := map[string]interface{}{"jsonrpc": "2.0", "id": 1, "method": method}
	if params != nil {
		req["params"] = params
	}
	b, _ := json.Marshal(req)
	stdin.WriteString(string(b) + "\n")
	stdin.Flush()
	line, _ := reader.ReadString('\n')
	var resp map[string]interface{}
	json.Unmarshal([]byte(line), &resp)
	return resp
}

func mainClient() {
	fmt.Println("=======================================================")
	fmt.Println("  手写 MCP：JSON-RPC over stdio（server + client）")
	fmt.Println("=======================================================")

	// 启动 server 子进程，走 stdio 管道
	cmd := exec.Command(os.Args[0], "--server")
	stdinPipe, _ := cmd.StdinPipe()
	stdoutPipe, _ := cmd.StdoutPipe()
	cmd.Start()

	stdin := bufio.NewWriter(stdinPipe)
	reader := bufio.NewReader(stdoutPipe)

	// ① 握手
	r := rpc(stdin, reader, "initialize", nil)
	b, _ := json.Marshal(r)
	fmt.Printf("\n① initialize 响应：%s\n", string(b))

	// ② 发现工具
	r = rpc(stdin, reader, "tools/list", nil)
	fmt.Println("\n② tools/list 响应：")
	res := r["result"].(map[string]interface{})
	for _, t := range res["tools"].([]interface{}) {
		tm := t.(map[string]interface{})
		fmt.Printf("   - %v: %v\n", tm["name"], tm["description"])
	}

	// ③ 调用工具
	r = rpc(stdin, reader, "tools/call", map[string]interface{}{
		"name":      "get_weather",
		"arguments": map[string]interface{}{"city": "北京"},
	})
	res = r["result"].(map[string]interface{})
	content := res["content"].([]interface{})
	first := content[0].(map[string]interface{})
	text := first["text"].(string)
	fmt.Println("\n③ tools/call 结果：", text)

	stdinPipe.Close()
	cmd.Wait()
}

// ============ 表达式求值器（对应 Python 的 eval）============

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

func main() {
	if len(os.Args) > 1 && os.Args[1] == "--server" {
		serverMain()
	} else {
		mainClient()
	}
}
