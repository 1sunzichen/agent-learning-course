"""
关卡 1-3 · 加记忆 RAG（填空版）

执行流程图（python3 fill_rag.py）：

【一次性启动 · 建知识库】
  ├─ ① 加载 embedding 模型
  ├─ ② 定义 DOCS（知识库文档）
  └─ ③ 写 Chroma：embed → 存向量      ← 填空 2 在这里（collection.add）

【Agent 主循环】
  └─ for step in range(10):
       ├─ client.chat.completions.create(messages, tools=TOOLS)
       ├─ msg.tool_calls ?
       │    ├─ 否 → 打印最终答案 → break
       │    └─ 是 → 调用 search 时：
       │          ├─ embed(查询词)     ← 填空 1 在这里（encode）
       │          ├─ collection.query   ← 填空 3 在这里（相似度检索）
       │          └─ messages.append(role="tool", ...)
       └─ 循环

规则：
  1. 下面有 3 个空（标了「填空 X」），填对了代码才能跑通。
  2. 每个空旁边有提示，先自己想，实在卡住再看 answers.md。
  3. 填完跑 python3 fill_rag.py，跑通 = 过关。
"""

import json
import re
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from modelscope.hub.snapshot_download import snapshot_download
from sentence_transformers import SentenceTransformer
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# ── ① 加载 embedding 模型 ──────────────────────────
print("加载 embedding 模型...")
model_dir = snapshot_download("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embed_model = SentenceTransformer(model_dir)


class LocalEmbeddingFunction(EmbeddingFunction):
    """把文本编码成向量，接入 Chroma"""
    def __call__(self, input: Documents) -> Embeddings:
        # ── 填空 1 ──────────────────────────────
        # 用 embedding 模型把输入的文本列表编码成向量列表
        # 提示：embed_model 有个 encode 方法，返回 numpy 数组，要 .tolist() 转成 list
        return ________   # ← 填空 1


# ── ② 知识库文档 ──────────────────────────────────
DOCS = [
    {"id": "1", "text": "ReAct 是 Agent 的一种决策模式，通过 Thought（思考）→ Action（行动）→ Observation（观察）循环逐步解决问题。"},
    {"id": "2", "text": "Function Calling 让 LLM 结构化调用工具：LLM 输出工具名和 JSON 参数，程序按名字分发执行，LLM 本身不执行。"},
    {"id": "3", "text": "RAG（检索增强生成）先检索相关文档，再把文档喂给 LLM 生成答案，解决 LLM 知识过时和幻觉问题。"},
    {"id": "4", "text": "Embedding 把文本映射成高维向量，语义相近的文本向量方向接近，通常用余弦相似度衡量。"},
    {"id": "5", "text": "向量数据库（Chroma、Milvus、pgvector）专门存储和检索高维向量，支持近似最近邻搜索。"},
    {"id": "6", "text": "Multi-Agent 是多个专业 Agent 协作的系统，有层级式、流水线式、协作式、竞争式四种架构。"},
    {"id": "7", "text": "MCP（Model Context Protocol）是连接 LLM 与外部工具/数据源的开放协议，被称为 AI 的 USB 接口。"},
    {"id": "8", "text": "Agent 记忆分短期和长期，长期记忆常用向量库存储加检索，配合时间衰减和重要性加权排序。"},
    {"id": "9", "text": "上下文工程把上下文窗口当作预算经营，通过压缩、裁剪、按需检索等手段避免超限和 lost in the middle。"},
    {"id": "10", "text": "Agent 是能自主规划、调用工具、执行多步骤任务的 AI 系统，核心是决策循环加工具调用。"},
]

# ── ③ 建向量库，写入文档 ──────────────────────────
db = chromadb.Client()
collection = db.create_collection(
    name="agent_memory",
    embedding_function=LocalEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"},
)
# ── 填空 2 ──────────────────────────────────
# 把 DOCS 里的文档写进向量库
# 提示：collection.add 需要三个参数：ids（文档id列表）、documents（文本列表）
collection.add(
    ids=________,        # ← 填空 2a：所有文档的 id
    documents=________,  # ← 填空 2b：所有文档的 text
)
print(f"知识库已建好，共 {collection.count()} 条文档\n")


# ── 工具实现 ──────────────────────────────────────
def calculator(expression):
    if not re.fullmatch(r"[\d+\-*/().%\s]+", expression):
        return "表达式含非法字符"
    return eval(expression)


def get_weather(city):
    return f"{city} 今天晴，25 度（模拟数据）"


def search(query, n=3):
    """真 RAG 检索：查询词 → embed → 向量库相似度搜索 → 返回原文"""
    # ── 填空 3 ──────────────────────────────────
    # 用查询词去向量库检索最相关的 n 篇文档
    # 提示：collection.query 用 query_texts 传查询词，n_results 传返回条数
    #       返回结果里 results["documents"][0] 是文档文本列表
    results = collection.query(
        query_texts=________,   # ← 填空 3a
        n_results=________,     # ← 填空 3b
    )
    docs = results["documents"][0]
    return "\n".join(f"- {d}" for d in docs)


TOOL_FUNCS = {"calculator": calculator, "get_weather": get_weather, "search": search}

# ── 工具白名单 ────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，返回数值结果",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "如 37*53"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某城市的天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "检索知识库文档，返回相关内容（用于回答需要查资料的问题）",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "检索关键词"}},
                "required": ["query"],
            },
        },
    },
]

SYSTEM = "你是 ReAct agent。回答知识性问题前，必须先调用 search 检索知识库，基于检索到的文档回答，不要凭自己的记忆编造。"

messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": "什么是 Multi-Agent？有哪几种架构？"},
]

# ── Agent 主循环 ──────────────────────────────────
for step in range(10):
    resp = client.chat.completions.create(
        model="deepseek-chat", messages=messages, tools=TOOLS, temperature=0,
    )
    msg = resp.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"🔧 调用工具: {name}({args})")
            result = TOOL_FUNCS[name](**args)
            print(f"   结果: {result}\n")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            })
    else:
        print("🎯 最终答案:\n", msg.content)
        break
