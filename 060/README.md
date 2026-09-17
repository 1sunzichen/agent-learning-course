./run.sh 加文件名字
./run.sh memory_agent.py
# 关卡 1-3 · 加记忆 RAG


## 一句话目标
给 agent 接向量库，让 search 工具从「模拟返回」升级成「真检索文档」，agent 的答案从此有据可查。

## 关卡进度

| 关卡 | 主题 | 文件 | 核心 |
|---|---|---|---|
| 1-1 | 代码执行 ReAct | index2.py | LLM 写 Python 代码，subprocess 执行（玩具版） |
| 1-2 | 工具调用 Function Calling | tool_agent.py / fill_agent.py | LLM 从白名单选工具，结构化传参（生产级） |
| 1-3 | 加记忆 RAG | rag_agent.py / fill_rag.py | search 工具真检索向量库 |
| 1-4 | 持久记忆（多轮+长期记忆） | memory_agent.py / fill_memory.py | 短期记忆 vs 长期记忆，落盘跨会话 |

## 和 1-2 的本质区别

| | 1-2 模拟搜索 | 1-3 真 RAG（本关） |
|---|---|---|
| search 返回什么 | 写死的字符串 "模拟结果" | 向量库里最相关的 top-k 原文 |
| 答案来源 | LLM 自己编 | 检索到的文档（有据可查） |
| 记忆能力 | 无 | 有（知识库 = 长期记忆） |
| 面试价值 | 基础 | ⭐ 最能打的点 |

## 三个关键概念

1. **Embedding**：把文本编码成向量，语义相近的文本向量方向接近。
2. **入库**：文档 → embed → 存 Chroma（存「向量 + 原文」）。
3. **检索**：查询词 → embed → 向量相似度搜索 top-k → 原文喂回 LLM。

## 运行

```bash
pip3 install openai chromadb sentence-transformers modelscope
python3 rag_agent.py     # 完整版，直接跑通看效果
```

首次会下载 embedding 模型（约 470MB），之后有缓存。

你会看到 agent 先调用 `search(query="Multi-Agent")`，从知识库里检索出相关文档，再基于文档回答，而不是直接编。

## 验收标准

1. 日志里 `search` 返回的是知识库里的真实原文（不是"模拟结果"）。
2. 最终答案的内容来自检索到的文档，不是 LLM 凭空编的。
3. 换成知识库里没有的问题（比如"北京天气"），看 agent 是调 get_weather 还是硬用 search 瞎找——理解工具选择。

## 下一步（1-4 多轮记忆 / 流式输出 / 可观测）

给 agent 加多轮对话的持久记忆，或加 tracing 看每一步的 token/耗时。生产级 agent 的三个必修：流式、重试、可观测。
