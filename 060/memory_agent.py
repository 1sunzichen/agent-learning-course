#!/usr/bin/env python3
"""
关卡 1-4 · 持久记忆（多轮对话 + 长期记忆）

核心：区分「短期记忆」和「长期记忆」
  短期记忆 = messages 列表（本次会话内的对话历史，进程一退就没了）
  长期记忆 = Chroma PersistentClient（存磁盘，重启进程还在）

和 1-3 的本质区别：
  1-3 用 chromadb.Client()           —— 临时库，存内存，退进程就消失（只能算"会话内检索"）
  1-4 用 chromadb.PersistentClient()  —— 落盘，重启还在（这才是"真长期记忆"）

依赖: pip3 install openai chromadb sentence-transformers modelscope
运行: python3 memory_agent.py

执行流程图（python3 memory_agent.py）：

【启动】
  ├─ 加载 embedding 模型
  └─ 打开持久化向量库 ./memory_db（落盘，重启还在）  ← 和 1-3 的唯一本质区别

【交互循环】
  └─ while True:
       ├─ input("你: ")                          ← 用户输入
       ├─ 调 LLM（带 remember / recall 工具）
       ├─ 用户说"我叫Patrick，喜欢Go" → remember → 写入向量库（落盘）
       ├─ 用户问"我叫什么"           → recall  → 从向量库检索
       └─ quit 退出

【验证持久化】
  第 1 次运行：输入"我叫Patrick，喜欢Go和Python"，quit 退出
  第 2 次运行：输入"我叫什么名字？喜欢什么？"，看它从磁盘回忆出来

方法调用关系：
  顶层脚本 ──> client.chat.completions.create()   （调 LLM）
  remember() ──> collection.add()                 （写长期记忆）
  recall()   ──> collection.query()               （读长期记忆）
"""

import json
import uuid
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from modelscope.hub.snapshot_download import snapshot_download
from sentence_transformers import SentenceTransformer
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# ── ① 加载 embedding 模型 ──────────────────────────
print("加载 embedding 模型...")
model_dir = snapshot_download("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embed_model = SentenceTransformer(model_dir)


class LocalEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return embed_model.encode(input).tolist()


# ── ② 长期记忆：持久化到磁盘（关键！）────────────
# PersistentClient 会把数据存到 ./memory_db 目录，进程退了数据还在
db = chromadb.PersistentClient(path="./memory_db")
collection = db.get_or_create_collection(
    name="long_term_memory",
    embedding_function=LocalEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"},
)
print(f"长期记忆里已有 {collection.count()} 条记录（重启也不会丢）\n")


# ── 工具实现 ──────────────────────────────────────
def remember(fact):
    """把重要信息写进长期记忆"""
    collection.add(ids=[uuid.uuid4().hex], documents=[fact])
    return f"已记住：{fact}"


def recall(query, n=3):
    """从长期记忆检索相关信息"""
    results = collection.query(query_texts=[query], n_results=n)
    docs = results["documents"][0]
    if not docs:
        return "（长期记忆里没有相关信息）"
    return "\n".join(f"- {d}" for d in docs)


TOOL_FUNCS = {"remember": remember, "recall": recall}

# ── 工具白名单 ────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "把关于用户的重要信息（名字、喜好、背景等）写进长期记忆",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string", "description": "要记住的事实，完整一句话"}},
                "required": ["fact"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "从长期记忆检索过去存下的、和用户有关的信息",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "检索关键词"}},
                "required": ["query"],
            },
        },
    },
]

SYSTEM = """你是一个有记忆的 AI 助手。
- 当用户告诉你关于 TA 自己的信息（名字、喜好、背景等）时，调用 remember 存进长期记忆。
- 当用户询问关于过去或 TA 自己的信息时，调用 recall 从长期记忆检索。
- 其他普通问题直接回答，用中文。"""

messages = [{"role": "system", "content": SYSTEM}]

print("=" * 45)
print("   有记忆的 agent ｜ 输入 quit 退出")
print("=" * 45)
print("演示两步：")
print("  1. 输入「我叫Patrick，喜欢Go和Python」，然后 quit")
print("  2. 重新运行本脚本，输入「我叫什么？」，看它从磁盘回忆\n")

while True:
    try:
        user = input("你: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 再见！")
        break

    if not user:
        continue
    if user.lower() == "quit":
        print("👋 再见！（长期记忆已落盘，下次运行还在）")
        break

    messages.append({"role": "user", "content": user})

    for step in range(5):   # 单轮最多 5 次工具调用
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS, temperature=0,
        )
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"  🔧 {name}({args})")
                result = TOOL_FUNCS[name](**args)
                print(f"     → {result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result),
                })
        else:
            print(f"AI: {msg.content}\n")
            messages.append({"role": "assistant", "content": msg.content})
            break
