# robust_tools_real.py · 工具超时与重试

课程：1-8 · 全课程第 8 节。源码快照 SHA-256 前 12 位：`1a84b0772873`。

[原文件](../robust_tools_real.py) · [网页阅读](pages/robust_tools_real.py.html) · [放大调用图](graphs/robust_tools_real.py.svg)

## 这份文件要完成什么

给天气工具增加失败重试、超时处理和结果缓存。

## 为什么需要它

外部请求会失败或重复发生，不能让一次偶发错误终止整个流程。

## 当前文件的实际状态

- 通过 requests 访问真实天气服务，HTTP 请求带 timeout；与随机失败的本地 get_weather 模拟版用途不同。
- 存在外部服务或模型依赖；执行前需按源文件配置依赖和凭据，可能联网或产生 API 费用。 本次只做静态解析，没有运行练习，也没有替你填写或修改原代码。

## 调用图 / 阅读与数据流程

实线：源码中的直接调用；虚线：函数引用/注册、动态调用或按方法名推断的候选。L 是调用所在源码行号。箭头不表示执行顺序或每次必经；分支、循环、异步调度及框架内部调用需结合源码。灰色是外部/未解析目标，橙色是动态分发；省略 print、len 和常规容器操作以减少干扰。孤立函数可能尚未接入。

![流程图](graphs/robust_tools_real.py.svg)

<details><summary>Mermaid 图源</summary>

```mermaid
flowchart LR
  n0["get_weather_real · L34"]
  n1["call_weather · L54"]
  n2["模块顶层 / 条件入口"]
  n3["random.random"]
  n4["requests.exceptions.ConnectionError"]
  n5["requests.exceptions.Timeout"]
  n6["resp.raise_for_status"]
  n7["resp.json"]
  n8["time.sleep"]
  n0 -->|"L36, L37"| n3
  n0 -->|"L38"| n4
  n0 -->|"L40"| n5
  n0 -->|"L46"| n6
  n0 -->|"L47"| n7
  n1 -->|"L62"| n0
  n1 -->|"L69"| n8
  n2 -->|"L77, L78"| n1
```

</details>

## 从哪里开始看

先从 模块入口 出发，沿箭头找到本文件函数，再查看外部调用或动态分发。右侧调用清单保留所有静态调用点，能回到原文件逐行对照。

## 关键函数与依赖

| 函数 / 定义行 | 职责（源码注释供参考） | 函数体中的调用 |
|---|---|---|
| `get_weather_real` [L34](../robust_tools_real.py#L34) | 以源码函数体为准；下列调用展示其依赖。 | `random.random, requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.get, resp.raise_for_status, resp.json` |
| `call_weather` [L54](../robust_tools_real.py#L54) | 以源码函数体为准；下列调用展示其依赖。 | `range, get_weather_real, print, time.sleep` |

## 这样做的优点

临时故障可恢复，相同查询命中缓存时减少重复请求。

## 代价与局限

重试增加延迟；按城市缓存会过期。缓存查询结果不等于保证写操作幂等。

## 适合什么场景

只读查询、可以安全重复的工具。

## 不适合直接照搬的场景

扣款、发信等有副作用的操作，除非另有业务幂等机制。

## 改一个条件，检验是否理解

让第一次请求失败，检查重试次数；再查同城，检查缓存是否省去请求。

如果当前文件有未实现位置，先预测应该怎样变化，补齐后再验证；不要把“能启动”当作“实现正确”。

## 全部静态调用点

这是语法分析清单，包含图中省略的基础操作；不记录参数值。

| 调用方 | 目标表达式 | 行号 | 类型 |
|---|---|---|---|
| get_weather_real | `random.random` | 36 | 调用表达式 |
| get_weather_real | `random.random` | 37 | 调用表达式 |
| get_weather_real | `requests.exceptions.ConnectionError` | 38 | 调用表达式 |
| get_weather_real | `requests.exceptions.Timeout` | 40 | 调用表达式 |
| get_weather_real | `requests.get` | 45 | 调用表达式 |
| get_weather_real | `resp.raise_for_status` | 46 | 调用表达式 |
| get_weather_real | `resp.json` | 47 | 调用表达式 |
| call_weather | `range` | 60 | 调用表达式 |
| call_weather | `get_weather_real` | 62 | 调用表达式 |
| call_weather | `print` | 66 | 调用表达式 |
| call_weather | `print` | 68 | 调用表达式 |
| call_weather | `time.sleep` | 69 | 调用表达式 |
| <模块入口> | `print` | 76 | 调用表达式 |
| <模块入口> | `print` | 77 | 调用表达式 |
| <模块入口> | `call_weather` | 77 | 调用表达式 |
| <模块入口> | `print` | 78 | 调用表达式 |
| <模块入口> | `call_weather` | 78 | 调用表达式 |
