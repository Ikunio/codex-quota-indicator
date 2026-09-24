# Codex Quota Indicator

**中文名：Codex 状态栏额度显示器**

在 Ubuntu GNOME 桌面右上角显示 Codex 当前额度窗口的剩余百分比，例如 `Codex 5h 80% · 7d 65%`。点击状态栏条目可查看各窗口的重置时间、手动刷新或退出。程序每 5 分钟自动刷新。

本工具只调用 Codex CLI 的只读 `account/rateLimits/read` 方法，不创建对话、不向模型发送提示词，因此刷新本身不会消耗 Codex 模型额度。显示的是**配额窗口剩余百分比**，不是可用 token 的绝对数量。[Codex app-server 文档](https://learn.chatgpt.com/docs/app-server)

## 支持范围

- 已在 **Ubuntu 24.04、GNOME 46、X11** 上验证。
- 依赖 Python 3、GTK 3、Ayatana AppIndicator 以及 GNOME 的 AppIndicator 扩展。其他发行版或桌面环境尚未验证。
- 需要已安装 Codex CLI，并使用 **ChatGPT 账号**登录。仅使用 OpenAI API key 的 Codex 登录方式不提供此处的 ChatGPT 额度数据。[官方接口说明](https://learn.chatgpt.com/docs/app-server)

## 新电脑部署操作手册

### 1. 安装系统依赖

在 Ubuntu 24.04 的终端执行：

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 \
  gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator git
```

Ubuntu Desktop 通常已提供 AppIndicator 支持。如果是新安装的 GNOME 扩展，请在“扩展”应用里确认它已启用，然后退出并重新登录桌面会话。**不要为了本工具运行 `gnome-shell --replace`。**

### 2. 安装并登录 Codex CLI

按 [OpenAI 官方 Codex CLI 指南](https://learn.chatgpt.com/docs/codex/cli)安装 CLI。当前官方 Linux 安装命令为：

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

运行 `codex`，按界面提示选择 **Sign in with ChatGPT** 并完成登录。检查命令是否可用：

```bash
codex --version
```

CLI 可能随时间更新，请以上述官方指南为准。安装脚本会记录当前 CLI 的路径，让桌面自启动也能找到它。如果你移动了 CLI，重新运行 `./install.sh`；临时运行查询脚本时也可设置 `CODEX_BIN=/绝对路径/codex`。

### 3. 下载并安装本工具

```bash
git clone https://github.com/Ikunio/codex-quota-indicator.git
cd codex-quota-indicator
./install.sh
```

安装程序只复制本工具的两个 Python 文件和 CLI 路径记录到 `~/.local/share/codex-quota-indicator/`，并创建 `~/.config/autostart/codex-quota-indicator.desktop`。它会尝试立即启动托盘程序；今后每次登录 GNOME 也会自动启动。**无需重载 GNOME Shell。**

### 4. 验证

先检查只读额度查询：

```bash
python3 quota.py
```

正常结果包含 `"ok": true` 和 `primary` / `secondary` 的 `remaining` 百分比。然后查看桌面右上角是否出现 `Codex …`。点击条目可看到重置时间和“立即刷新”。

安装后若未立即出现，先确认 AppIndicator 扩展已启用，再退出并重新登录 GNOME。可以运行以下命令检查托盘程序：

```bash
systemctl --user status codex-quota-indicator.service
```

这条状态命令只用于检查当前会话的即时启动；登录自启动由 `.desktop` 文件负责。

## 常见问题

**显示 `Codex —`：** 点击状态栏条目查看错误信息，运行 `python3 quota.py` 复查。确认 Codex CLI 已用 ChatGPT 登录、网络可用，并且 CLI 版本支持 `codex app-server`。API key 登录模式无法提供此额度。

**顶栏没有条目：** 确认 `gir1.2-ayatanaappindicator3-0.1` 和 AppIndicator 扩展已安装、已启用；新装扩展后正常退出并重新登录桌面。不需要手动重启 GNOME Shell。

**额度百分比看起来没变化：** 自动刷新间隔为 5 分钟，可点击“立即刷新”。额度数据由 Codex 服务返回；本工具不会自行估算 token 数。

**不想自启动：** 删除 `~/.config/autostart/codex-quota-indicator.desktop`，然后在状态栏菜单选择“退出额度显示”。

## 更新与卸载

更新时进入克隆目录，执行 `git pull` 和 `./install.sh`。卸载时先在状态栏菜单选择“退出额度显示”，然后执行：

```bash
./uninstall.sh
```

## 隐私与实现

程序通过本机 Codex CLI 向官方 Codex 服务读取额度数据，使用当前用户已有的 Codex 登录状态；不会读取、复制或上传 `~/.codex/auth.json`，也不会保存凭据或完整服务器响应。只有剩余百分比、窗口时长和重置时间会显示在本机状态栏。公开仓库不包含本机凭据。

实现文件：`indicator.py` 负责 GNOME 状态栏和菜单，`quota.py` 负责通过 app-server 读取额度，`install.sh` 与 `uninstall.sh` 负责用户级部署。

## 开源许可

MIT License，详见 [LICENSE](LICENSE)。
