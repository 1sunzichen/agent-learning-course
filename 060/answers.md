# 关卡 1-2 填空答案 + 三个挑战

先自己填 fill_agent.py 的三个空，卡住了再往下看。填完跑通 = 过关。

---

## 填空答案

**填空 1**（工具描述）：
```
查询某城市的天气，返回天气情况
```
（写什么都行，只要让 LLM 明白"这是查天气的"，它就会在需要天气时调用。描述是 LLM 的"说明书"。）

**填空 2**（分发执行）：
```python
result = TOOL_FUNCS[name](**args)
```
（关键理解：执行工具的是你的程序，不是 LLM。`TOOL_FUNCS[name]` 取出函数，`(**args)` 传参调用。）

**填空 3**（tool_call_id）：
```python
"tool_call_id": tc.id,
```
（关键理解：喂回结果时要带上 `tc.id`，LLM 才能把"这条结果"和"我刚才要调的工具"对上号。）

---

## 挑战 1：加一个 get_time 工具

**目标**：让 agent 除了查天气，还能查当前时间。

**提示**：
1. 定义一个 `get_time()` 函数（用 `datetime.datetime.now()`）
2. 在 `TOOLS` 列表里再加一个 schema（name="get_time"，不需要参数）
3. 把 `get_time` 加进 `TOOL_FUNCS` 字典
4. 改问题为"北京现在几点？"，测试

**答案**（卡住再看）：
```python
import datetime

def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# TOOLS 里加：
{
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "查询当前日期和时间",
        "parameters": {"type": "object", "properties": {}},
    },
},

# TOOL_FUNCS 里加：
"get_time": get_time,
```

---

## 挑战 2：把天气从"假数据"换成真 API

**目标**：get_weather 返回真实天气，而不是写死的"晴，25度"。

**提示**：用免费天气 API wttr.in，不需要注册 key：
```python
import urllib.request
def get_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    return urllib.request.urlopen(url).read().decode()
```
把这行换成真的，再跑，看 agent 是不是拿到了真实天气。

---

## 挑战 3：一次回答调用多个工具

**目标**：问题改成"北京天气怎么样？顺便告诉我现在几点"，让 agent 一轮里连续调用 get_weather 和 get_time 两个工具。

**提示**：代码其实已经支持了（for 循环会遍历所有 tool_calls），你只需要改 `messages` 里的 user 问题。跑起来看它是不是自动连续调了两个工具，再综合回答。

**验收**：跑出来的日志里，出现两行"调用工具"（get_weather 和 get_time），然后一个最终答案。

---

# 关卡 1-3 填空答案 + 三个挑战

先自己填 fill_rag.py 的三个空（共 5 处），卡住了再往下看。填完跑通 = 过关。

## 填空答案

**填空 1**（embed 编码）：
```python
return embed_model.encode(input).tolist()
```
（关键理解：Embedding 就是把「文本」变成「向量」。`encode` 输入一批文本，输出 numpy 数组，`.tolist()` 转成普通 list 才能交给 Chroma。入库和检索都要用同一个模型，向量空间才对得上。）

**填空 2a / 2b**（写入文档）：
```python
collection.add(
    ids=[d["id"] for d in DOCS],
    documents=[d["text"] for d in DOCS],
)
```
（关键理解：入库存的是「原文 + 向量」。向量负责相似度检索，真正喂给 LLM 的是原文 text，别搞混。）

**填空 3a / 3b**（检索）：
```python
results = collection.query(
    query_texts=[query],
    n_results=n,
)
```
（关键理解：检索时把查询词 embed 成向量，去库里的向量空间找「方向最接近」的 top-n。`query_texts` 传列表，所以外面要包一层 `[query]`。）

---

## 挑战 1：给知识库加一条你自己的文档

**目标**：往 DOCS 里加一条关于「Go 语言」的知识，验证它能被检索到。

