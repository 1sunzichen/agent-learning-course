# 关卡 2-15 ~ 3-9 答案（033 ~ 044）· Python 填空版 + Go 完整版对照

> 每个关卡同时给「Python 填空答案」和「Go 版对应实现」。Go 版是完整可跑的（不是填空），
> 这里把 Go 里「对应 Python 每个空」的那段代码摘出来，方便对照理解。
> 先自己填 0XX.py 的空，卡住了再往下看。

---

## 033（关卡 2-15 · 跨 agent 分布式 tracing）

**填空 1**（生成 trace_id）：
```python
trace_id = uuid.uuid4().hex[:8]
```
Go 对应（Go 没有 uuid，用 crypto/rand 取 4 字节转 hex）：
```go
func newID() string {
    b := make([]byte, 4)
    rand.Read(b)
    return hex.EncodeToString(b)
}
```
关键理解：trace_id 标识「一次完整请求」，跨多少 agent 都共享同一个，才能把零散 span 聚成一条链路。

**填空 2**（记录一个 span）：
```python
span_id = uuid.uuid4().hex[:8]
self.spans.append({"trace": trace_id, "span": span_id, "parent": parent_id, "name": name})
return span_id
```
Go 对应（span 用 struct，父 span 用空字符串表示 None）：
```go
func (t *Tracer) recordSpan(traceID, name, parentID string) string {
    spanID := newID()
    t.spans = append(t.spans, Span{trace: traceID, span: spanID, parent: parentID, name: name})
    return spanID
}
```
关键理解：span 有自己的 span_id + parent（父 span id），靠 parent 才能连成树；`return span_id` 让调用者能把它当「父」传下去。

**填空 3**（跨 agent 传播上下文）：
```python
span_id = tracer.record_span(trace_id, agent_name, parent_id=parent_span)
```
Go 对应：
```go
func callAgent(t *Tracer, traceID, parentSpan, agentName string) string {
    return t.recordSpan(traceID, agentName, parentSpan)
}
```
关键理解：分布式 tracing 的灵魂是「上下文传播」——调用下一个 agent 时必须把 trace_id + 自己的 span_id（作 parent）传下去，否则链路就断了。

---

## 034（关卡 2-16 · 成本分摊与预算控制）

**填空 1**（算单次成本）：
```python
return (prompt_tokens * PRICE_INPUT + completion_tokens * PRICE_OUTPUT) / 1_000_000
```
Go 对应（int 先转 float64）：
```go
func costOf(promptTokens, completionTokens int) float64 {
    return (float64(promptTokens)*priceInput + float64(completionTokens)*priceOutput) / 1_000_000
}
```
关键理解：单价单位是「元/百万 token」，所以要除 1_000_000；输入输出单价不同（输出更贵）必须分开乘。

**填空 2**（成本分摊到各 agent）：
```python
ledger[agent_name] = ledger.get(agent_name, 0.0) + cost
```
Go 对应（map 读不存在的 key 返回零值，天然兜底 0）：
```go
func allocate(ledger map[string]float64, agentName string, cost float64) {
    ledger[agentName] += cost
}
```
关键理解：`get(agent_name, 0.0)` 处理第一次出现的 agent；Go 里 map 的零值机制直接等效，不用显式 get。

**填空 3**（预算止损）：
```python
if total > BUDGET:
    print("  ⛔ 触发预算止损，停止派发新任务")
    stopped = True
    break
```
Go 对应：
```go
if total > budget {
    fmt.Println("  ⛔ 触发预算止损，停止派发新任务")
    stopped = true
    break
}
```
关键理解：止损 = 累计成本超预算线就立即停派。必须在派发循环里每步检查，不是跑完了才发现超支。

---

## 035（关卡 2-17 · 人机协同 HITL）

**填空 1**（判断是否关键节点）：
```python
return step[1]
```
Go 对应（step 是 struct，直接取字段）：
```go
func isCritical(s step) bool {
    return s.critical
}
```
关键理解：step 是 `(名称, 是否关键)` 元组，第二项就是布尔标记；关键节点 = 高风险、不可逆、出错代价大的动作。

