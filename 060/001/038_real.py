#!/usr/bin/env python3
"""
038_real.py · 真实版 LangChain 工具调用 Agent（langchain 1.x 新 API）

⚠️ 版本差异（重要）：
  课程 038.py 用旧 API —— create_tool_calling_agent + AgentExecutor，
  这个接口在 langchain 1.0 里被删除了。今天 pip install langchain 装到的是 1.x。
  本文件用 1.x 的新 API —— create_agent（一行搞定，连 prompt/scratchpad 都不用手写）。
  想跑课程原版 038.py，需要锁旧版：pip install "langchain<1.0" langchain-openai<1.0

和 038.py 的三处「模拟 → 真实」：
  1. get_weather 真调 Open-Meteo 免费天气 API（无需 key）
  2. calc 用 ast 安全求值替代危险的 eval
  3. llm 真调 DeepSeek —— 需要你自己的 key

跑法：
  source .venv/bin/activate   # 或 .venv/bin/python 038_real.py
  python3 038_real.py         # 只改 api_key 一处
"""

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent   # 1.x 新 API：替代 create_tool_calling_agent

import ast
import operator
import urllib.request
import urllib.parse
import json


# ── LLM：连 DeepSeek（OpenAI 兼容接口）──────────────────────────────
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],          # ← 只改这一处
    base_url="https://api.deepseek.com",
    temperature=0,
)


# ── 工具 1：get_weather —— 真实调 Open-Meteo API（免费、无需 key）──
@tool
def get_weather(city: str) -> str:
    """查询某个城市的实时天气。参数 city 是中文城市名，如「北京」。"""
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
        {"name": city, "count": 1, "language": "zh", "format": "json"}
    )
    with urllib.request.urlopen(geo_url, timeout=10) as r:
        geo = json.load(r)
    if not geo.get("results"):
        return f"没找到城市「{city}」"
    loc = geo["results"][0]

    w_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode(
        {
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "current": "temperature_2m,weather_code",
        }
    )
    with urllib.request.urlopen(w_url, timeout=10) as r:
        w = json.load(r)
    cur = w["current"]

    codes = {0: "晴", 1: "多云", 2: "阴", 3: "阴", 45: "雾",
             61: "小雨", 63: "中雨", 65: "大雨", 71: "小雪", 95: "雷雨"}
    desc = codes.get(cur["weather_code"], f"天气码{cur['weather_code']}")
    return f"{loc['name']} 当前{desc}，气温 {cur['temperature_2m']}°C"


# ── 工具 2：calc —— ast 安全求值（替代 Python 的 eval）─────────────
_ALLOWED = {ast.Expression, ast.BinOp, ast.UnaryOp, ast.Add, ast.Sub,
            ast.Mult, ast.Div, ast.USub, ast.UAdd, ast.Constant}
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def _safe_eval(node):
    if type(node) not in _ALLOWED:
        raise ValueError(f"不允许的节点 {type(node).__name__}")
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("不支持的表达式")


@tool
def calc(expr: str) -> str:
    """计算数学表达式，如 3*(5+2)。支持 + - * / 和括号。"""
    try:
        return str(_safe_eval(ast.parse(expr, mode="eval")))
    except Exception as e:
        return f"表达式错误：{e}"


# ── 组装 agent：1.x 一行搞定，system_prompt 直接传字符串 ───────────
agent = create_agent(
    model=llm,
    tools=[get_weather, calc],
    system_prompt="你是一个助手。查天气用 get_weather，算数用 calc。回答用中文。",
)


if __name__ == "__main__":
    print("=" * 55)
    print("  真实版 LangChain 工具调用 Agent（langchain 1.x + 真 API）")
    print("=" * 55)
    result = agent.invoke({
        "messages": [{"role": "user",
                      "content": "北京天气怎么样？顺便算一下 3*(5+2) 等于多少"}],
    })
    # 最终答案在最后一条消息里
    final = result["messages"][-1].content
    print("\n🎯 最终答案:", final)
