# 关卡 2-11 ~ 2-15 填空答案（029 ~ 033）

> 先自己填对应的 0XX.py 的填空，卡住了再往下看。
> 每关都有「关键理解」，不只是给答案，还讲为什么。

---

## 029.py（关卡 2-11 · 任务分解与子 agent 委派）

**填空 1**（拆成子任务）：
```python
subtasks = [line.strip() for line in task.split("\n") if line.strip()]
```
关键理解：任务分解的工程本质就是「把一段长文本拆成可独立执行的单元」。`task.split("\n")` 按行拆，`if line.strip()` 过滤掉空行，`line.strip()` 去掉首尾空白。拆出来的每个子任务才能被单独路由。

**填空 2**（按能力路由）：
```python
for a in AGENTS:
    if any(k in subtask for k in a["keywords"]):
        return a
return None
```
关键理解：路由 = 「谁擅长谁来做」。每个子 agent 声明自己擅长哪些关键词，dispatcher 用 `any(k in subtask for k in a["keywords"])` 判断这个子任务该交给谁。这是最简单的能力匹配——生产里会换成更细的「能力描述 + LLM 打分」或向量相似度匹配。

**填空 3**（委派执行 + 收集结果）：
```python
results = []
for st in subtasks:
    a = route(st)
    results.append(f"  [{a['name']}] {a['run'](st)}")
return results
```
关键理解：找到 agent 后真正调它的 `run(st)` 才算「委派」，结果收进列表统一汇总。注意这里 `a['run']` 是真实 Python 函数（用 lambda 模拟的），不是 LLM 装样子——委派的本质是把活「派」出去执行。

---

## 030.py（关卡 2-12 · 消息路由与事件总线）

**填空 1**（登记订阅者）：
```python
self._subs.setdefault(topic, []).append(handler)
```
关键理解：`setdefault(topic, [])` 是「有就取出来，没有就建一个空列表再取出来」的惯用法，然后把 handler 追加进去。这样第一个订阅者自动建列表，后面的直接追加，不会 KeyError。

**填空 2**（按 topic 投递）：
```python
for h in self._subs.get(topic, []):
    h(message)
```
关键理解：`self._subs.get(topic, [])` 拿到「只订阅了该 topic」的 handler 列表，逐个调用。没人订阅时 get 返回空列表，循环不执行——所以 sport 消息没人收到。这就是「路由不串台」的关键：消息只发给明确订阅了该 topic 的人。

**填空 3**（完成三个订阅）：
```python
bus.subscribe("weather", weather_agent)
bus.subscribe("news", news_agent)
bus.subscribe("stock", stock_agent)
```
关键理解：发布/订阅是「解耦」的——发布者不知道（也不需要知道）谁在听，订阅者各自声明自己要听哪个 topic。新增订阅者不需要改发布者的代码，这就是事件总线比「直接调用」灵活的地方。

---

## 031.py（关卡 2-13 · 黑板模式/共享记忆）

**填空 1**（写黑板）：
```python
self.data[key] = value
```
关键理解：黑板就是一块共享 dict，写 = 存键值对。agent 之间不直接传参数，全靠写黑板暴露自己的中间结果。

**填空 2**（读黑板）：
```python
result = self.data.get(key)
```
关键理解：读 = 按 key 取，`get` 没有就返回 None（不抛异常）。这样「谁先写谁后写」不重要，读的人只关心「现在黑板上有没有这个 key」。

**填空 3**（读多个结果拼最终建议）：
```python
w = bb.read("weather")
t = bb.read("traffic")
f = bb.read("food")
bb.write("advice", f"天气{w}，路况{t}，就餐建议：{f}。综合建议：打车出行，穿薄外套。")
```
关键理解：顾问 agent 自己不做天气/交通/美食查询，它只「读黑板」把别人写好的结果拼起来。这就是黑板模式的精髓——**每个 agent 只补自己擅长的那块，最终由某个 agent 汇总黑板拼出完整答案**。agent 之间零直接通信，全通过黑板间接协作。

---

## 032.py（关卡 2-14 · 死锁与循环检测）

**填空 1**（死锁：撞到灰色节点）：
```python
if c == 1: return True
```
关键理解：三色标记 DFS 里，「灰」= 正在递归访问的路径上的节点。如果从当前节点走到下一个节点发现它是「灰」的，说明绕了一圈回到自己正在访问的路径 → 等待关系成环 → 死锁。`c == 0`（白）才继续深入，`c == 2`（黑）已处理过跳过。

**填空 2**（循环：状态重复）：
```python
if s in seen: return True, "状态重复：原地打转"
```
关键理解：如果 agent 产出的状态之前出现过，说明它在「原地打转」——同样的输入 → 同样的动作 → 同样的状态，无限循环。用 `seen` 集合去重是检测这种循环最直接的办法。

**填空 3**（循环：步数超限）：
```python
if len(states) > max_steps: return True, "步数超限：停不下来"
```
关键理解：状态不重复也可能死循环（比如 agent 一直在产生「步骤1、步骤2、步骤3…」各不相同但永远不停）。所以除了去重，还要设一个步数上限，超过就判为循环。生产里的 agent loop 通常「双保险」：去重 + max_steps。

---

## 033.py（关卡 2-15 · 跨 agent 分布式 tracing）

**填空 1**（生成 trace_id）：
```python
trace_id = uuid.uuid4().hex[:8]
```
关键理解：trace_id 标识「一次完整请求」。一次请求跨多少 agent，它们共享同一个 trace_id，所以能把这些零散的 span 聚合成一条链路。

**填空 2**（记录一个 span）：
```python
span_id = uuid.uuid4().hex[:8]
self.spans.append({"trace": trace_id, "span": span_id, "parent": parent_id, "name": name})
return span_id
```
关键理解：span = 一个 agent 的「一段工作」。它有自己的 span_id，还要记录 parent（父 span 的 id），这样 span 才能连成树。`return span_id` 是关键——调用者拿到这个 id，才能把它作为「父 span」传给下一个 agent。

**填空 3**（跨 agent 传播上下文）：
```python
span_id = tracer.record_span(trace_id, agent_name, parent_id=parent_span)
```
关键理解：这是「分布式 tracing」的灵魂——**上下文传播**。一个 agent 调用另一个 agent 时，必须把 trace_id 和自己的 span_id（作为 parent）传下去，否则两个 agent 的 span 连不起来，链路就断了。生产里这个 context 通过 HTTP header（如 W3C `traceparent`）或消息队列的 metadata 传递。
