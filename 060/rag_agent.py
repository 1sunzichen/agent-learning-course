#!/usr/bin/env python3
"""
关卡 1-3 · 加记忆 RAG
给 agent 接向量库，让 search 工具从「模拟返回」升级成「真检索文档」。

和 1-2 的本质区别：
  1-2（模拟搜索）：search 直接 return 写死的字符串，LLM 要什么都是"模拟结果"
  1-3（真 RAG）：   search 把查询词 embed → 到向量库找最相关的文档 → 返回原文
                    agent 的答案从此「有据可查」，不是拍脑袋编

依赖: pip3 install openai chromadb sentence-transformers modelscope
运行: python3 rag_agent.py
（首次会下载 embedding 模型约 470MB，之后有缓存）

执行流程图（python3 rag_agent.py）：

【一次性启动 · 建知识库】
  ├─ ① 加载 embedding 模型（sentence-transformers 本地模型）
  ├─ ② 定义 DOCS（知识库文档，10 条 AI/Agent 知识点）
  └─ ③ 写 Chroma：每条文档 embed 成向量 → 存库

【Agent 主循环】
  └─ for step in range(10):
       ├─ client.chat.completions.create(messages, tools=TOOLS)   ← 调 LLM（带工具白名单）
       ├─ msg.tool_calls ?
       │    ├─ 否 → 打印最终答案 → break
       │    └─ 是 → 遍历 tool_calls
       │          ├─ 调用 search 时：
       │          │     embed(查询词) → collection.query 相似度检索 → 返回 top-3 原文  ← 真 RAG
       │          └─ messages.append(role="tool", ...)    ← 检索结果喂回 LLM
       └─ 循环

方法调用关系：
  顶层脚本 ──> client.chat.completions.create()   （调 LLM）
  顶层脚本 ──> TOOL_FUNCS[name]()                 （分发执行工具）
  search()  ──> embed_model.encode()              （查询词转向量）
  search()  ──> collection.query()                （向量库相似度检索）
"""

import json
import re
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from modelscope.hub.snapshot_download import snapshot_download
from sentence_transformers import SentenceTransformer
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key（和 tool_agent.py 一样）
    base_url="https://api.deepseek.com",
)

# ── ① 加载 embedding 模型 ──────────────────────────
print("加载 embedding 模型（首次会下载，约 470MB）...")
model_dir = snapshot_download("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embed_model = SentenceTransformer(model_dir)


class LocalEmbeddingFunction(EmbeddingFunction):
    """把文本编码成向量，接入 Chroma"""
    def __call__(self, input: Documents) -> Embeddings:
        return embed_model.encode(input).tolist()


# ── ② 知识库文档（这就是 agent 的"记忆"）──────────
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
collection.add(
    ids=[d["id"] for d in DOCS],
    documents=[d["text"] for d in DOCS],
)
print(f"知识库已建好，共 {collection.count()} 条文档\n")


# ── 工具实现 ──────────────────────────────────────
def calculator(expression):
    if not re.fullmatch(r"[\d+\-*/().%\s]+", expression):
        return "表达式含非法字符"
    return eval(expression)   # 练习用 eval；生产环境用安全解析器


def get_weather(city):
    return f"{city} 今天晴，25 度（模拟数据）"


def search(query, n=3):
    """真 RAG 检索：查询词 → embed → 向量库相似度搜索 → 返回原文"""
    results = collection.query(query_texts=[query], n_results=n)
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

# ── Agent 主循环（和 1-2 完全一样，唯一区别是 search 变成了真 RAG）──
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
