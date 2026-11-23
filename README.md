# Visa Appointment Scout

A reusable Codex/AI-agent skill and local alert tool for visa-appointment research. It watches only explicitly selected Telegram chats on the user's Mac or Windows PC and gives a local notification when new or pending messages match configured phrases. Message text stays on the device and is not sent to an AI. It does **not** access or automate a protected visa-booking calendar.

## Use this with an AI agent

Give the agent this repository and ask it to read `SKILL.md` before doing visa-slot research. The skill sets source hierarchy, privacy rules, Telegram's current AI-use restriction, and the portal-access boundary. The files under `scripts/` set up a user's own local Telegram connection and background monitor. The account owner enters credentials and login codes in the local terminal; the monitor runs independently of prompts once installed.

For Codex, install or copy `SKILL.md` into a skill directory named `visa-appointment-scout`. For another agent, provide the repository and ask it to follow `SKILL.md` and the setup steps below. The skill file gives instructions; the local scripts provide ongoing monitoring.

## Set up your own Telegram connection

Use your own Telegram account and API credentials. Never share your API hash, phone login code, 2FA password, or `.session` file with the agent or another person.

```bash
git clone https://github.com/Ashish-DataGuy/visa-appointment-scout.git
cd visa-appointment-scout
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/configure_credentials.py
.venv/bin/python scripts/list_chats.py
```

On Windows PowerShell, use:

```powershell
git clone https://github.com/Ashish-DataGuy/visa-appointment-scout.git
Set-Location visa-appointment-scout
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\configure_credentials.py
.\.venv\Scripts\python.exe scripts\list_chats.py
```

Create your own Telegram API credentials at [my.telegram.org/apps](https://my.telegram.org/apps). The credential helper prompts in the local terminal, hides the API hash, and writes a Git-ignored `.env` with owner-only permissions. On Windows it applies an NTFS access-control rule for the current account; keep the project in your own user profile, not a shared folder. The first `list_chats.py` run prompts for the phone number, login code, and 2FA password locally. It lists dialog titles only.

## Configure and start local alerts

```bash
cp watchlist.example.json watchlist.local.json
```

On Windows PowerShell, use `Copy-Item watchlist.example.json watchlist.local.json`.

Edit `watchlist.local.json` and replace the example with exact titles from `list_chats.py`. Add phrases used by the groups where appointment availability is discussed. The watchlist is Git-ignored.

Test the local notification, then run the monitor in the foreground:

```bash
.venv/bin/python scripts/monitor_telegram.py --test-notification
.venv/bin/python scripts/monitor_telegram.py
```

For ongoing checks on macOS, install the user-level background service:

```bash
.venv/bin/python scripts/manage_monitor.py install
```

The installer copies code and private configuration into `~/Library/Application Support/Visa Appointment Scout/runtime` so the background process does not depend on the agent workspace. It starts at login and restarts after a crash while the account remains logged in. The Mac must be awake and online to receive updates promptly. To stop and remove it:

```bash
.venv/bin/python scripts/manage_monitor.py uninstall
```

On Windows PowerShell, test and install the interactive Task Scheduler task with:

```powershell
.\.venv\Scripts\python.exe scripts\monitor_telegram.py --test-notification
.\.venv\Scripts\python.exe scripts\manage_monitor.py install
```

The task starts at sign-in in the user's interactive session so Windows notifications can appear. Keep the PC awake and online. Remove it with:

```powershell
.\.venv\Scripts\python.exe scripts\manage_monitor.py uninstall
```

The monitor processes new and pending Telegram updates locally using a fixed phrase list, never an AI model. It does not save message text or download media. Notifications are generic; the private local log contains only the selected chat title and message time, not post text. The user opens Telegram to find and verify the original post. Wording gaps can cause missed or noisy alerts; a group report is not proof of live availability.

Telegram's current terms prohibit using platform content with AI/ML systems unless every relevant user has given explicit, informed, ongoing consent scoped to that chat and content. This project therefore does not export Telegram messages for AI summaries. See the terms linked from `SKILL.md` before changing this design.

## Official and community sources

`sources.example.yml` lists official starting points and explains their access mode. Copy it to `sources.local.yml` to add permitted public sources; that local file is Git-ignored.

Use published RSS feeds or APIs only where the agency provides them and its terms allow the proposed use. The U.S. Department of State wait-time page provides estimates, not live slot inventory. For the India scheduling portal, the current terms prohibit automated access through bots, crawlers, or scripts. Telegram alerts can point to a possible community lead, but the applicant must check the official calendar and book manually.

## Privacy before sharing

- Keep `.env`, `private/`, virtual environments, and all Telethon session files out of Git.
- A Telegram session can access the account's other dialogs. Keep it owner-only and never upload it.
- Do not share Telegram message text, excerpts, screenshots, or AI summaries unless Telegram's consent requirements are met.
- The repository contains no author field or personal email. Commits use first-name-only attribution and a GitHub `noreply` address. Check the repository and commit metadata before adding your own changes.
