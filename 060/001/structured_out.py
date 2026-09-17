#!/usr/bin/env python3
"""
关卡 1-14 · 结构化输出（完整版）

核心：让 LLM 稳定吐 JSON，失败自动校验重试。
LLM 输出 JSON 不稳定（会多字、少括号、加解释），所以三招：
  ① 明确要求「只输出 JSON，不要其他文字」
  ② json.loads 校验
  ③ 失败把报错喂回去让它修正，最多重试 N 次

执行流程图（python3 structured_out.py）：

一段文本 → 让 LLM 提取结构化信息（JSON）
  └─ json.loads 校验
       ├─ 成功 → 返回 dict
       └─ 失败 → 把「上次输出 + 报错」喂回，重试（最多 3 次）

方法调用关系：
  extract_json() ──> client.chat.completions.create（提取）
       └─ json.loads（校验）──失败──> 重试修正

面试怎么讲（30 秒）：
  "让 LLM 稳定吐结构化数据，靠三招：明确要求 JSON、json.loads 校验、失败重试修正。
  更强的是 JSON mode 和函数调用（天然结构化），以及 pydantic 校验。"
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

TEXT = "张三 2024 年 5 月在北京创办了「星辰科技」，主营 AI 客服。"

SCHEMA_HINT = '{"name": "人名", "time": "时间", "city": "城市", "company": "公司名"}'


def extract_json(text, max_retry=3):
    """让 LLM 从文本提取信息，输出 JSON，失败自动修正重试"""
    messages = [
        {"role": "system", "content": "你只输出 JSON，不要输出任何其他文字、解释或代码块标记。"},
        {"role": "user", "content": f"从下面文本提取信息，按这个格式输出 JSON：\n{SCHEMA_HINT}\n\n文本：{text}"},
    ]
    for attempt in range(1, max_retry + 1):
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=messages, temperature=0,
        )
        raw = resp.choices[0].message.content
        try:
            data = json.loads(raw)      # 校验：能解析就说明是合法 JSON
            return data, attempt        # 返回结果 + 第几次成功
        except json.JSONDecodeError as e:
            print(f"  第 {attempt} 次输出不是合法 JSON（{e}），重试...")
            # 把上次的错误输出 + 报错喂回去，让它修正
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": f"你上面的输出无法解析成 JSON，报错：{e}。请重新输出，只输出合法的 JSON。"})
    return None, max_retry


if __name__ == "__main__":
    print("=" * 55)
    print("  结构化输出演示")
    print("=" * 55)
    print("  文本：" + TEXT)
    data, attempts = extract_json(TEXT)
    print(f"\n  （第 {attempts} 次成功）")
    print("  解析结果：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
