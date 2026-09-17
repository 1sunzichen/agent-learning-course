#!/usr/bin/env python3
"""
关卡 3-2 · LangGraph 状态机（填空版）

核心：把 2-1 层级式 Multi-Agent（orchestrator.py：拆任务→派 worker→汇总）重写成
LangGraph 状态图版。手写版靠「函数调用链」组织控制流；LangGraph 把「状态 + 节点 + 边」
显式建模成一张图，控制流变成图遍历。

执行流程图（python3 039.py）：

START
  └─ planner 节点：LLM 拆成 3 个子任务 → 写回 state["subtasks"]
       └─ workers 节点：逐个执行子任务 → 写回 state["results"]
            └─ summarizer 节点：LLM 汇总 → 写回 state["final"]
                 └─ END

三个核心概念（面试 30 秒）：
  1. State（TypedDict）：图的「共享内存」，节点之间靠它传数据
  2. Node（节点）：一个函数，输入 state、输出 state 的增量（状态转移）
  3. Edge（边）：节点间的转移关系，graph 按边决定执行顺序
LangGraph 比手写强在哪：状态显式、易加 checkpoint / 人审 / 并行分支（3-9 讲）。

依赖（先装）：
  pip3 install langgraph langchain-openai

规则：
  1. 下面有 3 个空（填空 2 含 a/b 两处），填对了才能跑通。
  2. 卡住看 answers-038-042.md（关卡 3-2 那节）。
  3. 跑通：打印出「📦 最终汇总：」那一行。
"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-你的key",               # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
    temperature=0,
)


def _llm(system, user):
    resp = llm.invoke([("system", system), ("human", user)])
    return resp.content.strip()


# 图的「状态」：所有节点共享的数据（每个字段是节点间传话的载体）
class AgentState(TypedDict):
    task: str
    subtasks: List[str]
    results: List[str]
    final: str


# 节点 1：planner，拆任务
def planner_node(state: AgentState):
    plan = _llm(
        "你是任务规划师。把用户的任务拆成 3 个独立的子任务，每行一个，不要编号。",
        f"任务：{state['task']}",
    )
    return {"subtasks": [s.strip("- ").strip() for s in plan.split("\n") if s.strip()]}


# 节点 2：workers，逐个执行子任务
def workers_node(state: AgentState):
    results = [
        _llm("你是一个执行者，简洁完成交给你的子任务。", f"子任务：{s}")
        for s in state["subtasks"]
    ]
    return {"results": results}


# 节点 3：summarizer，汇总
def summarizer_node(state: AgentState):
    joined = "\n".join(f"- {r}" for r in state["results"])
    final = _llm(
        "你是一个总结者，把各子任务的结果整合成一段完整回答。",
        f"任务：{state['task']}\n各子任务结果：\n{joined}\n请整合：",
    )
    return {"final": final}


# ── 填空 1 ──────────────────────────────────────
# 建 StateGraph，告诉它用哪个状态类型
# 提示：把上面定义的状态类传进去
builder = StateGraph(________)          # ← 填空 1：状态类名


# ── 填空 2 ──────────────────────────────────────
# 注册节点：把函数挂到图里并命名
builder.add_node("planner", planner_node)
builder.add_node("workers", ________)       # ← 填空 2a：workers 节点对应的函数
builder.add_node("summarizer", ________)    # ← 填空 2b：summarizer 节点对应的函数


# ── 填空 3 ──────────────────────────────────────
# 连边：定执行顺序（START → planner → workers → summarizer → END）
builder.add_edge(START, "planner")
builder.add_edge("planner", "workers")
builder.add_edge(________, ________)        # ← 填空 3：workers → summarizer
builder.add_edge("summarizer", END)


graph = builder.compile()                   # 把图固化成可执行的 Graph


if __name__ == "__main__":
    task = "介绍北京：包括地理位置、著名景点、特色美食三个方面"
    print("=" * 55)
    print("  LangGraph 状态机重写 2-1 层级式 Multi-Agent")
    print("=" * 55)
    result = graph.invoke({"task": task, "subtasks": [], "results": [], "final": ""})
    print("\n📦 最终汇总：\n" + result["final"])
