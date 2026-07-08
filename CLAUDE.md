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
| `docs/README.md` | Plain-English changelog per the docs rule |

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

---

## Change History
| Date | File | What Changed |
|------|------|--------------|
| 2026-07-07 | `playbooks/Jamf - Lost or Stolen Device.{py,json}`, `README.md`, `docs/README.md`, `CLAUDE.md` | **New template: Lost or Stolen Device (#1, PR #16).** Resolve by serial (`artifact:*.cef.serialNumber` code-block `collect2`) → `decision_1` device-found → `decision_2` device_type → **mobile: enable lost mode / computer: lock device** → containment note → **analyst approval prompt** → wipe **only** on "Yes"; decline/timeout/no-device → note. **Each device_type branch carries its OWN note→prompt→wipe tail (no reconvergence)** — a shared downstream makes SOAR insert a join that waits for both branches and never fires (skips the note/prompt/wipe); this was hit + fixed live. Unique functionId per type (decision_1..4, code_1..5, prompt_1..2, wipe_device_1..2) — reusing an id per type → `function-redefined`. Wipe `confirm == device_id`, `device_type` = resolved type; lock PIN `000000` (6-digit; placeholder fails the connector's ASCII-digit validator). **Computer path LIVE-verified end-to-end** (resolve→lock→note→prompt→declined→End, no wipe); mobile path structurally identical, not yet live-run. **Review (pr-review-toolkit: code-reviewer + silent-failure-hunter): no Critical; wipe gate sound on both branches.** Applied: `.py`/`.json` note bodies synced; `code_5` distinguishes a genuine "no device matched" from a PARTIAL lookup where a platform was skipped for auth (`summary.skipped`) — so a privilege gap isn't read as a clean miss; notes/prompt **enumerate all matched devices** so the analyst sees the full wipe blast-radius (single-match hard-gate deferred to v2); reworded "(queued): failed". Distribution scrub: `<your-jamf-asset>` (5 blocks), approver → `<security-analyst-role>` role (2 prompts, I1 pattern), no leaked values (full credential sweep clean). Runnable copy on `playbook/lost-or-stolen-device`; scrubbed PR from `dist/lost-or-stolen-device`. Delivered to SOAR via `.tgz` import (source-control connection unreliable on the box). Enrichment (#5) + quarantine = v2. |
| 2026-07-07 | `playbooks/Jamf - Compromised User Device Sweep.{py,json}`, docs | **PR #12 review rework (#2).** Fixed the destructive spine (Sarah + Amanda): **C1** containment note built from real per-action `action_result.status` per device; **C2** wipe prompt enumerates all N devices ("Wipe ALL") + flags failed containment; **C3** device-resolution gate → "no devices found" terminal; **`confirm == device_id`** (was inert with `confirm:True`; fixed *with* C1–C3); **I1** per-platform quarantine groups; **I2** per-device 6-digit Mac lock PIN surfaced in the note; **I3** wipe-outcome note; dedup resolved devices by id; timeout no longer misreported as denial. Contain/wipe blocks use self-contained `collect2` (explicit datapath order). Design note: containment failure **surfaces in the prompt** rather than hard-blocking the wipe. Config: `<your-jamf-asset>`, `<your-computer/mobile-suspended-group-id>`, `<your-callback-number>`, `<your-approver-role>`. |
| 2026-07-07 | `playbooks/Jamf - IdP Breach Bulk Quarantine.{py,json}` | **PR #15 review fixes (Sarah).** (#1, gating) reconcile INPUT usernames vs resolved — a partial resolve failure (some accounts 403/zero-match in a multi-user breach) is now surfaced (`X in / Y resolved / Z failed`) in the preview AND results notes, warning when any account resolved to no device (was silently dropped). (#2, docs) qualified the "verified end-to-end" wording in `docs/README.md` — the runs cover the committed `.py`; the `.json` is a stub graph. Nits: `actionType` `contain`→`investigate` on the two read actions; prompt references the exact preview-note title. Also deduped by DISTINCT username (Sarah optional edge) so the same user across two artifacts counts once. Deferred (Sarah-optional): interpolate device count into the prompt; move the cap ahead of the compliance fan-out. `.py` `py_compile`-clean; `.json` 15/17, no warnings. **Re-validated + verified live (TEST 258, `passed_validation`): the approve run rendered the account reconciliation in BOTH the preview and results notes (`1 in / 1 resolved / 0 failed`) with honest per-action counts.** |
| 2026-07-07 | `playbooks/Jamf - IdP Breach Bulk Quarantine.{py,json}` | New (#6, PR #15): **IdP Breach Bulk Quarantine** — highest-risk template, built on Ron's #12 loop pattern + Sarah's #12 review. Resolve set (`get device by username` over `cef.sourceUserName`) → **devices-found gate (C3: status==success AND id present)** → compliance enrich (surfaced in the preview) → dry-run preview note → **aggregate batch-size cap** (in `build_quarantine_preview` code: over `MAX_DEVICES`=25 → abort note; gates the REAL total, not per-username `summary.total`) → **single up-front batched approval disclosing full scope (C2)** → sequential contain loop (add to static group [`group_id` per `device_type`, I1] + lock + blank push) → **results note built from real per-action statuses (C1: non-`success` incl. None counts as failed; lock/push labelled QUEUED-not-confirmed; reconciled vs approved count)**. **Bulk wipe excluded by default.** 15 nodes / 17 edges; `passed_validation: true`, no warnings. **Verified end-to-end live:** approve path (run 67 — resolve→…→add-to-group 5 + lock + blank push all `success` on a real Mac → results note), no-devices path (run 66 → note, no containment), and **aggregate-cap abort (run 69, MAX=0 → "batch too large", no approval/containment)**. Generic placeholders committed; real values only in a local TEST copy. **`.py`/`.json` divergence (documented):** the per-`device_type` group branch, real-status reporting, aggregate cap, and compliance-in-preview live in the `.py` (source of truth); the `.json` has single-value placeholders + stub code nodes. |
| 2026-07-06 | `CLAUDE.md`, `playbooks/Jamf - FileVault Recovery Access (macOS).{py,json}` | **PR #11 review fixes (#7) + re-sync with `main`.** Ron's re-review left two items live. **B1 (blocking, security):** the change-history rows in `CLAUDE.md` still printed the real recovery-lock password, dev serial, approver, phone, and asset the scrub had replaced everywhere else — redacted them (describe the scrub without the literals; a repo-wide `git grep` for all five tokens is now clean). **The exposed recovery-lock password is in git history; rotating it on the tenant is tracked as an operational follow-up (#14)** — the connector repo is confirmed clean (no trace), and for a private repo rotating the credential is the accepted mitigation (git-history rewrite not warranted). Both prior `SetRecoveryLock` commands failed (`connection to service`), so it likely never applied; rotate once the test Mac is reachable. **I1 (safety gate):** the wipe-approval prompt set `user="<security-analyst-role>"` / `role=None`, so a placeholder in the `user=` slot won't resolve to a SOAR user and the analyst-in-the-loop gate can fail to route on import — flipped to `role="<security-analyst-role>"` / `user=None` (`.py`) and approver node `type:"user"→"role"` (`.json`), matching PR #10. I2 (wipe result note) / I3 (prompt names the target device) staged as follow-ups. Then **merged `origin/main` into `dist/filevault-recovery-access`** (PR #10 / #4 compliance-drift landed on `main`, touching the shared docs) — resolved doc conflicts in `CLAUDE.md` / `README.md` / `docs/README.md` (combined both sides; #10 now **merged**, #11 **in review**). `.py` `py_compile`-clean; `.json` valid. |
| 2026-07-06 | `playbooks/` (merged from main, PR #9) | First playbook (#5, PR #9): **Device Enrichment & Triage** (read-only). Shipped as an **Input sub-playbook** (`Jamf - Device Enrichment (Input)`: get device + 6 enrich actions → format → `enrichment_summary` output) plus an **Automation wrapper** (`Jamf - Device Enrichment and Triage`: resolve by username → call sub-playbook → `add_note`). Asset scrubbed to `<your-jamf-asset>`. Adaptation points: sub-playbook repo reference (`jamf-soar-playbooks/…`) re-linked on import; resolver reads `artifact.*.cef.sourceUserName`; serial/name/MAC + mobile branches deferred. *(Row carried over during the rebase onto main.)* |
| 2026-07-06 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}` | **v3 — re-review fixes (Ron's B3 blocker + 2 hardening items); validated + live-run green.** 19→**23 nodes / 28 edges**. (B3) new `wipe_ok` decision on `wipe_device:action_result.status == success` → `note_wipe_queued`; else → new `note_wipe_failed` — stops the false "ERASE queued" note when a wipe errors (HTTP 500 / no managementId / 403). (Hardening) new `has_serial` gate before `resolve_device` (empty serial → `note_no_serial`, no silent dead-end); approval-prompt reworded to "quarantine and lock were QUEUED (lock is async — queued, not confirmed applied)". Also dropped the echoed `pin` from `wipe_device`. Imported clean (`passed_validation: true`, no warnings) and ran green (run 61): `has_serial` correctly passed through (serial present), same compliant/empty path as v2. New failure/edge paths (no-serial, wipe-failed) not triggerable by a healthy device — verified by validation, not live. `.py` matches the 23-node graph 1:1. |
| 2026-07-06 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json,BUILD.md}` | **Renamed to the `Jamf - <Scenario>` standard (Ron's filename nit).** `git mv` from `jamf_compliance_drift_remediation.*` → `Jamf - Compliance Drift and MDM Tamper Remediation.*`, matching sibling templates (`Jamf - FileVault Recovery Access (macOS)`, `Jamf - Device Enrichment and Triage`) and the display name. The scenario's `/` ("Compliance Drift / MDM Tamper") was reworded to "and" so the filename carries no path separator. Dropped the earlier "snake_case is intentional" note. Internal title (`.py` docstring, `.json` description) aligned; all doc references updated. No logic/graph change. |
| 2026-07-06 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}` | **v2 rebuild — all flagged review logic; built, validated, and live-run green.** Rebuilt the graph (12→**19 nodes / 22 edges**) from the known-good export + FileVault's validated `code`/`decision` schemas. Fixes: **B1** wipe `confirm` → resolve-id datapath; **B2/I1** `is_compliant` positive `NON_COMPLIANT` match (AND `status==success`), else → manual-review note; **I3** new `containment_ok` gate (quarantine AND lock succeeded) before the wipe prompt; **I4** new `device_found` gate; **I2/I5** an `add_note` on every terminal path (no-device / no-drift / containment-failed / wipe-declined / wipe-queued); **I8** dropped undeclared `device_type` from redeploy, added it to quarantine (computer-only scope). Imported to SOAR clean (`passed_validation: true`, **no node warnings** — old node-7 warning gone) and **ran green end-to-end** (live run against the test device via the wired test asset): resolve → device_found → redeploy → blank push → **compliance read succeeded** (privilege now granted; 0 records) → `is_compliant` correctly routed to `note_no_drift` (no escalation on an empty read). Repo `.py`/`.json` are **byte-for-byte identical to SOAR's canonical stored copy** (verified). Not exercised: quarantine→lock→prompt→wipe (B1) — the tenant returns 0 compliance records for the test device, so no `NON_COMPLIANT` state is ever produced. `.py` `py_compile`-clean; committed files stay generic (placeholders); real test values (asset, group, PIN) live only in a local TEST `.tgz`, never committed. |
| 2026-07-06 | `playbooks/{README.md,…BUILD.md}`, `CLAUDE.md`, `docs/README.md` | **PR #10 deep-pass review — more doc-only fixes; logic deferred.** Verified each finding against the connector source + the committed graph, fixed doc-only ones: (I6) `BUILD.md` block-11 row no longer teaches the broken wipe wiring — now wires `confirm` to the resolve-id datapath with a "still broken in the committed files, fix in VPE before merge" note; (I7) walked back the "canonical export" claim — confirmed node 7 (`is_compliant`) in the `.json` carries `warnings:{config:["Reconfigure invalid datapath."]}` + a hand-minted comparison key (`comparison_key_a65ee7ac-…`) from patching in the case-(d) guard outside a clean round-trip, so BUILD.md + the File Map now say it's not import-clean and needs a VPE re-open/re-export; (I8) surfaced the computer-only scope in the adopter-facing `playbooks/README.md`. **Deferred (logic, VPE + live re-verify):** B1 wire `confirm→device_id`, B2/I1 positive `NON_COMPLIANT` match + UNKNOWN/None→manual-review, I3 gate wipe on containment success, I4/I5 device-found + wipe-declined/timeout notes, I8 wiring, approver-role placeholder. |
| 2026-07-06 | `CLAUDE.md`, `playbooks/README.md`, `docs/README.md` | **PR #10 second review (Sarah) — doc-only fixes; logic deferred.** Verified against the connector source, then fixed docs only: (1) **C1 wrong guidance** — `jamf_connector.py:1674-1680` requires wipe `confirm` to *exactly equal `device_id`*; our prior "change to string `\"true\"`" advice was wrong (still ≠ device_id, wipe can never fire). Recorded the real bug + correct fix (wire `confirm` to `resolve_device:...data.*.id`) as a pending VPE edit. (2) **I5 privilege table** — `lock`/`wipe`/`send blank push` queue via `/api/v2/mdm/commands`, so they need the v2 **Send MDM command information in Jamf Pro API** privilege, not Classic per-command ones (`jamf_connector.py:1576-1577`); added the blank-push row. (3) **I5 overclaim** — walked back "verified end-to-end / EVERY action green"; the live compliance read 403'd and only the wipe-deny path ran. **Deferred (logic, needs VPE + live re-verify):** C1 code fix, C2 (failed read → manual-review path, not silent END), I1 positive `NON_COMPLIANT` match, I2 terminal-path notes, I3 gate wipe on containment success, I4 `device_type` branching, approver-role placeholder. |
| 2026-07-06 | `README.md`, `playbooks/README.md` | **PR #10 review fixes (docs only — no `.py`/`.json` change).** (1) **Blocking:** root `README.md` was stale — flipped the "no playbooks built yet" status note and added a **Compliance drift / MDM tamper — In review (PR #10)** row to the Planned-templates table (matches the pattern PR #9 set). (2) Noted the issue-#4 **enrichment stage as deferred** in `playbooks/README.md` (reuse PR #9's enrichment Input engine once it merges; `update inventory` stays permanently dropped for computers). (3) Documented the **`snake_case` filename** deviation as intentional (the `/` in `Jamf - <Scenario>` makes SOAR export it as a subdirectory; display name inside SOAR is unchanged). |
| 2026-07-03 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}` | **Closed the case-(d) empty-read gap in `is_compliant`** (PR-review finding). Added a third OR term to the IF→END group: `check_compliance:action_result.summary.total == 0`, so a *successful-but-empty* compliance read (zero records, `status==success`) ends the run instead of falling through to contain. Escalation now requires `status==success` AND `summary.total!=0` AND `compliance_state!=COMPLIANT`. `summary.total` is a declared numeric output of `get compliance status` (verified via `/rest/app/4/actions`), so the guard reliably fires. Edit made in the VPE and exported; during editing the block name reverted to `decision_7`, restored to `is_compliant` via string swap (safe — decisions feed no downstream datapaths, edges are numeric). Asset re-scrubbed, `hash` blanked (per the generic-template hash reality). **Note:** SOAR test playbook id 196 currently lags git by this one condition (lost during the VPE rename round-trip); immaterial to the template and the guard can't be live-tested anyway (403 short-circuits at `status!=success`). `.py` re-`py_compile`d; `.json` 12 nodes/13 edges. |
| 2026-07-03 | `CLAUDE.md`, `playbooks/{README.md,…BUILD.md}` | **PR-review fixes (#10, docs only — no `.py`/`.json` change).** (1) Corrected the wipe-`confirm` docs: earlier rows wrongly claimed the `.json` exports boolean `True` — the `.json` graph actually holds string `"true"` (`data_type:string`); only SOAR's generated `.py` has boolean `True`. Documented the py/json split + that it's unverified on a real erase. (2) **Scrubbed real specifics** from historical change-history rows (test serial, real asset names, SOAR host, exported hash prefix) → generic phrasing; a `git grep` for those tokens is now clean. (3) `BUILD.md` block-6 config rewritten to the committed OR/IF→END fail-safe form (was the logically-equivalent AND form, which a literal builder would mis-clone) + noted the case-(d) success-empty gap; approver-role corrected to the shipped `Administrator` default (was a nonexistent placeholder). |
| 2026-07-03 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}` | **Re-synced from SOAR's canonical VPE export** (the editable `local` source-control repo). Opened → saved → exported the playbook and replaced both files with SOAR's own output, so the repo mirrors what actually runs. Verified the fail-safe survived the round-trip: SOAR renders `is_compliant` as `OR(compliance_state==COMPLIANT, status!=success)→END; else→quarantine` — same truth table as the hand-authored `AND(status==success, !=COMPLIANT)→escalate` (a failed/403 read never escalates). Wipe gate unchanged (`responses.0=="Yes"`). **Scrubbed** the leaked real test-env asset name (7× per file) → `<your-jamf-asset>`. Consequences of the export: `.py` is now SOAR-generated (per-block `collect2`/param loops + `Custom Code` stubs; hand-written `_dev()` helper + comments gone). **Wipe `confirm` py/json split:** the `.json` graph stores `confirm: "true"` (string, `data_type:string` — consistent with the 2026-07-01 live finding), but SOAR's own codegen emitted `confirm: True` (Python boolean) in the `.py`. Left both as SOAR produced them (don't hand-edit the canonical export); runtime executes the `.py` boolean — **still unverified on a real erase** (wipe has never fired). `hash` set back to `""` — SOAR's exported hash was computed over the real-asset graph and can't match the scrubbed placeholder graph (SOAR recomputes on import). `.py` re-`py_compile`d; `.json` re-validated (12 nodes/13 edges). |
| 2026-06-08 | All files | Initial governance skeleton created: README, CONTRIBUTING, CLAUDE.md, .gitignore, new-playbook issue template, docs/README.md. No actual playbooks yet. |
| 2026-06-30 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}`, `playbooks/README.md` | New (branch `playbook/compliance-drift-remediation`, issue #4): first hand-authored template. Correct-first backbone (redeploy framework → blank push → update inventory → flag EA → re-check compliance → decide corrected? → contain (quarantine group + lock) if not → analyst approval prompt with irreversibility warning → gated wipe). Applies #8 naming/block conventions; all values are `<...>` placeholders, no secrets. `.py` validated (`py_compile`); `.json` is a 20-node best-effort VPE graph (`draft_mode: true`) to re-save in the editor. |
| 2026-07-01 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}` | Datapaths + params corrected against the LIVE connector "Jamf Pro" v1.0.0 (queried via the SOAR REST API in the test env). Fixes: resolver device id `action_result.data.*.jamf_device_id`→`.id`, device type `.device_type`→`.type`; compliance decision `.compliant`(bool)→`.compliance_state`=="COMPLIANT"(string); update-extension-attribute param `extension_attribute_id`→`ea_id`; wipe `confirm` boolean→required string "true". Action names (`wipe device`, `add to static group`, `update extension attribute`) confirmed correct as-is (the 2026-06-09 handover's `erase_device`/`add_to_group`/`set_extension_attribute` were never the implemented names). Logic test still green. Still confirm the `compliance_state` enum value and wipe `confirm` token against a real device response. |
| 2026-07-01 | `playbooks/README.md`, `CLAUDE.md` | Documented the live-verified datapaths and the `get compliance status` prerequisite (conditional-access / device-compliance API privilege) after a live run in the SOAR test env: resolver + `get device by serial` succeeded against the real tenant (a test-device serial); `get compliance status` returned HTTP 403 `INVALID_PRIVILEGE` (Jamf API-role privilege gap, not a playbook bug). |
| 2026-07-01 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,json}` | **Rebuilt to a VPE-valid graph and verified live end-to-end.** Hand-authored node schemas (utility/prompt/decision) didn't open in the editor; rebuilt by cloning the validated filevault playbook's node schemas + the edge-level `conditions` branch mapping (12 nodes / 13 edges). Dropped `update inventory` (connector rejects it for computers — macOS recon is policy-based, not MDM). Ran in SOAR against the real tenant (resolve → redeploy → blank push → compliance → add-to-group → lock), held at the approval prompt, wipe never fired (denied). **Correction (PR #10 review I5 — earlier "EVERY action green / verified end-to-end" overclaimed):** `get compliance status` 403'd (API-role privilege gap) and only the wipe-*deny* path ran; the compliance read and the wipe path are NOT verified live. Committed files re-genericized: `<your-jamf-asset>`, `<your-quarantine-group>`, `<your-6-digit-pin>` (real test values kept only in the SOAR copy). |
| 2026-07-01 | `playbooks/README.md` | Added "Prerequisites — Jamf API role privileges" table (per-action privileges incl. the easy-to-miss **Read Check-In** for redeploy) + required-config-values note, so adopters configure privileges/pin/group before first run and avoid surprise 403s. |
| 2026-07-01 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.BUILD.md` | New: block-by-block VPE build sheet (the reliable authoring path — SOAR only accepts editor-built playbooks; API create/delete are blocked). |
| 2026-07-02 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.{py,BUILD.md}`, `playbooks/README.md`, `docs/README.md`, `CLAUDE.md` | **PR-review fixes (#4).** (1) **Leak scrubbed:** `BUILD.md` still named the real asset + test-device serial → `<...>` placeholders. (2) **Fail-safe compliance decision:** `is_compliant` now escalates only when `check_compliance` status==`success` AND `compliance_state != "COMPLIANT"`; a failed/403/empty read ends the run instead of silently escalating to contain→wipe (the live run's 403 had been doing exactly that). (3) **Block rename** to descriptive verbs per #8 (`resolve_device`, `redeploy_framework`, `force_checkin`, `check_compliance`, `is_compliant`, `quarantine_device`, `lock_device`, `approve_wipe`, `is_wipe_approved`, `wipe_device`); docs realigned (README/BUILD had ~6 stale/nonexistent block names, `WAIT_MINUTES`, `Approve`→`Yes`). (4) `BUILD.md` regenerated from the real 12-node graph (was describing an old 20-node design incl. dropped `update inventory`/flag EA). (5) `wipe_device` now sets the required 6-digit `pin`; prompt reworded to say containment was *queued*, not asserted. `.py` re-`py_compile`d. |
| 2026-07-02 | `playbooks/Jamf - Compliance Drift and MDM Tamper Remediation.json` | **Regenerated the VPE graph in-place** (programmatic edit of the known-good export, not a hand-authored graph) so SOAR runs the fixed playbook without manual VPE rebuild. Safe because: node `id`/`functionId` and all edges are numeric, so the 10 block renames are pure string swaps that don't touch wiring; the `is_compliant` fail-safe is added as an **OR** on the existing IF→END branch (`compliance_state==COMPLIANT` OR `status!=success`), so no branch edges were rewired (avoids inverting a wipe playbook). Also added wipe `pin`, updated prompt text. `blockly:false` (graph lives only in `coa.data`, nothing to desync); `hash` was already `""` and `draft_mode` left `false` to match the proven-importable Jul-1 `.tgz`. Repackaged as `Jamf - Compliance Drift and MDM Tamper Remediation.tgz` (gzip tar of the `.py`+`.json` at root — the exact 2-file export layout) for manual import. **Residual:** must be opened once in the VPE + live-run to confirm it loads and to recompute the hash — a hand-edited graph is draft until proven, and the fail-safe wants one confirming run. |
| 2026-07-02 | playbooks/Jamf - FileVault Recovery Access (macOS).{json,py}, CLAUDE.md, docs/README.md | **First playbook: renamed + genericized (#7).** (1) **Renamed in the SOAR VPE** `Jamf - FileVault Key / Recovery Access (macOS)` → `Jamf - FileVault Recovery Access (macOS)` to kill the `/` that had become an accidental `playbooks/… Key /…` subdirectory on export (SOAR re-pushed clean filenames; old slashed files gone). (2) **Export-scrubbed** the `.py` + `.json` in sync for template distribution: the dev asset name → `<your-jamf-asset>` (7 blocks), the approver username → `<security-analyst-role>`, and a **real recovery-lock password**, a test lock-message, and a test phone number → placeholders (`<your-recovery-lock-password>` / `<your-lock-screen-message>` / `<your-support-phone>`), wipe prompt reworded to state irreversibility (#8), docstring filled. `.json` re-validated; `.py` re-parsed; no dev values remain except the deliberately-kept serial + PIN. **Context:** local repo was 9 commits stale — the remote had advanced via SOAR VPE saves adding the resolve→(device-found?)→…→notify(note stub)→approval→wipe/decline/no-device branches; reset local to the remote tip (dropped an obsolete local scrub done on the pre-rename files) before re-scrubbing. **Still open:** notify step is a note STUB (build a restricted-channel Slack notify), serial hardcoding (blocked on #8), block renaming (VPE). |
| 2026-07-03 | playbooks/Jamf - FileVault Recovery Access (macOS).{json,py}, CLAUDE.md, docs/README.md | **Un-hardcoded the serial + prepped distribution PR (#7).** (1) **Serial un-hardcoded in the VPE:** `serial_number` now binds the datapath `artifact:*.cef.serialNumber` (SOAR generates a `collect2`) instead of the previously-hardcoded dev serial — adopting #4's proven pattern (a code-block `collect2` sidesteps the VPE picker's literal-trap; verified in the pushed `.json`/`.py`). #8 "contract" is effectively settled by this pattern. (2) **Recovered a dropped playbook:** the earlier scrub push (`fd52b32`, placeholder asset) made SOAR drop the playbook when the non-persistent source-control connection re-synced; restored the runnable version (`18ce9f7`), re-created the connection, playbook reappeared. **Lesson:** the SOAR-synced dev branch must stay RUNNABLE — the scrubbed distribution template can't be its tip. (3) **Distribution split:** feature branch `playbook/filevault-recovery-access` stays runnable (SOAR-happy); scrubbed template lives on `dist/filevault-recovery-access` → PR to `main` (asset / recovery-lock password / phone / message / approver → placeholders, prompt irreversibility, docstring; serial datapath + PIN kept). **Still open:** notify step is a note STUB; block renaming (VPE). |
