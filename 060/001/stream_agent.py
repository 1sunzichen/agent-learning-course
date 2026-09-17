#!/usr/bin/env python3
"""
关卡 1-5 · 流式输出（完整版）

核心：stream=True 时，API 返回「增量流」，逐 chunk 返回 delta，要自己累积才能拼出完整内容。

执行流程图（python3 stream_agent.py）：

【开启流式】create(stream=True)  → 返回迭代器（不是一次性完整响应）
【遍历增量】for chunk in stream:
  ├─ delta.content       → 累积普通文本（逐片拼接 + 实时打印）
  └─ delta.tool_calls    → 累积工具调用（arguments 分片按 index 拼接）
【收尾】返回累积的完整内容 + 工具调用列表

和 1-4（非流式）的本质区别：
  非流式：create() 一次返回完整 msg.content，直接读
  流式：   create(stream=True) 返回迭代器，逐 chunk 读 delta，自己累积

方法调用关系：
  stream_chat() ──> client.chat.completions.create(stream=True)
       ├─ delta.content  → 累进 full_content + print 逐字
       └─ delta.tool_calls → 按 index 累积到 tool_calls[]
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)


def get_weather(city):
    return f"{city} 晴，25度"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某城市的天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "城市名"}},
                "required": ["city"],
            },
        },
    },
]


def stream_chat(messages, tools=None):
    # ① 开启流式：stream=True 让 create 返回「增量迭代器」
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        stream=True,          # ← 关键：开启流式
        temperature=0,
    )

    full_content = ""          # 累积普通文本
    tool_calls = []            # 累积工具调用（按 index 区分多个调用）

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta

        # ② 累积普通文本：delta.content 是「这一小片」，逐片拼起来 + 实时打印
        if delta.content:
            full_content += delta.content
            print(delta.content, end="", flush=True)   # end=""不换行 flush=True立即刷屏

        # ③ 累积工具调用：arguments 是「分片」，按 index 拼到同一个槽位
        if delta.tool_calls:
            for tcd in delta.tool_calls:
                idx = tcd.index
                while len(tool_calls) <= idx:
                    tool_calls.append({"id": "", "name": "", "arguments": ""})
                if tcd.id:
                    tool_calls[idx]["id"] = tcd.id
                if tcd.function and tcd.function.name:
                    tool_calls[idx]["name"] = tcd.function.name
                if tcd.function and tcd.function.arguments:
                    tool_calls[idx]["arguments"] += tcd.function.arguments   # 分片拼接

    return full_content, tool_calls


# ── 演示 1：普通流式 ──
print("=== 普通流式 ===")
content, calls = stream_chat([{"role": "user", "content": "用三句话介绍你自己"}])
print("\n\n完整内容：", content)

# ── 演示 2：工具调用流式 ──
print("\n=== 工具调用流式 ===")
content, calls = stream_chat([{"role": "user", "content": "北京天气怎么样？"}], TOOLS)
print("\n完整工具调用：", calls)
