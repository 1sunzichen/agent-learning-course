#!/usr/bin/env python3
"""
关卡 1-12 · token 计数与成本优化（完整版）

核心：token 就是钱。要会两件事：
  1. 算一次调用花了多少 token（精确值看 usage.total_tokens，本地估算用近似函数）
  2. 算花了多少钱（token × 单价）

执行流程图（python3 token_cost.py）：

[贵写法 prompt] ──> 调 LLM ──> 记 usage（token 数）
[省写法 prompt] ──> 调 LLM ──> 记 usage（token 数）
  └─ 对比两次的 token 和成本，看省了多少

省钱策略（面试会问）：
  ① 压缩 prompt     —— 去掉冗余 system 指令
  ② 少用工具定义    —— 不用的工具别塞 TOOLS
  ③ 结果缓存        —— 相同问题返回缓存（1-15 展开）
  ④ 摘要            —— 长对话压成摘要（1-11 已讲）
  ⑤ 选便宜模型      —— 简单任务用便宜模型

方法调用关系：
  estimate_tokens() ──> 本地近似估算（字符数）
  cost() ──> prompt_tokens*单价 + completion_tokens*单价
  ask() ──> client.chat.completions.create（拿 usage）

面试怎么讲（30 秒）：
  "优化成本先得会算 token。精确值用 API 返回的 usage，本地估算用 tiktoken（GPT）
  或近似函数。成本 = token × 单价，省钱靠压 prompt、减工具定义、缓存、摘要、选便宜模型。"
"""

import re
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# deepseek-chat 单价（元/百万 token）。价格会变，这里演示计算逻辑，实际以官网为准
PRICE_INPUT = 1.0    # 输入 1 元 / 百万 token
PRICE_OUTPUT = 2.0   # 输出 2 元 / 百万 token


def estimate_tokens(text):
    """本地近似估算 token：中文 1 字≈1 token，英文按词估。
    GPT 可用 tiktoken 精确算；deepseek 未公开 tokenizer，这里用近似。"""
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return chinese + int(english_words * 1.3)


def cost(prompt_tokens, completion_tokens):
    """算一次调用的成本（元）"""
    return (prompt_tokens * PRICE_INPUT + completion_tokens * PRICE_OUTPUT) / 1_000_000


# 贵写法：system 又长又啰嗦
EXPENSIVE_SYSTEM = (
    "你是一个由顶尖团队精心打造的高级智能助手，你的职责是全方位、多角度、"
    "事无巨细地解答用户提出的各种问题。请你始终保持专业、礼貌、热情、耐心、"
    "细致、严谨的态度，用最详细、最完整、最全面的方式回答每一个问题，"
    "尽可能地提供更多的背景信息、相关知识、注意事项和补充说明。"
)

# 省写法：一句话说清
CHEAP_SYSTEM = "你是一个助手，简洁回答用户问题。"


def ask(system, question):
    """调一次 LLM，返回 (答案, prompt_tokens, completion_tokens)"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": question}],
        temperature=0,
    )
    usage = resp.usage
    answer = resp.choices[0].message.content
    return answer, usage.prompt_tokens, usage.completion_tokens


if __name__ == "__main__":
    question = "用一句话解释什么是函数。"

    print("=" * 55)
    print("  token 计数与成本对比")
    print("=" * 55)

    # 贵写法
    print("\n【贵写法】system 预估 token：", estimate_tokens(EXPENSIVE_SYSTEM))
    ans1, pt1, ct1 = ask(EXPENSIVE_SYSTEM, question)
    c1 = cost(pt1, ct1)
    print(f"  实际：prompt {pt1} tok + completion {ct1} tok = {pt1 + ct1} tok")
    print(f"  成本：¥{c1:.6f}")

    # 省写法
    print("\n【省写法】system 预估 token：", estimate_tokens(CHEAP_SYSTEM))
    ans2, pt2, ct2 = ask(CHEAP_SYSTEM, question)
    c2 = cost(pt2, ct2)
    print(f"  实际：prompt {pt2} tok + completion {ct2} tok = {pt2 + ct2} tok")
    print(f"  成本：¥{c2:.6f}")

    print("\n" + "=" * 55)
    print(f"  省下 token：{(pt1 + ct1) - (pt2 + ct2)}")
    print(f"  省下成本：¥{c1 - c2:.6f}")
    print(f"  省了 {(c1 - c2) / c1 * 100:.0f}% 的钱")
    print("=" * 55)
