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
Two playbooks now exist (of the planned set); playbooks live under `playbooks/`
as `.py` + `.json` pairs:

- **Device Enrichment & Triage — MERGED (PR #9).** Read-only; a reusable **Input
  sub-playbook** (`Jamf - Device Enrichment (Input)`) + a thin **Automation
  wrapper** (`Jamf - Device Enrichment and Triage`) that resolves the device (by
  username), calls the sub-playbook, and writes a summary note. No destructive
  step. This is the shared enrichment engine the other templates are meant to reuse.
- **FileVault Recovery Access (macOS) — in review (PR #11), branch
  `dist/filevault-recovery-access`.** Secured recovery access to a Mac after a
  compromise or during offboarding. Flow: resolve by serial (from
  `artifact:*.cef.serialNumber`) → (device found?) → enrich (FileVault recovery
  key [SENSITIVE], local users, compliance) → secure (recovery lock, lock) →
  note/notify → analyst approval gate → wipe **only** on approval; decline /
  no-device paths add a note. Authored in the VPE + export-scrubbed for
  distribution. State: approval gate ✅ (`confirm` wired to `device_id`);
  genericized (asset/approver/password/phone/message → placeholders); serial
  un-hardcoded (`artifact:*.cef.serialNumber`); **notify step still a note STUB**;
  lock PIN kept `000000`; block-renaming deferred.

In-progress / planned: compromised user (#12, in review), lost/stolen (#1),
IdP breach, malicious file, compliance drift (#10, in review).

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
- **Input sub-playbooks with paired inputs (e.g. `device_id` + `device_type`)
  must zip them, not cross them.** SOAR collects each `playbook_input:` datapath
  separately and auto-generates a *nested* loop (Cartesian product), so for a
  multi-device user the wrong id/type pairs resolve to unrelated devices and the
  action silently hits the wrong device. Fix: rebuild `parameters` by `zip`-ing
  in each action's Custom Code. **Input contract:** callers must pass
  `device_id` and `device_type` as paired, equal-length lists (the engine
  asserts this). Flat Automation playbooks are immune — they read both from one
  action-result `collect2`, which returns aligned tuples. (See the
  `Jamf - Device Enrichment (Input)` engine; PR #9 C1.)

---

## Change History
| Date | File | What Changed |
|------|------|--------------|
| 2026-07-06 | `playbooks/` | First playbook (#5, PR #9): **Device Enrichment & Triage** (read-only). Shipped as an **Input sub-playbook** (`Jamf - Device Enrichment (Input)`: get device + 6 enrich actions → format → `enrichment_summary` output) plus an **Automation wrapper** (`Jamf - Device Enrichment and Triage`: resolve by username → call sub-playbook → `add_note`). Asset scrubbed to `<your-jamf-asset>`. Known adaptation points: sub-playbook repo reference (`jamf-soar-playbooks/…`) must be re-linked on import; resolver reads `artifact.*.cef.sourceUserName`; serial/name/MAC + mobile branches deferred. |
| 2026-06-08 | All files | Initial governance skeleton created: README, CONTRIBUTING, CLAUDE.md, .gitignore, new-playbook issue template, docs/README.md. No actual playbooks yet. |
| 2026-07-02 | playbooks/Jamf - FileVault Recovery Access (macOS).{json,py}, CLAUDE.md, docs/README.md | **First playbook: renamed + genericized (#7).** (1) **Renamed in the SOAR VPE** `Jamf - FileVault Key / Recovery Access (macOS)` → `Jamf - FileVault Recovery Access (macOS)` to kill the `/` that had become an accidental `playbooks/… Key /…` subdirectory on export (SOAR re-pushed clean filenames; old slashed files gone). (2) **Export-scrubbed** the `.py` + `.json` in sync for template distribution: asset `test1` → `<your-jamf-asset>` (7 blocks), approver `Sarah` → `<security-analyst-role>`, a **real recovery-lock password `TestRecovery123`** + a test lock-message + test phone `555-0100` → placeholders, wipe prompt reworded to state irreversibility (#8), docstring filled. `.json` re-validated; `.py` re-parsed; no dev values remain except the deliberately-kept serial + PIN. **Context:** local repo was 9 commits stale — the remote had advanced via SOAR VPE saves adding the resolve→(device-found?)→…→notify(note stub)→approval→wipe/decline/no-device branches; reset local to the remote tip (dropped an obsolete local scrub done on the pre-rename files) before re-scrubbing. **Still open:** notify step is a note STUB (build a restricted-channel Slack notify), serial hardcoding (blocked on #8), block renaming (VPE). |
| 2026-07-03 | playbooks/Jamf - FileVault Recovery Access (macOS).{json,py}, CLAUDE.md, docs/README.md | **Un-hardcoded the serial + prepped distribution PR (#7).** (1) **Serial un-hardcoded in the VPE:** `serial_number` now binds the datapath `artifact:*.cef.serialNumber` (SOAR generates a `collect2`) instead of the literal `HNWYQ246Q2` — adopting #4's proven pattern (a code-block `collect2` sidesteps the VPE picker's literal-trap; verified in the pushed `.json`/`.py`). #8 "contract" is effectively settled by this pattern. (2) **Recovered a dropped playbook:** the earlier scrub push (`fd52b32`, placeholder asset) made SOAR drop the playbook when the non-persistent source-control connection re-synced; restored the runnable version (`18ce9f7`), re-created the connection, playbook reappeared. **Lesson:** the SOAR-synced dev branch must stay RUNNABLE — the scrubbed distribution template can't be its tip. (3) **Distribution split:** feature branch `playbook/filevault-recovery-access` stays runnable (SOAR-happy); scrubbed template lives on `dist/filevault-recovery-access` → PR to `main` (asset/`TestRecovery123`/phone/message/approver → placeholders, prompt irreversibility, docstring; serial datapath + PIN kept). **Still open:** notify step is a note STUB; block renaming (VPE). |
