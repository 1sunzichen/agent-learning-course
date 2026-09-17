# Phase 1 · 单 Agent 打地基（Day 1-20）

## 目标
把单个 agent 的每个生产细节手写过一遍，每天一个主题（2 小时/天，学深学透）。
1-1~1-5 已完成，从这里（1-6）继续。

## 文件组织
- 完整版（先看懂）：按关卡命名，如 `memory_agent.py`、`stream_agent.py`、`plan_agent.py`
- 填空版（再自己填）：挖空关键逻辑，先想再跑，如 `001.py`、`003.py`、`005.py`
- `answers.md`：本 Phase 所有关卡的填空答案 + 挑战

## 关卡表（每天一个主题）

| 关卡 | 主题 | 完整版 | 填空版 |
|---|---|---|---|
| 1-1 | ReAct 代码执行 | index2.py | — |
| 1-2 | 工具调用 Function Calling | tool_agent.py | fill_agent.py |
| 1-3 | 加记忆 RAG | rag_agent.py | fill_rag.py |
| 1-4 | 多轮对话 + 持久记忆 | memory_agent.py | 001.py |
| 1-5 | 流式输出 | stream_agent.py | 003.py |
| 1-6 | Plan-and-Execute | plan_agent.py | 005.py |
| 1-7 | Reflection 自我修正 | reflect_agent.py | 007.py |
| 1-8 | 工具设计进阶（重试/超时/幂等） | robust_tools.py | 008.py |
| 1-9 | 可观测性 tracing | trace_agent.py | 009.py |
| 1-10 | 综合单 Agent | full_agent.py | 010.py |
| 1-11 | 上下文窗口管理 | ctx_window.py | 011.py |
| 1-12 | token 计数与成本优化 | token_cost.py | 012.py |
| 1-13 | Prompt 工程 | prompt_eng.py | 013.py |
| 1-14 | 结构化输出 | structured_out.py | 014.py |
| 1-15 | 缓存策略 | caching.py | 015.py |
| 1-16 | Prompt Injection 防御 | prompt_sec.py | 016.py |
| 1-17 | 对话状态机 | dialogue_fsm.py | 待生成 |
| 1-18 | 异步并发调用 | async_tools.py | 待生成 |
| 1-19 | 单 agent 评测 | agent_eval.py | 待生成 |
| 1-20 | Phase 1 复盘 | review_phase1.md | — |

> 1-17~1-20 的完整版/填空版会在做到对应关卡时再生成。

## 依赖
```bash
pip3 install openai chromadb sentence-transformers modelscope
```

## 验收铁律
每关都要写代码跑通才算过关（真知识，不背概念）。填空版先自己想，卡住看 answers.md。
