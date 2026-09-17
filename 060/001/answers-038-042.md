# 关卡 3-1~3-5 填空答案（038.py ~ 042.py）

> 先自己填对应 .py 的填空，卡住了再往下看。

---

## 038.py（关卡 3-1 · LangChain 重写）填空答案

**填空 1a / 1b**（ChatOpenAI 连 DeepSeek）：

```python
llm = ChatOpenAI(
    model="deepseek-chat",                # ← 填空 1a
    api_key="sk-你的key",
    base_url="https://api.deepseek.com",  # ← 填空 1b
    temperature=0,
)
```

关键理解：DeepSeek 提供 OpenAI 兼容接口，所以 LangChain 的 `ChatOpenAI` 只要把 `base_url` 指过去、`model` 换成 `deepseek-chat`，就能复用。这就是框架的「适配层」——框架不认识 DeepSeek，但 DeepSeek 会说 OpenAI 的「方言」。

**填空 2**（agent_scratchpad 占位）：

```python
MessagesPlaceholder("agent_scratchpad"),
```

关键理解：tool-calling agent 的 prompt 里必须留一个 `agent_scratchpad` 占位，AgentExecutor 在每一轮「工具调用→结果」往返时把中间消息塞进这里。少了它，agent 记不住自己调过什么工具、结果是什么。

**填空 3a / 3b / 3c**（组装 agent）：

```python
agent = create_tool_calling_agent(
    llm,                    # ← 填空 3a
    [get_weather, calc],    # ← 填空 3b
    prompt,                 # ← 填空 3c
)
```

关键理解：`create_tool_calling_agent(llm, tools, prompt)` 三件套——LLM、工具列表、prompt。它返回一个 agent（本质是 Runnable），再包 `AgentExecutor` 才能跑循环。

### 面试 30 秒

「1-10 手写 160 行的综合 agent，用 LangChain 重写只要 40 行：`@tool` 装饰器替代 tools schema dict，`AgentExecutor` 替代手写 while 循环。但框架不替你写重试/tracing/防护，这些生产细节还得自己补。」

### 挑战：把 1-8 的四层防护包进 @tool

把 1-8 的 `call_weather`（重试/超时/幂等/降级）逻辑搬进 `get_weather` 的 `@tool` 函数体内，看框架的 `@tool` 和手写防护怎么共存——框架管「调度」，你管「工具内部的健壮性」。

---

## 039.py（关卡 3-2 · LangGraph 状态机）填空答案

**填空 1**（状态类）：

```python
builder = StateGraph(AgentState)   # ← 填空 1
```

关键理解：`StateGraph` 的泛型参数就是你的状态类（TypedDict）。它定义了图里流通的数据结构——每个节点读它、返回它的增量。

**填空 2a / 2b**（注册节点）：

```python
builder.add_node("workers", workers_node)      # ← 填空 2a
builder.add_node("summarizer", summarizer_node) # ← 填空 2b
```

关键理解：`add_node("名字", 函数)` 把一个「状态转移函数」挂到图里。节点函数签名是 `(state) -> 部分状态`，返回的 dict 会 merge 回总状态。LangGraph 自动做了「返回值合并回 state」这一步。

**填空 3**（连边）：

```python
builder.add_edge("workers", "summarizer")      # ← 填空 3
```

关键理解：`add_edge(起点, 终点)` 定义节点间的转移关系。加上 `START` 和 `END` 两个特殊节点，就画出了完整执行路径。图的执行顺序完全由「边」决定，不是靠函数调用链。

### 面试 30 秒

「2-1 手写的层级式多 agent，用 LangGraph 重写成 StateGraph：状态是 TypedDict，planner/workers/summarizer 是三个节点，边定义执行顺序。好处是状态显式、天然支持 checkpoint 持久化和人审节点。」

### 挑战：给 results 加 reducer 实现并行累加

LangGraph 支持 `Annotated[List[str], operator.add]` 做「累加 reducer」——多个 worker 并行跑时，各自的结果自动追加而不是覆盖。试试把 `results` 字段改成这种写法，理解为什么多 agent 需要 reducer。

---

## 040.py（关卡 3-3 · MCP 手写实现）填空答案

**填空 1**（tools/list 遍历）：

```python
for name, spec in TOOLS.items()      # ← 填空 1
```

关键理解：`tools/list` 是把 server 侧的 `TOOLS` 字典（内部表示）转成 MCP 标准格式（name/description/inputSchema 三件套）发给客户端。这就是「服务发现」——客户端在调用前先问清楚 server 有什么。

**填空 2a / 2b**（tools/call 执行）：

```python
text = call_tool(name, args)                      # ← 填空 2a
return {
    "content": [{"type": "text", "text": text}],  # ← 填空 2b
    "isError": False,
}
```

关键理解：`tools/call` 是真正干活的方法——拿到工具名和参数，调用本地函数，把结果包成 `{"type": "text", "text": ...}` 的标准 content 格式。注意 `isError` 字段：工具执行失败时置 True，客户端据此区分「正常结果」和「错误」。

**填空 3**（客户端取结果）：

