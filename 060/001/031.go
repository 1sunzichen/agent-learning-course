package main

/*
关卡 2-13 · Go 版 · 黑板模式 / 共享记忆（对比 Python 版 031.py）

核心：多个 agent 不直接通信，都往一块「黑板」上读写；谁看到缺什么就补什么，
逐步拼出完整答案。黑板 = 一个共享的 map。

执行流程（go run 031.go）：
  黑板(共享 map) → 天气agent写weather → 交通agent写traffic → 美食agent读weather写food
                → 顾问agent读全部拼最终建议

Go 和 Python 最大的不同：
  Python：黑板是 dict，直接 bb.write/bb.read 调用。
  Go：把 map 包进 struct，方法（write/read）挂在 struct 上，这是 Go 的「面向对象」写法
      ——没有 class，用「struct + 方法」代替。
  另一个坑（下面 main 里会讲）：Go 遍历 map 的顺序是随机的，不能像 Python 那样
  for k,v in bb.data.items() 按插入顺序打印，得自己维护顺序。
*/

import "fmt"

type Blackboard struct {
	data map[string]string
}

func NewBlackboard() *Blackboard {
	return &Blackboard{data: make(map[string]string)}
}

// write：把 value 写到黑板（以 key 为键）
func (b *Blackboard) write(key, value string) {
	b.data[key] = value
}

// read：读黑板上的 key。
// Go 里 map 读不存在的 key 返回零值（空字符串 ""），
// 正好对应 Python 的 .get(key) 返回 None——都是「读不到就给个空值」。
func (b *Blackboard) read(key string) string {
	return b.data[key]
}

func weatherAgent(bb *Blackboard) string {
	bb.write("weather", "晴 25度")
	return "天气agent：查到了天气，写进黑板"
}

func trafficAgent(bb *Blackboard) string {
	bb.write("traffic", "二环轻微拥堵")
	return "交通agent：查到了路况，写进黑板"
}

func foodAgent(bb *Blackboard) string {
	w := bb.read("weather")
	bb.write("food", "天气「"+w+"」，推荐清淡的淮扬菜")
	return "美食agent：读了天气，推荐了餐厅"
}

func advisorAgent(bb *Blackboard) string {
	w := bb.read("weather")
	t := bb.read("traffic")
	f := bb.read("food")
	bb.write("advice", "天气"+w+"，"+t+"，"+f+" → 建议轻装出行、避开二环")
	return "顾问agent：读了黑板全部结果，生成了最终建议"
}

func main() {
	bb := NewBlackboard()
	for _, a := range []func(*Blackboard) string{weatherAgent, trafficAgent, foodAgent, advisorAgent} {
		fmt.Println("  " + a(bb))
	}

	// 按固定顺序打印（Go map 遍历顺序随机，不能依赖插入顺序）
	fmt.Println("\n黑板最终内容：")
	for _, k := range []string{"weather", "traffic", "food", "advice"} {
		fmt.Printf("    %s: %s\n", k, bb.read(k))
	}

	fmt.Printf("\n最终建议：%s\n", bb.read("advice"))
	fmt.Println("\n（agent 之间不直接说话，全靠黑板协作）")
}
