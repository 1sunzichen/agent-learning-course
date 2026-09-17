# 关卡 3-10 · 框架源码导读

> 面试会问「你说你用 LangChain，那它底层是怎么串起来的？」。这一关不教你背 API，教你读透一个模块——**Runnable / LCEL**，因为它是整个框架的「最小公倍数」。

---

## 一、为什么读这个模块（而不是别的）

LangChain 有几百个模块，读哪个最划算？答案是 **Runnable 协议 + LCEL（LangChain Expression Language）**。理由：

1. **所有组件都实现它**——LLM、Prompt、Parser、Retriever、Tool 全都是 Runnable。
2. **一个 `|` 管道串起一切**——`prompt | llm | parser` 这一行是 LangChain 的灵魂，读懂它就懂了 80% 的框架。
3. **读懂它 = 读懂 tracing 的原理**——每个 Runnable 就是一条 trace span。

---

## 二、核心原理：Runnable 协议（4 个方法）

`Runnable` 是一个接口（协议），核心方法：

| 方法 | 作用 | 对应场景 |
|---|---|---|
| `invoke` | 同步执行，吃一个输入吐一个输出 | 一次调用 |
| `ainvoke` | 异步执行 | asyncio 里 |
| `batch` | 批处理一组输入 | 批量跑 |
| `stream` | 流式吐结果 | 打字机效果 |

**关键理解**：这 4 个方法统一了「同步 / 异步 / 批 / 流」四种执行方式。你写的任何一个组件只要实现这 4 个方法，就能和框架里所有组件自由组合——这就是「接口即契约」。

---

## 三、`|` 操作符的魔法：RunnableSequence

`prompt | llm | parser` 底层发生了什么？

1. `|` 运算符调用了 `Runnable.__or__` 方法；
2. 它把左右两个 Runnable 包成一个 **RunnableSequence**（组合器）；
3. `RunnableSequence.invoke(x)` 做的事：**从左到右遍历，前一个的输出喂给后一个的输入**；
4. 所以 `prompt | llm | parser` = 「输入 → 填进模板 → 调 LLM → 解析输出」。

一句话：**LCEL 就是「用管道把一堆 Runnable 串成数据流」**。这是函数式编程的管道思想，`prompt | llm` 和 shell 的 `cat | grep` 是同一个心智模型。

---

## 四、两个辅助 Runnable（面试常问）

- **RunnableLambda**：把一个普通 Python 函数包装成 Runnable，让「非框架代码」也能进管道。`RunnableLambda(lambda x: x.upper())`。
- **RunnablePassthrough**：透传器，把输入原样传下去，常用于管道里「要保留原始输入」的分支。`{"context": retriever, "question": RunnablePassthrough()}` 这种 dict 结构就是「并行子管道 + 透传」的组合。

---

## 五、一次真实的阅读路径（照这个走）

假设你读这一行：`chain = prompt | llm | StrOutputParser()`，然后 `chain.invoke("你好")`。

1. **找入口**：从 `Runnable.__or__` 进去，确认返回的是 `RunnableSequence`。
2. **读核心类**：看 `RunnableSequence.invoke` 怎么遍历 steps——维护一个 `input` 变量，逐个 `step.invoke(input)` 并把返回值赋给下一个。
3. **读叶子节点**：`ChatPromptTemplate.invoke`（填模板）、`ChatOpenAI.invoke`（真正调 API，把响应包成 `AIMessage`）、`StrOutputParser.invoke`（从 `AIMessage` 里取 `.content` 字符串）。
4. **验证理解**：自己 `print(chain.get_graph().draw_ascii())` 或手动 `prompt.invoke(x)` 逐级看输出，确认每一步的输入输出类型。

读源码的通用方法：**找入口 → 读核心类 → 画调用链 → 手动跑单步验证**。别逐行死磕，抓「数据怎么流动」这条主线。

---

## 六、这套设计牛在哪（面试加分）

1. **统一接口**：同步/异步/批/流一套协议，组件自由换（换个 LLM 只改一个节点）。
2. **可组合**：`|` 管道 + dict 并行子管道，复杂流程用简单语法表达。
3. **天然可观测**：每个 Runnable 是一个 span，LangSmith/Langfuse 的 trace 树就是 Runnable 的调用树——所以「用 LangChain 自动获得 tracing」不是魔法，是设计使然。
4. **这也是 LangGraph 的地基**：LangGraph 的节点本质上还是 Runnable，只是把「管道」升级成了「有环的图」，能支持循环、分支、人审。

---

## 七、面试标准答法（背下来）

「LangChain 的核心抽象是 Runnable 协议 + LCEL。Runnable 统一了 invoke/ainvoke/batch/stream 四种执行方式，所有组件（LLM、Prompt、Parser、Retriever）都实现它。`prompt | llm | parser` 里的 `|` 调的是 `Runnable.__or__`，把左右两个 Runnable 包成 RunnableSequence，invoke 时从左到右、前一个输出喂给后一个输入。所以 LCEL 本质是用管道把 Runnable 串成数据流，这套设计同时带来了组件可替换、可组合、可自动 tracing。LangGraph 就是把这条『直线管道』升级成『有环有分支的图』。」

---

## 八、自检清单（讲不清就重看）

- [ ] 能说出 Runnable 的 4 个方法，以及它为什么是「框架的最小公倍数」
- [ ] 能解释 `prompt | llm | parser` 里 `|` 到底调了什么方法、返回了什么对象
- [ ] 能说出 RunnableSequence.invoke 的核心逻辑（左到右，前出后入）
- [ ] 知道 RunnableLambda 和 RunnablePassthrough 分别干嘛
- [ ] 能讲清「LCEL 管道」和「LangGraph 图」的关系（直线 vs 有环有分支）
- [ ] 能解释为什么用 LangChain 自动就有 tracing（每个 Runnable 是一个 span）
