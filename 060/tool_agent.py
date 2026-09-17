#!/usr/bin/env python3
"""
关卡 1-2 · 接工具 Function Calling
把 ReAct 的 Action 从「写任意代码」升级成「调用预定义工具」。

和关卡 1-1 的本质区别：
  1-1（代码执行）：LLM 写任意 Python 代码 → 你 subprocess 跑（灵活但危险、要解析文本）
  1-2（工具调用）：LLM 从工具白名单里选一个，结构化输出「调哪个 + 参数」→ 你按名字分发执行（安全、可控、生产级）

依赖: pip3 install openai
运行: python3 tool_agent.py

执行流程图（python3 tool_agent.py）：

顶层脚本
 │
 ├─ 定义 TOOLS（白名单 schema：calculator / get_weather / search）
 ├─ 定义 TOOL_FUNCS（工具实现函数）
 ├─ 初始化 messages = [system, user]
 │
 └─ for step in range(10):                    ← 主循环
      │
      ├─ client.chat.completions.create(messages, tools=TOOLS)  ← ① 调 LLM（带工具白名单）
      │     └─ msg = LLM 的回复（可能含 tool_calls）
      │
      ├─ msg.tool_calls 存在 ?
      │     ├─ 否 → 打印最终答案 → break（结束）
      │     └─ 是 ↓
      │
      ├─ 遍历 tool_calls：
      │     ├─ name = tc.function.name              ← LLM 要调的工具名
      │     ├─ args = json.loads(tc.function.arguments)  ← 结构化参数
      │     ├─ TOOL_FUNCS[name](**args)              ← ② 按名字分发执行
      │     └─ messages.append(role="tool", ...)     ← ③ 结果喂回
      │
      └─ 循环

方法调用关系：
  顶层脚本 ──> client.chat.completions.create()   （调 LLM，带 tools 白名单）
  顶层脚本 ──> TOOL_FUNCS[name]()                 （按工具名分发执行）
"""

import json
import re
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# ── 工具白名单（关键：LLM 只能调这些，不能写任意代码）──
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，返回数值结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "如 37*53"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "搜索互联网信息，返回相关文本",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"],
            },
        },
    },
]

# ── 工具的真实实现（LLM 不执行，执行的是这里）────────
def calculator(expression):
    if not re.fullmatch(r"[\d+\-*/().%\s]+", expression):
        return "表达式含非法字符"
    return eval(expression)   # 练习用 eval；生产环境用安全解析器


def get_weather(city):
    return f"{city} 今天晴，25 度（模拟数据）"


def search(query):
    return f"关于「{query}」的搜索结果（模拟）：这是一段模拟的检索结果。"


TOOL_FUNCS = {"calculator": calculator, "get_weather": get_weather, "search": search}

SYSTEM = "你是 ReAct agent。需要信息时调用工具，不要自己编造答案。"

messages = [
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": "北京今天天气怎么样？顺便帮我算一下 37×53，再查一下 AI Agent 是什么。"},
]

for step in range(10):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS,        # ← 把工具白名单交给 LLM
        temperature=0,
    )
    msg = resp.choices[0].message

    if msg.tool_calls:
        # LLM 决定调用工具：结构化输出了「工具名 + 参数」
        messages.append(msg)   # 把 assistant 消息（含 tool_calls）原样加回
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            print(f"🔧 调用工具: {name}({args})")
            result = TOOL_FUNCS[name](**args)   # 程序按名字分发执行
            print(f"   结果: {result}\n")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            })
    else:
        print("🎯 最终答案:", msg.content)
        break
