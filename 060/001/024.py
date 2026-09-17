#!/usr/bin/env python3
"""
关卡 2-5 · A2A 通信协议（填空版）

核心：多 agent 用统一的结构化 JSON 协议通信（A2A）。
消息字段：msg_id / sender / receiver / type / payload / timestamp。

执行流程图（python3 024.py）：

agent A → make_message 构造 JSON → agent B → validate/handle → 回信

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers.md（关卡 2-5 那节）。
  3. 跑通：看到 A 发的 JSON 消息、B 的回信、非法消息被拦截。
"""

import json
import time
import uuid

# 合法的消息类型
MSG_TYPES = {"request", "response", "result", "error"}


def make_message(sender, receiver, type_, payload):
    # ── 填空 1 ──────────────────────────────
    # 构造 A2A 消息字典
    # 提示：字典里要有 msg_id（uuid.uuid4().hex[:8]）、sender、receiver、
    #       type、payload、timestamp（time.time()）
    """构造一条 A2A 消息"""
    return {
            "msg_id": uuid.uuid4().hex[:8],
            "sender": sender,
            "receiver": receiver,
            "type": type_,
            "payload": payload,
            "timestamp": time.time(),
    }


def validate_message(msg):
    # ── 填空 2 ──────────────────────────────
    # 校验消息：必填字段都要在 msg 里，type 要在 MSG_TYPES 里
    # 提示：required 字段列表 = ["msg_id", "sender", "receiver", "type", "payload"]，
    #       用 for 逐个检查 field 是否在 msg 里，缺了就 return False
    required = ["msg_id", "sender", "receiver", "type", "payload"]  # ← 填空 2：补全 required 字段 + 校验逻辑
    for field in required:
        if field not in msg:
            return False, f"缺少字段：{field}"
    if msg["type"] not in MSG_TYPES:
        return False, f"非法消息类型：{msg['type']}"
    return True, "合法"


def handle_message(msg):
    # ── 填空 3 ──────────────────────────────
    # 校验 → 处理 → 回信
    # 提示：先 validate_message，不合法就回一条 error 消息；
    #       type 是 request 回 response，否则回 result。
    #       回信时 sender/receiver 要互换（谁收到谁回给谁）
    ok, reason = validate_message(msg)
    if not ok:
        return make_message(msg["receiver"], msg["sender"], "error", f"消息非法：{reason}")
    return make_message(msg["receiver"], msg["sender"], "result", f"处理完成：{msg['payload']}")  # ← 填空 3：补全处理 + 回信逻辑


if __name__ == "__main__":
    print("=" * 55)
    print("  A2A 通信协议演示（agent A ↔ agent B）")
    print("=" * 55)

    msg = make_message("agent_A", "agent_B", "request", "帮我查一下北京天气")
    print("\n📤 A 发出的消息：")
    print(json.dumps(msg, ensure_ascii=False, indent=2))

    reply = handle_message(msg)
    print("\n📥 B 的回信：")
    print(json.dumps(reply, ensure_ascii=False, indent=2))

    bad = {"sender": "agent_A", "receiver": "agent_B", "type": "hack", "payload": "x"}
    ok, reason = validate_message(bad)
    print(f"\n❌ 非法消息校验：{'合法' if ok else '非法'}（{reason}）")
