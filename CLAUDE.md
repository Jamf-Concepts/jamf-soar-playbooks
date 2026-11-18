# CLAUDE.md — jamf-soar-playbooks

## Project Purpose
A collection of **Splunk SOAR playbook templates** for the Jamf SOAR connector
app. These playbooks orchestrate the connector's actions into incident-response
flows (resolve device → contain → enrich/notify → timer → analyst approval gate
→ destructive step). This repo is NOT a connector — it holds reusable playbooks
that *call* the app's actions. The companion app lives in `jamf-splunk-soar`.

## Documentation Rule
After every user-visible change, add a one-line entry to `docs/CHANGELOG.md`.
Update the Architecture/File Map sections above only when they've gone stale;
don't keep a running narrative here — commit messages and PRs are the record
of what changed and why.

---

## Architecture

### Current state
Three templates now exist under `playbooks/` (each a `.py` + `.json` pair):

- **Device Enrichment & Triage** (#5, **merged PR #9**) — read-only; a reusable
  **Input sub-playbook** (`Jamf - Device Enrichment (Input)`) plus an Automation
  wrapper (`Jamf - Device Enrichment and Triage`). The shared enrichment engine
  the other templates are meant to reuse. No destructive step.
- **Compliance Drift & MDM Tamper Remediation** (#4, **merged PR #10**) —
  correct-first backbone with an analyst-gated wipe.
- **FileVault Recovery Access (macOS)** — **in review (PR #11)**, branch
  `dist/filevault-recovery-access`. Secured recovery access to a Mac after a
  compromise or during offboarding. Flow: resolve by serial (from
  `artifact:*.cef.serialNumber`) → (device found?) → enrich (FileVault recovery
  key [SENSITIVE], local users, compliance) → secure (recovery lock, lock) →
  note/notify → analyst approval gate → wipe **only** on approval; decline /
  no-device paths add a note. Authored in the VPE + export-scrubbed for
  distribution. State: approval gate ✅ (`confirm` wired to `device_id`);
  genericized (asset/approver/password/phone/message → placeholders); serial
  un-hardcoded (`artifact:*.cef.serialNumber`); approval prompt routes by
  `role`; **notify step still a note STUB**; lock PIN kept `000000`.

In-progress / planned: **IdP breach (#6, in review PR #15)** — bulk quarantine
with an up-front batched approval + batch cap, no bulk wipe; compromised user
(#12, in review); **lost/stolen (#1, in review PR #16)** — resolve by serial →
device_type branch (mobile: enable lost mode / computer: lock) → note → analyst
gate → wipe on approval; per-branch tails; computer path live-verified; malicious file.

Templates are developed on feature branches and merged via PR — **never
committed directly to `main`**.

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
| `docs/CHANGELOG.md` | Public-facing changelog — one line per user-visible change, written for security admins, not contributors |

### File Map — Playbooks
| File | Issue | Purpose |
|------|-------|---------|
| `playbooks/README.md` | — | Index of templates; authoring note (`.py` is source of truth, `.json` is a VPE graph to re-save in the editor) |
| `playbooks/Jamf - Device Enrichment (Input).{py,json}` | #5 (PR #9) | Reusable enrichment **Input sub-playbook**: get device + 6 enrich actions → format → `enrichment_summary` output. Callers pass `device_id`+`device_type` as paired equal-length lists (engine `zip`s them — see gotcha). |
| `playbooks/Jamf - Device Enrichment and Triage.{py,json}` | #5 (PR #9) | Automation wrapper: resolve by username (`artifact.*.cef.sourceUserName`) → call the Input sub-playbook → `add_note` with the summary. Read-only, no approval gate. |
| `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.py` | #4 | **v3** (PR #10 review + re-review). Serial-present gate → correct-first → device-found gate → compliance check → positive `NON_COMPLIANT` match → contain-if-needed → containment-success gate → analyst approval → gated wipe → **wipe-success gate** (B3), with an `add_note` on every terminal path. `confirm` wired to the resolved device id (B1); wipe `pin` dropped. `py_compile`-clean; block set matches the 23-node graph 1:1. Executed green (v3 run 61). |
| `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.json` | #4 | **v3 graph — 23 nodes / 28 edges** (PR #10 review rebuild + re-review B3). Imported to SOAR clean (`passed_validation: true`, **no node warnings**) and **live-run green** (v2 run 57; v3 run 61). Decisions: `has_serial`, `device_found`, `is_compliant` (positive `NON_COMPLIANT` match, AND `status==success`), `containment_ok` (quarantine AND lock succeeded), `is_wipe_approved`, `wipe_ok` (B3 — gate the "ERASE queued" note on wipe `status==success`). Seven `code` notes on every terminal path (no-serial, no-device, no-drift, containment-failed, wipe-declined, wipe-queued, wipe-failed). **Wipe `confirm` wired to `resolve_device:action_result.data.*.id`** (B1); wipe `pin` dropped. Generic placeholders; `draft_mode:false`; `hash:""` (placeholder graph can never match a real instance — SOAR recomputes on import). |
| `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.BUILD.md` | #4 | VPE build sheet — the **"Target rebuild (v2)"** section (19 nodes / 22 edges) is the shipped design (verified action names/datapaths/prereqs + live-run status); the v1 12-node sections are kept as history |
| `playbooks/Jamf - IdP Breach Bulk Quarantine.{py,json}` | #6 (in review PR #15) | Highest-risk **bulk quarantine** for an IdP breach. Resolve set by username → devices-found gate → compliance enrich → dry-run preview + **aggregate batch cap** → **single up-front batched approval (full scope)** → contain loop (add-to-group per `device_type` + lock + blank push) → results note from real statuses. **No bulk wipe.** 15 nodes / 17 edges. `.py` is source of truth (aggregate cap / per-type group / real-status report / compliance-in-preview live only in the `.py`). |

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
- **A generic template's `.json` hash can never match a real instance.** SOAR stamps
  `coa.data.hash` over the graph on export, but the graph embeds the asset name — and a
  shareable template must carry `<your-jamf-asset>`, not a real asset. Scrubbing the real
  asset name (mandatory) invalidates SOAR's exported hash, and SOAR recomputes the hash on
  import against the customer's own wired asset regardless. So commit `hash:""` (proven
  importable Jul-1) rather than a hash that won't match the placeholder graph.
- **Wipe `confirm` must equal `device_id` — FIXED in v2 (PR #10 review B1).** The connector's
  confirmation gate (`jamf_connector.py:1674-1680`) requires `confirm` to **exactly equal the
  target `device_id` string** (`if confirm != device_id: return WIPE_NOT_CONFIRMED`). The v1 graph
  sent a truthy flag (`"true"` / boolean `True`), so an approved wipe was silently rejected. **v2
  wires `confirm` to `resolve_device:action_result.data.*.id`** — the same datapath as `device_id`
  — like the FileVault playbook. NOTE: still **not fired end-to-end on a real erase** — the test
  tenant reports 0 compliance records for the test device (no compliance vendor), so runs never
  reach a `NON_COMPLIANT` state → never quarantine → never reach the wipe prompt. B1 is verified
  against the connector contract, not yet by a live erase. (Earlier guidance in this file to
  "change it to string `\"true\"`" was wrong — a string still ≠ device_id.)
- **`get compliance status` needs the `Read Device Compliance Information` privilege — now
  RESOLVED and verified working.** It calls
  `/api/v1/conditional-access/device-compliance-information/...`; the OAuth API role needs
  **`Read Device Compliance Information`** (+ **`Read Computers`** for the connector's inventory
  existence pre-check). Without it → HTTP 403 `INVALID_PRIVILEGE` (the block on every run through
  2026-07-01). Granting it fixed the 403: run 57 (2026-07-06) returned `status: success`. Exact
  privilege name confirmed via Jamf's endpoint→privilege table (developer.jamf.com).
- **Verified connector datapaths:** resolvers return device id at `data.*.id` and type
  at `data.*.type` (NOT `jamf_device_id`/`device_type`); compliance is `data.*.compliance_state`.
- **Compliance decision — positive `NON_COMPLIANT` match (v2).** `complianceState` enum is
  `UNKNOWN / NON_COMPLIANT / COMPLIANT` (`jamf_client.py:340`). `is_compliant` escalates ONLY on
  `status == "success"` AND `compliance_state == "NON_COMPLIANT"`; COMPLIANT, UNKNOWN, None, an
  empty read, or a failed/403 read all fall to `note_no_drift` → END. This closes both a failed
  read escalating (fail-open-on-posture) and `UNKNOWN` over-escalating. **Verified live 2026-07-06**
  the empty-read case: run 57's compliance read succeeded with **0 records** and correctly routed
  to `note_no_drift` (no containment). The literal `NON_COMPLIANT` token is source-confirmed but
  **not yet observed on a live non-compliant device** — the test tenant reports 0 records (no
  compliance vendor), so the escalation branch is still unexercised end-to-end.
- **Playbooks must be authored in the VPE (Visual Playbook Editor), then exported to git.**
  Hand-authored `.json` graphs do NOT open — the utility/prompt/decision node schemas are
  intricate and decision branches are mapped by an edge-level `conditions:[{index,conditionKey}]`
  array (both branches share `<id>_out`), not by port name. SOAR blocks playbook create/delete
  via REST (`Method not allowed`); the working route is VPE build → export → commit, or import a
  correctly-formatted `.tgz` (py + json pair, no embedded python — the .py is a separate file).
  To rebuild by hand, clone node schemas from an existing validated playbook.
- **`update inventory` is mobile-only in the connector** — for computers, macOS recon runs
  on-device via a policy, not as an MDM command; calling it for a computer fails.
- **`lock device` / `wipe device` on a computer need a 6-digit `pin`** and their own remote-command
  privileges; they are queued MDM commands that actually lock/erase a real device — test on a spare.
- **Redeploy management framework 403 trap:** the API role needs BOTH `Send Computer Remote Command
  to Install Package` AND `Read Check-In` (Jamf Pro Server Settings). The Check-In read is the
  commonly-missed one. Full per-action privilege table is in `playbooks/README.md`.
