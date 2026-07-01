# Docs Changelog — jamf-soar-playbooks

Plain-English summary of every change made to the repo. Newest entries at the
top. Mirrors the technical change history in `CLAUDE.md` but written for
people who aren't deep in the playbooks.

---

## 2026-06-30 — First playbook template: Compliance Drift / MDM Tamper

Added the first real playbook template under `playbooks/` (issue #4), on the
`playbook/compliance-drift-remediation` branch:

- **`jamf_compliance_drift_remediation.py` / `.json`** — responds to a device
  flagged as non-compliant or MDM-tampered. Unlike a "contain first" flow, this
  one **tries to fix the device first** (re-establish MDM control, force a
  check-in, refresh inventory, flag it as under review), then **re-checks**. If
  the device is healthy again, it just notes that and stops. Only if it's *still*
  broken does it quarantine and lock the device — and a full wipe happens **only**
  after an analyst clicks Approve on a prompt that spells out the wipe is
  permanent and irreversible.
- **`playbooks/README.md`** — an index of templates and how to adapt them.

Everything in the template is a clearly-marked placeholder (Jamf asset,
quarantine group, the flag attribute, approver role) — no real names, no
secrets. It follows the naming/safety conventions agreed in issue #8.

One caveat: the `.py` (the actual logic) is complete and syntax-checked, but the
paired `.json` (the visual diagram SOAR draws) is a best-effort version that
should be opened and re-saved once in SOAR's Visual Playbook Editor to tidy up
the layout.

**Update (2026-07-01):** we checked the template against the *real* Jamf connector
that's actually installed in the SOAR test environment (not a guess) and corrected
the data wiring: the connector returns a device's id as `id` (not `jamf_device_id`),
its type as `type`, and compliance as a `compliance_state` text field (not a
true/false `compliant`); the "flag" attribute uses `ea_id`; and the wipe safety
`confirm` is a text value. The action names we used were already right. The
playbook's logic still passes its flow test after the fixes.

**Update (2026-07-01) — rebuilt and proven working live.** The first hand-written
version wouldn't open in SOAR's Visual Playbook Editor (the file format for the
decision/prompt/note blocks is too intricate to write by hand). We rebuilt it by
copying the structure of an already-working playbook, then **ran it live in the SOAR
test environment against the real Jamf tenant — every step succeeded** (look up device
→ redeploy management → force check-in → check compliance → quarantine → lock), it
**paused for analyst approval before the wipe**, and we **denied, so nothing was
erased**. That's a full end-to-end proof of the playbook and its safety gate.

Two things we learned and wrote down so nobody trips on them:
- **Prerequisites matter.** Each action needs specific Jamf API permissions (there's a
  table in `playbooks/README.md`), plus real values for the quarantine group and a
  6-digit lock PIN. Missing permissions show up as "403" errors at run time.
- **Playbooks are built in SOAR's editor, then saved to git** — not written by hand.
  There's now a step-by-step build sheet (`playbooks/…​.BUILD.md`) for recreating it.

The committed template keeps generic `<placeholders>` (no real asset names, group
names, or PINs) so it's safe to share; real values live only in the SOAR instance.

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
