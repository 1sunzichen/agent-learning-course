# orchestrator.py · 调度者与执行者

课程：2-1 · 全课程第 21 节。源码快照 SHA-256 前 12 位：`c4abf11a6267`。

[原文件](../orchestrator.py) · [网页阅读](pages/orchestrator.py.html) · [放大调用图](graphs/orchestrator.py.svg)

## 这份文件要完成什么

调度者拆任务，执行者分头处理，最后汇总。

## 为什么需要它

不同子任务有不同目标，把职责分开便于控制。

## 当前文件的实际状态

- 存在外部服务或模型依赖；执行前需按源文件配置依赖和凭据，可能联网或产生 API 费用。 本次只做静态解析，没有运行练习，也没有替你填写或修改原代码。

## 调用图 / 阅读与数据流程

实线：源码中的直接调用；虚线：函数引用/注册、动态调用或按方法名推断的候选。L 是调用所在源码行号。箭头不表示执行顺序或每次必经；分支、循环、异步调度及框架内部调用需结合源码。灰色是外部/未解析目标，橙色是动态分发；省略 print、len 和常规容器操作以减少干扰。孤立函数可能尚未接入。

![流程图](graphs/orchestrator.py.svg)

<details><summary>Mermaid 图源</summary>

```mermaid
flowchart LR
  n0["llm · L35"]
  n1["orchestrator_plan · L44"]
  n2["worker · L52"]
  n3["orchestrator_summarize · L57"]
  n4["模块顶层 / 条件入口"]
  n5["OpenAI"]
  n6["client.chat.completions.create"]
  n4 -->|"L29"| n5
  n0 -->|"L36"| n6
  n1 -->|"L46"| n0
  n2 -->|"L54"| n0
  n3 -->|"L60"| n0
  n4 -->|"L73"| n1
  n4 -->|"L80"| n2
  n4 -->|"L86"| n3
```

</details>

## 从哪里开始看

先从 模块入口 出发，沿箭头找到本文件函数，再查看外部调用或动态分发。右侧调用清单保留所有静态调用点，能回到原文件逐行对照。

## 关键函数与依赖

| 函数 / 定义行 | 职责（源码注释供参考） | 函数体中的调用 |
|---|---|---|
| `llm` [L35](../orchestrator.py#L35) | 以源码函数体为准；下列调用展示其依赖。 | `client.chat.completions.create, resp.choices[动态键].message.content.strip` |
| `orchestrator_plan` [L44](../orchestrator.py#L44) | 主 agent：把大任务拆成子任务 | `llm` |
| `worker` [L52](../orchestrator.py#L52) | worker：执行单个子任务 | `llm` |
| `orchestrator_summarize` [L57](../orchestrator.py#L57) | 主 agent：汇总所有 worker 的结果 | `动态对象.join, llm` |

## 这样做的优点

拆解和汇总各自清楚，便于替换某个执行者。

## 代价与局限

调度者可能成为瓶颈，拆错任务会影响全链路。

## 适合什么场景

能分解为几个专业子任务的报告或分析。

## 不适合直接照搬的场景

简单请求，或子任务之间需要密集交互却没有共享机制。

## 改一个条件，检验是否理解

让一个执行者只返回部分信息，检查汇总是否说明缺失。

如果当前文件有未实现位置，先预测应该怎样变化，补齐后再验证；不要把“能启动”当作“实现正确”。

## 全部静态调用点

这是语法分析清单，包含图中省略的基础操作；不记录参数值。

| 调用方 | 目标表达式 | 行号 | 类型 |
|---|---|---|---|
| <模块入口> | `OpenAI` | 29 | 调用表达式 |
| llm | `client.chat.completions.create` | 36 | 调用表达式 |
| llm | `resp.choices[动态键].message.content.strip` | 41 | 调用表达式 |
| orchestrator_plan | `llm` | 46 | 调用表达式 |
| worker | `llm` | 54 | 调用表达式 |
| orchestrator_summarize | `动态对象.join` | 59 | 调用表达式 |
| orchestrator_summarize | `llm` | 60 | 调用表达式 |
| <模块入口> | `print` | 68 | 调用表达式 |
| <模块入口> | `print` | 69 | 调用表达式 |
| <模块入口> | `print` | 70 | 调用表达式 |
| <模块入口> | `orchestrator_plan` | 73 | 调用表达式 |
| <模块入口> | `line.strip().strip` | 74 | 调用表达式 |
| <模块入口> | `line.strip` | 74 | 调用表达式 |
| <模块入口> | `plan.split` | 74 | 调用表达式 |
| <模块入口> | `line.strip` | 74 | 调用表达式 |
| <模块入口> | `print` | 75 | 调用表达式 |
| <模块入口> | `enumerate` | 76 | 调用表达式 |
| <模块入口> | `print` | 77 | 调用表达式 |
| <模块入口> | `worker` | 80 | 调用表达式 |
| <模块入口> | `print` | 81 | 调用表达式 |
| <模块入口> | `enumerate` | 82 | 调用表达式 |
| <模块入口> | `print` | 83 | 调用表达式 |
| <模块入口> | `orchestrator_summarize` | 86 | 调用表达式 |
| <模块入口> | `print` | 87 | 调用表达式 |
