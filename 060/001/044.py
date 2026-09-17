#!/usr/bin/env python3
"""
关卡 3-9 · LangGraph 进阶（填空版）

核心：图状态用 checkpoint 持久化，人审节点用 interrupt() 暂停 + Command(resume=...) 恢复。

依赖：pip install langgraph langgraph-checkpoint-sqlite
（人审节点 interrupt 必须配合 checkpointer 才能用，两者是一对，这也是本关把它们放一起的原因）

执行流程图（python3 044.py）：

   第一次 graph.invoke(...) ──▶ generate 节点（产出草稿）
        └─▶ review 节点 ──▶ interrupt() 暂停 ──▶ 图挂起，状态已落盘
   第二次 graph.invoke(Command(resume="approve")) ──▶ review 恢复 ──▶ 走到 END

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-043-044.md（关卡 3-9 那节）。
  3. 跑通：先看到「图已暂停」，再看到「图已恢复并结束，approved=True」。
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command


class State(TypedDict):
    """图的状态：节点之间共享的数据，checkpoint 落盘存的就是它"""
    content: str     # 生成的草稿
    approved: bool   # 人审结果


def generate_node(state: State) -> dict:
    """节点 1：生成内容（简化版，不真调 LLM）"""
    return {"content": "这是 AI 生成的营销文案草稿（请人工审核）。"}


def review_node(state: State) -> dict:
    """节点 2：人审 —— 在这里暂停图，等人类拍板"""
    # ── 填空 2 ──────────────────────────────────────
    # 用 interrupt() 把「需要人审的内容」抛给外界，图在此挂起；
    # 它的返回值 = 恢复时用 Command(resume=...) 传进来的那个值。
    # 提示：interrupt({"message": ..., "options": ["approve", "reject"]})
    decision = ________   # ← 填空 2
    return {"approved": decision == "approve"}


builder = StateGraph(State)
builder.add_node("generate", generate_node)
builder.add_node("review", review_node)
builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_edge("review", END)

# ── 填空 1 ──────────────────────────────────────
# checkpoint 持久化：把每个节点的状态落盘到 sqlite 文件。
# 提示：SqliteSaver.from_conn_string("checkpoints.sqlite")
# 注：只想存内存不落盘可用 MemorySaver()，但 interrupt 必须有 checkpointer 才能工作。
checkpointer = ________   # ← 填空 1
graph = builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    print("=" * 55)
    print("  LangGraph 进阶：checkpoint + 人审节点")
    print("=" * 55)

    config = {"configurable": {"thread_id": "thread-1"}}

    print("\n第一次调用：跑到 review 节点会 interrupt 暂停……")
    result = graph.invoke({"approved": False}, config)
    print(f"  [图已暂停] 当前状态: {result}")

    # ── 填空 3 ──────────────────────────────────────
    # 人类审完，用 Command(resume=...) 把决定喂回图，让它从暂停点继续跑。
    # 提示：graph.invoke(Command(resume="approve"), config)
    final = graph.invoke(________, config)   # ← 填空 3
    print(f"\n  [图已恢复并结束] 最终状态: {final}")
    print(f"  ✅ approved = {final['approved']}（人审通过）")
