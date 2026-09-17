"""
执行流程图（python3 index2.py）：

顶层脚本
 │
 ├─ 定义 client / SYSTEM / run_python(code)
 ├─ 初始化 messages = [system, user]
 │
 └─ for step in range(10):                    ← 主循环（最多 10 轮）
      │
      ├─ client.chat.completions.create(messages)      ← ① 调 LLM
      │     └─ reply = LLM 的「思考 + 行动」
      │
      ├─ 打印 reply
      ├─ reply 含 "Final Answer" ?
      │     ├─ 是 → break（结束）
      │     └─ 否 ↓
      │
      ├─ 从 reply 提取 python 代码块
      │     └─ run_python(code)                 ← ② 调内部函数
      │            └─ subprocess.run(...)        ← ③ 真执行代码
      │            └─ 返回 obs
      │
      ├─ 打印 Observation
      └─ messages.append(...)                    ← 喂回，进入下一轮

方法调用关系：
  顶层脚本 ──> client.chat.completions.create()   （调 LLM）
  顶层脚本 ──> run_python()                       （执行 agent 写的代码）
  run_python ──> subprocess.run()                 （调系统执行）
"""

import subprocess
from openai import OpenAI

client = OpenAI(
    api_key=__import__("os").environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

SYSTEM = """你是 ReAct agent，通过「思考→行动→观察」循环解决问题。

每轮严格按下面格式输出，一次只输出一步：

Thought: 你的思考
Action: python
```python
<要运行的代码>
```

当你已经有答案时，输出：

Thought: 有答案了
Final Answer: <最终答案>

规则：涉及计算时你必须写 Python 代码来算，不许心算。每次只走一步，等看到 Observation 再继续。"""

def run_python(code):
    try:
        r = subprocess.run(["python3","-c",code], capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr).strip() or "(无输出)"
    except Exception as e:
        return f"执行出错: {e}"

messages = [{"role":"system","content":SYSTEM},
            {"role":"user","content":"37 × 53 等于多少？"}]

for step in range(10):                      # 最多循环 10 轮
    resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0)
    reply = resp.choices[0].message.content
    print("=" * 50)
    print(reply)

    if "Final Answer" in reply:
        print("\n🎉 agent 自己算出了答案")
        break

    if "```python" in reply:
        code = reply.split("```python")[1].split("```")[0].strip()
    else:
        code = None
    obs = run_python(code) if code else "(没有可执行代码)"

    print(f"\nObservation: {obs}\n")
    messages.append({"role":"assistant","content":reply})
    messages.append({"role":"user","content":f"Observation: {obs}"})