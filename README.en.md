# Codex Quota Indicator

**Chinese name:** Codex 状态栏额度显示器

Show the remaining Codex quota percentages in the top-right GNOME indicator area. The menu shows reset times and provides a manual refresh action. The indicator refreshes every five minutes.

It calls the read-only `account/rateLimits/read` method through the locally installed Codex CLI. It does not start a conversation or send a prompt to a model. The percentages describe remaining quota in each time window, not an absolute token balance. See the [Codex app-server documentation](https://learn.chatgpt.com/docs/app-server).

## Requirements

Tested on Ubuntu 24.04, GNOME 46, and X11. You need a Codex CLI installation signed in with a **ChatGPT account**. API-key-only authentication does not return this ChatGPT quota data. Other Linux desktop environments are untested.

Install the Ubuntu packages:

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 \
  gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator git
```

If you just installed the GNOME AppIndicator extension, enable it in the Extensions app, then sign out and back in. Do not restart GNOME Shell with `gnome-shell --replace` for this tool.

Install and sign in to Codex CLI using the [official Codex CLI guide](https://learn.chatgpt.com/docs/codex/cli). Choose **Sign in with ChatGPT**.

## Install

```bash
git clone https://github.com/Ikunio/codex-quota-indicator.git
cd codex-quota-indicator
./install.sh
```

The installer copies the Python scripts and the discovered Codex CLI path to `~/.local/share/codex-quota-indicator/`, creates an XDG autostart entry, and tries to start the indicator immediately. It will launch automatically at the next GNOME login.

Verify the read-only query with `python3 quota.py`. A working response contains `"ok": true` and `remaining` percentages. If the indicator is missing, check that AppIndicator support is enabled and sign out and back in.

## Update and remove

Run `git pull && ./install.sh` to update. To remove it, choose **Quit** from the indicator menu, then run `./uninstall.sh`.

## Privacy and license

The app uses the Codex CLI's existing login state. It does not copy your authentication file or store credentials. Licensed under [MIT](LICENSE).
