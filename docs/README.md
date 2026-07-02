# Docs Changelog — jamf-soar-playbooks

Plain-English summary of every change made to the repo. Newest entries at the
top. Mirrors the technical change history in `CLAUDE.md` but written for
people who aren't deep in the playbooks.

---

## 2026-07-02 — First playbook: Jamf - FileVault Recovery Access (macOS)

The first real playbook is in (issue #7): **Jamf - FileVault Recovery Access
(macOS)**. It gives IT/security secured recovery access to a Mac — after a
compromise or during employee offboarding:

1. **Resolve** the Mac by serial number; if none matches, it stops with a note.
2. **Enrich** — pull the FileVault recovery key (sensitive!), local user
   accounts, and compliance status.
3. **Secure** — set a recovery lock, then lock the device.
4. **Note / notify** — record what happened (today a note; meant to become a
   restricted-channel Slack alert — see below).
5. **Ask a human** — an analyst approval prompt before any wipe.
6. **Only on "Yes"** — wipe the device (offboarding erase). A "No" just leaves a
   note. It never wipes on its own.

Cleanups done this session:
- **Renamed** the playbook to drop a `/` in its title (the slash was accidentally
  creating a folder inside the repo).
- **Made it generic** — swapped one environment's specifics for clearly-marked
  placeholders: the dev asset name, the approver, and a **real recovery-lock
  password and test phone number** that had been left in. The wipe prompt now
  spells out that the erase is permanent and irreversible.

Still to finish (per issue #7):
- **Build the real notify step.** Right now step 4 is just a note with a "replace
  me" reminder; it needs to send to a restricted channel (the recovery key must
  never go to a broad channel).
- **Wire the serial to the event** instead of a fixed placeholder — waiting on a
  shared decision about device-identifier fields (issue #8).
- **Friendlier block names** (a tidy-up best done in the SOAR editor).

---

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
