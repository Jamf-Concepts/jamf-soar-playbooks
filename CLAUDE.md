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
Governance skeleton plus the first templates landing under `playbooks/` (one
`.py` + `.json` pair per template). Templates are developed on feature branches
and merged via PR — **never committed directly to `main`**.

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

### File Map — Playbooks
| File | Issue | Purpose |
|------|-------|---------|
| `playbooks/README.md` | — | Index of templates; authoring note (`.py` is source of truth, `.json` is a VPE graph to re-save in the editor) |
| `playbooks/jamf_compliance_drift_remediation.py` | #4 | Compliance drift / MDM tamper: correct-first remediation, re-check, contain-if-needed, gated wipe |
| `playbooks/jamf_compliance_drift_remediation.json` | #4 | Paired VPE graph (20 nodes / 21 edges); `draft_mode: true` until canonicalized in the editor |

### Playbook conventions (from issue #8 + benchmark research)
- **Playbook name:** `Jamf - <Scenario>` (Title Case + dash).
- **Block names:** imperative verbs, descriptive (`resolve_device`, `recheck_compliance`),
  not auto-numbered (`get_device_by_serial_1`). Decision blocks read as a question.
- **Destructive-step prompt** states the action's consequence + irreversibility in the
  message the approver sees.
- **Generic only:** every customer value is a `<...>` placeholder / named config point —
  no real asset names, group ids, approver names, or secrets.
- **Authoring:** hand-authored `.py` is the reviewable source of truth; the `.json` is a
  best-effort VPE graph to open and re-save in the editor to regenerate ports/layout/hash.

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
| 2026-06-30 | `playbooks/jamf_compliance_drift_remediation.{py,json}`, `playbooks/README.md` | New (branch `playbook/compliance-drift-remediation`, issue #4): first hand-authored template. Correct-first backbone (redeploy framework → blank push → update inventory → flag EA → re-check compliance → decide corrected? → contain (quarantine group + lock) if not → analyst approval prompt with irreversibility warning → gated wipe). Applies #8 naming/block conventions; all values are `<...>` placeholders, no secrets. `.py` validated (`py_compile`); `.json` is a 20-node best-effort VPE graph (`draft_mode: true`) to re-save in the editor. Verify `jamf_device_id` + `compliant` datapaths against the connector. |