**填空 2**（模拟等人确认）：
```python
if HUMAN_REPLIES:
    return HUMAN_REPLIES.pop(0)
return "approve"
```
Go 对应（切片 `[1:]` 模拟 pop(0)）：
```go
func askHuman(question string) string {
    if len(humanReplies) > 0 {
        reply := humanReplies[0]
        humanReplies = humanReplies[1:]
        return reply
    }
    return "approve"
}
```
关键理解：真实系统这里是「发通知给人 + 挂起 + 等人点批准/拒绝」；离线用预置队列模拟，弹空默认 approve 是防御性兜底。

**填空 3**（拒绝即中止）：
```python
if decision != "approve":
    print("  🛑 人工拒绝，流程中止")
    break
```
Go 对应：
```go
if decision != "approve" {
    fmt.Println("  🛑 人工拒绝，流程中止")
    break
}
```
关键理解：HITL 的价值是「人能叫停」——拒绝立即 break，后续步骤不执行，把最终决定权留给人。

---

## 036（关卡 2-18 · 多 agent 评测）

**填空 1**（任务完成率）：
```python
return run["completed"] / run["total"]
```
Go 对应（int 除法要显式转 float）：
```go
func completionRate(r run) float64 {
    return float64(r.completed) / float64(r.total)
}
```
关键理解：完成率 = 完成的子任务/总子任务。多 agent 任务被拆成多个子任务，协作失败常表现为「部分子任务没完成」。

**填空 2**（协作效率）：
```python
return 1.0 / run["rounds"]
```
Go 对应：
```go
func efficiencyScore(r run) float64 {
    return 1.0 / float64(r.rounds)
}
```
关键理解：效率用「共识对话轮数」衡量，1/轮数 把轮数转成 0~1 的分（轮数 1 满分，轮数 5 只有 0.2）。

**填空 3**（加权综合）：
```python
return 0.4 * completion_rate(run) + 0.3 * efficiency_score(run) + 0.3 * quality_score(run)
```
Go 对应：
```go
func overall(r run) float64 {
    return 0.4*completionRate(r) + 0.3*efficiencyScore(r) + 0.3*qualityScore(r)
}
```
关键理解：综合分 = 完成率 0.4 + 效率 0.3 + 质量 0.3；权重按业务侧重调。真实系统「质量」由 LLM-as-Judge 或 golden 比对得出。

---

## 037（关卡 2-19 · 安全与权限隔离）

**填空 1**（白名单查权限）：
```python
return tool in ROLES.get(agent, [])
```
Go 对应（Go 没有 `in`，手写 contains）：
```go
func hasPermission(agent, tool string) bool {
    return contains(roles[agent], tool)
}
```
关键理解：最小权限的落点——每个 agent 只给够用的白名单；`ROLES.get(agent, [])` 对未注册 agent 兜底空列表（默认无权）。

**填空 2**（越权拒绝 + 审计）：
```python
audit_log.append((agent, tool, "无权限"))
return f"⛔ 拒绝：{agent} 无权限调用 {tool}"
```
Go 对应：
```go
if !hasPermission(agent, tool) {
    auditLog = append(auditLog, auditEntry{agent, tool, "无权限"})
    return fmt.Sprintf("⛔ 拒绝：%s 无权限调用 %s", agent, tool)
}
```
关键理解：权限门不在 prompt 里「求模型别乱来」，而在执行层硬拦截——越权直接 return，根本不给执行机会，同时留审计日志。

**填空 3**（敏感操作管理员门槛）：
```python
if tool in SENSITIVE and agent != "管理员":
    audit_log.append((agent, tool, "敏感操作仅限管理员"))
    return f"⛔ 拒绝：敏感操作 {tool} 仅限管理员"
```
Go 对应（set 换成 map[string]bool）：
```go
if sensitive[tool] && agent != "管理员" {
    auditLog = append(auditLog, auditEntry{agent, tool, "敏感操作仅限管理员"})
    return fmt.Sprintf("⛔ 拒绝：敏感操作 %s 仅限管理员", tool)
}
```
关键理解：纵深防御——白名单管「有没有权」，敏感门槛管「够不够格」，两层独立。

