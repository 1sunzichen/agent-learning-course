#!/usr/bin/env bash
# 用 060 目录下的 .venv 跑 Python 脚本（绕开 conda base / homebrew 的 python 干扰）
#
# 用法: ./run.sh memory_agent.py
#       ./run.sh tool_agent.py
#       ./run.sh rag_agent.py
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$DIR/.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "找不到虚拟环境: $PY" >&2
  echo "请确认 $DIR/.venv 存在" >&2
  exit 1
fi

exec "$PY" "$@"
