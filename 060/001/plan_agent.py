#!/usr/bin/env python3
"""
关卡 1-6 · Plan-and-Execute（完整版）

核心：把「规划」和「执行」拆成两个阶段。
  1. Planner：让 LLM 先一次性输出完整计划（步骤列表，结构化 JSON）
  2. Executor：按顺序逐步执行，每步该调工具就调工具，结果累积进上下文

执行流程图（python3 plan_agent.py）：

【规划】planner(任务) ──> LLM 输出 JSON 计划 {"steps":[{step,desc,tool,args},...]}
【执行】for step in plan["steps"]:
   ├─ 有 tool  → 调真实函数 get_weather(...)
   └─ 无 tool  → LLM 根据「已完成结果」写该步内容
【汇总】把所有步骤结果拼成最终答案

和 ReAct（1-4/1-5）的本质区别：
  ReAct：想一步 → 做一步 → 看结果 → 再想下一步（思考/行动每步交错、每步重新决策）
  Plan-and-Execute：先想好全部步骤 → 再机械推进执行（规划一次、执行分离）

方法调用关系：
  planner() ──> client.chat.completions.create（输出 JSON 计划）
  executor() ──> for 循环遍历 steps
       ├─ TOOL_FUNCS[name](**args)  → 工具步骤
       └─ client.chat.completions.create  → 无工具步骤

面试怎么讲（30 秒）：
  "ReAct 每步都重新推理下一步，灵活但慢、token 多；Plan-and-Execute 先出完整计划再执行，
  适合步骤多、目标明确的任务，省 token、方便看到全局，但计划一旦定下就不易中途调整。"
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)


def get_weather(city):
    """查询天气（模拟）"""
    return f"{city} 晴，25 度"


TOOL_FUNCS = {"get_weather": get_weather}

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

# 让 LLM 明确输出「计划」的格式约束（这是 Plan-and-Execute 区别于 ReAct 的关键）
PLAN_SYSTEM = """你是一个任务规划器。给定任务，先拆解成有序步骤，输出 JSON 计划。

输出格式（严格 JSON，不要多余文字）：
{"steps": [
  {"step": 1, "desc": "这一步要做什么", "tool": "get_weather", "args": {"city": "北京"}},
  {"step": 2, "desc": "这一步要做什么", "tool": null, "args": null}
]}

规则：
- tool 只能是 "get_weather" 或 null（null 表示这步靠 LLM 自己写，不调工具）
- 步骤按依赖顺序排列
- 步骤数 2~4 步，不要过多
"""


def planner(task):
    """阶段 1：让 LLM 一次性输出完整计划"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": PLAN_SYSTEM},
            {"role": "user", "content": f"任务：{task}\n请给出计划："},
        ],
        temperature=0,
    )
    raw = resp.choices[0].message.content
    # 去掉可能包裹的 ```json ... ``` 标记，再解析成 dict
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    plan = json.loads(raw)
    return plan


def executor(task, plan):
    """阶段 2：按顺序执行每个步骤"""
    results = []
    for s in plan["steps"]:
        if s.get("tool"):
            # 步骤要求调工具 → 调真实函数
            fn = TOOL_FUNCS[s["tool"]]
            result = fn(**s["args"])
            results.append(f"步骤{s['step']}（{s['desc']}）→ {result}")
        else:
            # 步骤不调工具 → 让 LLM 基于「已完成的结果」写这一步的内容
            ctx = "\n".join(results)
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你负责执行计划的单个步骤，输出该步骤的产出。用中文，简洁。"},
                    {"role": "user", "content": f"任务：{task}\n已完成：\n{ctx}\n\n当前步骤：{s['desc']}"},
                ],
                temperature=0,
            )
            results.append(f"步骤{s['step']}（{s['desc']}）→ {resp.choices[0].message.content}")
    return results


if __name__ == "__main__":
    task = "帮我查一下北京今天的天气，再写一句适合发朋友圈的短文案"

    print("=" * 50)
    print("  阶段 1 · Planner：先生成完整计划")
    print("=" * 50)
    plan = planner(task)
    print("计划：")
    for s in plan["steps"]:
        tool = s.get("tool") or "无(LLM 写)"
        print(f"  步骤{s['step']}: {s['desc']}  [tool={tool}]")

    print("\n" + "=" * 50)
    print("  阶段 2 · Executor：逐步执行")
    print("=" * 50)
    results = executor(task, plan)
    for r in results:
        print("  " + r)

    print("\n" + "=" * 50)
    print("  最终结果")
    print("=" * 50)
    for r in results:
        print("  " + r)
