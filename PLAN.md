# 60 天 AI Agent 工程师计划（每天一个主题 · 2 小时）

> 目标：从「会调 API」到「能独立设计 Multi-Agent 系统 + 生产落地」，拿下麦炽科技的 Multi-Agent 岗。
> 铁律：每关都要写代码跑通才算过关（真知识，不背概念）。每天一个主题，学深学透。填空版先自己想，卡住看 answers。

---

## 一、总原则（你的学习法，写死在这）

1. **每天 2 小时怎么分**：
   - 前 20 分钟：复习昨天的关卡（重跑一遍代码 / 回忆关键点，错题本记下卡住的）
   - 中间 90 分钟：今天的新主题（完整版看懂 → 填空版自己填 → 跑通 → 做挑战）
   - 后 10 分钟：写 100~200 字笔记（今天学到什么 + 面试怎么讲）

2. **每关产出**：一个能跑的 .py + 一段笔记。文件全放 `/Users/iss/goPro/algo/2026/060/`（Phase 1 在 001/ 子目录）。

3. **每天一个主题**：不贪多，一个主题学透（原理 + 代码 + 面试点）比囫囵吞枣强。

4. **面试连接点**：每个主题都问自己一句——「面试官问这个，我 30 秒怎么讲？」笔记里写下来。

---

## 二、阶段总览（60 天 · 每天一个主题）

| 阶段 | 天数 | 主题 | 面试价值 |
|---|---|---|---|
| Phase 1 | Day 1-20 | 单 Agent 打地基（生产级细节） | ⭐⭐⭐ |
| Phase 2 | Day 21-40 | Multi-Agent 架构（★核心★） | ⭐⭐⭐⭐⭐ |
| Phase 3 | Day 41-52 | 框架 + 生态（LangChain/LangGraph/MCP/评估） | ⭐⭐⭐⭐ |
| Phase 4 | Day 53-60 | 实战项目 + 部署 + 面试 | ⭐⭐⭐⭐⭐（收口） |

---

## 三、Phase 1 · 单 Agent 打地基（Day 1-20）

> 目标：把单个 agent 的每个生产细节手写过一遍。1-1~1-5 已完成，从 1-6 继续。

| 天 | 关卡 | 主题 | 产出文件 | 验收标准 |
|---|---|---|---|---|
| 1 | 1-1 | ReAct 代码执行 | index2.py | LLM 写 Python 代码，subprocess 执行（玩具版） |
| 2 | 1-2 | 工具调用 Function Calling | tool_agent.py | LLM 从白名单选工具，结构化传参（生产级） |
| 3 | 1-3 | 加记忆 RAG | rag_agent.py | search 工具真检索向量库 |
| 4 | 1-4 | 多轮对话 + 持久记忆 | memory_agent.py | 短期=历史，长期=写向量库，重启还在 |
| 5 | 1-5 | 流式输出 | stream_agent.py | stream=True 逐字吐；tool_calls 的 delta 正确累积 |
| 6 | 1-6 | Plan-and-Execute | plan_agent.py | 先出完整计划再执行，对比 ReAct 差异 |
| 7 | 1-7 | Reflection 自我修正 | reflect_agent.py | 执行完让 LLM 反思错误并重试 |
| 8 | 1-8 | 工具设计进阶 | robust_tools.py | 重试/超时/幂等/降级，模拟失败自动恢复 |
| 9 | 1-9 | 可观测性 tracing | trace_agent.py | 每步 thought/action/observation + token + 耗时进日志 |
| 10 | 1-10 | 综合单 Agent | full_agent.py | 多工具+记忆+流式+重试+tracing 全串起来 |
| 11 | 1-11 | 上下文窗口管理 | ctx_window.py | 长对话超窗时用截断/摘要，不丢关键信息 |
| 12 | 1-12 | token 计数与成本优化 | token_cost.py | 能算出每次调用的 token 数，对比省钱策略 |
| 13 | 1-13 | Prompt 工程 | prompt_eng.py | few-shot / CoT / 角色设定各跑一遍看效果 |
| 14 | 1-14 | 结构化输出 | structured_out.py | LLM 稳定吐 JSON，失败自动校验重试 |
| 15 | 1-15 | 缓存策略 | caching.py | prompt 缓存 / 结果缓存，相同请求不重复花钱 |
| 16 | 1-16 | Prompt Injection 防御 | prompt_sec.py | 构造注入攻击，写出基本防御 |
| 17 | 1-17 | 对话状态机 | dialogue_fsm.py | 用 FSM 管多轮流程（订餐/挂号类）不跑偏 |
| 18 | 1-18 | 异步并发调用 | async_tools.py | asyncio 并行调多个独立工具，省时间 |
| 19 | 1-19 | 单 agent 评测 | agent_eval.py | 建一个小 eval 集，量化 agent 好坏 |
| 20 | 1-20 | Phase 1 复盘 | review_phase1.md | 1-1~1-19 全部重跑，整理成面试弹药 |

