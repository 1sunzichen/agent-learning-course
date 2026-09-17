"""
关卡 1-4 · 持久记忆（填空版）

执行流程图（python3 fill_memory.py）：

【启动】
  ├─ 加载 embedding 模型
  └─ 打开持久化向量库              ← 填空 1 在这里（PersistentClient）

【交互循环】
  └─ 调 LLM（带 remember / recall 工具）
       ├─ remember → collection.add   ← 填空 2（写长期记忆）
       └─ recall   → collection.query ← 填空 3（读长期记忆）

规则：
  1. 下面有 3 个空（标了「填空 X」），填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-4 那节）。
  3. 填完跑 python3 fill_memory.py，两步演示跑通 = 过关。
"""

import json
import uuid
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from modelscope.hub.snapshot_download import snapshot_download
from sentence_transformers import SentenceTransformer
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

print("加载 embedding 模型...")
model_dir = snapshot_download("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
embed_model = SentenceTransformer(model_dir)


class LocalEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return embed_model.encode(input).tolist()


# ── 填空 1 ──────────────────────────────────
# 打开一个「持久化」的向量库，让数据落到磁盘（重启还在）
# 提示：Chroma 有两个客户端，临时库是 chromadb.Client()，
#       持久化库是 chromadb.PersistentClient(path=...)
#       路径写 "./memory_db"，数据会存进这个目录
db = ________   # ← 填空 1

collection = db.get_or_create_collection(
    name="long_term_memory",
    embedding_function=LocalEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"},
)
print(f"长期记忆里已有 {collection.count()} 条记录（重启也不会丢）\n")


# ── 工具实现 ──────────────────────────────────────
def remember(fact):
    """把重要信息写进长期记忆"""
    # ── 填空 2 ──────────────────────────────
    # 把 fact 写进向量库
    # 提示：collection.add 需要 ids 和 documents 两个参数
    #       ids 用 uuid.uuid4().hex 生成唯一 id，避免覆盖
    collection.add(
        ids=________,          # ← 填空 2a
        documents=________,    # ← 填空 2b
    )
    return f"已记住：{fact}"


def recall(query, n=3):
    """从长期记忆检索相关信息"""
    # ── 填空 3 ──────────────────────────────
    # 用查询词检索最相关的 n 条记忆
    # 提示：和 1-3 的 search 一样，用 collection.query
    results = collection.query(
        query_texts=________,   # ← 填空 3a
        n_results=________,     # ← 填空 3b
    )
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

    for step in range(5):
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
