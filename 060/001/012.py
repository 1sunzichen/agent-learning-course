"""
关卡 1-12 · token 计数与成本优化（填空版）

核心：token 就是钱。会算 token、会算成本、会对比省钱策略。

执行流程图（python3 012.py）：

[贵写法 prompt] ──> 调 LLM ──> 记 usage（token 数）
[省写法 prompt] ──> 调 LLM ──> 记 usage（token 数）
  └─ 对比两次的 token 和成本

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-12 那节）。
  3. 跑通：能看到贵写法 vs 省写法省了多少 token 和多少钱。
"""

import re
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

PRICE_INPUT = 1.0    # 输入 1 元 / 百万 token
PRICE_OUTPUT = 2.0   # 输出 2 元 / 百万 token


def estimate_tokens(text):
    """本地近似估算 token：中文 1 字≈1 token，英文按词估"""
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    # ── 填空 1 ──────────────────────────────
    # 估算总 token：中文按字数算 1 字 1 token，英文按词数 ×1.3 近似
    # 提示：chinese 是中文数量，english_words 是英文词数，英文每词约 1.3 token
    return chinese + int(english_words * 1.3)                   # ← 填空 1


def cost(prompt_tokens, completion_tokens):
    """算一次调用的成本（元）"""
    # ── 填空 2 ──────────────────────────────
    # 成本 = (输入 token × 输入单价 + 输出 token × 输出单价) / 百万
    # 提示：单价单位是「元/百万 token」，所以要除以 1_000_000
    return (prompt_tokens * PRICE_INPUT + completion_tokens * PRICE_OUTPUT) / 1_000_000  # ← 填空 2


EXPENSIVE_SYSTEM = (
    "你是一个由顶尖团队精心打造的高级智能助手，你的职责是全方位、多角度、"
    "事无巨细地解答用户提出的各种问题。请你始终保持专业、礼貌、热情、耐心、"
    "细致、严谨的态度，用最详细、最完整、最全面的方式回答每一个问题，"
    "尽可能地提供更多的背景信息、相关知识、注意事项和补充说明。"
)

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
    # ── 填空 3 ──────────────────────────────
    # 从 usage 里取「输入 token」和「输出 token」返回
    # 提示：usage.prompt_tokens 是输入，usage.completion_tokens 是输出
    return answer, usage.prompt_tokens, usage.completion_tokens   # ← 填空 3


if __name__ == "__main__":
    question = "用一句话解释什么是函数。"

    print("=" * 55)
    print("  token 计数与成本对比")
    print("=" * 55)

    print("\n【贵写法】system 预估 token：", estimate_tokens(EXPENSIVE_SYSTEM))
    ans1, pt1, ct1 = ask(EXPENSIVE_SYSTEM, question)
    c1 = cost(pt1, ct1)
    print(f"  实际：prompt {pt1} tok + completion {ct1} tok = {pt1 + ct1} tok")
    print(f"  成本：¥{c1:.6f}")

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
