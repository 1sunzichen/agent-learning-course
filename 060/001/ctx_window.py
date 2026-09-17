#!/usr/bin/env python3
"""
关卡 1-11 · 上下文窗口管理（完整版）

核心：LLM 一次能看进去的内容有上限（上下文窗口，deepseek-chat 是 64K token）。
对话越聊越长，迟早超窗。超窗的后果：报错 / 丢信息 / 变贵。
管理策略：截断、摘要、滑动窗口、RAG 召回。这关演示「摘要」策略。

执行流程图（python3 ctx_window.py）：

[长对话 messages]（越来越长）
  └─ estimate_tokens(messages) 估算总 token
       ├─ < MAX_TOKENS：直接用，不处理
       └─ ≥ MAX_TOKENS：
            ├─ 把「最旧的若干轮」抽出来（更早的）
            ├─ summarize() 用 LLM 压成一段摘要
            ├─ 用摘要替换那些旧消息（腾出空间）
            └─ 得到压缩后的 messages = system + 摘要 + 最近几条

四种策略（面试会问）：
  截断 truncation  —— 直接砍掉最早的，简单但丢信息
  摘要 summarization —— LLM 把早期对话压成一段，留信息丢细节（本关演示）
  滑动窗口 sliding —— 只保留最近 N 条，中间的全丢
  RAG 召回          —— 历史全存向量库，按需检索回来（最省窗口，但要额外基建）

方法调用关系：
  manage_window() ──> estimate_tokens()（估 token）
       └─ summarize() ──> client.chat.completions.create（LLM 摘要）

面试怎么讲（30 秒）：
  "长对话会撞上下文窗口上限。管理策略有四种：截断、摘要、滑动窗口、RAG 召回，
  工程上常组合用——近期对话用原文（滑动窗口），远期记忆摘要或存向量库按需召回。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

MAX_TOKENS = 4000   # 假设窗口很小，方便演示超窗
KEEP_RECENT = 6     # 最近几条保留原文，更早的摘要掉


def estimate_tokens(messages):
    """粗估 token：中文 1 字≈1 token，这里直接用字符数近似（生产用 tiktoken 更准）"""
    total = 0
    for m in messages:
        total += len(m["content"]) + 4   # +4 是每条消息的固定开销（角色标记等）
    return total


def summarize(old_messages):
    """用 LLM 把早期对话压成一段摘要"""
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in old_messages)
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "把下面的对话摘要成一段话，保留所有关键信息（人名、结论、决定），去掉寒暄和重复。"},
            {"role": "user", "content": transcript},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content


def manage_window(messages):
    """超窗时：把最旧的对话摘要掉，保留 system + 摘要 + 最近几条"""
    before = estimate_tokens(messages)
    if before <= MAX_TOKENS:
        return messages, before, before   # 没超窗，不动

    # 找出 system（如果有）和要处理的其他消息
    head = [m for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]

    # 最近 KEEP_RECENT 条保留原文，更早的摘要掉
    keep = rest[-KEEP_RECENT:]
    old = rest[:-KEEP_RECENT]

    summary = summarize(old)
    new_messages = head + [{"role": "user", "content": f"[之前对话摘要] {summary}"}] + keep
    after = estimate_tokens(new_messages)
    return new_messages, before, after


if __name__ == "__main__":
    # 造一段「超长」对话历史，模拟聊了很久
    messages = [{"role": "system", "content": "你是一个助手。"}]
    for i in range(30):
        messages.append({"role": "user", "content": f"第{i+1}个问题：请详细讲讲这个概念的历史背景、原理、应用场景和注意事项，越详细越好。"})
        messages.append({"role": "assistant", "content": f"第{i+1}个回答：这是一个很长的回答，包含了很多细节、例子、推导过程和总结，字数很多很多很多……"})

    before = estimate_tokens(messages)
    print("=" * 55)
    print("  上下文窗口管理演示")
    print("=" * 55)
    print(f"  原始对话：{len(messages)} 条消息，估算 {before} token")
    print(f"  窗口上限：{MAX_TOKENS} token")
    print(f"  {'⚠️ 超窗了！需要压缩' if before > MAX_TOKENS else '✅ 没超窗'}")

    new_messages, b, a = manage_window(messages)
    print(f"\n  压缩后：{len(new_messages)} 条消息，估算 {a} token")
    print(f"  省下 {before - a} token（{(before - a) / before * 100:.0f}%）")
    print("\n  压缩后的消息结构：")
    for m in new_messages:
        content = m["content"]
        print(f"    [{m['role']}] {content[:50]}{'...' if len(content) > 50 else ''}")
