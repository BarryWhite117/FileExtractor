#!/bin/zsh
# 快捷启动 FileExtractor（双击即可运行）

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境（若存在）
if [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
fi

# 运行应用
python3 -m src.gui.main_window

read -r -p "\n程序已退出，按任意键关闭窗口..." _


