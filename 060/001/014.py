"""
关卡 1-14 · 结构化输出（填空版）

核心：让 LLM 稳定吐 JSON，失败自动校验重试。三招：
  ① 明确要求「只输出 JSON」
  ② json.loads 校验
  ③ 失败把报错喂回去重试

执行流程图（python3 014.py）：

一段文本 → 让 LLM 提取结构化信息（JSON）
  └─ json.loads 校验
       ├─ 成功 → 返回 dict
       └─ 失败 → 把报错喂回，重试

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-14 那节）。
  3. 跑通：能从文本里解析出结构化的 JSON 结果。
"""

import json
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

TEXT = "张三 2024 年 5 月在北京创办了「星辰科技」，主营 AI 客服。"

SCHEMA_HINT = '{"name": "人名", "time": "时间", "city": "城市", "company": "公司名"}'


def extract_json(text, max_retry=3):
    """让 LLM 从文本提取信息，输出 JSON，失败自动修正重试"""
    messages = [
        # ── 填空 1 ──────────────────────────────
        # system 要「明确要求只输出 JSON」，避免模型加解释、加代码块标记
        # 提示：强调「只输出 JSON，不要其他文字/解释/代码块」
        {"role": "system", "content": "你只输出 JSON，不要输出任何其他文字、解释或代码块标记。"},  # ← 填空 1
        {"role": "user", "content": f"从下面文本提取信息，按这个格式输出 JSON：\n{SCHEMA_HINT}\n\n文本：{text}"},
    ]
    for attempt in range(1, max_retry + 1):
        resp = client.chat.completions.create(
            model="deepseek-chat", messages=messages, temperature=0,
        )
        raw = resp.choices[0].message.content
        try:
            # ── 填空 2 ──────────────────────────────
            # 校验：把 LLM 返回的字符串解析成 dict，解析失败会抛 JSONDecodeError
            # 提示：用 json.loads 解析 raw 字符串
            data = json.loads(raw)                          # ← 填空 2
            return data, attempt
        except json.JSONDecodeError as e:
            print(f"  第 {attempt} 次输出不是合法 JSON（{e}），重试...")
            # ── 填空 3 ──────────────────────────────
            # 把上次的错误输出 + 报错喂回去，让模型看到「错在哪」再重新输出
            # 提示：先 append 一条 assistant 角色（上次输出），再 append 一条 user 角色（报错+要求重来）
            messages.append({"role": "assistant", "content": raw})  # ← 填空 3
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
