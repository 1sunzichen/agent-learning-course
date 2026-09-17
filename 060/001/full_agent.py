#!/usr/bin/env python3
"""
关卡 1-10 · 综合单 Agent（完整版）

核心：把前面 9 关串成一个「生产级单 agent」：
  1-2 工具调用    —— 多工具白名单（get_weather + calc）
  1-4 短期记忆    —— 多轮 messages 累积
  1-8 四层防护    —— 重试/超时/幂等/降级（call_weather）
  1-9 tracing     —— 每步留痕 + 耗时 + token

执行流程图（python3 full_agent.py）：

用户提问 → 进入对话循环
  for step in 循环：
    ① 调 LLM（带工具定义 + 记 trace）
    ② 有工具调用？
        ├─ 从 TOOL_FUNCS 取出「包了四层防护」的工具执行
        └─ 结果喂回 messages，继续
    ③ 无工具调用 → 输出最终答案，回到「等你提问」
  （多轮：短期记忆 messages 一直累积，下一轮还记得上一轮）

方法调用关系：
  run_agent() ──> client.chat.completions.create（LLM）
       ├─ call_weather()（四层防护：重试/超时/幂等/降级）
       ├─ calc()（计算器）
       └─ record()（tracing）

面试怎么讲（30 秒）：
  "一个生产级单 agent = 工具调用 + 记忆 + 防护 + 可观测。我手写过：多工具白名单、
  多轮短期记忆、工具四层防护、每步 tracing。这是 multi-agent 里每个 worker 的地基。"
"""

import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# ===== 工具 1：天气（四层防护，来自 1-8）=====
def get_weather_raw(city):
    r = random.random()
    if r < 0.7:
        return f"{city} 晴，25度"
    elif r < 0.9:
        raise ConnectionError("网络抖动")
    else:
        time.sleep(3)
        return f"{city} 多云"

_executor = ThreadPoolExecutor(max_workers=4)
_cache = {}

def call_weather(city, max_retry=2, timeout=1.5):
    # 幂等：缓存命中直接返回
    if city in _cache:
        return _cache[city] + "（缓存）"
    # 重试 + 超时
    for attempt in range(1, max_retry + 1):
        fut = _executor.submit(get_weather_raw, city)
        try:
            result = fut.result(timeout=timeout)
            _cache[city] = result
            return result
        except TimeoutError:
            print(f"    [weather] 第{attempt}次超时，重试...")
        except Exception as e:
            print(f"    [weather] 第{attempt}次失败({e})，重试...")
        time.sleep(0.3 * attempt)
    # 降级
    return f"{city} 天气服务不可用，降级返回默认值"

# ===== 工具 2：计算器 =====
def calc(expr):
    try:
        allowed = set("0123456789+-*/(). ")
        if any(c not in allowed for c in expr):
            return "表达式含非法字符"
        return str(eval(expr))
    except Exception as e:
        return f"计算失败：{e}"

TOOL_FUNCS = {"get_weather": call_weather, "calc": calc}

TOOLS = [
    {"type": "function", "function": {"name": "get_weather", "description": "查城市天气", "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "城市名"}}, "required": ["city"]}}},
    {"type": "function", "function": {"name": "calc", "description": "算数学表达式", "parameters": {"type": "object", "properties": {"expr": {"type": "string", "description": "如 3*(5+2)"}}, "required": ["expr"]}}},
]

SYSTEM = "你是一个助手。查天气用 get_weather，算数用 calc。回答用中文。"

# ===== tracing（来自 1-9）=====
trace = []

def record(kind, content, tokens=None, t0=None):
    entry = {"step": len(trace) + 1, "kind": kind, "content": content}
    if tokens is not None:
        entry["tokens"] = tokens
    if t0 is not None:
        entry["ms"] = round((time.time() - t0) * 1000)
    trace.append(entry)
    tail = ""
    if tokens is not None:
        tail += f"  [{tokens} tok]"
    if t0 is not None:
        tail += f"  ({entry['ms']}ms)"
    print(f"  [trace #{entry['step']}] {kind}: {content}{tail}")


def run_agent(question, messages):
    messages.append({"role": "user", "content": question})
    for step in range(8):
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
    messages = [{"role": "system", "content": SYSTEM}]   # 短期记忆：跨轮累积
    print("=" * 55)
    print("  综合单 Agent：多工具 + 防护 + tracing（输入 quit 退出）")
    print("=" * 55)
    print('试试："北京天气怎么样？"   "3*(5+2)等于多少？"\n')
    while True:
        try:
            user = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break
        if not user:
            continue
        if user.lower() == "quit":
            print("👋 再见！")
            break
        answer = run_agent(user, messages)
        print(f"\nAI: {answer}\n")
