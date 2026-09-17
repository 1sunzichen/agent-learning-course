#!/usr/bin/env python3
"""
关卡 1-9 · 可观测性 tracing（完整版）

核心：agent 是个黑盒——你不知道它每一步「想了什么、调了什么、耗时多久、花了多少 token」。
tracing 就是给 agent 装摄像头，把每一步都记下来，出问题能定位到「哪一步慢 / 哪一步错」。

执行流程图（python3 trace_agent.py）：

用户提问
  └─ for step in 循环：
       ├─ 调 LLM（计时 + 记 token）→ record("llm_call", ...)
       ├─ 有工具调用？
       │    ├─ record("action", 工具名+参数)
       │    ├─ 执行工具 → record("observation", 结果)
       │    └─ 把结果喂回 messages，继续循环
       └─ 没有工具调用 → record("final", 最终答案)，结束
  └─ 打印 trace 汇总：每步耗时 + 总 token + 总耗时

和前面关卡的区别：
  1-1~1-8 的 agent 都在「裸奔」——跑错了只能靠 print 猜
  1-9 给 agent 加了一层 trace，每步留痕，可回溯

方法调用关系：
  record() ──> trace.append（记一条）+ print（实时显示）
  run_agent() ──> client.chat.completions.create（计时/记token）+ record()

面试怎么讲（30 秒）：
  "生产 agent 必须可观测。tracing 就是记录 agent 每一步的输入输出、耗时、token 用量，
  出问题能定位到具体哪一步。OpenTelemetry、LangSmith、Langfuse 都是干这个的。"
"""

import time
import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 一个简单的天气工具
def get_weather(city):
    return f"{city} 晴，25度"

TOOL_FUNCS = {"get_weather": get_weather}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "查询某个城市的天气",
        "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "城市名"}}, "required": ["city"]},
    }},
]

SYSTEM = "你是一个助手。用户问天气就调用 get_weather 工具。"

# ===== trace 记录器 =====
trace = []

def record(kind, content, tokens=None, t0=None):
    """记录一条 trace。kind=类型，content=内容，tokens=token数，t0=开始时间戳（算耗时用）"""
    entry = {"step": len(trace) + 1, "kind": kind, "content": content}
    if tokens is not None:
        entry["tokens"] = tokens
    if t0 is not None:
        entry["ms"] = round((time.time() - t0) * 1000)   # 耗时转毫秒
    trace.append(entry)
    # 实时打印
    tail = ""
    if tokens is not None:
        tail += f"  [{tokens} tok]"
    if t0 is not None:
        tail += f"  ({entry['ms']}ms)"
    print(f"  [trace #{entry['step']}] {kind}: {content}{tail}")
    return entry


def run_agent(question):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": question}]
    for step in range(6):
        t0 = time.time()
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS, temperature=0,
        )
        usage = resp.usage
        record("llm_call", f"第{step+1}次调用 LLM",
               tokens=usage.total_tokens if usage else None, t0=t0)
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                record("action", f"{name}({args})")
                result = TOOL_FUNCS[name](**args)
                record("observation", str(result))
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})
        else:
            record("final", msg.content)
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content
    return "（达到最大步数仍未结束）"


if __name__ == "__main__":
    print("=" * 55)
    print("  带 trace 的 agent：问「北京天气怎么样？」")
    print("=" * 55)
    answer = run_agent("北京天气怎么样？")

    print("\n" + "=" * 55)
    print("  📊 trace 汇总")
    print("=" * 55)
    total_tokens = sum(e.get("tokens", 0) for e in trace)
    total_ms = sum(e.get("ms", 0) for e in trace)
    llm_calls = sum(1 for e in trace if e["kind"] == "llm_call")
    print(f"  总步骤：{len(trace)} 步")
    print(f"  LLM 调用：{llm_calls} 次")
    print(f"  总 token：{total_tokens}")
    print(f"  总耗时：{total_ms}ms")
    print(f"  最终答案：{answer}")