---

## 四、Phase 2 · Multi-Agent 架构（Day 21-40）★核心★

> 目标：手写四种多 agent 架构 + 生产细节。麦炽「Multi-Agent 产品 0-1」岗位核心，面试必考。

| 天 | 关卡 | 主题 | 产出文件 | 验收标准 |
|---|---|---|---|---|
| 21 | 2-1 | 层级式 Orchestrator + Workers | orchestrator.py | 主 agent 拆任务→分派→汇总 |
| 22 | 2-2 | 流水线式 pipeline | pipeline.py | 研究→写作→审核串联 |
| 23 | 2-3 | 协作式（对话/辩论） | collab.py | 两个 agent 多轮对话直到一致 |
| 24 | 2-4 | 竞争式（生成 + judge） | competitive.py | 多个 agent 生成，judge 选最优 |
| 25 | 2-5 | A2A 通信协议 | a2a.py | agent 间结构化 JSON 协议 |
| 26 | 2-6 | 状态与上下文共享 | shared_state.py | 子 agent 之间如何共享中间结果 |
| 27 | 2-7 | 容错与降级 | fault_tolerance.py | 某个子 agent 挂掉，整体不崩 |
| 28 | 2-8 | 并发与限流 | concurrency.py | 并行派发 + 控制并发防打爆 API |
| 29 | 2-9 | 架构选型实战（白板对比） | arch_compare.md | 四种架构画出图、说清怎么选 |
| 30 | 2-10 | Multi-Agent 综合项目 | multi_agent_project.py | 一个完整的多 agent 协作任务跑通 |
| 31 | 2-11 | 任务分解与子 agent 委派 | task_decompose.py | 复杂任务怎么拆、怎么分给合适的子 agent |
| 32 | 2-12 | 消息路由与事件总线 | msg_router.py | 谁该收到什么消息，怎么路由不串台 |
| 33 | 2-13 | 黑板模式（共享记忆） | blackboard.py | 多 agent 通过共享黑板协作 |
| 34 | 2-14 | 死锁与循环检测 | deadlock.py | 检测 agent 互相等待 / 无限循环 |
| 35 | 2-15 | 跨 agent 分布式 tracing | dist_trace.py | 一条请求跨多个 agent 也能完整追踪 |
| 36 | 2-16 | 成本分摊与预算控制 | budget.py | 多 agent 的 token 怎么算、怎么设预算止损 |
| 37 | 2-17 | 人机协同 | human_loop.py | 关键节点停下来等人确认（human-in-the-loop） |
| 38 | 2-18 | 多 agent 评测 | multi_eval.py | 协作质量怎么量化 |
| 39 | 2-19 | 多 agent 安全与权限隔离 | agent_sec.py | 不同 agent 不同权限，防止越权 |
| 40 | 2-20 | Phase 2 复盘 | review_phase2.md | 架构面试弹药整理 |

**面试连接点（Phase 2 结束必答得上）**：
- 四种架构分别是什么、适用什么场景、怎么选？
- 层级式和流水线式的本质区别？（控制流 vs 数据流）
- A2A 和 MCP 的区别？（agent-agent vs agent-工具）
- 多 agent 生产落地最大的三个坑？（状态共享 / 容错 / 成本）

---

## 五、Phase 3 · 框架 + 生态（Day 41-52）

