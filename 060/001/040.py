#!/usr/bin/env python3
"""
关卡 3-3 · MCP 手写实现（填空版）

核心：手写一个极简 MCP（Model Context Protocol）server + client，理解协议本质。
MCP = 「JSON-RPC 2.0」+「三个方法」+「stdio 传输」。别被"协议"吓到，本质就是：
客户端往 server 的 stdin 写一行 JSON 请求，server 从 stdout 回一行 JSON 响应。

执行流程图（python3 040.py）：

client（主进程）
  ├─ 启动 server 子进程（stdio 管道相连）
  ├─ ① initialize  → 握手，拿 server 的协议版本和能力
  ├─ ② tools/list  → 发现 server 暴露了哪些工具（name + JSON schema）
  ├─ ③ tools/call  → 按名字 + 参数调用工具，拿回结果
  └─ 打印全过程，看到真实往返的 JSON 报文

三个核心方法（面试 30 秒）：
  1. initialize    ：握手 + 版本协商（"AI 的 USB 接口"插上先握手）
  2. tools/list    ：服务发现（客户端不知道 server 有啥工具，先问）
  3. tools/call    ：真正执行（name + arguments → 结果）
JSON-RPC 2.0 报文格式：请求 {jsonrpc, id, method, params}；响应 {jsonrpc, id, result|error}

依赖：无第三方库，纯标准库（json + subprocess + sys）。

规则：
  1. 下面有 3 个空（填空 2 含 a/b 两处），填对了才能跑通。
  2. 卡住看 answers-038-042.md（关卡 3-3 那节）。
  3. 跑通：打印出 ③ tools/call 的天气结果。
"""

import json
import subprocess
import sys


# ================= MCP Server 端 =================
TOOLS = {
    "get_weather": {
        "description": "查询城市天气",
        "inputSchema": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    "calc": {
        "description": "计算数学表达式",
        "inputSchema": {
            "type": "object",
            "properties": {"expr": {"type": "string"}},
            "required": ["expr"],
        },
    },
}


def call_tool(name, args):
    """真正执行工具（这是 server 的核心逻辑）"""
    if name == "get_weather":
        return f"{args['city']} 今天晴，25 度（MCP 模拟）"
    if name == "calc":
        allowed = set("0123456789+-*/(). ")
        if any(c not in allowed for c in args["expr"]):
            return "表达式含非法字符"
        return str(eval(args["expr"]))
    return f"未知工具：{name}"


def handle_request(req):
    """按 method 分发，返回 result（这就是 MCP 的「协议处理」）"""
    method = req.get("method")
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "my-mini-mcp", "version": "0.1.0"},
        }
    if method == "tools/list":
        # ── 填空 1 ──────────────────────────────
        # 返回工具列表。MCP 规定每个工具是 {name, description, inputSchema} 三件套
        # 提示：把上面定义的 TOOLS 字典展开成标准格式
        return {
            "tools": [
                {"name": name, "description": spec["description"],
                 "inputSchema": spec["inputSchema"]}
                for name, spec in ________.items()      # ← 填空 1：遍历哪个字典
            ]
        }
    if method == "tools/call":
        # ── 填空 2 ──────────────────────────────
        # 取出工具名和参数，调用真正的函数，把结果包成 MCP 规定的 content 格式
        # 提示：结果是 [{"type": "text", "text": ...}]，isError 表示执行是否出错
        params = req["params"]
        name = params["name"]
        args = params["arguments"]
        text = ________(name, args)                     # ← 填空 2a：调用哪个函数
        return {
            "content": [{"type": "text", "text": ________}],   # ← 填空 2b：把 text 放进去
            "isError": False,
        }
    return {"error": f"未知 method: {method}"}


def server_main():
    """server 主循环：从 stdin 逐行读 JSON 请求，往 stdout 逐行写 JSON 响应"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        req = json.loads(line)
        result = handle_request(req)
        resp = {"jsonrpc": "2.0", "id": req.get("id")}
        if "error" in result:
            resp["error"] = result["error"]
        else:
            resp["result"] = result
        print(json.dumps(resp, ensure_ascii=False), flush=True)


# ================= MCP Client 端 =================
def rpc(proc, method, params=None):
    """发一个 JSON-RPC 请求，收一个响应"""
    req = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        req["params"] = params
    proc.stdin.write(json.dumps(req, ensure_ascii=False) + "\n")
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())


def main_client():
    print("=" * 55)
    print("  手写 MCP：JSON-RPC over stdio（server + client）")
    print("=" * 55)

    # 启动 server 子进程，走 stdio 管道
    proc = subprocess.Popen(
        [sys.executable, __file__, "--server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )

    # ① 握手
    r = rpc(proc, "initialize")
    print("\n① initialize 响应：", json.dumps(r, ensure_ascii=False))

    # ② 发现工具
    r = rpc(proc, "tools/list")
    print("\n② tools/list 响应：")
    for t in r["result"]["tools"]:
        print(f"   - {t['name']}: {t['description']}")

    # ③ 调用工具
    r = rpc(proc, "tools/call", {"name": "get_weather", "arguments": {"city": "北京"}})
    # ── 填空 3 ──────────────────────────────────
    # 从响应里取出工具返回的文本
    # 提示：结果在 r["result"]["content"]，是列表，取第一项的 "text" 字段
    text = ________                             # ← 填空 3：取结果文本
    print("\n③ tools/call 结果：", text)

    proc.terminate()


if __name__ == "__main__":
    if "--server" in sys.argv:
        server_main()
    else:
        main_client()
