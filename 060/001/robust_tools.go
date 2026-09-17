package main

/*
关卡 1-8 · Go 版 · 工具设计进阶（对比 Python 版 robust_tools_real.py）

核心：四层防护 —— 重试 / 超时 / 幂等 / 降级

执行流程图（go run robust_tools.go）：

callWeather(北京)
  ① 幂等：查 map 缓存（加锁），命中直接返回
  ② 重试循环：
       context.WithTimeout 建带超时的 ctx
       http 请求用 NewRequestWithContext(ctx) —— 超时自动取消
       失败/超时 → 退避 → 重试
  ③ 降级：3 次都失败 → 返回兜底

Go 和 Python 最大的不同（超时）：
  Python：没有原生的「可取消函数调用」，得靠线程池 + Future + result(timeout)
  Go：context 原生支持取消 + 超时，http 请求天然吃 context，
      一个 WithTimeout 就搞定，不需要「协程池」

面试怎么讲（30 秒）：
  "Go 里做超时不靠协程池，靠 context。context.WithTimeout 建一个带截止时间的上下文，
  http.NewRequestWithContext 把请求绑上去，超时后请求自动被取消，Do 返回 DeadlineExceeded。"
*/

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

// 人为注入开关：0=纯真实；设成 0.7 则 70% 概率人为制造失败
const CHAOS = 0

// 真实天气接口（Open-Meteo 免费），超时靠 context
func getWeather(ctx context.Context, city string) (string, error) {
	if CHAOS > 0 && rand.Float64() < CHAOS {
		if rand.Float64() < 0.5 {
			return "", fmt.Errorf("人为注入：网络抖动")
		}
		return "", context.DeadlineExceeded // 人为注入：超时
	}

	url := "https://api.open-meteo.com/v1/forecast?latitude=39.9&longitude=116.4&current_weather=true"
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil) // 绑定 ctx，超时自动取消
	if err != nil {
		return "", err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return "", err // ctx 超时时，这里返回的 err 包裹了 context.DeadlineExceeded
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return "", fmt.Errorf("HTTP %d", resp.StatusCode)
	}
	var data struct {
		CurrentWeather struct {
			Temperature float64 `json:"temperature"`
			Windspeed   float64 `json:"windspeed"`
		} `json:"current_weather"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return "", err
	}
	w := data.CurrentWeather
	return fmt.Sprintf("%s 当前 %.1f°C，风速 %.1f km/h", city, w.Temperature, w.Windspeed), nil
}

// 幂等缓存：Go 的 map 不是并发安全的，要配一把锁（Python dict 靠 GIL 不用锁）
var (
	cacheMu sync.Mutex
	cache   = map[string]string{}
)

func callWeather(city string, maxRetry int, timeout time.Duration) string {
	// ① 幂等：查缓存
	cacheMu.Lock()
	if v, ok := cache[city]; ok {
		cacheMu.Unlock()
		return v + "（缓存）"
	}
	cacheMu.Unlock()

	// ② 重试 + 超时
	for attempt := 1; attempt <= maxRetry; attempt++ {
		ctx, cancel := context.WithTimeout(context.Background(), timeout)
		result, err := getWeather(ctx, city)
		cancel()

		if err == nil {
			cacheMu.Lock()
			cache[city] = result
			cacheMu.Unlock()
			return fmt.Sprintf("第 %d 次成功：%s", attempt, result)
		}
		// errors.Is 判断超时（真超时和人为注入的超时都算）
		if errors.Is(err, context.DeadlineExceeded) {
			fmt.Printf("  第 %d 次超时（>%v），重试...\n", attempt, timeout)
		} else {
			fmt.Printf("  第 %d 次失败（%v），重试...\n", attempt, err)
		}
		time.Sleep(time.Duration(attempt) * 500 * time.Millisecond) // 退避
	}

	// ③ 降级
	return fmt.Sprintf("%s 天气服务不可用，降级返回默认值", city)
}

func main() {
	fmt.Println("=== Go 版 · 四层防护天气工具 ===")
	fmt.Println("第 1 次查北京：", callWeather("北京", 3, 2*time.Second))
	fmt.Println("第 2 次查北京：", callWeather("北京", 3, 2*time.Second), " ← 应走缓存（幂等）")
}
