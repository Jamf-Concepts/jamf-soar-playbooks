# CLAUDE.md — jamf-soar-playbooks

## Project Purpose
A collection of **Splunk SOAR playbook templates** for the Jamf SOAR connector
app. These playbooks orchestrate the connector's actions into incident-response
flows (resolve device → contain → enrich/notify → timer → analyst approval gate
→ destructive step). This repo is NOT a connector — it holds reusable playbooks
that *call* the app's actions. The companion app lives in `jamf-splunk-soar`
(GitHub: `Jamf-Concepts/jamf-splunk-soar`).

## Documentation Rule
After every code or doc change, update `docs/README.md` and this file. Do not
skip this step.

---

## Architecture

### Current state
The **first playbook has landed** (issue #7, branch
`playbook/filevault-recovery-access`): `playbooks/Jamf - FileVault Recovery
Access (macOS).{json,py}` — a SOAR VPE export (blockly/coa `.json` + generated
`.py`). Scenario: secured recovery access to a Mac after a compromise or during
offboarding. Flow: resolve by serial → (device found?) → enrich (FileVault
recovery key [SENSITIVE], local user accounts, compliance status) → secure (set
recovery lock, lock device) → note/notify → analyst approval gate → wipe
**only** on approval; a decline or a no-device-found path just adds a note.
Authored in the SOAR VPE on the shared box and synced via git, then
**export-scrubbed** for template distribution.

