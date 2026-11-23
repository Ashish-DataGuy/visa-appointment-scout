---
name: visa-appointment-scout
description: Monitor permitted public agency feeds and user-selected Telegram chats for visa appointment signals, raise local alerts, and help applicants verify and prepare to schedule. Use for visa-slot monitoring or appointment research; do not automate a protected booking portal.
---

# Visa Appointment Scout

Help an individual applicant find timely appointment signals and prepare to act. Separate official information from community reports, protect applicants' data, and keep account actions under the applicant's control.

## How to use this skill

Install this folder as a skill in a compatible agent, or provide the repository and ask the agent to read `SKILL.md` and follow `README.md`. Setup helpers configure a private Telegram client; `scripts/monitor_telegram.py` watches only explicitly selected chats and can issue local keyword alerts. The local monitor does not use an AI model on Telegram content. The skill file by itself is guidance; scripts and a running local process provide monitoring.

## Telegram content and AI-use restriction

Recheck [Telegram's API Terms](https://core.telegram.org/api/terms) and [Content Licensing Terms](https://telegram.org/tos/content-licensing?setln=en) before using Telegram data. The terms reviewed on 2026-11-23 prohibit scraping, indexing, harvesting, aggregating, or using platform content to train, validate, develop, enhance, benchmark, or deploy AI/ML systems, except where all relevant users give explicit, informed, affirmative, continuing consent limited to that chat and content. Do not send Telegram posts to an AI model, summarize them with an AI, or use them as model context unless that consent requirement is met. A channel being public or a user joining it does not establish that consent.

The included monitor performs simple local phrase matching only, keeps message text in memory only, and sends no post text to an AI service or notification. Its local alert names the selected chat and asks the user to open the source in Telegram's ordinary interface. Do not add message archives, global search, bulk export, or AI classification. If Telegram changes these terms, reassess before changing this design.

## Portal access gate

Check the current country-specific appointment service terms before interacting with a scheduling portal. Recheck them when the task runs; do not rely on old instructions or third-party claims.

For the U.S. visa scheduling service used for India, the official portal terms reviewed on 2026-11-23 say users may not access the website through automated means, including bots, crawlers, or scripts. No official public appointment-slot API or AI-agent integration was identified in this review. Therefore:

- Do not log into, poll, scrape, or automate the protected appointment calendar.
- Do not reverse-engineer private endpoints, replay requests, use browser extensions, automate refreshes, bypass CAPTCHAs, queues, rate limits, or access restrictions.
- Do not book, reschedule, cancel, or pay through an agent.
- Use public official notices and published wait-time estimates for monitoring. They are not live slot inventory.
- Direct the applicant to the official scheduling portal to check and complete any appointment action themselves.

Only change this boundary if the responsible government agency or its authorized service provider publishes an API or written authorization that specifically permits the proposed automated access and actions. Verify the scope, authentication, rate limits, and booking permissions before use. Apply the same gate separately to every country and provider.

The U.S. Department of State says its published wait-time estimates are updated monthly, are not guarantees, and that posts release additional slots regularly; applicants should use the relevant post's scheduling instructions to check availability. Treat the official estimate and the live calendar as different things.

## Source order

Prefer, in this order:

1. Current official country and post instructions from the foreign ministry, embassy or consulate, and authorized scheduling service.
2. Official government announcements and public data feeds or APIs, but only through their published access methods.
3. Official case-status and application pages, such as CEAC or USCIS, when relevant to the applicant's question.
4. Community channels and firsthand reports, checked by the user in Telegram and clearly treated as unverified experience. Do not feed posts to an AI model unless the Telegram consent requirement above is met.

For third-country-national (TCN) questions, check the current rule and the specific post. The Department of State's July 15, 2026 guidance says nonimmigrant applicants should generally schedule in their country of nationality or residence; applying elsewhere may make qualification harder, fees may not transfer, and wait times may be longer. A successful story from one post is not evidence that another post will accept the same case.

Useful starting points:

- [U.S. Department of State visa appointment wait times](https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html)
- [Country-specific U.S. visa information](https://www.ustraveldocs.com/)
- [U.S. Department of State country-of-residence guidance for nonimmigrant visas](https://travel.state.gov/en/newsroom/visas/2026/adjudicating-nonimmigrant-visa--niv--applicants-in-their-country.html)
- [U.S. visa scheduling portal terms](https://atlasportalauthsa.z2.web.core.usgovcloudapi.net/B2C/assets/html/content-atlassusi.html)
- [CEAC visa status](https://ceac.state.gov/CEACStatTracker/Status.aspx)
- [USCIS](https://www.uscis.gov/)

## Local Telegram setup and alerts

Keep the Telegram reader in its own project directory and virtual environment. The repository includes a pinned Telethon dependency and setup scripts; follow the commands in `README.md`.

Provide `TG_API_ID` and `TG_API_HASH` either as process environment variables or in a local `.env` file. A template contains only empty keys:

```dotenv
TG_API_ID=
TG_API_HASH=
```

Add `.venv/`, `.env`, `.env.*`, `private/`, and `*.session*` to `.gitignore`; ensure `.env.example` is the only allowed `.env.*` exception. Restrict `.env` and session permissions to the owner. A Telethon session is a login credential, not a harmless cache. Never commit or share it.

For Windows PowerShell, use the venv interpreter from `.\.venv\Scripts\python.exe` and copy the watchlist with `Copy-Item watchlist.example.json watchlist.local.json`. The setup helper applies a current-user NTFS ACL to private files; keep the checkout in a non-shared folder under the user's profile. The Windows notification dependency is installed from `requirements.txt`.

On macOS, the monitor uses the built-in notification center through JavaScript for Automation; allow notifications for the process if macOS asks.

Load the local file without overriding values already exported by the user, and keep the session path inside `private/`. Ask the account owner to enter API values, phone number, login code, and any 2FA password directly in their local terminal; hide the API hash, code, and password while typing. Do not persist login codes or 2FA passwords. Each user should create and retain their own session.

List authorized dialog titles, then copy `watchlist.example.json` to `watchlist.local.json` and select exact group or channel titles. Set the phrases to match the community's wording. Start `scripts/monitor_telegram.py` in the foreground to see that the connection works; it alerts on new matching posts and Telegram's pending updates after reconnection. For ongoing use, install the platform service described in `README.md`: LaunchAgent on macOS or an interactive Task Scheduler job on Windows. On Windows, run the monitor with `.\.venv\Scripts\python.exe scripts\monitor_telegram.py` and install it with `.\.venv\Scripts\python.exe scripts\manage_monitor.py install`. It runs only while the user account is logged in; the computer must be awake and online. Sleep, outages, missed Telegram updates, notification settings, and keyword gaps can delay or prevent an alert. Do not claim every slot or message will be detected.

The matcher is deterministic and intentionally cautious: it can miss synonyms, non-English posts, images, or ambiguous phrasing, and can alert on rumors or outdated posts. The notification is a lead, not confirmation of live inventory. It tells the user to open the original post and manually check the official scheduling service. Store only the local Telethon session and monitor diagnostics; do not persist message text, scrape chat history, or send content to AI.

For government updates, prefer official RSS feeds, documented public APIs, and public notices. Use only each source's published access method. Do not scrape a site or automate a logged-in account when its terms do not allow it. The visa wait-time table is a monthly estimate; it is not a feed of live appointment slots.

## Telegram and community reports

Connect only through an account the applicant controls and only to channels or groups they are allowed to access. A Telegram API session can expose the account's other chats; never collect another person's credentials or session file.

- Keep each user's API credentials and login codes out of chat. Enter them locally or use an approved local secret store.
- Keep `.env` and Telegram session databases out of Git; restrict local permissions or Windows NTFS access controls and never share session files.
- Monitor only explicitly selected group/channel titles. Do not read or export historical message contents for AI analysis.
- The monitor may inspect incoming text in memory solely for local phrase matching. Do not download media or attachments.
- Do not send Telegram content, excerpts, screenshots, or user paraphrases of message content to an AI system unless the Telegram consent requirement above is met. Redaction alone does not establish consent.
- Do not post to groups, contact members, forward messages, or quote identifiable stories unless the applicant explicitly requests it and has permission to share.

The user must make any assessment of Telegram posts in the Telegram client. Do not classify, count, compare, summarize, or draw conclusions from Telegram-derived reports in the AI conversation unless the Telegram consent requirement above is met. The distinctions below are general guidance for the user when reviewing sources themselves:

- **Officially confirmed:** stated by the responsible agency or scheduling service.
- **Firsthand report:** a member describes their own experience; useful but unverified.
- **Secondhand or speculative:** hearsay, prediction, or advice; do not present as fact.

Independent firsthand reports may strengthen a person's lead, but do not confirm live inventory. Do not infer a release schedule from a short sample.

## Alerts and booking help

Make local alerts concise and non-alarming. The included monitor intentionally avoids copying the post or its text into the alert. It names the selected chat, says a post may mention an appointment opening, and asks the user to verify it in Telegram. Do not repeat Telegram-derived content back in the AI conversation unless the consent requirement is met.

The agent may summarize official instructions, prepare a personalized checklist from facts not derived from Telegram, and guide the applicant to the official portal. The applicant must personally sign in, handle any CAPTCHA or verification, review the date and submit or pay. Never ask for or accept passwords, one-time codes, 2FA passwords, payment details, or session files in chat.

Do not give legal or case-specific immigration conclusions based on group anecdotes. For eligibility, TCN strategy, refusals, administrative processing, or high-consequence form answers, point to current official instructions and, where appropriate, a qualified immigration attorney.

## Publishing and identity privacy

Keep shared skills and summaries free of personal names, email addresses, Telegram handles, API values, session data, and identifiable case examples. This skill intentionally has no author attribution.

Before publishing to a repository, check the repository's visibility, file content and history, and commit author metadata. A clean Markdown file does not hide the name or email attached to a Git commit. If the host is GitHub, use its private `noreply` commit email and check the public profile display name; changing the email setting does not rewrite earlier commits. Use only the first name if the owner chooses to display a name at all.

## Review record

The portal-access boundary and agency links above were reviewed on 2026-11-23. Recheck official terms and guidance before each future deployment; changeable rules and site access policies can change without notice.
