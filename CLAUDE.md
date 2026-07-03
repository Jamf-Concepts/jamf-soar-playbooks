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
| `playbooks/jamf_compliance_drift_remediation.py` | #4 | Compliance drift / MDM tamper: correct-first remediation, check, contain-if-needed, gated wipe. **SOAR-generated** (exported from the VPE 2026-07-03), so per-block `collect2`/param loops + `Custom Code` stubs, no hand-written `_dev()` helper or comments. Fail-safe compliance decision preserved (as `OR(compliant, status!=success)→END; else quarantine`). |
| `playbooks/jamf_compliance_drift_remediation.json` | #4 | Paired VPE graph (12 nodes / 13 edges), **exported from SOAR** (repo 2 `local`, playbook id 196) 2026-07-03. Descriptive node names; fail-safe `is_compliant`; wipe `pin` + `confirm:"true"` (string, `data_type:string`). `draft_mode:false`. `hash:""` — SOAR stamped a real hash on export but scrubbing the real asset name to `<your-jamf-asset>` invalidates it, and a generic template's placeholder graph can never match a real instance's hash (SOAR recomputes on import), so hash is deliberately blank. |
| `playbooks/jamf_compliance_drift_remediation.BUILD.md` | #4 | Block-by-block VPE build sheet (12 nodes; verified action names/datapaths/prereqs) + old→new rename map — the reliable authoring path |

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
- **A generic template's `.json` hash can never match a real instance.** SOAR stamps
  `coa.data.hash` over the graph on export, but the graph embeds the asset name — and a
  shareable template must carry `<your-jamf-asset>`, not a real asset. Scrubbing the real
  asset name (mandatory) invalidates SOAR's exported hash, and SOAR recomputes the hash on
  import against the customer's own wired asset regardless. So commit `hash:""` (proven
  importable Jul-1) rather than a hash that won't match the placeholder graph.
- **Wipe `confirm` differs between the `.py` and `.json` — by SOAR's own doing.** The exported
  `.json` graph stores `confirm: "true"` (string; the wipe node declares `data_type:string`),
  matching the 2026-07-01 live finding. SOAR's codegen then emitted `confirm: True` (Python
  boolean) in the generated `.py`. Runtime executes the `.py`, so a real erase would send the
  boolean. Left as-is (canonical export, not hand-edited) and **unverified on a real wipe** —
  the wipe has never fired (always denied at the gate). If a live wipe is ever rejected for a
  bad `confirm` type, change the `.py` to string `"true"` to match the graph/connector.