**提示**：
1. 在 DOCS 列表里加一条，id 用 "11"
2. 把 user 问题改成 "Go 语言有什么特点？"
3. 跑起来，看 search 检索返回的文档里有没有你加的那条

**验收**：日志里 search 返回的结果第一行就是你写的 Go 那条。

---

## 挑战 2：调 top-k 数量，看答案怎么变

**目标**：把 search 返回的文档数从 3 改成 1 或 5，观察检索结果和最终答案的变化。

**提示**：改 `search` 函数的默认参数 `n=3`，或者改调用时的 n。

**思考**：n 太小会漏掉相关信息（召回不足），n 太大又可能塞进不相关的内容干扰 LLM（噪声）。这是 RAG 里要调的核心超参数之一。

---

## 挑战 3：让答案必须「引用原文」

**目标**：让 agent 回答时明确指出依据的是哪条文档，而不是直接编。

**提示**：改 SYSTEM，加一句要求，比如：
```
回答时先复述检索到的相关内容，再给出结论，并说明依据。
```

**验收**：最终答案里能看到 agent 明确引用了 search 返回的原文内容，而不是从自己脑子里直接答。

---

# 关卡 1-4 填空答案 + 三个挑战

先自己填 fill_memory.py 的三个空（共 5 处），卡住了再往下看。填完跑通 = 过关。

## 填空答案

**填空 1**（持久化向量库）：
```python
db = chromadb.PersistentClient(path="./memory_db")
```
（关键理解：和 1-3 的 `chromadb.Client()` 相比，`PersistentClient` 会把数据落到 `./memory_db` 目录。进程退出后数据还在，这才是「长期记忆」。临时库退进程就没了。）

**填空 2a / 2b**（写记忆）：
```python
collection.add(
    ids=[uuid.uuid4().hex],
    documents=[fact],
)
```
（关键理解：`uuid.uuid4().hex` 生成唯一 id，避免重复写入时覆盖旧记录。ids 和 documents 都要是列表。）

**填空 3a / 3b**（读记忆）：
```python
results = collection.query(
    query_texts=[query],
    n_results=n,
)
```
（关键理解：和 1-3 的检索一样，查询词包成列表传进去，取 top-n 最相关的记忆。）

---

## 挑战 1：让记忆带「时间戳」

**目标**：remember 时记录时间，recall 时能知道这条记忆是什么时候存的。

**提示**：
1. remember 里 `collection.add` 加 `metadatas=[{"time": 当前时间}]`
2. recall 里读 `results["metadatas"][0]`，把时间拼进返回值

**思考**：这就是「记忆流时间衰减权重」的雏形——越近的记忆越重要。面试被问"长期记忆怎么排序"，你能答到这一层。

---

## 挑战 2：验证「短期 vs 长期」的边界

**目标**：理解短期记忆（messages）和长期记忆（向量库）各自的生命周期。

**操作**：
1. 运行一次，输入"我叫 Patrick"，quit（记住：此刻长期记忆里有了，短期 messages 在退出时清零）
2. 再运行一次，先输入"我刚才跟你说了什么？"——它会答不上来（因为短期记忆没了）
3. 再输入"我叫什么？"——它从长期记忆 recall 出来

**思考**：为什么同一个"关于我的信息"，第二次跑「我刚说了什么」答不上、但「我叫什么」答得上？因为前者在短期记忆（重启消失），后者进了长期记忆（落盘还在）。

---

## 挑战 3：什么时候该记、什么时候不该记？（面试题）

**思考题**：如果把每一句对话都调 remember 存进长期记忆，会出什么问题？

**答案方向**：
1. 噪声爆炸——大量无意义信息淹没真正重要的记忆，recall 时召回到垃圾
2. 成本高——每条都 embed + 存，浪费算力和存储
3. 所以生产级 agent 的记忆是「有选择地记」：LLM 判断重要性、打分（1~10）、只记重要的，配合时间衰减排序。这就是 Generative Agents 记忆流三权重（recency/importance/relevance）的来源。

