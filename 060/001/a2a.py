#!/usr/bin/env python3
"""
关卡 2-5 · A2A 通信协议（完整版）

核心：多 agent 要协作，得有个「统一语言」。A2A（Agent-to-Agent）协议
就是定义 agent 之间通信的结构化 JSON 格式——每条消息都带 消息ID、发送方、
接收方、类型、内容、时间戳，让不同 agent 能无歧义地理解彼此、校验彼此。

执行流程图（python3 a2a.py）：

agent A ── make_message 构造 JSON 消息 ──> agent B
  └─ validate_message 校验格式 → handle_message 处理 → 回一条新消息 → A

消息结构（JSON）：
  { msg_id, sender, receiver, type, payload, timestamp }

方法调用关系：
  make_message() ──> 构造消息字典（uuid 生成 id + time 打时间戳）
  validate_message() ──> 校验必填字段 + 类型合法性
  handle_message() ──> 校验 → 按 type 处理 → 回信

面试怎么讲（30 秒）：
  "多 agent 之间要用统一的结构化协议通信，A2A 就是定义消息的 JSON 格式——
  sender/receiver/type/payload 等字段。好处是解耦、可校验、可追踪；
  对比 MCP 是 agent 和工具之间的协议，A2A 是 agent 和 agent 之间的协议。"
"""

import json
import time
import uuid

# 合法的消息类型
MSG_TYPES = {"request", "response", "result", "error"}


def make_message(sender, receiver, type_, payload):
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
    """校验消息是否符合 A2A 协议，返回 (是否合法, 原因)"""
    required = ["msg_id", "sender", "receiver", "type", "payload"]
    for field in required:
        if field not in msg:
            return False, f"缺少字段：{field}"
    if msg["type"] not in MSG_TYPES:
        return False, f"非法消息类型：{msg['type']}"
    return True, "合法"


def handle_message(msg):
    """agent 收到消息：校验 → 处理 → 回信"""
    ok, reason = validate_message(msg)
    if not ok:
        return make_message(msg["receiver"], msg["sender"], "error", f"消息非法：{reason}")

    if msg["type"] == "request":
        return make_message(msg["receiver"], msg["sender"], "response", f"已收到请求：{msg['payload']}")
    return make_message(msg["receiver"], msg["sender"], "result", f"处理完成：{msg['payload']}")


if __name__ == "__main__":
    print("=" * 55)
    print("  A2A 通信协议演示（agent A ↔ agent B）")
    print("=" * 55)

    # A 发请求给 B
    msg = make_message("agent_A", "agent_B", "request", "帮我查一下北京天气")
    print("\n📤 A 发出的消息：")
    print(json.dumps(msg, ensure_ascii=False, indent=2))

    # B 处理并回信
    reply = handle_message(msg)
    print("\n📥 B 的回信：")
    print(json.dumps(reply, ensure_ascii=False, indent=2))

    # 演示非法消息被拦截
    bad = {"sender": "agent_A", "receiver": "agent_B", "type": "hack", "payload": "x"}
    ok, reason = validate_message(bad)
    print(f"\n❌ 非法消息校验：{'合法' if ok else '非法'}（{reason}）")