- **`get compliance status` needs a Jamf privilege.** It calls
  `/api/v1/conditional-access/device-compliance-information/...`; the OAuth API role
  must have the conditional-access / device-compliance read privilege (and the tenant
  must have conditional access configured) or it returns HTTP 403 `INVALID_PRIVILEGE`.
  Verified live 2026-07-01 — the compliance-drift template (#4) depends on this.
- **Verified connector datapaths:** resolvers return device id at `data.*.id` and type
  at `data.*.type` (NOT `jamf_device_id`/`device_type`); compliance is `data.*.compliance_state`.
- **Compliance decision must be fail-safe.** A `get compliance status` 403/error/empty result
  collects zero rows, so a decision that only tests `== "COMPLIANT"` treats a *failed read* as
  "not compliant" and silently escalates to contain → toward wipe. Gate escalation on
  `action_result.status == "success"` AND non-compliant, so a missing signal ends the run
  instead of escalating. (#4's `is_compliant` block does this.) The exact non-compliant
  `compliance_state` token is still unconfirmed — currently escalates on `!= "COMPLIANT"`.
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
| 2026-07-03 | `playbooks/jamf_compliance_drift_remediation.{py,json}` | **Closed the case-(d) empty-read gap in `is_compliant`** (PR-review finding). Added a third OR term to the IF→END group: `check_compliance:action_result.summary.total == 0`, so a *successful-but-empty* compliance read (zero records, `status==success`) ends the run instead of falling through to contain. Escalation now requires `status==success` AND `summary.total!=0` AND `compliance_state!=COMPLIANT`. `summary.total` is a declared numeric output of `get compliance status` (verified via `/rest/app/4/actions`), so the guard reliably fires. Edit made in the VPE and exported; during editing the block name reverted to `decision_7`, restored to `is_compliant` via string swap (safe — decisions feed no downstream datapaths, edges are numeric). Asset re-scrubbed, `hash` blanked (per the generic-template hash reality). **Note:** SOAR test playbook id 196 currently lags git by this one condition (lost during the VPE rename round-trip); immaterial to the template and the guard can't be live-tested anyway (403 short-circuits at `status!=success`). `.py` re-`py_compile`d; `.json` 12 nodes/13 edges. |
| 2026-07-03 | `CLAUDE.md`, `playbooks/{README.md,…BUILD.md}` | **PR-review fixes (#10, docs only — no `.py`/`.json` change).** (1) Corrected the wipe-`confirm` docs: earlier rows wrongly claimed the `.json` exports boolean `True` — the `.json` graph actually holds string `"true"` (`data_type:string`); only SOAR's generated `.py` has boolean `True`. Documented the py/json split + that it's unverified on a real erase. (2) **Scrubbed real specifics** from historical change-history rows (test serial, real asset names, SOAR host, exported hash prefix) → generic phrasing; a `git grep` for those tokens is now clean. (3) `BUILD.md` block-6 config rewritten to the committed OR/IF→END fail-safe form (was the logically-equivalent AND form, which a literal builder would mis-clone) + noted the case-(d) success-empty gap; approver-role corrected to the shipped `Administrator` default (was a nonexistent placeholder). |
| 2026-07-03 | `playbooks/jamf_compliance_drift_remediation.{py,json}` | **Re-synced from SOAR's canonical VPE export** (the editable `local` source-control repo). Opened → saved → exported the playbook and replaced both files with SOAR's own output, so the repo mirrors what actually runs. Verified the fail-safe survived the round-trip: SOAR renders `is_compliant` as `OR(compliance_state==COMPLIANT, status!=success)→END; else→quarantine` — same truth table as the hand-authored `AND(status==success, !=COMPLIANT)→escalate` (a failed/403 read never escalates). Wipe gate unchanged (`responses.0=="Yes"`). **Scrubbed** the leaked real test-env asset name (7× per file) → `<your-jamf-asset>`. Consequences of the export: `.py` is now SOAR-generated (per-block `collect2`/param loops + `Custom Code` stubs; hand-written `_dev()` helper + comments gone). **Wipe `confirm` py/json split:** the `.json` graph stores `confirm: "true"` (string, `data_type:string` — consistent with the 2026-07-01 live finding), but SOAR's own codegen emitted `confirm: True` (Python boolean) in the `.py`. Left both as SOAR produced them (don't hand-edit the canonical export); runtime executes the `.py` boolean — **still unverified on a real erase** (wipe has never fired). `hash` set back to `""` — SOAR's exported hash was computed over the real-asset graph and can't match the scrubbed placeholder graph (SOAR recomputes on import). `.py` re-`py_compile`d; `.json` re-validated (12 nodes/13 edges). |
| 2026-06-08 | All files | Initial governance skeleton created: README, CONTRIBUTING, CLAUDE.md, .gitignore, new-playbook issue template, docs/README.md. No actual playbooks yet. |
| 2026-06-30 | `playbooks/jamf_compliance_drift_remediation.{py,json}`, `playbooks/README.md` | New (branch `playbook/compliance-drift-remediation`, issue #4): first hand-authored template. Correct-first backbone (redeploy framework → blank push → update inventory → flag EA → re-check compliance → decide corrected? → contain (quarantine group + lock) if not → analyst approval prompt with irreversibility warning → gated wipe). Applies #8 naming/block conventions; all values are `<...>` placeholders, no secrets. `.py` validated (`py_compile`); `.json` is a 20-node best-effort VPE graph (`draft_mode: true`) to re-save in the editor. |
| 2026-07-01 | `playbooks/jamf_compliance_drift_remediation.{py,json}` | Datapaths + params corrected against the LIVE connector "Jamf Pro" v1.0.0 (queried via the SOAR REST API in the test env). Fixes: resolver device id `action_result.data.*.jamf_device_id`→`.id`, device type `.device_type`→`.type`; compliance decision `.compliant`(bool)→`.compliance_state`=="COMPLIANT"(string); update-extension-attribute param `extension_attribute_id`→`ea_id`; wipe `confirm` boolean→required string "true". Action names (`wipe device`, `add to static group`, `update extension attribute`) confirmed correct as-is (the 2026-06-09 handover's `erase_device`/`add_to_group`/`set_extension_attribute` were never the implemented names). Logic test still green. Still confirm the `compliance_state` enum value and wipe `confirm` token against a real device response. |
| 2026-07-01 | `playbooks/README.md`, `CLAUDE.md` | Documented the live-verified datapaths and the `get compliance status` prerequisite (conditional-access / device-compliance API privilege) after a live run in the SOAR test env: resolver + `get device by serial` succeeded against the real tenant (a test-device serial); `get compliance status` returned HTTP 403 `INVALID_PRIVILEGE` (Jamf API-role privilege gap, not a playbook bug). |
| 2026-07-01 | `playbooks/jamf_compliance_drift_remediation.{py,json}` | **Rebuilt to a VPE-valid graph and verified live end-to-end.** Hand-authored node schemas (utility/prompt/decision) didn't open in the editor; rebuilt by cloning the validated filevault playbook's node schemas + the edge-level `conditions` branch mapping (12 nodes / 13 edges). Dropped `update inventory` (connector rejects it for computers — macOS recon is policy-based, not MDM). Ran in SOAR against the real tenant with EVERY action green (resolve → redeploy → blank push → compliance → add-to-group → lock), held at the approval prompt, wipe never fired (denied). Committed files re-genericized: `<your-jamf-asset>`, `<your-quarantine-group>`, `<your-6-digit-pin>` (real test values kept only in the SOAR copy). |
| 2026-07-01 | `playbooks/README.md` | Added "Prerequisites — Jamf API role privileges" table (per-action privileges incl. the easy-to-miss **Read Check-In** for redeploy) + required-config-values note, so adopters configure privileges/pin/group before first run and avoid surprise 403s. |
| 2026-07-01 | `playbooks/jamf_compliance_drift_remediation.BUILD.md` | New: block-by-block VPE build sheet (the reliable authoring path — SOAR only accepts editor-built playbooks; API create/delete are blocked). |
| 2026-07-02 | `playbooks/jamf_compliance_drift_remediation.{py,BUILD.md}`, `playbooks/README.md`, `docs/README.md`, `CLAUDE.md` | **PR-review fixes (#4).** (1) **Leak scrubbed:** `BUILD.md` still named the real asset + test-device serial → `<...>` placeholders. (2) **Fail-safe compliance decision:** `is_compliant` now escalates only when `check_compliance` status==`success` AND `compliance_state != "COMPLIANT"`; a failed/403/empty read ends the run instead of silently escalating to contain→wipe (the live run's 403 had been doing exactly that). (3) **Block rename** to descriptive verbs per #8 (`resolve_device`, `redeploy_framework`, `force_checkin`, `check_compliance`, `is_compliant`, `quarantine_device`, `lock_device`, `approve_wipe`, `is_wipe_approved`, `wipe_device`); docs realigned (README/BUILD had ~6 stale/nonexistent block names, `WAIT_MINUTES`, `Approve`→`Yes`). (4) `BUILD.md` regenerated from the real 12-node graph (was describing an old 20-node design incl. dropped `update inventory`/flag EA). (5) `wipe_device` now sets the required 6-digit `pin`; prompt reworded to say containment was *queued*, not asserted. `.py` re-`py_compile`d. |
| 2026-07-02 | `playbooks/jamf_compliance_drift_remediation.json` | **Regenerated the VPE graph in-place** (programmatic edit of the known-good export, not a hand-authored graph) so SOAR runs the fixed playbook without manual VPE rebuild. Safe because: node `id`/`functionId` and all edges are numeric, so the 10 block renames are pure string swaps that don't touch wiring; the `is_compliant` fail-safe is added as an **OR** on the existing IF→END branch (`compliance_state==COMPLIANT` OR `status!=success`), so no branch edges were rewired (avoids inverting a wipe playbook). Also added wipe `pin`, updated prompt text. `blockly:false` (graph lives only in `coa.data`, nothing to desync); `hash` was already `""` and `draft_mode` left `false` to match the proven-importable Jul-1 `.tgz`. Repackaged as `jamf_compliance_drift_remediation.tgz` (gzip tar of the `.py`+`.json` at root — the exact 2-file export layout) for manual import. **Residual:** must be opened once in the VPE + live-run to confirm it loads and to recompute the hash — a hand-edited graph is draft until proven, and the fail-safe wants one confirming run. |
