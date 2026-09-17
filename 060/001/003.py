"""
关卡 1-5 · 流式输出（stream）

核心：stream=True 时，API 不是一次性返回完整消息，而是返回一个「增量流」（迭代器）。
每个 chunk 里是 delta（增量），要自己累积，才能拼出完整内容。

和普通（非流式）的本质区别：
  非流式：一次 create() 返回完整 msg.content，直接用
  流式：   create(stream=True) 返回迭代器，逐 chunk 返回 delta.content，要自己累积

执行流程图（python3 003.py）：

【开启流式】create(stream=...)              ← 填空 1
【遍历增量】for chunk in stream:
  ├─ delta.content       → 累积普通文本      ← 填空 2
  └─ delta.tool_calls    → 累积工具调用参数（分片） ← 填空 3
【收尾】返回累积的完整内容 + 工具调用

规则：
  1. 下面有 3 个空（共 4 处），填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-5 那节）。
  3. 跑通：能看到文字逐字吐出来，且工具调用的参数正确拼起来。
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
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
    # ── 填空 1 ──────────────────────────────
    # 开启流式：让 create 返回一个「增量迭代器」，而不是一次性完整响应
    # 提示：create 里加一个 stream 参数，设成 True
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        stream=True,   # ← 填空 1
        temperature=0,
    )

    full_content = ""      # 累积普通文本
    tool_calls = []        # 累积工具调用（可能有多个，按 index 区分）

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta

        # ── 填空 2 ──────────────────────────────
        # 累积普通文本：delta.content 是「这一小片」文字，要拼到总内容上
        # 提示：逐片追加；打印时 end="" 不换行、flush=True 立即刷屏，才有"逐字吐"的效果
        if delta.content:
            full_content +=delta.content          # ← 填空 2a：把这一片拼进总内容
            print(delta.content, end="", flush=True)   # ← 填空 2b：实时打印这一片

        # ── 填空 3 ──────────────────────────────
        # 累积工具调用：流式下 arguments 是「分片」传来的，要按 index 拼到同一个槽位
        # 提示：tcd.index 表示这是第几个工具调用；同名调用的分片要拼到同一个 tool_calls[idx]
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
                    tool_calls[idx]["arguments"] += tcd.function.arguments  # ← 填空 3：拼接 arguments 分片

    return full_content, tool_calls


# ── 演示 1：普通流式 ──────────────────────────
print("=== 普通流式 ===")
messages = [{"role": "user", "content": "用三句话介绍你自己"}]
content, calls = stream_chat(messages)
print("\n\n完整内容：", content)

# ── 演示 2：工具调用流式 ──────────────────────
print("\n=== 工具调用流式 ===")
messages = [{"role": "user", "content": "北京天气怎么样？"}]
content, calls = stream_chat(messages, TOOLS)
print("\n完整工具调用：", calls)
