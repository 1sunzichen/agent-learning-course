#!/usr/bin/env python3
"""
关卡 2-15 · 跨 agent 分布式 tracing（填空版）

核心：一条请求跨多个 agent 时，靠「trace_id + span_id + parent_span_id」把每个环节串成一条完整链路，
出问题能定位到具体是哪个 agent 的哪一步。

执行流程图（python3 033.py）：

入口生成 trace_id → orchestrator 记根 span → 调用子 agent 时传递 trace_id + 父 span → 按 parent 拼成调用树

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-029-033.md（关卡 2-15 那节）。
  3. 跑通：看到一条 trace 里多个 span 按父子关系拼成调用树，还原完整链路。
"""

import uuid


class Tracer:
    def __init__(self):
        self.spans = []  # 所有 span 记录

    def start_trace(self):
        # ── 填空 1 ──────────────────────────────
        # 一次请求一个 trace_id：用 uuid 生成短 id 作为整条链路的标识
        # 提示：uuid.uuid4().hex[:8]
        trace_id = None   # ← 填空 1：生成 trace_id
        return trace_id

    def record_span(self, trace_id, name, parent_id=None):
        # ── 填空 2 ──────────────────────────────
        # 每个 span 有独立 span_id，记下 (trace_id, span_id, parent_id, name) 并返回 span_id
        # 提示：span_id = uuid.uuid4().hex[:8]；self.spans.append({...})；return span_id
        span_id = None   # ← 填空 2：记录一个 span 并返回它的 span_id
        return span_id


def call_agent(tracer, trace_id, parent_span, agent_name):
    """模拟「跨 agent 调用」：把 tracing 上下文（trace_id + 父 span）传给下一个 agent"""
    # ── 填空 3 ──────────────────────────────
    # 给被调用的 agent 记一个 span，parent 指向调用者的 span_id（这就是上下文传播）
    # 提示：tracer.record_span(trace_id, agent_name, parent_id=parent_span)
    span_id = None   # ← 填空 3：为子 agent 记录 span（挂到父 span 下）
    return span_id


def render_tree(spans):
    """按 parent_id 把 span 拼成树形文本"""
    children = {}
    for s in spans:
        children.setdefault(s["parent"], []).append(s)

    def walk(parent, indent):
        for s in children.get(parent, []):
            print(f"  {indent}└─ {s['name']} (span={s['span']})")
            walk(s["span"], indent + "  ")

    walk(None, "")


def main():
    tracer = Tracer()
    trace_id = tracer.start_trace()

    # orchestrator 是入口 agent，记根 span
    root = tracer.record_span(trace_id, "orchestrator")

    # 模拟调用链：orchestrator → planner / worker → fetcher
    call_agent(tracer, trace_id, root, "planner")
    w = call_agent(tracer, trace_id, root, "worker")
    call_agent(tracer, trace_id, w, "fetcher")

    print(f"trace_id = {trace_id}")
    print(f"共 {len(tracer.spans)} 个 span，调用树：")
    render_tree(tracer.spans)
    print("\n（同一条 trace 里的所有 span 共享 trace_id，靠 parent 串成树，"
          "这就是分布式 tracing）")


if __name__ == "__main__":
    print("=" * 55)
    print("  跨 agent 分布式 tracing 演示")
    print("=" * 55)
    main()
