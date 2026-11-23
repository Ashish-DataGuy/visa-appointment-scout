---
name: visa-appointment-scout
description: Surface visa appointment signals from official public updates and authorized community reports, summarize consular experiences, and help applicants prepare to schedule. Use for visa-slot monitoring or appointment research; do not automate a protected booking portal unless its current official terms expressly permit it.
---

# Visa Appointment Scout

Help an individual applicant understand appointment availability and prepare to act. Separate official information from community reports, protect applicants' data, and keep account actions under the applicant's control.

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
4. Community channels and firsthand reports, clearly labeled as unverified experience.

For third-country-national (TCN) questions, check the current rule and the specific post. The Department of State's July 15, 2026 guidance says nonimmigrant applicants should generally schedule in their country of nationality or residence; applying elsewhere may make qualification harder, fees may not transfer, and wait times may be longer. A successful story from one post is not evidence that another post will accept the same case.

Useful starting points:

- [U.S. Department of State visa appointment wait times](https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html)
- [Country-specific U.S. visa information](https://www.ustraveldocs.com/)
- [U.S. Department of State country-of-residence guidance for nonimmigrant visas](https://travel.state.gov/en/newsroom/visas/2026/adjudicating-nonimmigrant-visa--niv--applicants-in-their-country.html)
- [U.S. visa scheduling portal terms](https://atlasportalauthsa.z2.web.core.usgovcloudapi.net/B2C/assets/html/content-atlassusi.html)
- [CEAC visa status](https://ceac.state.gov/CEACStatTracker/Status.aspx)
- [USCIS](https://www.uscis.gov/)

## Local Telegram setup pattern

Keep the Telegram reader in its own project directory and virtual environment. A typical setup uses Telethon with `python-dotenv`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install telethon python-dotenv
```

Provide `TG_API_ID` and `TG_API_HASH` either as process environment variables or in a local `.env` file. A template contains only empty keys:

```dotenv
TG_API_ID=
TG_API_HASH=
```

Add `.venv/`, `.env`, `.env.*`, `private/`, and `*.session*` to `.gitignore`; ensure `.env.example` is the only allowed `.env.*` exception. Restrict `.env` and session permissions to the owner. A Telethon session is a login credential, not a harmless cache. Never commit or share it.

Load the local file without overriding values already exported by the user, and keep the session path inside `private/`. Ask the account owner to enter API values, phone number, login code, and any 2FA password directly in their local terminal; hide the API hash, code, and password while typing. Do not persist login codes or 2FA passwords. Each user should create and retain their own session.

First list the authorized dialog titles to confirm the intended channels; this does not require reading history. When the user requests message analysis, fetch a bounded recent sample (300 messages per channel is a useful starting point), record the date range, then paginate older only as needed to cover the requested period. Do not interpret reaching a message limit as evidence that the sample is representative.

For government updates, prefer official RSS feeds, documented public APIs, and public notices. Use only each source's published access method. Do not scrape a site or automate a logged-in account when its terms do not allow it. The visa wait-time table is a monthly estimate; it is not a feed of live appointment slots.

## Telegram and community reports

Connect only through an account the applicant controls and only to channels or groups they are allowed to access. A Telegram API session can expose the account's other chats; never collect another person's credentials or session file.

- Keep each user's API credentials and login codes out of chat. Enter them locally or use an approved local secret store.
- Keep `.env` and Telegram session databases out of Git; restrict local permissions and never share session files.
- Read a bounded, user-selected recent window first. Expand the date range only when needed for the question; do not retain an unlimited message archive by default.
- Use message text and timestamps only when sufficient. Avoid downloading media or attachments unless the applicant specifically asks and the material is needed.
- Remove names, handles, phone numbers, email addresses, passport or case identifiers, and unrelated personal details before analysis or sharing.
- Do not post to groups, contact members, forward messages, or quote identifiable stories unless the applicant explicitly requests it and has permission to share.

For each useful report, capture only the minimum needed: source, timestamp and time zone, country/post, visa category, appointment stage (for example biometrics or interview), whether the person merely saw a date or actually booked it, and the reported outcome. Deduplicate forwards and copied messages. Keep the distinction between:

- **Officially confirmed:** stated by the responsible agency or scheduling service.
- **Firsthand report:** a member describes their own experience; useful but unverified.
- **Secondhand or speculative:** hearsay, prediction, or advice; do not present as fact.

Multiple independent firsthand reports can strengthen a signal, but they do not confirm live inventory. State how many messages and what date range were reviewed. Report sample limits, conflicting reports, and missing evidence. Do not infer a release schedule from a short sample.

## Alerts and booking help

Make alerts concise and non-alarming. Include the post, visa category, reported appointment stage, source time, confidence label, and a link to the official page. Say “member reported seeing a slot” unless a booking is independently confirmed. Do not send repeated alerts for duplicate posts.

The agent may summarize official instructions, prepare a personalized checklist from the applicant's facts, explain what a community report does and does not establish, and guide the applicant to the official portal. The applicant must personally sign in, handle any CAPTCHA or verification, review the date and post, and submit or pay. Never ask for or accept passwords, one-time codes, 2FA passwords, payment details, or session files in chat.

Do not give legal or case-specific immigration conclusions based on group anecdotes. For eligibility, TCN strategy, refusals, administrative processing, or high-consequence form answers, point to current official instructions and, where appropriate, a qualified immigration attorney.

## Publishing and identity privacy

Keep shared skills and summaries free of personal names, email addresses, Telegram handles, API values, session data, and identifiable case examples. This skill intentionally has no author attribution.

Before publishing to a repository, check the repository's visibility, file content and history, and commit author metadata. A clean Markdown file does not hide the name or email attached to a Git commit. If the host is GitHub, use its private `noreply` commit email and check the public profile display name; changing the email setting does not rewrite earlier commits. Use only the first name if the owner chooses to display a name at all.

## Review record

The portal-access boundary and agency links above were reviewed on 2026-11-23. Recheck official terms and guidance before each future deployment; changeable rules and site access policies can change without notice.
