#!/usr/bin/env python3
"""
关卡 1-17 · 对话状态机（完整版）

核心：多轮对话如果让 LLM 自由发挥，容易跑偏（漏问、重复问、跳步）。
对话状态机（FSM）用一个「状态」变量管住流程：每个状态只问一个明确的问题，
答完才转移到下一个状态，不跑偏、不漏项。

执行流程图（python3 dialogue_fsm.py）：

state = "menu"（初始状态）
  └─ 循环直到 done：
       ├─ 打印当前状态的问题（PROMPTS[state]）
       ├─ 读用户输入
       ├─ 用 LLM 提取当前状态需要的信息（extract）
       ├─ 记录到 order
       └─ state = NEXT_STATE[state]（转移到下一状态）

方法调用关系：
  extract() ──> client.chat.completions.create（LLM 提取信息）
  主循环 ──> 用 NEXT_STATE 字典做状态转移

面试怎么讲（30 秒）：
  "多轮对话用状态机管流程，每个状态一个明确意图，答完才转移。
  好处是不跑偏、不漏问，坏处是流程写死、灵活度低。适合订餐/挂号这类固定流程，
  灵活场景要混合 LLM 自由对话 + 状态约束。"
"""

from openai import OpenAI

client = OpenAI(
    api_key="sk-6c0...74e2",   # ← 换成你自己的 key
    base_url="https://api.deepseek.com",
)

# 状态转移表：当前状态 → 下一个状态（FSM 的核心）
NEXT_STATE = {
    "menu": "quantity",
    "quantity": "address",
    "address": "confirm",
    "confirm": "done",
}

# 每个状态问用户什么
PROMPTS = {
    "menu": "你好！今天想吃点什么？（A 宫保鸡丁30元 / B 鱼香肉丝28元 / C 麻婆豆腐22元）",
    "quantity": "要几份？",
    "address": "送到哪个地址？",
    "confirm": "确认下单吗？（回复「确认」或「取消」）",
}


def extract(state, user_input):
    """用 LLM 从用户输入里提取当前状态需要的信息"""
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个信息提取器。只输出提取到的结果，不要解释。"},
            {"role": "user", "content": f"当前要收集的信息：{state}\n用户说：{user_input}\n请提取关键内容（一句话）："},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


if __name__ == "__main__":
    order = {}           # 收集到的订单信息
    state = "menu"       # 初始状态
    print("=" * 50)
    print("  订餐机器人（对话状态机演示）｜ 输入 quit 退出")
    print("=" * 50)

    while state != "done":
        # 当前状态问用户
        print(f"\n[状态:{state}] {PROMPTS[state]}")
        user = input("你: ").strip()
        if user.lower() == "quit":
            print("👋 再见！")
            break
        if not user:
            continue

        # confirm 状态要特殊处理（判断是确认还是取消）
        if state == "confirm":
            if "确认" in user or "是" in user or "好" in user:
                order[state] = "已确认"
            else:
                print("订单已取消，再见！")
                break
        else:
            # 用 LLM 提取信息
            info = extract(state, user)
            order[state] = info
            print(f"   ✓ 已记录：{info}")

        state = NEXT_STATE[state]   # 转移到下一状态

    if state == "done":
        print("\n" + "=" * 50)
        print("  🎉 订单完成！")
        for k, v in order.items():
            print(f"    {k}: {v}")
        print("=" * 50)
