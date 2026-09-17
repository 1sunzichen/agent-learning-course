# multi_agent_project.py · 多 Agent 综合流程

课程：2-10 · 全课程第 30 节。源码快照 SHA-256 前 12 位：`cba9c5541e97`。

[原文件](../multi_agent_project.py) · [网页阅读](pages/multi_agent_project.py.html) · [放大调用图](graphs/multi_agent_project.py.svg)

## 这份文件要完成什么

组合并发 worker、失败处理和结果汇总。

## 为什么需要它

分工只有在失败、等待和汇总都被处理后才能形成完整流程。

## 当前文件的实际状态

- 存在外部服务或模型依赖；执行前需按源文件配置依赖和凭据，可能联网或产生 API 费用。 本次只做静态解析，没有运行练习，也没有替你填写或修改原代码。

## 调用图 / 阅读与数据流程

实线：源码中的直接调用；虚线：函数引用/注册、动态调用或按方法名推断的候选。L 是调用所在源码行号。箭头不表示执行顺序或每次必经；分支、循环、异步调度及框架内部调用需结合源码。灰色是外部/未解析目标，橙色是动态分发；省略 print、len 和常规容器操作以减少干扰。孤立函数可能尚未接入。

![流程图](graphs/multi_agent_project.py.svg)

<details><summary>Mermaid 图源</summary>

```mermaid
flowchart LR
  n0["worker · L39"]
  n1["safe_worker · L49"]
  n2["main · L57"]
  n3["模块顶层 / 条件入口"]
  n4["AsyncOpenAI"]
  n5["aclient.chat.completions.create"]
  n6["asyncio.gather"]
  n7["asyncio.run"]
  n3 -->|"L33"| n4
  n0 -->|"L41"| n5
  n1 -->|"L52"| n0
  n2 -->|"L70"| n6
  n2 -->|"L70"| n1
  n3 -->|"L81"| n7
  n3 -->|"L81"| n2
```

</details>

## 从哪里开始看

先从 main 及模块入口 出发，沿箭头找到本文件函数，再查看外部调用或动态分发。右侧调用清单保留所有静态调用点，能回到原文件逐行对照。

## 关键函数与依赖

| 函数 / 定义行 | 职责（源码注释供参考） | 函数体中的调用 |
|---|---|---|
| `worker` [L39](../multi_agent_project.py#L39) | worker：执行单个子任务（调 LLM） | `aclient.chat.completions.create, resp.choices[动态键].message.content.strip` |
| `safe_worker` [L49](../multi_agent_project.py#L49) | 带容错的 worker：失败就降级标记，不影响其他 worker | `worker` |
| `main` [L57](../multi_agent_project.py#L57) | 以源码函数体为准；下列调用展示其依赖。 | `print, asyncio.gather, safe_worker, enumerate` |

## 这样做的优点

一个请求能协调多个执行者，便于比较单 Agent 与多 Agent。

## 代价与局限

部分失败时结果含义复杂；需要区分失败文本和有效答案。

## 适合什么场景

多个独立分析维度的综合报告原型。

## 不适合直接照搬的场景

任何一个子结果错误都会导致不可接受后果的直接自动执行。

## 改一个条件，检验是否理解

让一个 worker 抛错，检查其他任务是否继续，以及汇总是否暴露失败。

如果当前文件有未实现位置，先预测应该怎样变化，补齐后再验证；不要把“能启动”当作“实现正确”。

## 全部静态调用点

这是语法分析清单，包含图中省略的基础操作；不记录参数值。

| 调用方 | 目标表达式 | 行号 | 类型 |
|---|---|---|---|
| <模块入口> | `AsyncOpenAI` | 33 | 调用表达式 |
| worker | `aclient.chat.completions.create` | 41 | 调用表达式 |
| worker | `resp.choices[动态键].message.content.strip` | 46 | 调用表达式 |
| safe_worker | `worker` | 52 | 调用表达式 |
| main | `print` | 64 | 调用表达式 |
| main | `print` | 65 | 调用表达式 |
| main | `print` | 66 | 调用表达式 |
| main | `print` | 67 | 调用表达式 |
| main | `asyncio.gather` | 70 | 调用表达式 |
| main | `safe_worker` | 70 | 调用表达式 |
| main | `enumerate` | 72 | 调用表达式 |
| main | `print` | 73 | 调用表达式 |
| main | `print` | 75 | 调用表达式 |
| main | `print` | 76 | 调用表达式 |
| main | `print` | 77 | 调用表达式 |
| <模块入口> | `asyncio.run` | 81 | 调用表达式 |
| <模块入口> | `main` | 81 | 调用表达式 |