> 目标：掌握主流框架，简历能写、面试能聊。手写过的要能用框架重写并对比。

| 天 | 关卡 | 主题 | 产出文件 | 验收标准 |
|---|---|---|---|---|
| 41 | 3-1 | LangChain 重写 | langchain_agent.py | 把 1-10 用 LangChain 重写，对比代码量 |
| 42 | 3-2 | LangGraph 状态机 | langgraph_agent.py | 把 2-1 层级式重写成 LangGraph 版 |
| 43 | 3-3 | MCP 手写实现 | mcp_server.py / mcp_client.py | 手写 MCP server + client，理解协议本质 |
| 44 | 3-4 | 评估 eval harness | eval_harness.py | 20 case eval + LLM-as-Judge，跑出通过率 |
| 45 | 3-5 | RAG 进阶 | rag_adv.py | chunking/rerank/混合检索，对比效果 |
| 46 | 3-6 | 向量库选型对比 | vector_db_compare.md | Chroma/Milvus/FAISS 场景怎么选 |
| 47 | 3-7 | embedding 模型选型 | embed_compare.md | 不同 embedding 的中文效果/维度/成本对比 |
| 48 | 3-8 | 检索质量评估 | retrieval_eval.py | 用 recall/NDCG/MRR 量化检索好坏 |
| 49 | 3-9 | LangGraph 进阶 | langgraph_adv.py | checkpoint 持久化 + 人审节点 |
| 50 | 3-10 | 框架源码导读 | langchain_src.md | 读透 LangChain 一个模块，能讲清原理 |
| 51 | 3-11 | 框架选型对比 | framework_compare.md | LangChain vs 手写 vs 轻量框架怎么选 |
| 52 | 3-12 | Phase 3 复盘 | review_phase3.md | 生态面试弹药整理 |

---

## 六、Phase 4 · 实战项目 + 面试（Day 53-60）

> 目标：一个能写进简历的完整项目 + 部署上线 + 面试收口。

| 天 | 关卡 | 主题 | 产出 | 验收标准 |
|---|---|---|---|---|
| 53 | 4-1 | 项目需求拆解与设计 | research_agent/design.md | 需求拆解 + 架构图 + 技术选型 |
| 54 | 4-2 | 实战：联网检索 agent | research_agent/search_agent.py | 能联网搜 + 检索 + 引用来源 |
| 55 | 4-3 | 实战：多 agent 协作 | research_agent/orchestrator.py | 检索→写作→审核多 agent 串起来 |
| 56 | 4-4 | 实战：报告产出 + API | research_agent/app.py | 输入主题，产出结构化报告 |
| 57 | 4-5 | 服务化 | research_agent/api.py | FastAPI 封装，有 HTTP 接口 |
| 58 | 4-6 | 部署上线 | deploy.md | Docker 部署，拿到公网链接 |
| 59 | 4-7 | 简历 + 系统设计 | resume_projects.md | 项目写成 4 条 bullet + 系统设计题自答 |
| 60 | 4-8 | 模拟面试 | interview_qa.md | 15 道高频题自问自答，录一遍回听 |

---

## 七、里程碑检查点（到点自检，不过关别往下）

- **Day 20（Phase 1 完）**：能不看答案手写一个带工具+记忆+流式+重试的单 agent 循环，并说清上下文管理、结构化输出、安全这些生产细节。
- **Day 40（Phase 2 完）**：能白板画出四种 Multi-Agent 架构，说清区别、适用场景，以及状态共享/容错/成本三大生产坑。
- **Day 52（Phase 3 完）**：LangChain/LangGraph 各有一个能跑的项目，MCP 手写过，eval 跑过，能说清框架和向量库怎么选。
- **Day 60（收口）**：一个部署上线的 Multi-Agent 项目 + 简历 4 条 bullet + 面试模拟一遍。

---

## 八、每天开工前的自检三连（花 20 分钟）

1. 昨天的关卡代码，还能默写出核心循环吗？（不能就重跑一遍）
2. 昨天卡住的地方，现在能一句话说清「为什么卡」吗？
3. 如果面试官现在问昨天的内容，我 30 秒能答上来吗？

答不上来的，记进错题本，今天开工前先补。
