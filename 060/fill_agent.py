"""
关卡 1-2 · Function Calling（填空版）

执行流程图（python3 fill_agent.py）：

顶层脚本
 │
 ├─ 定义 TOOLS（白名单）        ← 填空 1 在这里（description）
 ├─ 定义 TOOL_FUNCS / messages
 │
 └─ for step in range(5):
      │
      ├─ client.chat.completions.create(tools=TOOLS)   ← 调 LLM
      ├─ msg.tool_calls ?
      │    ├─ 否 → 打印最终答案，break
      │    └─ 是 → 遍历 tool_calls
      │          ├─ result = ???            ← 填空 2（分发执行）
      │          └─ messages.append(...)    ← 填空 3（tool_call_id）
      └─ 循环

规则：
  1. 下面有 3 个空（标了「填空 X」），填对了代码才能跑通。
  2. 每个空旁边有提示，先自己想，实在卡住再看 answers.md。
  3. 填完跑 python3 fill_agent.py，跑通 = 过关。
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

# ── 填空 1 ──────────────────────────────────────
# 给 get_weather 写一句「工具描述」，让 LLM 知道什么时候该调用它
# 提示：描述是给 LLM 看的"说明书"，写清楚这个工具干嘛、什么时候用
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气",   # ← 填空 1
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
]


def get_weather(city):
    return f"{city} 今天晴，25 度（模拟）"


TOOL_FUNCS = {"get_weather": get_weather}

messages = [
    {"role": "system", "content": "你是 ReAct agent。需要信息时调用工具，不要自己编造。"},
    {"role": "user", "content": "北京今天天气怎么样？"},
]

for step in range(5):
    resp = client.chat.completions.create(
        model="deepseek-chat", messages=messages, tools=TOOLS, temperature=0)
    msg = resp.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments)
            # ── 填空 2 ──────────────────────────────
            # 按工具名分发执行，拿到结果
            # 提示：TOOL_FUNCS 是个字典，key 是工具名，value 是函数
            result = ________   # ← 填空 2
            # ── 填空 3 ──────────────────────────────
            # 把结果喂回 LLM，要带上 tool_call_id 让它对上号
            # 提示：tc 对象上有个 id 字段
            messages.append({
                "role": "tool",
                "tool_call_id": ________,   # ← 填空 3
                "content": str(result),
            })
    else:
        print("🎯 最终答案:", msg.content)
        break
