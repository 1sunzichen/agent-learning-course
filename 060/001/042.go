package main

/*
关卡 3-5 · Go 版 · RAG 进阶（对比 Python 版 042.py）

核心：三个进阶技巧——chunking（切块）、混合检索（dense 向量 + sparse BM25）、
rerank（重排），并对比效果。

执行流程（go run 042.go）：
  长文档 → chunking 切块 → 对每块建索引（dense 字符 bigram 余弦 + sparse 简化 BM25）
         → 查询：dense 分 + sparse 分加权融合（混合检索）
         → rerank：对 top-k 精排（本文件用本地版，见下）
         → 对比打印 dense-only vs hybrid vs hybrid+rerank 的命中顺序

三个核心概念（面试 30 秒）：
  1. chunking：文档太长会「稀释」语义，切成小块（带重叠防切断），检索命中更精准
  2. 混合检索 = dense（语义相近）+ sparse（关键词命中），互补：dense 懂意思，sparse 不漏专有名词
  3. rerank：粗召回后对 top-k 精排，把最相关的顶上去

Go 和 Python 最大的不同：
  Python 的 rerank 用 LLM 打分（rerank_with_llm），没 key 就退回 rerank_local（用混合分重排）；
  Go 这里直接采用「本地版」——rerank 用 hybrid_score 对 top-3 重排，不真调 LLM。
  Python 的 Counter / set 在 Go 里换成 map[string]int / map[string]bool。
  Python 的 s[i:i+2] 按字符切片，Go 的中文要转 []rune 再切片，否则字节会拦腰切断。
*/

import (
	"fmt"
	"math"
	"regexp"
	"sort"
)

// 长文档（关键句故意把「混合检索」和「重排序」放一起，方便验证 rerank 能顶到最前）
var doc = "" +
	"RAG 即检索增强生成，先检索相关文档再让 LLM 生成答案，能解决幻觉和知识过时问题。" +
	"Embedding 把文本映射成高维向量，语义相近的文本向量方向接近。" +
	"向量数据库如 Chroma、Milvus、pgvector 专门存储和检索高维向量。" +
	"混合检索把稠密向量检索和稀疏关键词检索结合，再配合重排序 rerank 精排，召得更准更全。" +
	"分块 chunking 把长文档切成小块，带重叠防止切断语义。"

// chunk：按固定窗口切块，块与块之间保留重叠（步长 = 窗口 - 重叠）
func chunk(text string, size, overlap int) []string {
	runes := []rune(text)
	step := size - overlap
	var chunks []string
	for i := 0; i < len(runes); i += step {
		end := i + size
		if end > len(runes) {
			end = len(runes)
		}
		chunks = append(chunks, string(runes[i:end]))
	}
	return chunks
}

var chunks = chunk(doc, 30, 8)

var spaceRe = regexp.MustCompile(`\s+`)
var tokenRe = regexp.MustCompile(`[\p{Han}]|[a-zA-Z]+`)

// bigrams：字符 bigram（去空白后，相邻两字符一组）
func bigrams(s string) []string {
	r := []rune(spaceRe.ReplaceAllString(s, ""))
	var out []string
	for i := 0; i+1 < len(r); i++ {
		out = append(out, string(r[i:i+2]))
	}
	return out
}

// vec：文本 → bigram 词频向量
func vec(text string) map[string]int {
	v := map[string]int{}
	for _, b := range bigrams(text) {
		v[b]++
	}
	return v
}

// cosine：余弦相似度 = 点积 / (|a| * |b|)
func cosine(a, b map[string]int) float64 {
	if len(a) == 0 || len(b) == 0 {
		return 0.0
	}
	dot := 0.0
	for w := range a {
		if _, ok := b[w]; ok {
			dot += float64(a[w] * b[w])
		}
	}
	na := 0.0
	for _, v := range a {
		na += float64(v * v)
	}
	nb := 0.0
	for _, v := range b {
		nb += float64(v * v)
	}
	if na == 0 || nb == 0 {
		return 0.0
	}
	return dot / (math.Sqrt(na) * math.Sqrt(nb))
}

