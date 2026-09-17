#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-8080}"
if ! [[ "$PORT" =~ ^[0-9]{1,5}$ ]] || ((10#$PORT < 1 || 10#$PORT > 65535)); then
  echo '端口必须是 1–65535 的整数。' >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo '请先安装 Python 3。' >&2
  exit 1
fi
cd "$PROJECT_DIR"
echo "课程：http://localhost:$PORT/agent-checkin.html?v=6"
echo "文件地图：http://localhost:$PORT/060/001/file-guides/index.html"
echo '按 Ctrl+C 停止服务。'
exec python3 -m http.server "$PORT" --bind 127.0.0.1
