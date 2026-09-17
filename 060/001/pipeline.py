#!/usr/bin/env python3
"""
关卡 2-2 · 流水线式 Multi-Agent（完整版）

核心：流水线式（Pipeline）——多个 agent 串联，上一个的输出是下一个的输入。
像工厂流水线：研究 → 写作 → 审核。
和层级式的区别：层级式是「控制流」（主 agent 派活），流水线是「数据流」（结果一路流下去）。

执行流程图（python3 pipeline.py）：

[主题]
  └─ research（研究 agent 收集素材）
       └─ write（写作 agent 基于素材写文章）
            └─ review（审核 agent 挑毛病并给改进版）
                 └─ 最终成品

方法调用关系：
  research() ──> llm()（收集素材）
  write() ──> llm()（基于素材写，material 传进来）
  review() ──> llm()（审核改进）

面试怎么讲（30 秒）：
  "流水线式是 agent 串联，上一个输出是下一个输入，适合「有固定工序」的任务
  （研究→写作→审核）。优点是简单清晰，缺点是流水线一断全断、不能并行。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
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
    """阶段1：研究，收集素材"""
    return llm("你是研究员，围绕主题列出 3 个关键素材点。", f"主题：{topic}")


def write(topic, material):
    """阶段2：写作，基于素材写文章"""
    return llm(
        "你是作家，基于素材写一段 100 字左右的介绍。",
        f"主题：{topic}\n素材：\n{material}",
    )


def review(article):
    """阶段3：审核，挑毛病并给改进版"""
    return llm("你是编辑，指出问题并给出改进后的版本。", f"文章：\n{article}")


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
