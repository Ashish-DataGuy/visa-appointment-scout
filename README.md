# Visa Appointment Scout

A reusable Codex/AI-agent skill and local Telegram starter kit for visa-appointment research. It gathers authorized Telegram message text for summaries and points to official public information. It does **not** access or automate a protected visa-booking calendar.

## Use this with an AI agent

Give the agent this repository and ask it to read `SKILL.md` before doing visa-slot research. The skill sets the source hierarchy, privacy rules, message-analysis workflow, and portal-access boundary. The files under `scripts/` provide a starting point for each user's own local Telegram connection. If the agent can run programs on the user's computer, it can follow the setup and invoke the tools there. Otherwise, the user runs the commands locally and decides what output to share with the agent. The repository does not install an AI agent or create a background monitor by itself.

For Codex, install or copy `SKILL.md` into a skill directory named `visa-appointment-scout`. For another agent, provide the repository and ask it to follow `SKILL.md` and the setup steps below. The skill file alone gives instructions; it does not install software, create API credentials, connect accounts, or run continuously.

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

Create your own Telegram API credentials at [my.telegram.org/apps](https://my.telegram.org/apps). The credential helper prompts in the local terminal, hides the API hash, and writes a Git-ignored `.env` with owner-only permissions. The first `list_chats.py` run prompts for the phone number, login code, and 2FA password locally. It lists dialog titles only.

To pass a bounded sample from channels you are allowed to access to your AI agent for analysis, run:

```bash
.venv/bin/python scripts/export_recent_messages.py \
  --channel "Exact channel title" \
  --channel "Another exact channel title" \
  --limit 300 \
  --confirm-read
```

The exporter prints JSONL to standard output and does not write message history to disk. It omits sender IDs and applies simple masks to email addresses, common phone-number formats, case-like IDs, and Telegram handles. These masks are not perfect; inspect data before sharing. Media is not downloaded. Only run the exporter when the account owner has authorized message analysis.

Each channel starts with its latest messages. The first JSONL record for each channel is `page_info`, including its count, UTC date range, and—when the page is full—a `next_offset_id` cursor. To read the next older page, rerun the command with one `--offset-id` per `--channel`, in the same order. For example, for two channels, add `--offset-id 12345 --offset-id 67890`, using each channel's own cursor from its latest `page_info`. A cursor of `null` means that page reached the available history. Keep the requested total bounded; the agent should state how many messages and what date range it actually reviewed.

## Official and community sources

`sources.example.yml` lists official starting points and explains their access mode. Copy it to `sources.local.yml` to add your own permitted sources; that local file is Git-ignored. Add Telegram titles only for channels or groups you are allowed to read.

Use published RSS feeds or APIs only where the agency provides them and their terms allow the proposed use. The U.S. Department of State wait-time page provides estimates, not live slot inventory. For the India scheduling portal, the current terms prohibit automated access through bots, crawlers, or scripts. The agent can report and contextualize Telegram sightings, but the applicant must check the official calendar and book manually.

## Privacy before sharing

- Keep `.env`, `private/`, virtual environments, and all Telethon session files out of Git.
- A Telegram session can access the account's other dialogs. Keep it owner-only and never upload it.
- Share only summaries or minimum redacted samples. Avoid publicizing identifiable applicant stories, screenshots, or case details.
- The repository contains no author field or personal email. Commits use first-name-only attribution and a GitHub `noreply` address. Check the repository and commit metadata before adding your own changes.