// tokenize：中文单字 / 英文单词（简化分词）
func tokenize(s string) []string {
	return tokenRe.FindAllString(s, -1)
}

// idf：每个词出现在多少个 chunk 里
var idf = func() map[string]int {
	m := map[string]int{}
	for _, c := range chunks {
		seen := map[string]bool{}
		for _, term := range tokenize(c) {
			if !seen[term] {
				m[term]++
				seen[term] = true
			}
		}
	}
	return m
}()

var nChunks = len(chunks)

// bm25Score：简化 BM25（词频 + 逆文档频率）
func bm25Score(query, chunkText string) float64 {
	score := 0.0
	cterms := tokenize(chunkText)
	count := func(term string) int {
		n := 0
		for _, t := range cterms {
			if t == term {
				n++
			}
		}
		return n
	}
	for _, t := range tokenize(query) {
		tf := count(t)
		if tf == 0 {
			continue
		}
		idfVal := math.Log((float64(nChunks)-float64(idf[t])+0.5)/(float64(idf[t])+0.5) + 1)
		score += idfVal * float64(tf)
	}
	return score
}

// hybridScore：dense + sparse 加权融合
func hybridScore(query, chunkText string, alpha float64) float64 {
	d := cosine(vec(query), vec(chunkText))
	s := bm25Score(query, chunkText)
	return alpha*d + (1-alpha)*s
}

// rankChunks：按分数降序返回 chunk 下标（对应 Python 的 sorted + CHUNKS.index）
func rankChunks(query string, scorer func(string, string) float64) []int {
	type scored struct {
		idx   int
		score float64
	}
	var list []scored
	for i, c := range chunks {
		list = append(list, scored{i, scorer(query, c)})
	}
	sort.Slice(list, func(a, b int) bool { return list[a].score > list[b].score })
	out := make([]int, len(list))
	for i, s := range list {
		out[i] = s.idx
	}
	return out
}

func main() {
	query := "混合检索和重排序是什么"
	fmt.Println("=======================================================")
	fmt.Println("  RAG 进阶：chunking / 混合检索 / rerank 对比")
	fmt.Println("=======================================================")
	fmt.Printf("\n长文档切成 %d 块（窗口 30，重叠 8）：\n", len(chunks))
	for i, c := range chunks {
		fmt.Printf("  [%d] %s\n", i, c)
	}

	// ① dense-only：只按向量余弦
	denseOnly := rankChunks(query, func(q, c string) float64 { return cosine(vec(q), vec(c)) })
	fmt.Printf("\n① dense-only 命中顺序：%v\n", firstN(denseOnly, 3))

	// ② hybrid：dense + sparse 融合
	hybrid := rankChunks(query, func(q, c string) float64 { return hybridScore(q, c, 0.5) })
	fmt.Printf("② hybrid 命中顺序：   %v\n", firstN(hybrid, 3))

	// ③ hybrid + rerank：对 top-3 精排（本地版用 hybrid_score，真系统用 LLM/交叉编码器）
	top3 := append([]int(nil), hybrid[:3]...)
	sort.SliceStable(top3, func(a, b int) bool {
		return hybridScore(query, chunks[top3[a]], 0.5) > hybridScore(query, chunks[top3[b]], 0.5)
	})
	fmt.Printf("③ hybrid+rerank 顺序：%v\n", top3)

	fmt.Println("\n（人工看：正确答案是覆盖「混合检索」和「重排序 rerank」的块，应该排到最前；")
	fmt.Println("这也正好演示了为什么要「带重叠」切块，避免关键词被拦腰切断）")
}

func firstN(xs []int, n int) []int {
	if len(xs) <= n {
		return xs
	}
	return xs[:n]
}
