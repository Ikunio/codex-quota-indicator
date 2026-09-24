#!/usr/bin/env python3
"""Show read-only Codex quota snapshots in the GNOME app indicator area."""

from datetime import datetime
import fcntl
import os
from pathlib import Path
import threading

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3 as AppIndicator, GLib, Gtk

from quota import query


REFRESH_SECONDS = 300


def window_name(window, fallback, short=False):
    minutes = window.get("windowMinutes") if window else None
    if not isinstance(minutes, (int, float)) or minutes <= 0:
        return fallback
    if minutes % 1440 == 0:
        amount, unit = int(minutes // 1440), "d" if short else "天"
    elif minutes % 60 == 0:
        amount, unit = int(minutes // 60), "h" if short else "小时"
    else:
        amount, unit = int(minutes), "m" if short else "分钟"
    return f"{amount}{unit}" if short else f"{amount} {unit}"


def reset_time(timestamp):
    if not isinstance(timestamp, (int, float)):
        return "未知"
    return datetime.fromtimestamp(timestamp).strftime("%m-%d %H:%M")


def detail(name, window):
    if window is None:
        return f"{name}：暂无数据"
    return f"{name}：剩余 {window['remaining']}% · 重置 {reset_time(window['resetsAt'])}"


class QuotaIndicator:
    def __init__(self):
        self.indicator = AppIndicator.Indicator.new(
            "codex-quota-indicator",
            "utilities-system-monitor-symbolic",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.indicator.set_label("Codex …", "Codex 5h 100% · 7d 100%")

        menu = Gtk.Menu()
        self.primary_item = Gtk.MenuItem(label="5 小时：正在查询")
        self.primary_item.set_sensitive(False)
        menu.append(self.primary_item)
        self.secondary_item = Gtk.MenuItem(label="7 天：正在查询")
        self.secondary_item.set_sensitive(False)
        menu.append(self.secondary_item)
        self.status_item = Gtk.MenuItem(label="")
        self.status_item.set_sensitive(False)
        menu.append(self.status_item)
        menu.append(Gtk.SeparatorMenuItem())

        refresh_item = Gtk.MenuItem(label="立即刷新")
        refresh_item.connect("activate", lambda *_: self.refresh())
        menu.append(refresh_item)
        quit_item = Gtk.MenuItem(label="退出额度显示")
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)
        menu.show_all()
        self.indicator.set_menu(menu)

        self.busy = False
        self.refresh()
        GLib.timeout_add_seconds(REFRESH_SECONDS, self.refresh)

    def refresh(self):
        if self.busy:
            return True
        self.busy = True
        threading.Thread(target=self._fetch, daemon=True).start()
        return True

    def _fetch(self):
        try:
            result = query()
            GLib.idle_add(self._show, result)
        except Exception as exc:
            GLib.idle_add(self._show_error, str(exc))

    def _show(self, result):
        primary = result.get("primary")
        secondary = result.get("secondary")
        self.primary_item.set_label(detail(window_name(primary, "主额度"), primary))
        self.secondary_item.set_label(detail(window_name(secondary, "次额度"), secondary))
        self.status_item.set_label(f"更新于 {reset_time(result.get('checkedAt'))}")
        parts = []
        if primary:
            parts.append(f"{window_name(primary, '主', short=True)} {primary['remaining']}%")
        if secondary:
            parts.append(f"{window_name(secondary, '次', short=True)} {secondary['remaining']}%")
        self.indicator.set_label(
            f"Codex {' · '.join(parts)}" if parts else "Codex —",
            "Codex 5h 100% · 7d 100%",
        )
        self.busy = False
        return False

    def _show_error(self, message):
        self.indicator.set_label("Codex —", "Codex 5h 100% · 7d 100%")
        self.status_item.set_label(f"查询失败：{message}")
        self.busy = False
        return False

    def quit(self, *_):
        self.indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
        Gtk.main_quit()


def main():
    runtime = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
    lock_path = runtime / "codex-quota-indicator.lock"
    with lock_path.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        app = QuotaIndicator()
        Gtk.main()
        del app


if __name__ == "__main__":
    main()
