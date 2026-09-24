#!/usr/bin/env python3
"""Read Codex rate limits through the local app-server, without starting a turn."""

import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import time


TIMEOUT_SECONDS = 20


def codex_binary():
    configured = os.environ.get("CODEX_BIN")
    if configured:
        return configured
    installed_path = Path(__file__).resolve().parent / "codex-path"
    if installed_path.is_file():
        candidate = Path(installed_path.read_text().strip())
        if candidate.is_file():
            return str(candidate)
    local = Path.home() / ".local/bin/codex"
    if local.is_file():
        return str(local)
    return shutil.which("codex")


def send(process, message):
    process.stdin.write((json.dumps(message, separators=(",", ":")) + "\n").encode())
    process.stdin.flush()


def read_message(process, selector, pending, deadline):
    while time.monotonic() < deadline:
        if b"\n" in pending:
            line, _, rest = pending.partition(b"\n")
            pending = bytearray(rest)
            try:
                return json.loads(line), pending
            except json.JSONDecodeError:
                continue
        events = selector.select(max(0, deadline - time.monotonic()))
        if not events:
            break
        chunk = os.read(process.stdout.fileno(), 65536)
        if not chunk:
            raise RuntimeError("Codex 服务已关闭")
        pending.extend(chunk)
    raise TimeoutError("查询超时")


def await_response(process, selector, pending, request_id, deadline):
    while True:
        message, pending = read_message(process, selector, pending, deadline)
        if message.get("id") == request_id:
            if "error" in message:
                raise RuntimeError("Codex 服务返回错误")
            return message.get("result") or {}, pending


def window(snapshot):
    if not isinstance(snapshot, dict):
        return None
    used = snapshot.get("usedPercent")
    if not isinstance(used, (int, float)) or isinstance(used, bool):
        return None
    return {
        "remaining": round(max(0, min(100, 100 - used))),
        "windowMinutes": snapshot.get("windowDurationMins"),
        "resetsAt": snapshot.get("resetsAt"),
    }


def query():
    binary = codex_binary()
    if not binary:
        raise RuntimeError("未找到 Codex CLI")
    process = subprocess.Popen(
        [binary, "app-server", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0,
    )
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    pending = bytearray()
    deadline = time.monotonic() + TIMEOUT_SECONDS
    try:
        send(process, {
            "id": 1,
            "method": "initialize",
            "params": {"clientInfo": {
                "name": "codex_gnome_quota",
                "title": "Codex GNOME Quota",
                "version": "1.0.0",
            }},
        })
        _, pending = await_response(process, selector, pending, 1, deadline)
        send(process, {"method": "initialized"})
        send(process, {"id": 2, "method": "account/rateLimits/read"})
        result, _ = await_response(process, selector, pending, 2, deadline)
        limits = (result.get("rateLimitsByLimitId") or {}).get("codex") or result.get("rateLimits") or {}
        if not isinstance(limits, dict) or not (limits.get("primary") or limits.get("secondary")):
            raise RuntimeError("未返回 Codex 额度；请确认已用 ChatGPT 账号登录 Codex")
        return {
            "ok": True,
            "primary": window(limits.get("primary")),
            "secondary": window(limits.get("secondary")),
            "checkedAt": int(time.time()),
        }
    finally:
        selector.close()
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == "__main__":
    try:
        print(json.dumps(query(), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