---

## 038（关卡 3-1 · LangChain 重写）

**填空 1a / 1b**（ChatOpenAI 连 DeepSeek）：
```python
model="deepseek-chat"
base_url="https://api.deepseek.com"
```
Go 版说明：Go 没有 LangChain，038.go 手写了一个「极简工具调用 agent」（tools 切片 + findTool 按名分发 + agentLoop 循环），把 LangChain 替你省掉的样板显式写出来。没有对应的「连 LLM」这一空，因为 Go 版离线模拟。

**填空 2**（agent_scratchpad 占位）：
```python
MessagesPlaceholder("agent_scratchpad"),
```
Go 对应（agentLoop 里的「调用计划 + 结果喂回」就是这个占位在 Python 里装的东西）：
```go
calls := []call{
    {"get_weather", map[string]string{"city": "北京"}},
    {"calc", map[string]string{"expr": "3*(5+2)"}},
}
```
关键理解：tool-calling agent 的 prompt 必须有 agent_scratchpad 占位，框架在每轮「工具调用→结果」往返时把中间消息塞进去，少了它 agent 记不住自己调过什么。

**填空 3a / 3b / 3c**（组装 agent）：
```python
agent = create_tool_calling_agent(llm, [get_weather, calc], prompt)
```
Go 对应（工具表 + 按名分发就是 create_tool_calling_agent 帮你做的绑定）：
```go
var tools = []Tool{
    {"get_weather", "查询某个城市的天气", ...},
    {"calc", "计算数学表达式，如 3*(5+2)", ...},
}
func findTool(name string) (Tool, bool) { ... }
```
关键理解：create_tool_calling_agent(llm, tools, prompt) 三件套，返回 agent 再包 AgentExecutor 跑循环。框架不替你写重试/tracing/防护，这些生产细节还得自己补。

---

## 039（关卡 3-2 · LangGraph 状态机）

**填空 1**（状态类）：
```python
builder = StateGraph(AgentState)
```
Go 对应（状态是 struct，图是 nodes + edges 两个 map）：
```go
type AgentState struct {
    task     string
    subtasks []string
    results  []string
    final    string
}
```
关键理解：StateGraph 的泛型参数是状态类，定义了图里流通的数据结构；每个节点读它、返回它的增量。

**填空 2a / 2b**（注册节点）：
```python
builder.add_node("workers", workers_node)
builder.add_node("summarizer", summarizer_node)
```
Go 对应：
```go
g.addNode("workers", workersNode)
g.addNode("summarizer", summarizerNode)
```
关键理解：add_node("名字", 函数) 把状态转移函数挂到图里；LangGraph 自动做「返回值 merge 回 state」。

**填空 3**（连边）：
```python
builder.add_edge("workers", "summarizer")
```
Go 对应：
```go
g.addEdge("workers", "summarizer")
```
关键理解：add_edge(起点, 终点) 定义转移关系，执行顺序完全由「边」决定，不是函数调用链。

---

## 040（关卡 3-3 · MCP 手写实现）

**填空 1**（tools/list 遍历）：
```python
for name, spec in TOOLS.items()
```
Go 对应（tools 直接用切片，天然保序）：
```go
case "tools/list":
    return map[string]interface{}{"tools": tools}
```
关键理解：tools/list 把内部 TOOLS 转成 MCP 标准三件套（name/description/inputSchema）发给客户端，这就是「服务发现」。

**填空 2a / 2b**（tools/call 执行）：
```python
text = call_tool(name, args)
return {"content": [{"type": "text", "text": text}], "isError": False}
```
Go 对应：
```go
text := callTool(name, args)
return map[string]interface{}{
    "content": []map[string]interface{}{{"type": "text", "text": text}},
    "isError": false,
}
```
关键理解：tools/call 是真正干活的方法——拿工具名+参数调本地函数，结果包成标准 content 格式；isError 让客户端区分「正常结果」和「错误」。

