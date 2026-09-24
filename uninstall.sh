#!/usr/bin/env bash
set -euo pipefail

data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
install_dir="$data_home/codex-quota-indicator"
autostart_file="$config_home/autostart/codex-quota-indicator.desktop"

systemctl --user stop codex-quota-indicator.service >/dev/null 2>&1 || true
rm -f -- "$autostart_file"
rm -f -- "$install_dir/indicator.py" "$install_dir/quota.py" "$install_dir/codex-path"
rm -f -- "$install_dir/__pycache__/indicator."*.pyc "$install_dir/__pycache__/quota."*.pyc
rmdir -- "$install_dir/__pycache__" 2>/dev/null || true
rmdir -- "$install_dir" 2>/dev/null || true
echo "已移除安装文件。若顶栏仍显示，请在其菜单选择退出额度显示。"