**State of this playbook:**
- Analyst approval gate before wipe ✅ (never auto-wipes); `wipe device`
  `confirm` wired to `device_id` (matches the connector's #7 gate).
- Genericized (2026-07-02): asset → `<your-jamf-asset>` (7 blocks), approver →
  `<security-analyst-role>`, recovery-lock password / lock message / phone →
  placeholders (a **real `TestRecovery123` password** + a test phone were
  scrubbed), wipe prompt states irreversibility, docstring filled.
- **Notify step is a STUB** — `code_1` adds a note with a TODO to replace it with
  a real restricted-channel Slack notification (key never posted). Still to build.
- **Deliberately left:** resolve serial `HNWYQ246Q2` (a real wired datapath needs
  the #8 artifact-field contract — a hand-typed non-standard CEF path stores as a
  literal and never resolves) and lock PIN `000000` (a `<...>` placeholder would
  fail the connector's 6-ASCII-digit rule).
- **Deferred to a VPE pass:** block renaming to the imperative #8 convention
  (blocks are still `get_device_by_serial_1`, `prompt_1`, `decision_1/2`, `code_1/2/3`).

### How it fits together
- Each playbook is a **SOAR playbook synced via git**. SOAR clones this repo as
  a source-control repository (Administration → Source Control) and keeps the
  playbooks in sync, or a customer imports a `.tgz` export.
- Playbooks are **kept generic** — they are templates, not one customer's
  deployment. No real asset names, group names/IDs, tenant URLs, or analyst
  addresses. Every customer-config point is marked.
- The playbooks **depend on the `jamf-splunk-soar` app** being installed in SOAR
  with a configured Jamf asset. They reference the app's actions by app +
  action name.

### File Map — Governance
| File | Purpose |
|------|---------|
| `README.md` | What the repo is, prerequisites (app + asset), distribution model (source-control repo vs `.tgz` import), planned templates, links to the app repo |
| `CONTRIBUTING.md` | Issue-first workflow, `[playbook]` prefix, git-sync note, keep-templates-generic note, analyst-in-the-loop safety rule, PR workflow |
| `.gitignore` | Secrets + SOAR `.tgz`/`.tar.gz` exports + Python build junk + OS/editor junk + `personal/` scratch |
| `.github/ISSUE_TEMPLATE/new-playbook.md` | Template for proposing a playbook |
| `docs/README.md` | Plain-English changelog per the docs rule |

### Planned playbook templates
Backbone for every template: resolve device → contain → enrich/notify →
(timer) → analyst approval gate → destructive step.

1. **Lost / stolen device** — FIRST template to build.
2. Compromised user.
3. Identity-provider (IdP) breach.
4. Malicious file.

---

## API / Integrations

### Dependency on the connector app
These playbooks have no API surface of their own. They invoke actions exposed
by the `jamf-splunk-soar` app. The contract that matters here is the app's
**action names + their input/output datapaths and `contains` types** — that's
how blocks chain (one action's output datapath feeds the next action's input).

- Playbooks reference actions by **app name + action name** (e.g. the Jamf app's
  `lock device`, `add to static group`, `wipe device`).
- Wiring between blocks relies on the app's declared `contains` types (e.g.
  `jamf device id`, `jamf command uuid`) so SOAR can auto-suggest datapaths.
- If the app changes an action's name or datapaths, dependent playbooks break —
  track app releases.

### Splunk SOAR
- Playbooks run inside Splunk SOAR (Cloud or On-prem).
- Managed via git-backed source control or `.tgz` import — NOT bundled in the
  app `.tgz`.

---

## Decisions Log
| Date | Decision | Reason |
|------|----------|--------|
| 2026-06-08 | Keep playbooks in a separate repo from the connector app | SOAR manages playbooks via git source control separately from the app `.tgz`; decoupled release cadence; clean ownership |
| 2026-06-08 | Build the lost / stolen device playbook first | Highest-value, best-understood scenario; exercises the full backbone (contain → approval gate → erase) and sets the pattern for the rest |
| 2026-06-08 | Destructive steps must sit behind an analyst approval gate | Safety: never auto-wipe. A competitor mass-unenrolled thousands of devices via unattended automation — non-negotiable rule |

---

## Gotchas
- Playbooks reference the connector's actions by **app + action name**. Renaming
  an action in `jamf-splunk-soar` (or changing its datapaths) breaks dependent
  playbooks.
- These playbooks **require the `jamf-splunk-soar` app installed AND a wired
  Jamf asset**. Without both, action blocks won't resolve on import/sync.
- **Never auto-wipe.** Every destructive step (wipe/erase, mass group change)
  must be gated behind an analyst-in-the-loop approval prompt. This is a hard
  rule, not a guideline.
- **`.tgz` playbook exports can embed environment specifics** — asset names,
  group IDs, label values, analyst addresses. Scrub these before committing or
  sharing an export so a template doesn't leak one customer's config.
- Keep all templates generic — use clearly-marked placeholders for any
  customer-specific value.
- **A playbook is a `.py` + `.json` pair; the `.json` (blockly/coa) is
  canonical.** SOAR's VPE drives the `.json` and regenerates the `.py`.
  Hand-editing risks drift — for value scrubs, edit BOTH in sync (asset/param
  values live in `coa.data.nodes.*`; `blockly_xml` does NOT carry them).
- **Genericizing the asset is an EXPORT scrub, not a VPE edit.** The VPE asset
  field is a dropdown of *configured* assets — you can't type `<your-jamf-asset>`.
  So the placeholder swap is done on the committed export files (git-side) as the
  FINAL step before sharing. After scrubbing, do NOT re-open/Save in the VPE
  (SOAR would push its real-asset store copy and clobber the scrub) — or re-scrub.
- **A `/` in a SOAR playbook NAME becomes a directory separator on export.** #7
  was first named `… Key / Recovery Access …`, which git stored as an accidental
  `playbooks/… Key /…` subdirectory. Fixed by renaming in the VPE to drop the
  slash. Avoid `/` in playbook names.
- **The shared box pushes to the branch from other sessions — your local can be
  badly stale.** #7's remote advanced 9 commits (VPE saves) while the local repo
  sat at the old base, so a scrub done locally was on obsolete, wrongly-named
  files. ALWAYS `git fetch` and reconcile before editing/scrubbing an
  actively-synced playbook branch (ties to the per-dev-connection rule).

---

## Change History
| Date | File | What Changed |
|------|------|--------------|
| 2026-06-08 | All files | Initial governance skeleton created: README, CONTRIBUTING, CLAUDE.md, .gitignore, new-playbook issue template, docs/README.md. No actual playbooks yet. |
| 2026-07-02 | playbooks/Jamf - FileVault Recovery Access (macOS).{json,py}, CLAUDE.md, docs/README.md | **First playbook: renamed + genericized (#7).** (1) **Renamed in the SOAR VPE** `Jamf - FileVault Key / Recovery Access (macOS)` → `Jamf - FileVault Recovery Access (macOS)` to kill the `/` that had become an accidental `playbooks/… Key /…` subdirectory on export (SOAR re-pushed clean filenames; old slashed files gone). (2) **Export-scrubbed** the `.py` + `.json` in sync for template distribution: asset `test1` → `<your-jamf-asset>` (7 blocks), approver `Sarah` → `<security-analyst-role>`, a **real recovery-lock password `TestRecovery123`** + a test lock-message + test phone `555-0100` → placeholders, wipe prompt reworded to state irreversibility (#8), docstring filled. `.json` re-validated; `.py` re-parsed; no dev values remain except the deliberately-kept serial + PIN. **Context:** local repo was 9 commits stale — the remote had advanced via SOAR VPE saves adding the resolve→(device-found?)→…→notify(note stub)→approval→wipe/decline/no-device branches; reset local to the remote tip (dropped an obsolete local scrub done on the pre-rename files) before re-scrubbing. **Still open:** notify step is a note STUB (build a restricted-channel Slack notify), serial hardcoding (blocked on #8), block renaming (VPE). |
