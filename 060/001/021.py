#!/usr/bin/env python3
"""
关卡 2-2 · 流水线式 Multi-Agent（填空版）

核心：研究 → 写作 → 审核 串联，上一个输出是下一个输入。

执行流程图（python3 021.py）：

主题 → research 出素材 → write 基于素材写 → review 审核出最终版

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-2 那节）。
  3. 跑通：看到研究、写作、审核三个阶段的产出依次流下来。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)


def llm(system, user):
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


def research(topic):
    # ── 填空 1 ──────────────────────────────
    # 阶段1：研究，收集素材
    # 提示：system 说「你是研究员，列出 3 个关键素材点」，user 带上 topic
    return llm("你是研究员，列出 3 个关键素材点", topic)   # ← 填空 1：补全 system 和 user


def write(topic, material):
    # ── 填空 2 ──────────────────────────────
    # 阶段2：写作，基于素材写文章
    # 提示：关键是把 material（素材）也传进去，LLM 才能基于素材写
    return llm("你是作家，基于素材写一段 100 字左右的介绍。", f"主题：{topic}\n素材：\n{material}",)   # ← 填空 2：补全 system 和 user（记得带上 material）


def review(article):
    # ── 填空 3 ──────────────────────────────
    # 阶段3：审核，挑毛病并给改进版
    # 提示：system 说「你是编辑，指出问题给改进版」，user 带上 article
    return llm("你是编辑，指出问题给改进版", article)   # ← 填空 3：补全 system 和 user


if __name__ == "__main__":
    topic = "人工智能对教育的影响"
    print("=" * 55)
    print("  流水线式 Multi-Agent：研究 → 写作 → 审核")
    print("=" * 55)

    material = research(topic)
    print(f"\n🔍 研究阶段产出：\n{material}")

    article = write(topic, material)
    print(f"\n✍️ 写作阶段产出：\n{article}")

    final = review(article)
    print(f"\n✅ 审核阶段产出（最终版）：\n{final}")
