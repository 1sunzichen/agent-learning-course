package main

/*
关卡 2-15 · Go 版 · 跨 agent 分布式 tracing（对比 Python 版 033.py）

核心：一条请求跨多个 agent 时，靠「trace_id + span_id + parent_span_id」把每个环节
串成一条完整链路，出问题能定位到具体是哪个 agent 的哪一步。

执行流程（go run 033.go）：
  入口生成 trace_id → orchestrator 记根 span → 调用子 agent 时传递 trace_id + 父 span
                   → 按 parent 拼成调用树

Go 和 Python 最大的不同（看不懂看这里）：
  Python 用 uuid.uuid4().hex[:8] 生成短 id，Go 标准库没有 uuid，改用 crypto/rand
  取 4 个随机字节再 hex 编码，同样得到 8 位十六进制 id。
  Python 的 span 用 dict（None 表示「没有父 span」），Go 用 struct，父 span 用空字符串 "" 表示。
  递归打印树的闭包 walk，Go 里先 var walk func(...) 声明再赋值（匿名函数引用自己要先声明变量）。
*/

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
)

// Span：一次跨 agent 调用的一个环节
type Span struct {
	trace  string // 属于哪条 trace
	span   string // 自己的 span_id
	parent string // 父 span_id（"" = 根，没有父）
	name   string // 环节名（agent 名）
}

// Tracer：收集所有 span
type Tracer struct {
	spans []Span
}

// newID：生成 8 位十六进制短 id（4 随机字节 → hex）
func newID() string {
	b := make([]byte, 4)
	rand.Read(b)
	return hex.EncodeToString(b)
}

// startTrace：一次请求一个 trace_id，作为整条链路的标识
func (t *Tracer) startTrace() string {
	return newID()
}

// recordSpan：记一个 span（trace_id, 名字, 父 span），返回它的 span_id
func (t *Tracer) recordSpan(traceID, name, parentID string) string {
	spanID := newID()
	t.spans = append(t.spans, Span{trace: traceID, span: spanID, parent: parentID, name: name})
	return spanID
}

// callAgent：模拟「跨 agent 调用」——把 tracing 上下文（trace_id + 父 span）传给下一个 agent
func callAgent(t *Tracer, traceID, parentSpan, agentName string) string {
	return t.recordSpan(traceID, agentName, parentSpan)
}

// renderTree：按 parent 把 span 拼成树形文本
func renderTree(spans []Span) {
	children := map[string][]Span{}
	for _, s := range spans {
		children[s.parent] = append(children[s.parent], s)
	}
	var walk func(parent, indent string)
	walk = func(parent, indent string) {
		for _, s := range children[parent] {
			fmt.Printf("  %s└─ %s (span=%s)\n", indent, s.name, s.span)
			walk(s.span, indent+"  ")
		}
	}
	walk("", "")
}

func main() {
	tracer := &Tracer{}
	traceID := tracer.startTrace()

	// orchestrator 是入口 agent，记根 span（父 span 为空）
	root := tracer.recordSpan(traceID, "orchestrator", "")

	// 模拟调用链：orchestrator → planner / worker → fetcher
	callAgent(tracer, traceID, root, "planner")
	w := callAgent(tracer, traceID, root, "worker")
	callAgent(tracer, traceID, w, "fetcher")

	fmt.Printf("trace_id = %s\n", traceID)
	fmt.Printf("共 %d 个 span，调用树：\n", len(tracer.spans))
	renderTree(tracer.spans)
	fmt.Println("\n（同一条 trace 里的所有 span 共享 trace_id，靠 parent 串成树，这就是分布式 tracing）")
}
