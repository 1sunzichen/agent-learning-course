"""
关卡 1-10 · 综合单 Agent（填空版）

核心：把前面 9 关串成一个「生产级单 agent」。
这关的填空不考单个技巧，考「消息流闭环」——这是综合 agent 的骨架：
  短期记忆 = messages 列表，每轮都要正确地把用户输入、工具结果、最终答案「喂回」列表，
  漏任何一环，下一轮就「失忆」。

执行流程图（python3 010.py）：

用户提问 → run_agent(question, messages)
  ① 把用户输入加进 messages                    ← 填空 1
  ② 调 LLM（带工具 + 记 trace）
  ③ 有工具调用？结果喂回 messages              ← 填空 2
  ④ 无工具调用 → 最终答案加回 messages          ← 填空 3，然后返回

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-10 那节）。
  3. 跑通：能连续问两轮（先天气再算数），第二轮还记得第一轮聊过什么。
"""

import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
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
    if city in _cache:
        return _cache[city] + "（缓存）"
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
    return f"{city} 天气服务不可用，降级返回默认值"

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
    # ── 填空 1 ──────────────────────────────
    # 短期记忆：把用户这一轮的输入加进 messages 列表（多轮记忆的关键）
    # 提示：append 一条 user 角色的消息
    messages.append({"role": "user", "content": question})       # ← 填空 1
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
                # ── 填空 2 ──────────────────────────────
                # 把工具执行结果喂回 messages（tool 角色，带 tool_call_id）
                # 提示：role 是 "tool"，要带 tool_call_id=tc.id 和 content=str(result)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})  # ← 填空 2
        else:
            record("final", msg.content)
            # ── 填空 3 ──────────────────────────────
            # 把最终答案也加回 messages（assistant 角色），下一轮才记得自己说过啥
            # 提示：append 一条 assistant 角色的消息
            messages.append({"role": "assistant", "content": msg.content})   # ← 填空 3
            return msg.content
    return "（达到最大步数仍未结束）"


if __name__ == "__main__":
    messages = [{"role": "system", "content": SYSTEM}]
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