```python
text = r["result"]["content"][0]["text"]   # ← 填空 3
```

关键理解：客户端发的 `tools/call` 请求返回后，结果藏在 `result.content[0].text` 里。这条路径就是 MCP 协议定义的「工具返回文本」的位置。

### 面试 30 秒

「MCP 本质是 JSON-RPC 2.0 over stdio，三个方法：initialize 握手、tools/list 发现工具、tools/call 执行工具。别被协议吓到，就是客户端写一行 JSON 请求、server 回一行 JSON 响应。官方 SDK 只是帮你封装了这个往返。」

### 挑战：加错误处理

`handle_request` 现在对非法 JSON 会直接崩。给 `server_main` 加 try/except：解析失败时回一个 `{"error": {"code": -32700, "message": "Parse error"}}`（这是 JSON-RPC 2.0 规定的标准错误码）。

---

## 041.py（关卡 3-4 · 评估 eval harness）填空答案

**填空 1**（judge 的 system prompt）：

```python
system = "你是严格的阅卷老师。判断学生答案是否满足标准答案的关键点，忽略措辞差异，只输出「对」或「错」。"
```

关键理解：judge prompt 的三个要点——① 角色（严格阅卷）② 判据（只看关键点是否满足，忽略措辞差异）③ 输出格式（只输出对/错）。少了「只输出对/错」，judge 会输出一堆解释，后面的「对」字判定就会误判。

**填空 2**（布尔判定）：

```python
return "对" in verdict      # ← 填空 2
```

关键理解：judge 返回的是一段文字，用 `"对" in verdict` 把文字转成布尔。这是 LLM-as-Judge 的「弱解析」——只要输出里含「对」就算对。更强的做法是要求 judge 只输出 JSON（`{"correct": true}`），再 json.loads 解析。

**填空 3**（通过率）：

```python
rate = round(correct / total * 100)   # ← 填空 3
```

关键理解：通过率 = 答对数 / 总数 × 100，round 取整。这个数字就是「改代码前后对比」的基准——每次改完重跑，看 rate 涨没涨。

### 面试 30 秒

「评估 agent 要建 eval 集（问题+期望关键点），用 LLM-as-Judge 判对错，量化成通过率。没有 eval，改一版代码不知道变好还是变坏。生产里还会加：judge 输出 JSON、多 judge 投票、和人类标注对齐。」

### 挑战：judge 输出结构化 JSON

把 judge 改成只输出 `{"correct": true}` 格式，用 `json.loads` 解析。对比「弱解析」（`"对" in verdict`）和「结构化解析」——后者能拿到「correct 字段」，还能要求 judge 附一句理由，方便 debug 误判。

---

## 042.py（关卡 3-5 · RAG 进阶）填空答案

**填空 1**（chunking 步长）：

```python
for i in range(0, len(text), size - overlap):   # ← 填空 1
```

关键理解：步长 = 窗口大小 - 重叠大小。这样相邻两块之间有 `overlap` 个字符重叠，防止一句话被拦腰切断后两边都丢语义。这是 chunking 的核心参数——窗口太大语义被稀释，太小上下文断片，重叠就是折中。

**填空 2**（余弦相似度）：

```python
return dot / (na * nb)   # ← 填空 2
```

关键理解：余弦 = 点积 / (模长 a × 模长 b)。这里 `dot` 是公共 bigram 的计数乘积之和，`na`/`nb` 是两向量模长。它衡量的是「方向」而非「长度」，所以语义相近但长短不同的文本也能高分。

**填空 3**（混合融合）：

```python
return alpha * d + (1 - alpha) * s   # ← 填空 3
```

关键理解：混合检索 = dense 分 × alpha + sparse 分 × (1-alpha)。dense（语义）和 sparse（关键词）互补：dense 能召回「说法不同但意思一样」的，sparse 能召回「专有名词/精确词」不遗漏。alpha 是旋钮——语义要求高就调大，精确匹配要求高就调小。

**填空 4**（rerank）：

```python
reranked = rerank_with_llm(query, top3)          # ← 填空 4（有 key）
# 或没有 key 的纯本地版：
# reranked = rerank_local(query, top3, hybrid_score)
```

关键理解：rerank 是「粗召回 → 精排」的两段式检索。粗召回（向量/BM25）快但糙，先召回 top-k；rerank 用更强的模型（交叉编码器 / LLM）对这小批候选逐条精打分，把最相关的顶到最前。因为只对 top-k 精排，成本可控。

### 面试 30 秒

「RAG 进阶三招：chunking 带重叠切块防语义稀释；混合检索 dense+sparse 加权互补召回；rerank 对粗召回 top-k 精排。生产对应 sentence-transformers 做 embedding、BM25 做稀疏、bge-reranker 做精排。面试能答到「两段式检索（召回+重排）」这一层就够打。」

### 挑战：对比不同 chunk size 的效果

把 `size=30` 改成 `size=60`、`size=15` 各跑一遍，看命中顺序变不变。思考：窗口太大，关键句被无关内容「稀释」，dense 分数上不去；窗口太小，一句话被切碎，sparse 词频也散了——这就是 chunk size 要调的原因。
