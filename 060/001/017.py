#!/usr/bin/env python3
"""
关卡 1-17 · 对话状态机（填空版）

核心：用状态机（FSM）管多轮对话，每个状态只问一个问题，答完才转移，不跑偏。

执行流程图（python3 017.py）：

state="menu" → 循环：问问题 → 读输入 → LLM 提取信息 → 状态转移 → 直到 done

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 1-17 那节）。
  3. 跑通：跟着机器人走完订餐流程（选菜→数量→地址→确认），最后打印完整订单。
"""

from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# ── 填空 1 ──────────────────────────────
# 状态转移表：当前状态 → 下一个状态（FSM 的核心）
# 提示：订餐流程是 menu → quantity → address → confirm → done
NEXT_STATE = {
    "menu": "quantity",
    "quantity": "address",
    "address": "confirm",
    "confirm": "done",
}   # ← 填空 1：补全每个状态的下一个状态

PROMPTS = {
    "menu": "你好！今天想吃点什么？（A 宫保鸡丁30元 / B 鱼香肉丝28元 / C 麻婆豆腐22元）",
    "quantity": "要几份？",
    "address": "送到哪个地址？",
    "confirm": "确认下单吗？（回复「确认」或「取消」）",
}


def extract(state, user_input):
    # ── 填空 2 ──────────────────────────────
    # 用 LLM 从用户输入里提取当前状态需要的信息
    # 提示：messages 里 system 说「你是信息提取器，只输出结果」，
    #       user 里带上 state 和 user_input，返回 choices[0].message.content
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个信息提取器。只输出提取到的结果，不要解释。"},
            {"role": "user", "content": f"当前要收集的信息：{state}\n用户说：{user_input}\n请提取关键内容（一句话）："},
        ],
        temperature=0,
    )   # ← 填空 2：补全 system 和 user 消息，并 return 提取结果
    return resp.choices[0].message.content.strip()


if __name__ == "__main__":
    order = {}
    state = "menu"
    print("=" * 50)
    print("  订餐机器人（对话状态机演示）｜ 输入 quit 退出")
    print("=" * 50)

    while state != "done":
        print(f"\n[状态:{state}] {PROMPTS[state]}")
        user = input("你: ").strip()
        if user.lower() == "quit":
            print("👋 再见！")
            break
        if not user:
            continue

        if state == "confirm":
            if "确认" in user or "是" in user or "好" in user:
                order[state] = "已确认"
            else:
                print("订单已取消，再见！")
                break
        else:
            info = extract(state, user)
            order[state] = info
            print(f"   ✓ 已记录：{info}")

        # ── 填空 3 ──────────────────────────────
        # 转移到下一状态
        # 提示：用 NEXT_STATE 字典，根据当前 state 取下一个状态
        state = NEXT_STATE[state]   # ← 填空 3：补全状态转移

    if state == "done":
        print("\n" + "=" * 50)
        print("  🎉 订单完成！")
        for k, v in order.items():
            print(f"    {k}: {v}")
        print("=" * 50)
