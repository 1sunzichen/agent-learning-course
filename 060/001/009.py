"""
关卡 1-9 · 可观测性 tracing（填空版）

核心：agent 是个黑盒。tracing 给 agent 装摄像头，记录每一步：
  1. 每一步「类型 + 内容」（thought/action/observation/final）
  2. 每一步「耗时」（定位慢在哪）
  3. 每一次 LLM 调用「花了多少 token」（定位贵在哪）

执行流程图（python3 009.py）：

用户提问
  └─ for step in 循环：
       ├─ 调 LLM（计时 + 记 token）→ record("llm_call", ...)   ← 填空 2
       ├─ 有工具调用？ → record("action", ...) + 执行 + record("observation", ...)
       └─ 无工具调用 → record("final", ...) 结束
  └─ record() 里算耗时                                          ← 填空 1

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-9 那节）。
  3. 跑通：能看到每一步的 trace，以及最后的总耗时 / 总 token 汇总。
"""

import time
import json
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

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
        # ── 填空 1 ──────────────────────────────
        # 算这条 trace 的耗时（毫秒）：用当前时间减开始时间 t0
        # 提示：time.time() 拿当前时间，减 t0 得秒数，*1000 转毫秒，round 取整
        entry["ms"] = round((time.time() - t0) * 1000)          # ← 填空 1
    trace.append(entry)
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
        # ── 填空 2 ──────────────────────────────
        # 记录这次 LLM 调用：要带上 token 数（usage.total_tokens）和开始时间 t0
        # 提示：record(kind, content, tokens=..., t0=...)，token 为 None 时防御处理
        record("llm_call", f"第{step+1}次调用 LLM",
               tokens=usage.total_tokens if usage else None, t0=t0)   # ← 填空 2
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                # ── 填空 3 ──────────────────────────────
                # 记录「调用了哪个工具、什么参数」
                # 提示：用 record，kind 是 "action"，内容把工具名和参数拼起来
                record("action", f"{name}({args})")                 # ← 填空 3
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
