package main

/*
关卡 2-12 · Go 版 · 消息路由与事件总线（对比 Python 版 030.py）

核心：发布/订阅（pub/sub）——发布者发消息，总线只投递给「订阅了该主题」的订阅者，
没人订阅的主题一个都不投（不串台）。

执行流程（go run 030.go）：
  发布者 publish(topic, msg) → 总线按 topic 查订阅者 → 只投递给订阅该 topic 的 agent

Go 和 Python 最大的不同（重点，面试常问）：
  Python：EventBus 里 self._subs = {} 就是普通 dict，单线程下随便读写，因为 GIL 兜底。
  Go：map 不是并发安全的！多个 goroutine 同时读写同一个 map 会直接 panic（fatal error）。
       所以 Go 里给 map 配一把 sync.Mutex 锁，读写都先加锁。
       这是 Go 和 Python「并发心智」最大的区别：Python 靠 GIL，Go 靠显式加锁。
  （本演示是单线程，锁只是为了演示「正确写法」，让你养成习惯。）
*/

import (
	"fmt"
	"sync"
)

// EventBus：按 topic 把消息路由给订阅者
type EventBus struct {
	mu   sync.Mutex                  // 保护 subs 的锁（map 并发安全靠它）
	subs map[string][]func(string)   // topic -> [handler, ...]
}

func NewEventBus() *EventBus {
	return &EventBus{subs: make(map[string][]func(string))}
}

// subscribe：把 handler 登记到该 topic 的订阅者列表（topic 首次出现时自动建空切片）
func (b *EventBus) subscribe(topic string, handler func(string)) {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.subs[topic] = append(b.subs[topic], handler)
}

// publish：只把消息投递给「订阅了该 topic」的 handler；没人订阅就不投（不串台）
func (b *EventBus) publish(topic, message string) {
	b.mu.Lock()
	handlers := b.subs[topic] // 拿到该 topic 的订阅者（没人订阅就是 nil，循环直接跳过）
	b.mu.Unlock()
	for _, h := range handlers {
		h(message)
	}
}

// 三个订阅者：各自只关心自己的 topic
func weatherAgent(msg string) { fmt.Printf("    [天气agent] 收到：%s\n", msg) }
func newsAgent(msg string)    { fmt.Printf("    [新闻agent] 收到：%s\n", msg) }
func stockAgent(msg string)   { fmt.Printf("    [股票agent] 收到：%s\n", msg) }

func main() {
	bus := NewEventBus()
	// 三个 agent 各自订阅自己的 topic
	bus.subscribe("weather", weatherAgent)
	bus.subscribe("news", newsAgent)
	bus.subscribe("stock", stockAgent)

	fmt.Println("发布 weather 消息「北京明天晴」：")
	bus.publish("weather", "北京明天晴")
	fmt.Println("发布 news 消息「AI 大会开幕」：")
	bus.publish("news", "AI 大会开幕")
	fmt.Println("发布 stock 消息「某股大涨」：")
	bus.publish("stock", "某股大涨")
	fmt.Println("发布 sport 消息「足球比赛结果」（没人订阅）：")
	bus.publish("sport", "足球比赛结果")

	fmt.Println("\n（sport 消息没人订阅，所以没有任何 agent 收到——这就是路由不串台）")
}
