# Phase 3 · 043 / 044 填空答案

> 先自己填 043.py / 044.py 的填空，卡住了再往下看。

---

## 043.py（关卡 3-8 · 检索质量评估）填空答案

### 填空 1（recall@k：命中率）

```python
hits = len(set(retrieved[:k]) & relevant)
return hits / len(relevant)
```

**关键理解**：recall 回答的是「该找的找到了没有」。`set(retrieved[:k]) & relevant` 是「检索前 k 个 ∩ 相关文档」——交集。分母是相关文档总数。召回率 = 命中数 / 该有的数。它不管排序，只要相关文档「进了前 k 名」就算命中。丢文档（该召回没召回）时 recall 会掉。

### 填空 2（NDCG@k：归一化折损累计增益）

```python
return dcg_val / idcg_val if idcg_val else 0.0
```

**关键理解**：NDCG 在 recall 的基础上多考虑「排序位置」——相关文档排第一和排第三，得分不一样（排越前折扣越小、贡献越大）。DCG 用 `rel / log2(排名+1)` 给靠后的位置打折，IDCG 是「理想情况（相关文档全排最前）」的 DCG，两者相除归一化到 0~1。`if idcg_val else 0.0` 是防除零：一个相关文档都没有时 IDCG=0，直接返回 0。recall 一样的两套结果，NDCG 能区分「排得对」和「排得乱」。

### 填空 3（MRR：平均倒数排名）

```python
scores.append(1 / (i + 1))
```

**关键理解**：MRR 只看「第一个相关文档出现在第几名」，取倒数（第一名=1，第二名=0.5，第三名=0.333…），再对所有查询求平均。`i` 是 0 起下标，排名是 `i+1`，所以倒数 `1 / (i+1)`。找到就 break，找不到走 `else` 记 0。它最适合「只需要一条正确答案」的场景（问答、搜索），不关心后面还有几条相关。

三个指标一句话总结：**recall 看「找全没有」，NDCG 看「排对没有」，MRR 看「第一条相关在哪」。**

---

## 044.py（关卡 3-9 · LangGraph 进阶）填空答案

### 填空 1（checkpoint 持久化）

```python
checkpointer = SqliteSaver.from_conn_string("checkpoints.sqlite")
```

**关键理解**：checkpoint 是 LangGraph 把「图执行到哪一步、状态是什么」落盘的能力。`SqliteSaver` 存到 sqlite 文件（进程退出还在），`MemorySaver` 只存内存（退进程就没）。`builder.compile(checkpointer=checkpointer)` 把 saver 挂上后，图的每一步都会自动存快照。为什么本关它和人审节点放一起？因为 **interrupt 必须依赖 checkpointer**——没有 checkpoint，图就不知道「暂停在哪、怎么恢复」。

### 填空 2（interrupt：人审暂停）

```python
decision = interrupt({
    "message": f"请审核：{state['content']}",
    "options": ["approve", "reject"],
})
```

**关键理解**：`interrupt(value)` 把 `value`（要人看的内容）抛给外界，然后**图挂起**，函数不返回、代码停在这一行。等外面恢复时，`interrupt` 的返回值 = 恢复时用 `Command(resume=...)` 传进来的值。这就是 human-in-the-loop（人在环路）的标准姿势：敏感操作（发信、扣款、删数据）不能全自动，跑到这一步停下等人拍板。

### 填空 3（Command(resume=...)：恢复执行）

```python
final = graph.invoke(Command(resume="approve"), config)
```

**关键理解**：`interrupt` 挂起后，用 `Command(resume="approve")` 把「人的决定」喂回图，`interrupt` 那行才会返回 `"approve"`，图从暂停点继续往下走到 END。注意 `config` 里的 `thread_id` 要和第一次调用一致——它标识「这是同一次会话」，让 LangGraph 知道从哪个 checkpoint 恢复。这就是「多轮、可断点续跑」的会话机制。

两个概念合起来讲：**checkpoint 是「记忆」（存状态），interrupt+resume 是「刹车和油门」（停和继续）。**

---

## 自检挑战

- [ ] 改 043.py 的 `retrieved` 顺序（如把 d2 从第 3 名挪到第 1 名），看 NDCG 变不变、recall 变不变，验证「NDCG 排序敏感、recall 不敏感」。
- [ ] 给 043.py 加一个「查询一个相关文档都没召回」的用例，看三个指标分别会不会崩（recall=0、NDCG 靠 if 防除零、MRR 靠 else 记 0）。
- [ ] 044.py 里把 `SqliteSaver` 换成 `MemorySaver`（`from langgraph.checkpoint.memory import MemorySaver`），重跑，对比「进程退出后 checkpoint 还在不在」。
- [ ] 044.py 里把 `Command(resume="reject")` 传进去，看 `approved` 变 False，体会「人的决定真正影响了图的分支结果」。
- [ ] 面试预演：一句话说清「checkpoint、interrupt、resume 三者是什么关系」——checkpoint 存状态，interrupt 暂停抛给人，resume 把人的决定喂回继续。
