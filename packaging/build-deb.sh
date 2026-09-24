#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
version="0.2.0-1"
package="codex-quota-indicator"
output_dir="${1:-$repo_dir/dist}"
build_dir="$(mktemp -d)"
trap 'rm -rf -- "$build_dir"' EXIT

mkdir -p -- "$output_dir" \
    "$build_dir/DEBIAN" \
    "$build_dir/usr/bin" \
    "$build_dir/usr/lib/$package" \
    "$build_dir/usr/share/doc/$package" \
    "$build_dir/etc/xdg/autostart"

cat > "$build_dir/DEBIAN/control" <<EOF
Package: $package
Version: $version
Section: utils
Priority: optional
Architecture: all
Maintainer: Ikunio <Ikunio@users.noreply.github.com>
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-ayatanaappindicator3-0.1, gnome-shell-extension-appindicator
Homepage: https://github.com/Ikunio/codex-quota-indicator
Description: Show remaining Codex quota in the GNOME top bar
 Read Codex quota through the local Codex CLI without sending model prompts.
 Launch automatically at GNOME login and refresh every five minutes.
EOF

install -m 755 "$repo_dir/packaging/postinst" "$build_dir/DEBIAN/postinst"
install -m 755 "$repo_dir/packaging/prerm" "$build_dir/DEBIAN/prerm"
install -m 644 "$repo_dir/indicator.py" "$repo_dir/quota.py" "$build_dir/usr/lib/$package/"
install -m 644 "$repo_dir/README.md" "$repo_dir/README.en.md" "$build_dir/usr/share/doc/$package/"
install -m 644 "$repo_dir/LICENSE" "$build_dir/usr/share/doc/$package/copyright"

cat > "$build_dir/usr/bin/$package" <<'EOF'
#!/bin/sh
exec /usr/bin/python3 /usr/lib/codex-quota-indicator/indicator.py "$@"
EOF
chmod 755 "$build_dir/usr/bin/$package"

cat > "$build_dir/etc/xdg/autostart/$package.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Codex Quota Indicator
Name[zh_CN]=Codex 状态栏额度显示器
Comment=Show remaining Codex quota in the GNOME top bar
Exec=/usr/bin/codex-quota-indicator
Icon=utilities-system-monitor-symbolic
Terminal=false
OnlyShowIn=GNOME;
X-GNOME-Autostart-enabled=true
EOF
chmod 644 "$build_dir/etc/xdg/autostart/$package.desktop"

find "$build_dir" -type d -exec chmod 755 {} +
dpkg-deb --root-owner-group --build "$build_dir" \
    "$output_dir/${package}_${version}_all.deb"
