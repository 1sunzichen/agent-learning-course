# Agent 学习课程与文件地图

本项目包含 60 节 Agent 课程打卡页、交互练习、Agent 小镇，以及按代码文件整理的学习地图。文件地图说明每个文件的目的、调用关系、设计取舍和适用场景。

## 启动网页

只需要 Python 3，无须安装课程中调用模型用到的依赖。

在项目根目录执行：

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

macOS / Linux 也可以使用一键脚本（从任何目录执行均可）：

```bash
./start.sh
```

Windows 可以在项目根目录执行：

```powershell
py -m http.server 8080 --bind 127.0.0.1
```

启动后打开：

- [课程打卡页](http://localhost:8080/agent-checkin.html?v=6)
- [文件学习地图](http://localhost:8080/060/001/file-guides/index.html)
- [Agent 小镇](http://localhost:8080/agent-town.html)

保持终端运行，按 `Ctrl+C` 停止。网页地址中的 `localhost` 指运行服务的这台电脑。GitHub 保存代码，不会自动运行这个本地服务器。

若 8080 端口被占用，可运行 `./start.sh 8081`，并把上述地址的端口改为 `8081`。

## 目录

| 路径 | 内容 |
| --- | --- |
| `agent-checkin.html` | 课程打卡与复习入口 |
| `agent-town*` | Agent 小镇及交互逻辑、测试 |
| `quiz-*.html` | 章节测验 |
| `060/` | Python / Go 课程练习 |
| `060/001/file-guides/index.html` | 可搜索的文件学习地图 |
| `060/001/file-guides/pages/` | 各文件的 HTML 说明 |
| `060/001/file-guides/graphs/` | SVG 调用图和 Graphviz 图源 |

文件编号并不等于课程序号。例如 `038_real.py` 对应 3-1，也就是全课程第 41 节；`review_phase2.md` 对应第 40 节。

## 运行课程代码

启动网页只提供静态文件，不会自动执行 Python / Go 练习。部分练习保留了待填位置，文件地图里的“当前代码状态”会指出已知缺口；能打开网页不表示练习已完成。

真实模型请求使用环境变量，不在仓库中保存密钥。例如先在自己的终端设置：

```bash
export DEEPSEEK_API_KEY='替换为你自己的密钥'
```

具体依赖与配置请查看各练习文件的说明。部分旧示例使用其他变量名或不同框架接口，应以相应文件为准。`.env.example` 仅作配置示例，练习不会自动加载 `.env`。

Go 练习通常是各自独立的 `package main`，请按文件运行，例如 `go run 029.go`，不要把整个练习目录当成单一 Go 包构建。

上传副本已移除本地虚拟环境、记忆数据库、编辑器缓存、截图和日志；`checkpoints.json` 只保留空的示例结构。

## 调用图说明

程序图来自源码静态分析，不是实际运行轨迹。虚线区分动态调用、回调引用或推断的方法目标。文档和 JSON 文件展示阅读或数据使用流程。

如需重新生成说明，需要 Python 3、Go 和 Graphviz，在项目根目录运行：

```bash
go run 060/001/file-guides/tools/inspect_go.go 060/001 > 060/001/file-guides/tools/go-analysis.json
python3 060/001/file-guides/tools/build_guides.py
```
