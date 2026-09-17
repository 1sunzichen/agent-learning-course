package main

/*
关卡 3-8 · Go 版 · 检索质量评估（对比 Python 版 043.py）

核心：用 recall@k / NDCG@k / MRR 三个指标，把「检索好不好」从感觉变成数字。

执行流程（go run 043.go）：
  ① 构造小数据集：3 个查询，每个带「相关文档集合」+「检索返回列表」
  ② 逐个指标计算：recall_at_k（召回率）/ ndcg_at_k（排序位置）/ mrr（第一个相关文档排名）
  ③ 打印每个查询的 recall/ndcg + 三个查询的平均 MRR

三个指标一句话总结：
  recall 看「找全没有」，NDCG 看「排对没有」，MRR 看「第一条相关在哪」。

Go 和 Python 最大的不同：
  Python 的 relevant 是 set，`d in relevant` O(1)；Go 用 map[string]bool 等价。
  Python 的 sorted(rels, reverse=True) 对应 Go 的 sort.Float64s + 手动翻转。
  Python 的 for...else 在 Go 里没有，mrr 用 found 布尔标志替代。
*/

import (
	"fmt"
	"math"
	"sort"
)

// queryCase：每个查询的评测数据
type queryCase struct {
	query     string
	relevant  map[string]bool
	retrieved []string
}

var queries = []queryCase{
	{"向量数据库选型", map[string]bool{"d1": true, "d2": true, "d3": true}, []string{"d1", "d5", "d2"}},
	{"embedding 中文模型", map[string]bool{"d2": true, "d4": true}, []string{"d9", "d2", "d4"}},
	{"LangGraph 人审", map[string]bool{"d7": true}, []string{"d3", "d7", "d1"}},
}

// recallAtK：召回率@k = 前 k 个命中的相关文档数 / 相关文档总数
func recallAtK(relevant map[string]bool, retrieved []string, k int) float64 {
	hits := 0
	for i, d := range retrieved {
		if i >= k {
			break
		}
		if relevant[d] {
			hits++
		}
	}
	return float64(hits) / float64(len(relevant))
}

// ndcgAtK：NDCG@k = DCG / IDCG（考虑排序位置，位置越靠前折扣越小、贡献越大）
func ndcgAtK(relevant map[string]bool, retrieved []string, k int) float64 {
	dcg := func(rels []float64) float64 {
		sum := 0.0
		for i, rel := range rels {
			sum += rel / math.Log2(float64(i+2)) // 位置 i（0 起）对应排名 i+1，折扣 1/log2(i+2)
		}
		return sum
	}

	rels := []float64{}
	for i, d := range retrieved {
		if i >= k {
			break
		}
		if relevant[d] {
			rels = append(rels, 1.0)
		} else {
			rels = append(rels, 0.0)
		}
	}
	ideal := append([]float64(nil), rels...)
	sort.Float64s(ideal)
	for i, j := 0, len(ideal)-1; i < j; i, j = i+1, j-1 { // 翻转成降序（相关文档全排最前）
		ideal[i], ideal[j] = ideal[j], ideal[i]
	}

	dcgVal := dcg(rels)
	idcgVal := dcg(ideal)
	if idcgVal == 0 { // 一个相关都没有，避免除零
		return 0.0
	}
	return dcgVal / idcgVal
}

// mrr：每个查询「第一个相关文档」出现在第几名，取倒数后求平均
func mrr(pairs []queryCase) float64 {
	scores := []float64{}
	for _, p := range pairs {
		found := false
		for i, d := range p.retrieved {
			if p.relevant[d] {
				scores = append(scores, 1.0/float64(i+1)) // 排名从 1 起，倒数 1/rank
				found = true
				break
			}
		}
		if !found {
			scores = append(scores, 0.0)
		}
	}
	sum := 0.0
	for _, s := range scores {
		sum += s
	}
	return sum / float64(len(scores))
}

func main() {
	fmt.Println("=======================================================")
	fmt.Println("  检索质量评估：recall@k / NDCG@k / MRR")
	fmt.Println("=======================================================")

	for _, q := range queries {
		rel, ret := q.relevant, q.retrieved
		fmt.Printf("\n查询「%s」\n", q.query)
		fmt.Printf("  相关文档: %v   检索结果: %v\n", sortedKeys(rel), ret)
		fmt.Printf("  recall@3 = %.3f\n", recallAtK(rel, ret, 3))
		fmt.Printf("  ndcg@3   = %.3f\n", ndcgAtK(rel, ret, 3))
	}

	fmt.Printf("\nMRR（3 个查询平均）= %.3f\n", mrr(queries))
	fmt.Println("\n✅ 三个指标都算出来了：recall 看「找没找全」，NDCG 看「排没排对」，MRR 看「第一条相关在哪」。")
}

// sortedKeys：把 relevant 的键排序返回（对应 Python 的 sorted(rel)）
func sortedKeys(m map[string]bool) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}
