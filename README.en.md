# Codex Quota Indicator

**Chinese name:** Codex 状态栏额度显示器

Show remaining Codex quota percentages in the top-right GNOME indicator area. The menu shows reset times and provides a manual refresh action. The indicator refreshes every five minutes.

It calls the read-only `account/rateLimits/read` method through the locally installed Codex CLI. It does not start a conversation or send a prompt to a model. The percentages describe remaining quota in each time window, not an absolute token balance. See the [Codex app-server documentation](https://learn.chatgpt.com/docs/app-server).

## Requirements

Tested on Ubuntu 24.04, GNOME 46, and X11. You need a Codex CLI installation signed in with a **ChatGPT account**. API-key-only authentication does not return this ChatGPT quota data. Other Linux desktop environments are untested.

Install and sign in to Codex CLI using the [official Codex CLI guide](https://learn.chatgpt.com/docs/codex/cli). Choose **Sign in with ChatGPT**. The indicator finds the CLI at `~/.local/bin/codex` or on `PATH`; for other locations, set `CODEX_BIN` in its launch environment.

## Install from a release

Download `codex-quota-indicator_0.2.0-1_all.deb` from [GitHub Releases](https://github.com/Ikunio/codex-quota-indicator/releases/latest), then run from the download directory:

```bash
sudo apt install ./codex-quota-indicator_0.2.0-1_all.deb
```

APT installs the Python, GTK, Ayatana AppIndicator, and GNOME extension dependencies. The DEB installs a system-wide XDG autostart entry and attempts to show the indicator in an already running desktop session. It starts automatically at every subsequent GNOME login, including after a reboot. If the AppIndicator extension was newly installed or is disabled, enable it in GNOME Extensions and sign out and back in once. Do not use `gnome-shell --replace`.

Check the read-only query with:

```bash
/usr/bin/python3 /usr/lib/codex-quota-indicator/quota.py
```

A working response contains `"ok": true` and `remaining` percentages. If the indicator shows `Codex —`, click it for an error message.

To upgrade, install a newer DEB with the same APT command. To remove:

```bash
sudo apt remove codex-quota-indicator
```

## Install from source

Install the Ubuntu dependencies:

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0 \
  gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator git
```

Then install as your desktop user:

```bash
git clone https://github.com/Ikunio/codex-quota-indicator.git
cd codex-quota-indicator
./install.sh
```

This creates a user-level XDG autostart entry and attempts to start the indicator immediately. Run `git pull && ./install.sh` to update, or `./uninstall.sh` to remove. If migrating to the DEB, run `./uninstall.sh` first so the user-level autostart entry does not override the system-wide one.

## Build the DEB

```bash
./packaging/build-deb.sh
```

The package is written to `dist/`. Its autostart entry is installed to `/etc/xdg/autostart/`.

## Privacy and license

The app uses the Codex CLI's existing login state. It does not copy your authentication file or store credentials. Licensed under [MIT](LICENSE).