**填空 3**（客户端取结果）：
```python
text = r["result"]["content"][0]["text"]
```
Go 对应（JSON 解出来是 interface{}，要类型断言逐层取）：
```go
res := r["result"].(map[string]interface{})
content := res["content"].([]interface{})
text := content[0].(map[string]interface{})["text"].(string)
```
关键理解：结果藏在 result.content[0].text 里，这就是 MCP 协议定义的「工具返回文本」位置。

---

## 041（关卡 3-4 · 评估 eval harness）

**填空 1**（judge 的 system prompt）：
```python
system = "你是严格的阅卷老师。判断学生答案是否满足标准答案的关键点，忽略措辞差异，只输出「对」或「错」。"
```
Go 对应（离线模拟 judge 语义：答案里是否含期望关键点）：
```go
func judge(question, answer, expected string) bool {
    return strings.Contains(answer, expected)
}
```
关键理解：judge prompt 三要点——角色（严格阅卷）、判据（只看关键点、忽略措辞）、输出格式（只输出对/错）。Go 版用子串命中近似这个语义匹配。

**填空 2**（布尔判定）：
```python
return "对" in verdict
```
Go 对应：
```go
return strings.Contains(answer, expected)
```
关键理解：judge 返回文字，用「是否含对」转布尔是「弱解析」；更强做法是要求 judge 只输出 JSON 再解析。

**填空 3**（通过率）：
```python
rate = round(correct / total * 100)
```
Go 对应：
```go
rate := int(math.Round(float64(correct) / float64(total) * 100))
```
关键理解：通过率 = 答对数/总数×100，这个数字是「改代码前后对比」的基准。

---

## 042（关卡 3-5 · RAG 进阶）

**填空 1**（chunking 步长）：
```python
for i in range(0, len(text), size - overlap)
```
Go 对应（中文要转 []rune，否则字节会被拦腰切断）：
```go
runes := []rune(text)
step := size - overlap
for i := 0; i < len(runes); i += step {
    end := i + size
    if end > len(runes) { end = len(runes) }
    chunks = append(chunks, string(runes[i:end]))
}
```
关键理解：步长 = 窗口 - 重叠，相邻块之间有 overlap 个字符重叠，防止一句话被拦腰切断。

**填空 2**（余弦相似度）：
```python
return dot / (na * nb)
```
Go 对应：
```go
return dot / (math.Sqrt(na) * math.Sqrt(nb))
```
关键理解：余弦 = 点积/(模长a×模长b)，衡量「方向」而非「长度」，所以语义相近但长短不同的文本也能高分。

**填空 3**（混合融合）：
```python
return alpha * d + (1 - alpha) * s
```
Go 对应：
```go
func hybridScore(query, chunkText string, alpha float64) float64 {
    d := cosine(vec(query), vec(chunkText))
    s := bm25Score(query, chunkText)
    return alpha*d + (1-alpha)*s
}
```
关键理解：混合检索 = dense×alpha + sparse×(1-alpha)；dense 懂意思，sparse 不漏专有名词。

**填空 4**（rerank）：
```python
reranked = rerank_with_llm(query, top3)          # 有 key
# reranked = rerank_local(query, top3, hybrid_score)  # 无 key 降级
```
Go 对应（直接采用本地版：对 top-3 再用 hybrid_score 精排）：
```go
top3 := append([]int(nil), hybrid[:3]...)
sort.SliceStable(top3, func(a, b int) bool {
    return hybridScore(query, chunks[top3[a]], 0.5) > hybridScore(query, chunks[top3[b]], 0.5)
})
```
关键理解：rerank 是「粗召回→精排」两段式；真系统用交叉编码器/LLM 重排，本地降级版用混合分，效果弱但离线能跑。

---

## 043（关卡 3-8 · 检索质量评估）

