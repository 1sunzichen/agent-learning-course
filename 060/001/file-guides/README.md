# 文件学习地图

[打开网页入口](index.html)

覆盖原目录的 100 个文件，每份对应同名 `.md`、网页和 SVG 图。程序图来自 AST 静态分析；Markdown 与 JSON 是阅读/数据流程。源码没有被修改或执行。

再生成：先用 tools/inspect_go.go 更新 go-analysis.json，再运行 python3 tools/build_guides.py。需要 Python 3、Go 和 Graphviz dot。文字主题在 tools/topics.txt，逐文件说明在生成器 NOTES 中。

|文件|关卡|主题|
|---|---|---|
|[001.py](001.py.md)|1-4 · 全课程第 4 节|跨会话记忆|
|[003.py](003.py.md)|1-5 · 全课程第 5 节|流式输出与工具调用|
|[005.py](005.py.md)|1-6 · 全课程第 6 节|先计划再执行|
|[007.py](007.py.md)|1-7 · 全课程第 7 节|反思与修订|
|[008.py](008.py.md)|1-8 · 全课程第 8 节|工具超时与重试|
|[009.py](009.py.md)|1-9 · 全课程第 9 节|单 Agent 调用记录|
|[010.py](010.py.md)|1-10 · 全课程第 10 节|完整单 Agent|
|[011.py](011.py.md)|1-11 · 全课程第 11 节|上下文窗口管理|
|[012.py](012.py.md)|1-12 · 全课程第 12 节|Token 与费用估算|
|[013.py](013.py.md)|1-13 · 全课程第 13 节|提示词策略对比|
|[014.py](014.py.md)|1-14 · 全课程第 14 节|结构化结果|
|[015.py](015.py.md)|1-15 · 全课程第 15 节|请求缓存|
|[016.py](016.py.md)|1-16 · 全课程第 16 节|提示注入实验|
|[017.py](017.py.md)|1-17 · 全课程第 17 节|对话状态机|
|[018.py](018.py.md)|1-18 · 全课程第 18 节|异步工具并行|
|[019.py](019.py.md)|1-19 · 全课程第 19 节|单 Agent 评测|
|[020.py](020.py.md)|2-1 · 全课程第 21 节|调度者与执行者|
|[020_zhangdi.py](020_zhangdi.py.md)|2-1 · 全课程第 21 节|调度者与执行者|
|[021.py](021.py.md)|2-2 · 全课程第 22 节|多阶段流水线|
|[022.py](022.py.md)|2-3 · 全课程第 23 节|协作讨论|
|[023.py](023.py.md)|2-4 · 全课程第 24 节|竞争与裁判|
|[024.py](024.py.md)|2-5 · 全课程第 25 节|Agent 消息信封|
|[025.py](025.py.md)|2-6 · 全课程第 26 节|共享状态|
|[026.py](026.py.md)|2-7 · 全课程第 27 节|失败降级|
|[027.py](027.py.md)|2-8 · 全课程第 28 节|并发数量控制|
|[028.py](028.py.md)|2-10 · 全课程第 30 节|多 Agent 综合流程|
|[029.go](029.go.md)|2-11 · 全课程第 31 节|任务分解与路由|
|[029.py](029.py.md)|2-11 · 全课程第 31 节|任务分解与路由|
|[030.go](030.go.md)|2-12 · 全课程第 32 节|事件总线|
|[030.py](030.py.md)|2-12 · 全课程第 32 节|事件总线|
|[031.go](031.go.md)|2-13 · 全课程第 33 节|黑板协作|
|[031.py](031.py.md)|2-13 · 全课程第 33 节|黑板协作|
|[032.go](032.go.md)|2-14 · 全课程第 34 节|死锁与重复循环检测|
|[032.py](032.py.md)|2-14 · 全课程第 34 节|死锁与重复循环检测|
|[033.go](033.go.md)|2-15 · 全课程第 35 节|跨角色调用链|
|[033.py](033.py.md)|2-15 · 全课程第 35 节|跨角色调用链|
|[034.go](034.go.md)|2-16 · 全课程第 36 节|预算分摊|
|[034.py](034.py.md)|2-16 · 全课程第 36 节|预算分摊|
|[035.go](035.go.md)|2-17 · 全课程第 37 节|人工确认节点|
|[035.py](035.py.md)|2-17 · 全课程第 37 节|人工确认节点|
|[036.go](036.go.md)|2-18 · 全课程第 38 节|多 Agent 协作评测|
|[036.py](036.py.md)|2-18 · 全课程第 38 节|多 Agent 协作评测|
|[037.go](037.go.md)|2-19 · 全课程第 39 节|工具权限与审计|
|[037.py](037.py.md)|2-19 · 全课程第 39 节|工具权限与审计|
|[038.go](038.go.md)|3-1 · 全课程第 41 节|框架工具调用 Agent|
|[038.py](038.py.md)|3-1 · 全课程第 41 节|框架工具调用 Agent|
|[038_real.go](038_real.go.md)|3-1 · 全课程第 41 节|框架工具调用 Agent|
|[038_real.py](038_real.py.md)|3-1 · 全课程第 41 节|框架工具调用 Agent|
|[039.go](039.go.md)|3-2 · 全课程第 42 节|图式工作流|
|[039.py](039.py.md)|3-2 · 全课程第 42 节|图式工作流|
|[040.go](040.go.md)|3-3 · 全课程第 43 节|MCP 工具通信入门|
|[040.py](040.py.md)|3-3 · 全课程第 43 节|MCP 工具通信入门|
|[041.go](041.go.md)|3-4 · 全课程第 44 节|评测运行器|
|[041.py](041.py.md)|3-4 · 全课程第 44 节|评测运行器|
|[042.go](042.go.md)|3-5 · 全课程第 45 节|切块、混合检索与重排|
|[042.py](042.py.md)|3-5 · 全课程第 45 节|切块、混合检索与重排|
|[043.go](043.go.md)|3-8 · 全课程第 48 节|检索质量指标|
|[043.py](043.py.md)|3-8 · 全课程第 48 节|检索质量指标|
|[044.go](044.go.md)|3-9 · 全课程第 49 节|持久化与暂停恢复|
|[044.py](044.py.md)|3-9 · 全课程第 49 节|持久化与暂停恢复|
|[README.md](README.md.md)|总目录|课程文件导航|
|[a2a.py](a2a.py.md)|2-5 · 全课程第 25 节|Agent 消息信封|
|[agent_eval.py](agent_eval.py.md)|1-19 · 全课程第 19 节|单 Agent 评测|
|[answers-029-033.md](answers-029-033.md.md)|2-11 至 2-15|029—033 参考答案|
|[answers-033-044.md](answers-033-044.md.md)|2-15 至 3-9|033—044 Python/Go 对照|
|[answers-034-037.md](answers-034-037.md.md)|2-16 至 2-19|034—037 参考答案|
|[answers-038-042.md](answers-038-042.md.md)|3-1 至 3-5|038—042 参考答案|
|[answers-043-044.md](answers-043-044.md.md)|3-8 至 3-9|043—044 参考答案|
|[answers.md](answers.md.md)|多节|练习答案与挑战提示|
|[arch_compare.md](arch_compare.md.md)|2-9 · 全课程第 29 节|多 Agent 架构比较|
|[async_tools.py](async_tools.py.md)|1-18 · 全课程第 18 节|异步工具并行|
|[caching.py](caching.py.md)|1-15 · 全课程第 15 节|请求缓存|
|[checkpoints.json](checkpoints.json.md)|3-9 · 全课程第 49 节|暂停恢复的状态快照|
|[collab.py](collab.py.md)|2-3 · 全课程第 23 节|协作讨论|
|[competitive.py](competitive.py.md)|2-4 · 全课程第 24 节|竞争与裁判|
|[concurrency.py](concurrency.py.md)|2-8 · 全课程第 28 节|并发数量控制|
|[ctx_window.py](ctx_window.py.md)|1-11 · 全课程第 11 节|上下文窗口管理|
|[dialogue_fsm.py](dialogue_fsm.py.md)|1-17 · 全课程第 17 节|对话状态机|
|[embed_compare.md](embed_compare.md.md)|3-7 · 全课程第 47 节|Embedding 比较|
|[fault_tolerance.py](fault_tolerance.py.md)|2-7 · 全课程第 27 节|失败降级|
|[full_agent.py](full_agent.py.md)|1-10 · 全课程第 10 节|完整单 Agent|
|[langchain_src.md](langchain_src.md.md)|3-10 · 全课程第 50 节|LangChain 源码阅读路线|
|[multi_agent_project.py](multi_agent_project.py.md)|2-10 · 全课程第 30 节|多 Agent 综合流程|
|[orchestrator.py](orchestrator.py.md)|2-1 · 全课程第 21 节|调度者与执行者|
|[pipeline.py](pipeline.py.md)|2-2 · 全课程第 22 节|多阶段流水线|
|[plan_agent.py](plan_agent.py.md)|1-6 · 全课程第 6 节|先计划再执行|
|[prompt_eng.py](prompt_eng.py.md)|1-13 · 全课程第 13 节|提示词策略对比|
|[prompt_sec.py](prompt_sec.py.md)|1-16 · 全课程第 16 节|提示注入实验|
|[reflect_agent.py](reflect_agent.py.md)|1-7 · 全课程第 7 节|反思与修订|
|[review_phase1.md](review_phase1.md.md)|1-20 · 全课程第 20 节|Phase 1 复盘|
|[review_phase2.md](review_phase2.md.md)|2-20 · 全课程第 40 节|Phase 2 复盘与架构表达|
|[robust_tools.go](robust_tools.go.md)|1-8 · 全课程第 8 节|工具超时与重试|
|[robust_tools.py](robust_tools.py.md)|1-8 · 全课程第 8 节|工具超时与重试|
|[robust_tools_real.py](robust_tools_real.py.md)|1-8 · 全课程第 8 节|工具超时与重试|
|[shared_state.py](shared_state.py.md)|2-6 · 全课程第 26 节|共享状态|
|[stream_agent.py](stream_agent.py.md)|1-5 · 全课程第 5 节|流式输出与工具调用|
|[structured_out.py](structured_out.py.md)|1-14 · 全课程第 14 节|结构化结果|
|[token_cost.py](token_cost.py.md)|1-12 · 全课程第 12 节|Token 与费用估算|
|[trace_agent.py](trace_agent.py.md)|1-9 · 全课程第 9 节|单 Agent 调用记录|
|[vector_db_compare.md](vector_db_compare.md.md)|3-6 · 全课程第 46 节|向量存储比较|