"""
关卡 1-11 · 上下文窗口管理（填空版）

核心：LLM 一次能看进去的内容有上限（上下文窗口）。对话太长会超窗。
这关演示「摘要」策略：估算 token → 切分（最近保留原文 / 更早摘要）→ 用摘要替换。

执行流程图（python3 011.py）：

[长对话 messages]
  └─ estimate_tokens() 估算总 token                       ← 填空 1
       ├─ < 上限：不动
       └─ ≥ 上限：
            ├─ 切出「最近 KEEP_RECENT 条」和「更早的」     ← 填空 2
            ├─ summarize() 用 LLM 把更早的压成摘要
            └─ 拼成 new_messages = system + 摘要 + 最近     ← 填空 3

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-11 那节）。
  3. 跑通：能看到超窗 → 摘要压缩 → 省下大量 token。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

MAX_TOKENS = 4000
KEEP_RECENT = 6


def estimate_tokens(messages):
    """粗估 token：中文 1 字≈1 token，用字符数近似（生产用 tiktoken 更准）"""
    total = 0
    for m in messages:
        # ── 填空 1 ──────────────────────────────
        # 累加每条消息的估算 token：内容长度 + 固定开销
        # 提示：len(m["content"]) 拿字符数，每条消息加个固定开销（如 4）
        total += len(m["content"]) + 4                       # ← 填空 1
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
        return messages, before, before

    head = [m for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]

    # ── 填空 2 ──────────────────────────────
    # 切分：最近 KEEP_RECENT 条保留原文，更早的（rest 去掉最后 KEEP_RECENT 条）拿去摘要
    # 提示：用切片，rest[-KEEP_RECENT:] 是最后 N 条，rest[:-KEEP_RECENT] 是更早的
    keep = rest[-KEEP_RECENT:]                              # ← 填空 2
    old = rest[:-KEEP_RECENT]

    summary = summarize(old)
    # ── 填空 3 ──────────────────────────────
    # 拼出压缩后的消息：system 开头 + 一条「摘要」消息 + 最近保留的原文
    # 提示：head 是 system 列表，中间插一条 user 角色的摘要，最后接 keep
    new_messages = head + [{"role": "user", "content": f"[之前对话摘要] {summary}"}] + keep  # ← 填空 3
    after = estimate_tokens(new_messages)
    return new_messages, before, after


if __name__ == "__main__":
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