**填空 1**（recall@k）：
```python
return hits / len(relevant)
```
Go 对应（relevant 是 set，Go 用 map[string]bool）：
```go
func recallAtK(relevant map[string]bool, retrieved []string, k int) float64 {
    hits := 0
    for i, d := range retrieved {
        if i >= k { break }
        if relevant[d] { hits++ }
    }
    return float64(hits) / float64(len(relevant))
}
```
关键理解：recall 看「找全没有」——前 k 个 ∩ 相关文档 / 相关总数，不管排序。

**填空 2**（NDCG@k）：
```python
return dcg_val / idcg_val if idcg_val else 0.0
```
Go 对应：
```go
if idcgVal == 0 { return 0.0 }
return dcgVal / idcgVal
```
关键理解：NDCG = DCG/IDCG，考虑排序位置（靠前折扣小、贡献大）；IDCG 为 0（一个相关都没有）要防除零返回 0。

**填空 3**（MRR）：
```python
scores.append(1 / (i + 1))
```
Go 对应（Python 的 for...else 换成 found 标志）：
```go
for i, d := range p.retrieved {
    if p.relevant[d] {
        scores = append(scores, 1.0/float64(i+1))
        found = true
        break
    }
}
if !found { scores = append(scores, 0.0) }
```
关键理解：MRR 只看「第一个相关文档在第几名」取倒数求平均；i 是 0 起下标，排名 i+1，倒数 1/(i+1)。

---

## 044（关卡 3-9 · LangGraph 进阶：checkpoint + 人审）

**填空 1**（checkpoint 持久化）：
```python
checkpointer = SqliteSaver.from_conn_string("checkpoints.sqlite")
```
Go 对应（encoding/json 落盘到 checkpoints.json，等价 SqliteSaver）：
```go
func (g *Graph) save(s State) {
    b, _ := json.Marshal(s)
    os.WriteFile(checkpointFile, b, 0o644)
}
```
关键理解：checkpoint 把「图执行到哪、状态是什么」落盘；interrupt 必须依赖 checkpointer，否则不知道「暂停在哪、怎么恢复」。

**填空 2**（interrupt 暂停）：
```python
decision = interrupt({"message": ..., "options": ["approve", "reject"]})
```
Go 对应（Go 没有挂起原语，用「resume=="" 时停住并落盘」等价表达）：
```go
if resume == "" {
    s := generateNode(initial)
    g.save(s)
    return s, false   // false = 暂停了，没跑完
}
```
关键理解：interrupt(value) 把 value 抛给外界、图挂起；恢复时它的返回值 = Command(resume=...) 传进来的值。

**填空 3**（Command(resume=...) 恢复）：
```python
final = graph.invoke(Command(resume="approve"), config)
```
Go 对应：
```go
s, _ = g.run(s, "approve")   // 带 resume 值继续，走到 END
```
关键理解：interrupt 挂起后，用 Command(resume=...) 把人的决定喂回图，interrupt 那行才返回、图从暂停点继续；config 的 thread_id 要和第一次一致（标识同一次会话）。

---

## 一句话总结（面试速记）

- 033 tracing：trace_id 串整条链，span 靠 parent 连成树，跨 agent 靠「上下文传播」
- 034 成本：按 agent 记账分摊，超预算立即止损停派
- 035 HITL：高风险动作停下来等人确认，拒绝即中止
- 036 评测：完成率 + 效率 + 质量加权，多维度量化协作
- 037 权限：白名单 + 敏感操作双层门槛 + 审计留痕
- 038 LangChain：框架替你省「工具表 + 分发 + ReAct 循环」，生产细节还得自己补
- 039 LangGraph：状态 + 节点 + 边 = 图，控制流变图遍历
- 040 MCP：JSON-RPC 2.0 + 三个方法 + stdio，本质就是「写一行 JSON、回一行 JSON」
- 041 eval：eval 集 + LLM-as-Judge + 通过率，量化 agent 好坏
- 042 RAG 进阶：带重叠切块 + dense/sparse 混合 + rerank 精排
- 043 检索指标：recall 看找没找全、NDCG 看排没排对、MRR 看第一条相关在哪
- 044 checkpoint：checkpoint 是「记忆」存状态，interrupt+resume 是「刹车和油门」停和继续
