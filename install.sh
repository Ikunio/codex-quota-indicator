#!/usr/bin/env bash
set -euo pipefail

source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
data_home="${XDG_DATA_HOME:-$HOME/.local/share}"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
install_dir="$data_home/codex-quota-indicator"
autostart_dir="$config_home/autostart"
autostart_file="$autostart_dir/codex-quota-indicator.desktop"

if [[ "$(id -u)" -eq 0 ]]; then
    echo "请以普通桌面用户运行 ./install.sh，不要使用 sudo。" >&2
    exit 1
fi

if [[ "$install_dir" == *\"* ]]; then
    echo "安装路径含双引号，无法安全写入桌面自启动文件。" >&2
    exit 1
fi

if ! /usr/bin/python3 - <<'PY'
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3, Gtk
PY
then
    echo "缺少 GTK/Ayatana 依赖。请按 README 安装 Ubuntu 软件包后重试。" >&2
    exit 1
fi

if [[ -x "$HOME/.local/bin/codex" ]]; then
    codex_binary="$HOME/.local/bin/codex"
elif command -v codex >/dev/null 2>&1; then
    codex_binary="$(command -v codex)"
else
    echo "未找到 Codex CLI。请先按 README 安装并用 ChatGPT 账号登录。" >&2
    exit 1
fi

mkdir -p -- "$install_dir" "$autostart_dir"
install -m 644 "$source_dir/indicator.py" "$source_dir/quota.py" "$install_dir/"
printf '%s\n' "$codex_binary" > "$install_dir/codex-path"
chmod 644 "$install_dir/codex-path"
cat > "$autostart_file" <<EOF
[Desktop Entry]
Type=Application
Name=Codex Quota Indicator
Comment=Show remaining Codex quota in the GNOME top bar
Exec=/usr/bin/python3 "$install_dir/indicator.py"
Icon=utilities-system-monitor-symbolic
Terminal=false
OnlyShowIn=GNOME;
X-GNOME-Autostart-enabled=true
EOF
chmod 644 "$autostart_file"

echo "已安装到：$install_dir"
echo "登录自启动：$autostart_file"

if [[ "${SHOW_CODEX_USAGE_NO_START:-0}" == "1" ]]; then
    exit 0
fi

if command -v systemd-run >/dev/null 2>&1 && [[ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]]; then
    systemctl --user stop codex-quota-indicator.service >/dev/null 2>&1 || true
    if systemd-run --user --unit=codex-quota-indicator --collect \
        --property=Restart=on-failure /usr/bin/python3 "$install_dir/indicator.py"; then
        echo "托盘程序已启动。"
        exit 0
    fi
fi

echo "当前桌面未能立即启动托盘程序；下次登录 GNOME 时会自动启动。"
