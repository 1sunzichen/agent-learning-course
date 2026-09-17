"""
关卡 1-6 · Plan-and-Execute（填空版）

核心：把「规划」和「执行」拆成两个阶段。
  1. Planner：让 LLM 先一次性输出完整计划（步骤列表，结构化 JSON）
  2. Executor：按顺序逐步执行，每步该调工具就调工具，结果累积进上下文

执行流程图（python3 005.py）：

【规划】planner(任务) ──> LLM 输出 JSON 计划 {"steps":[{step,desc,tool,args},...]}
【执行】for step in plan["steps"]:
   ├─ 有 tool  → 调真实函数 get_weather(...)      ← 填空 2
   └─ 无 tool  → LLM 根据「已完成结果」写该步内容   ← 填空 3
【汇总】把所有步骤结果拼成最终答案

和 ReAct（1-4/1-5）的本质区别：
  ReAct：想一步 → 做一步 → 看结果 → 再想下一步（思考/行动每步交错）
  Plan-and-Execute：先想好全部步骤 → 再机械推进执行（规划一次、执行分离）

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-6 那节）。
  3. 跑通：先打印出完整计划，再按顺序执行每步，最后拼出最终答案。
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
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
    # 去掉可能包裹的 ```json ... ``` 标记
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    # ── 填空 1 ──────────────────────────────
    # LLM 返回的计划是「字符串」，要解析成 dict，后面的 for 循环才能遍历 steps
    # 提示：用 json 模块把 raw 转成 dict
    plan = json.loads(raw)   # ← 填空 1
    return plan


def executor(task, plan):
    """阶段 2：按顺序执行每个步骤"""
    results = []
    for s in plan["steps"]:
        if s.get("tool"):
            # 步骤要求调工具 → 调真实函数
            # ── 填空 2 ──────────────────────────────
            # 用步骤里带的函数名和参数，调真实的 Python 函数
            # 提示：从 TOOL_FUNCS 取出函数，再用 s["args"] 里的参数调用（** 展开）
            fn = TOOL_FUNCS[s["tool"]]
            result = fn(**s["args"])   # ← 填空 2
            results.append(f"步骤{s['step']}（{s['desc']}）→ {result}")
        else:
            # 步骤不调工具 → 让 LLM 基于「已完成的结果」写这一步的内容
            ctx = "\n".join(results)
            # ── 填空 3 ──────────────────────────────
            # 无工具步骤要让 LLM 写内容，必须把「任务 + 已完成结果 + 当前步骤」都喂进去，
            # 否则它不知道前面做了啥，写出来的内容会断档
            # 提示：user 消息里拼上 task、ctx、当前步骤 desc
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你负责执行计划的单个步骤，输出该步骤的产出。用中文，简洁。"},
                    {"role": "user", "content": f"任务：{task}\n已完成：\n{ctx}\n\n当前步骤：{s['desc']}"},   # ← 填空 3
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
