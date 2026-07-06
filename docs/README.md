# Docs Changelog — jamf-soar-playbooks

Plain-English summary of every change made to the repo. Newest entries at the
top. Mirrors the technical change history in `CLAUDE.md` but written for
people who aren't deep in the playbooks.

---

## 2026-07-06 — First playbook: Device Enrichment & Triage (in review)

The first real playbook landed (PR #9). It's **read-only** — it looks a device
up and writes a tidy summary note onto the case; it doesn't change anything, so
there's no approval gate needed.

It's built in two pieces on purpose:

- **`Jamf - Device Enrichment (Input)`** — the reusable "engine." Hand it a
  device and it gathers everything (device details, compliance, groups, installed
  apps, config profiles, local accounts, extension attributes), formats a
  summary, and hands it back. The other playbooks we build will call this instead
  of each rebuilding the same lookups.
- **`Jamf - Device Enrichment and Triage`** — the entry point. It finds the
  device (by username), calls the engine, and writes the summary as a note on the
  case.

Things to know when adopting it:

- Set your Jamf asset where it says `<your-jamf-asset>`.
- After importing, re-point the wrapper's sub-playbook block to your copy of the
  engine (SOAR ties sub-playbooks to a specific repo; naming your Source Control
  repo `jamf-soar-playbooks` makes the built-in reference line up).
- It currently finds devices by **username** (from the event's `sourceUserName`
  field). Finding by serial / name / MAC, and mobile-only steps, are planned next.

## 2026-06-08 — Repo skeleton created

This is the very first version of the repo. Nothing here runs yet — it's a
governance scaffold so people know what this repo is for, how to propose a
playbook, and the safety rules before any actual playbooks land.

What was added:

- **README.md** — Explains what the repo is (a library of Splunk SOAR playbook
  *templates* for the Jamf SOAR connector app), the prerequisites (the
  `jamf-splunk-soar` app installed in SOAR plus a configured Jamf asset), and
  how the playbooks get into SOAR (added as a git source-control repository, or
  imported as a `.tgz` export). Lists the four planned scenarios with lost /
  stolen device marked as first. Install/usage steps are placeholders for now.
- **CONTRIBUTING.md** — How to propose a playbook (issue first), the
  `[playbook]` title prefix, that playbooks are git-synced into SOAR, a reminder
  to keep template asset/group names generic, the non-negotiable
  analyst-in-the-loop safety rule, and the PR workflow (one playbook per PR,
  reference an issue). Non-engineers welcome.
- **CLAUDE.md** — Technical notes for future maintainers and AI assistants:
  how each playbook is a SOAR playbook synced via git, the dependency on the
  connector app's actions and datapaths, known gotchas, decisions log, and
  change history.
- **.gitignore** — Files git should never track: secrets (`.env`, asset configs,
  client-secret JSON), SOAR playbook export artifacts (`.tgz` / `.tar.gz`),
  Python build junk (playbooks can contain custom code blocks), OS and editor
  junk, logs, and a local `personal/` scratch folder.
- **Issue template** (in `.github/ISSUE_TEMPLATE/`):
  - `new-playbook.md` — Use when you want to propose a playbook. Captures the
    scenario/trigger, a plain-English description, the ordered chain of Jamf app
    actions, decision/approval gates, datapaths between steps, external tools,
    customer-config points, and acceptance criteria.

What's intentionally **not** here yet:

- No actual playbooks. The first one (lost / stolen device) will be added via
  its own issue and PR. We didn't want to commit empty playbook stubs that go
  stale.
- No license file. The repo is private; a license will be added before any
  public release.
- No SOAR source-control sync instructions beyond the high-level shape — those
  will be fleshed out alongside the first real playbook.
