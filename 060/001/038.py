#!/usr/bin/env python3
"""
关卡 3-1 · LangChain 重写（填空版）

核心：把 1-10 的综合单 Agent（full_agent.py，约 160 行手写：工具 schema dict + 函数分发 dict
+ 重试/超时/幂等/降级 + tracing + 手写 while 循环）用 LangChain 重写，看代码量缩到多少、
少了哪些样板。

执行流程图（python3 038.py）：

用户问题
  └─ agent_executor.invoke({"input": 问题})
       └─ LangChain 内置 ReAct 循环（不用你手写 while）：
            ├─ 带工具的 LLM 决定要不要调工具
            ├─ 要 → 执行 @tool 装饰的函数 → 结果自动喂回
            └─ 不要 → 返回最终答案

LangChain 帮你省掉的样板：
  1. TOOLS 的 JSON schema 声明  → @tool 装饰器自动从函数签名 + docstring 生成
  2. TOOL_FUNCS 字典 + 按名分发 → 框架自动绑定
  3. 手写 while 循环 / 消息组装 → AgentExecutor 内置
LangChain 不替你写的（还得自己补）：
  重试/超时/幂等/降级、tracing、防护 —— 这些「生产细节」框架不管。

依赖（先装，装不上先看代码理解概念）：
  pip3 install langchain langchain-openai

规则：
  1. 下面有 3 个空（填空 1 含 a/b 两处），填对了才能跑通。
  2. 卡住看 answers-038-042.md（关卡 3-1 那节）。
  3. 跑通：打印出「🎯 最终答案:」那一行。
"""

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor


# ── 填空 1 ──────────────────────────────────────
# 创建连 DeepSeek 的 ChatOpenAI。DeepSeek 是 OpenAI 兼容接口，所以用 ChatOpenAI 也能连。
# 提示：base_url 填 DeepSeek 的 OpenAI 兼容地址，model 填 deepseek-chat
llm = ChatOpenAI(
    model="________",                    # ← 填空 1a：模型名
    api_key="sk-你的key",                # ← 换成你自己的 key
    base_url="________",                 # ← 填空 1b：DeepSeek 的 OpenAI 兼容地址
    temperature=0,
)


# 工具：用 @tool 装饰器，schema（name/description/参数）自动从函数签名和 docstring 生成
@tool
def get_weather(city: str) -> str:
    """查询某个城市的天气。"""
    return f"{city} 今天晴，25 度（模拟）"


@tool
def calc(expr: str) -> str:
    """计算数学表达式，如 3*(5+2)。"""
    allowed = set("0123456789+-*/(). ")
    if any(c not in allowed for c in expr):
        return "表达式含非法字符"
    return str(eval(expr))


# ── 填空 2 ──────────────────────────────────────
# 拼 prompt：system 给角色，两个 MessagesPlaceholder 放「对话历史」和「中间工具往返记录」。
# 提示：tool-calling agent 必须有一个 agent_scratchpad 占位，框架往里塞「工具调用→结果」的往返
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手。查天气用 get_weather，算数用 calc。回答用中文。"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("________"),      # ← 填空 2：中间工具往返记录的占位名
])


# ── 填空 3 ──────────────────────────────────────
# 组装 agent：把「带工具的 LLM + prompt」变成工具调用 agent，再包一层执行器
# 提示：create_tool_calling_agent 三个参数是 (llm, tools, prompt)，tools 是 [get_weather, calc]
agent = create_tool_calling_agent(
    ________,        # ← 填空 3a：LLM
    ________,        # ← 填空 3b：工具列表
    ________,        # ← 填空 3c：prompt
)
agent_executor = AgentExecutor(agent=agent, tools=[get_weather, calc], verbose=True)


if __name__ == "__main__":
    print("=" * 55)
    print("  LangChain 重写 1-10 综合 Agent（对比代码量）")
    print("=" * 55)
    # 和 1-10 一样的问题，看 LangChain 版多简洁
    result = agent_executor.invoke({
        "input": "北京天气怎么样？顺便算一下 3*(5+2) 等于多少",
        "chat_history": [],
    })
    print("\n🎯 最终答案:", result["output"])
