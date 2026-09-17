# 关卡 2-16 ~ 2-19 · 填空答案

> 先自己填 034.py ~ 037.py 的空，卡住了再往下看。

---

## 034.py（关卡 2-16 · 成本分摊与预算控制）填空答案

**填空 1**（算单次成本）：
```python
return (prompt_tokens * PRICE_INPUT + completion_tokens * PRICE_OUTPUT) / 1_000_000
```
关键理解：单价单位是「元 / 百万 token」，所以要除以 1_000_000。输入、输出单价不同（输出更贵），必须分开乘。这就是多 agent 成本的地基——先会算每个 agent 一次调用花了多少钱。

**填空 2**（成本分摊到各 agent）：
```python
ledger[agent_name] = ledger.get(agent_name, 0.0) + cost
```
关键理解：成本分摊的核心是「按 agent 记账」。`get(agent_name, 0.0)` 处理第一次出现的 agent（还没有台账记录，兜底 0）。多 agent 里钱是分散花在各个 worker 身上的，不分摊就不知道「谁最烧钱」。

**填空 3**（预算止损）：
```python
if total > BUDGET:
    print("  ⛔ 触发预算止损，停止派发新任务")
    stopped = True
    break
```
关键理解：预算止损 = 累计成本超过预算线就立即停止派发新任务。这是多 agent 成本失控的最后一道防线——agent 越多越容易烧钱失控，必须在派发循环里每步检查，而不是跑完了才发现超支。

**面试 30 秒**：「多 agent 成本怎么控？每个 agent 的 token 记账、按 agent 分摊成本、总预算设止损线，超了就停派。源头省钱同单 agent：压 prompt、缓存、摘要、便宜模型。」

---

## 035.py（关卡 2-17 · 人机协同 HITL）填空答案

**填空 1**（判断是否关键节点）：
```python
return step[1]
```
关键理解：step 是 `(步骤名, 是否关键)` 元组，`step[1]` 就是那个布尔标记。关键节点 = 高风险、不可逆、出错代价大的动作（发信/改库/扣款），这类动作不能全自动。

**填空 2**（模拟等人确认）：
```python
if HUMAN_REPLIES:
    return HUMAN_REPLIES.pop(0)
return "approve"
```
关键理解：真实系统里这里是「发通知给人 + 挂起任务 + 等人点批准/拒绝」。离线演示用预置回答队列模拟人的决定。`pop(0)` 按顺序消费；队列空了默认 approve 是防御性兜底。

**填空 3**（拒绝即中止）：
```python
if decision != "approve":
    print("  🛑 人工拒绝，流程中止")
    break
```
关键理解：HITL 的价值在于「人能叫停」。批准才继续，拒绝立即 break 中止整个流程，后续步骤不执行。这就是把「最终决定权」留给人，而不是让 agent 一路自动到底。

**面试 30 秒**：「human-in-the-loop 什么时候必须？不可逆或高风险的副作用动作——发信、扣款、删数据、改配置。关键节点停下来等人确认，不全自动。它是安全兜底，和 prompt 层防御互为补充。」

---

## 036.py（关卡 2-18 · 多 agent 评测）填空答案

**填空 1**（任务完成率）：
```python
return run["completed"] / run["total"]
```
关键理解：完成率 = 完成的子任务 / 总子任务。多 agent 任务常被拆成多个子任务，协作失败的表现之一就是「部分子任务没完成」，单看最终答案会漏掉这一点。

**填空 2**（协作效率）：
```python
return 1.0 / run["rounds"]
```
关键理解：效率用「达成共识的对话轮数」衡量，轮数越少越高效。`1/轮数` 把「轮数」转成 0~1 的分（轮数 1 得满分 1.0，轮数 5 只有 0.2）。多 agent 协作容易陷入来回扯皮，这是单 agent 评测里没有的维度。

**填空 3**（加权综合）：
```python
return 0.4 * completion_rate(run) + 0.3 * efficiency_score(run) + 0.3 * quality_score(run)
```
关键理解：综合分 = 完成率 0.4 + 效率 0.3 + 质量 0.3 加权求和。各权重按业务侧重点调。真实系统里「质量」由 LLM-as-Judge 或 golden 答案比对得出。

**面试 30 秒**：「多 agent 评测和单 agent 差在哪？单 agent 看答对没（准确率），多 agent 还要看协作质量——完成率、共识效率（轮数）、产出质量、成本，多维度加权。协作过程本身会引入新失败模式，只测单个 worker 不够。」

---

## 037.py（关卡 2-19 · 安全与权限隔离）填空答案

**填空 1**（白名单查权限）：
```python
return tool in ROLES.get(agent, [])
```
关键理解：最小权限原则的落点——每个 agent 只给够用的工具白名单。`ROLES.get(agent, [])` 对未注册 agent 兜底空列表（默认无权）。查询就是判断 tool 在不在白名单里。

**填空 2**（越权拒绝 + 审计）：
```python
audit_log.append((agent, tool, "无权限"))
return f"⛔ 拒绝：{agent} 无权限调用 {tool}"
```
关键理解：权限门不在 prompt 里「求模型别乱来」，而在执行层硬拦截——越权直接 return 拒绝，根本不给执行机会。同时记审计日志（谁、要调什么、为什么拦），出问题能追责。

**填空 3**（敏感操作管理员门槛）：
```python
if tool in SENSITIVE and agent != "管理员":
    audit_log.append((agent, tool, "敏感操作仅限管理员"))
    return f"⛔ 拒绝：敏感操作 {tool} 仅限管理员"
```
关键理解：纵深防御——即使白名单里给了权限（如运维有 delete），敏感操作（delete/grant）还要额外要求是管理员。两层独立检查，单靠任何一层都不够：白名单管「有没有权」，敏感门槛管「够不够格」。

**面试 30 秒**：「多 agent 安全怎么做？最小权限（每个 agent 只给够用白名单）→ 调用前权限门（越权拒绝）→ 敏感操作额外门槛（delete/grant 仅管理员）→ 全程审计留痕。本质是不信任任何单个 agent，在架构层兜底，而不是靠 prompt 求它听话。」
