#!/usr/bin/env python3
"""
关卡 2-11 · 任务分解与子 agent 委派（填空版）

核心：复杂任务先拆成子任务，再按能力路由给最合适的子 agent，各司其职而不是一个 agent 硬扛。

执行流程图（python3 029.py）：

复杂任务字符串 → decompose 拆成子任务 → route 按关键词匹配 agent → 逐个委派执行 → 汇总结果

规则：
  1. 下面有 3 个空，填对了才能跑通。
  2. 卡住看 answers-029-033.md（关卡 2-11 那节）。
  3. 跑通：看到一个复杂任务被拆成 4 步，分别交给翻译/数学/总结/写作 agent 完成并汇总。
"""

import asyncio

# 子 agent 注册表：每个 agent 有名字 + 擅长的关键词 + 执行函数（纯模拟，离线可跑）
AGENTS = [
    {"name": "translator", "keywords": ["翻译", "英文"], "run": lambda t: f"「{t}」→ Hello, world!"},
    {"name": "math",       "keywords": ["计算", "等于"], "run": lambda t: f"「{t}」→ 42"},
    {"name": "summarizer", "keywords": ["总结", "摘要", "会议"], "run": lambda t: f"「{t}」→ （摘要）核心是把复杂任务拆小"},
    {"name": "writer",     "keywords": ["写", "文案", "推广"], "run": lambda t: f"「{t}」→ （文案）AI 让复杂任务更简单"},
]


def decompose(task):
    """把一整个复杂任务拆成子任务列表"""
    # ── 填空 1 ──────────────────────────────
    # 用换行符把任务拆开，去掉空行和首尾空白
    # 提示：task.split("\n")，再过滤掉 strip() 后为空的行
    subtasks = None   # ← 填空 1：拆成子任务列表
    return subtasks


def route(subtask):
    """根据子任务内容，匹配最合适的子 agent"""
    # ── 填空 2 ──────────────────────────────
    # 遍历 AGENTS，找到「某个关键词出现在 subtask 里」的 agent 并返回
    # 提示：for a in AGENTS，any(k in subtask for k in a["keywords"])，匹配到 return a
    agent = None   # ← 填空 2：返回匹配的 agent
    return agent


async def execute(subtasks):
    """委派每个子任务给匹配的 agent 执行，收集结果"""
    # ── 填空 3 ──────────────────────────────
    # 遍历每个子任务：route 找到 agent → 调它的 run(st) → 拼成一行结果存进列表
    # 提示：for st in subtasks: a = route(st); results.append(f"  [{a['name']}] {a['run'](st)}")
       # ← 填空 3：执行所有子任务并收集结果
    for st in subtasks: a = route(st);
    results = results.append(f"  [{a['name']}] {a['run'](st)}")
    return results


def main():
    task = (
        "把「你好」翻译成英文\n"
        "计算 40+2 等于几\n"
        "总结今天的会议纪要\n"
        "写一句产品推广文案"
    )
    subtasks = decompose(task)
    print(f"拆解出 {len(subtasks)} 个子任务：")
    for st in subtasks:
        print(f"  · {st}")
    print("\n委派执行：")
    for line in asyncio.run(execute(subtasks)):
        print(line)
    print("\n（每个子任务都交给了最合适的 agent，而不是一个 agent 硬扛）")


if __name__ == "__main__":
    print("=" * 55)
    print("  任务分解与子 agent 委派演示")
    print("=" * 55)
    main()
