# VPE Build Sheet — Jamf - Compliance Drift / MDM Tamper Remediation (Issue #4)

How to (re)build this template in SOAR's **Visual Playbook Editor (VPE)**. Action names,
parameters, and datapaths are **verified live** against the connector "Jamf Pro" v1.0.0.
Replace every `<...>` with your environment's value — no real asset names, group ids, PINs,
or serials belong in this file.

SOAR playbooks must be authored in the VPE — build here, and SOAR generates valid files.

> ✅ **The committed graph is now v2 — 19 nodes / 22 edges** (PR #10 review rebuild). It imported
> to SOAR clean (`passed_validation: true`, no node warnings) and **ran green live** (run 57).
> **Build/read from ["Target rebuild (v2)"](#target-rebuild-v2--pr-10-review) below — that is the
> shipped design.** Sections 0–7 that follow describe the superseded **v1 (12-node)** graph and
> are kept only as history; do not build them.

---

## 0. Create the playbook
- SOAR → **Playbooks → + Playbook**.
- Name: **`Jamf - Compliance Drift / MDM Tamper Remediation`**
- Type: **Automation** · Operates on label: **`<your-noncompliant-label>`** (e.g. `jamf_noncompliant_device`)
- You start with a **START** block on the canvas. Build left→right, connecting each block's
  output dot to the next block's input dot.

## VPE mechanics (quick reference)
- **Add a block:** drag from the START/out dot, or click **+**. Pick the block type:
  **Action** (a connector action), **Decision**, or **Prompt**.
- **Action block:** choose app **Jamf Pro** (asset **`<your-jamf-asset>`**), then the action.
  Fill each parameter — click the field → **Datapath** to reference an earlier block's output.
- **Datapath format:** `<block_name>:action_result.data.*.<field>`. The resolver's device id is
  `...data.*.id` and type is `...data.*.type` (NOT `jamf_device_id`).
- Connect blocks by dragging between the dots. Decisions/prompts have multiple out-paths.
- **Block names:** use the descriptive names below (issue #8 convention) — not the VPE
  auto-numbered defaults (`get_device_by_serial_1`). Rename each block after adding it.

---

## The blocks (in order) — 12 nodes

| # | Block name (type) | Action / config | Key parameters |
|---|---|---|---|
| 1 | **on_start** (START) | — | — |
| 2 | **resolve_device** (action) | `get device by serial` | `serial_number` ← `artifact:*.cef.serialNumber` |
| 3 | **redeploy_framework** (action) | `redeploy management framework` | `device_id` ← `resolve_device:...data.*.id` · `device_type` ← `resolve_device:...data.*.type` |
| 4 | **force_checkin** (action) | `send blank push` | `device_id` ← resolve id · `device_type` ← resolve type |
| 5 | **check_compliance** (action) | `get compliance status` | `device_id` ← resolve id · `device_type` ← resolve type |
| 6 | **is_compliant** (decision) | fail-safe conditions below | escalate → 7; else → END |
| 7 | **quarantine_device** (action) | `add to static group` | `device_id` ← resolve id · `group_name` = `<your-quarantine-group>` |
| 8 | **lock_device** (action) | `lock device` | `device_id` ← resolve id · `device_type` ← resolve type · `pin` = `<your-6-digit-pin>` · `message` = `<your-return-message>` · `phone_number` = `<your-callback-number>` |
| 9 | **approve_wipe** (prompt) | approval gate, config below | → 10 |
| 10 | **is_wipe_approved** (decision) | conditions below | approved → 11; else → END |
| 11 | **wipe_device** (action) | `wipe device` | `device_id` ← resolve id · `device_type` ← resolve type · `confirm` ← **resolve id** (same datapath as `device_id`; see note) · `pin` = `<your-6-digit-pin>` |
| 12 | **on_finish** (END) | — | — |

> **Block 11 `confirm` — critical (PR #10 review B1):** do NOT set `confirm` to a checkbox /
> boolean `True` / string `"true"`. The connector's wipe gate (`jamf_connector.py:1674-1680`)
> rejects the erase unless `confirm` **exactly equals `device_id`** — so `confirm` must be wired
> to the same resolved device-id datapath as `device_id` (`resolve_device:action_result.data.*.id`),
> exactly like the FileVault playbook. Any truthy-flag value yields `WIPE_NOT_CONFIRMED` and the
> approved wipe silently never fires. **The committed `.py`/`.json` still carry the broken
> truthy value — this must be corrected in the VPE before merge.**

> **Dropped vs. earlier drafts:** `update inventory` (connector rejects it for computers —
> macOS recon is policy-based, not MDM), the baseline/re-check compliance pair (single
> `check_compliance` now), the `update extension attribute` "flag under review" step, the
> `get configuration profiles`/`get extension attributes` enrichment, and the add-note
> utility blocks. Redeploy + blank push force a check-in; one compliance read decides.

---

## Decision configs

**Block 6 — "is_compliant" (fail-safe)**
Escalate to containment ONLY when the read succeeded AND the device is not compliant.
A failed/403 read or an empty/unknown value must fall through to END, never to containment.
The committed graph expresses this as the **safe-end-first** form (this is what SOAR's VPE
exports — match it so the build stays identical to the committed `.json`):
- **IF** (path → END) — `logical_operator = OR`, any one condition ends the run:
  - `check_compliance:action_result.data.*.compliance_state` **==** `COMPLIANT`
  - `check_compliance:action_result.status` **!=** `success`
  - `check_compliance:action_result.summary.total` **==** `0`  *(empty-read guard)*
- **ELSE** (path → block 7, contain): read succeeded AND returned ≥1 record AND device is not compliant.

This is logically equivalent (De Morgan) to "escalate when `status == success` AND
`summary.total != 0` AND `compliance_state != COMPLIANT`" — either wording yields the same
behaviour, but build the OR/IF→END form to match the committed graph exactly.

> **The third condition (`summary.total == 0`) closes the case-(d) gap:** a *successful-but-empty*
> compliance read (status `success`, zero records) would otherwise satisfy neither of the first
> two IF conditions and fall through to contain. `summary.total` is a declared numeric output of
> `get compliance status`, so `== 0` reliably ends the run on an empty read. (Note: this branch
> can't be live-exercised while `get compliance status` still 403s in the test env — a failed
> read short-circuits at `status != success` first — but it's schema-sound.)
> **Token now known from the connector source (was "still to confirm"):** `complianceState` is
> the enum **`UNKNOWN / NON_COMPLIANT / COMPLIANT`** (`jamf_client.py:340`). The v2 rebuild below
> positively matches `NON_COMPLIANT` instead of negating `COMPLIANT`. (Still can't be *live*-run
> until the conditional-access privilege lands, but the match value is no longer a guess.)

**Block 10 — "is_wipe_approved"**
- **IF** (path → block 11, wipe): `approve_wipe:action_result.summary.responses.0` **==** `Yes`
- **ELSE** (path → END, denied/timed-out)

---

## Prompt config — Block 9 "approve_wipe"
- **Approver:** the committed playbook ships the `Administrator` role as the default; change it
  to your security-analyst role (or the container owner) per environment.
- **Response time:** 30 minutes.
- **Response 1 (required, yes/no):**
  - Prompt text: **"Device is still reported non-compliant after automated correction. Quarantine + lock were queued (verify they applied). Approve device WIPE? This ERASES the device and is IRREVERSIBLE."**
  - Options: **Yes / No**

---

## Customer-config placeholders to fill (per environment)
- Jamf asset: `<your-jamf-asset>` (every action block)
- Trigger label: `<your-noncompliant-label>`
- Quarantine static group: `<your-quarantine-group>` (block 7)
- Lock/wipe PIN: `<your-6-digit-pin>` (blocks 8, 11 — the placeholder fails connector validation)
- Lock message + callback number: `<your-return-message>` / `<your-callback-number>` (block 8)
- Approver role: block 9 ships `Administrator` by default — change per environment

## Prerequisite (Jamf side)
`get compliance status` needs the API role to have the **conditional-access / device-compliance
read** privilege (and the tenant must have conditional access configured), or it returns
HTTP 403 `INVALID_PRIVILEGE`. See the full per-action privilege table in `README.md`.

## Save & test
1. **Save** the playbook (VPE compiles it — fixes any block errors it flags).
2. **Run** on a container with a `serialNumber` artifact (use a spare/test device serial).
3. Watch it execute block-by-block in the debugger. Destructive `wipe device` only fires
   after **Yes** at the prompt.

---

## Target rebuild (v2) — PR #10 review

Build this in the VPE to resolve every flagged finding. It supersedes the 12-node graph above.
Grows the graph to **~19 nodes** (adds two decisions + five terminal notes). Each item cites the
review finding it closes. Datapaths/enum values are verified against the connector source
(`jamf_connector.py`, `jamf_client.py`).

### Why in the VPE (not a hand-edit)
The current node-7 warning (I7) came from patching the graph outside the editor. Build v2 **in
the VPE** so every node is editor-clean, then export → scrub asset → blank hash → commit. Do NOT
hand-edit the `.json`.

### v2 block list (in order)

| # | Block name (type) | Action / config | Out-paths | Closes |
|---|---|---|---|---|
| — | on_start | — | → resolve_device | — |
| 1 | resolve_device (action) | `get device by serial` — `serial_number` ← artifact `serialNumber` | → device_found | — |
| 2 | **device_found** (decision) | IF `resolve_device:action_result.data.*.id` **!=** `""` | IF → redeploy_framework · ELSE → note_no_device | **I4** |
| 3 | note_no_device (note) | "No Jamf device matched the serial — ending; nothing to remediate." | → on_finish | I4 |
| 4 | redeploy_framework (action) | `redeploy management framework` — `device_id` ← resolve id · **DROP `device_type`** (undeclared; computer-only action) | → force_checkin | I8 |
| 5 | force_checkin (action) | `send blank push` — `device_id` ← resolve id · `device_type` ← resolve type | → check_compliance | — |
| 6 | check_compliance (action) | `get compliance status` — `device_id` ← resolve id · `device_type` ← resolve type | → is_compliant | — |
| 7 | **is_compliant** (decision) | IF (`...status` **==** `success` **AND** `...data.*.compliance_state` **==** `NON_COMPLIANT`), `logical_operator = AND` | IF → quarantine_device · ELSE → note_no_drift | **B2 / I1** |
| 8 | note_no_drift (note) | "Compliant / UNKNOWN / no compliance data / read failed — no containment taken. Manual review if drift is still suspected." | → on_finish | B2 / I2 |
| 9 | quarantine_device (action) | `add to static group` — `device_id` ← resolve id · **ADD `device_type` ← resolve type** · `group_name` = `<your-quarantine-group>` | → lock_device | I8 |
| 10 | lock_device (action) | `lock device` — `device_id` ← resolve id · `device_type` ← resolve type · `pin` = `<your-6-digit-pin>` · `message` · `phone_number` | → containment_ok | — |
| 11 | **containment_ok** (decision) | IF (`quarantine_device:action_result.status` **==** `success` **AND** `lock_device:action_result.status` **==** `success`), `logical_operator = AND` | IF → approve_wipe · ELSE → note_containment_failed | **I3** |
| 12 | note_containment_failed (note) | "Quarantine and/or lock did not succeed — device may be uncontained. Manual review required before any wipe." | → on_finish | I3 / I2 |
| 13 | approve_wipe (prompt) | required Yes/No; 30-min; approver `<your-security-analyst-role>` (see note) | → is_wipe_approved | Sug |
| 14 | is_wipe_approved (decision) | IF `approve_wipe:action_result.summary.responses.0` **==** `Yes` | IF → wipe_device · ELSE → note_wipe_declined | — |
| 15 | note_wipe_declined (note) | "Wipe declined or prompt timed out — device left quarantined + locked; follow up manually." | → on_finish | I5 / I2 |
| 16 | wipe_device (action) | `wipe device` — `device_id` ← resolve id · `device_type` ← resolve type · **`confirm` ← resolve id** (same datapath as device_id) · `pin` = `<your-6-digit-pin>` | → note_wipe_queued | **B1** |
| 17 | note_wipe_queued (note) | "ERASE_DEVICE command QUEUED (not a confirmed erase) — device wipes on next check-in." | → on_finish | I2 / N2 |
| — | on_finish | — | — | — |

### Critical wiring details
- **B1 — `wipe_device.confirm`:** set the `confirm` param via **Datapath** to
  `resolve_device:action_result.data.*.id` (the *same* value bound to `device_id`). The connector
  requires `confirm == device_id` (`jamf_connector.py:1674-1680`); a checkbox/boolean/`"true"`
  yields `WIPE_NOT_CONFIRMED` and the approved wipe silently never fires.
- **B2 / I1 — `is_compliant`:** positively match `NON_COMPLIANT` (enum from `jamf_client.py:340`:
  `UNKNOWN / NON_COMPLIANT / COMPLIANT`). Escalate **only** on `status == success` AND
  `compliance_state == NON_COMPLIANT`. Everything else — `COMPLIANT`, `UNKNOWN`, `None`, empty
  read, or a failed/403 read — falls to `note_no_drift` → END. A failed/unknown read now goes to
  a *visible manual-review note*, not a silent all-clear (fixes C2 fail-open-on-posture) and not
  an over-escalation of `UNKNOWN` (fixes I1). The prompt text (block 13) can now truthfully say
  "reported NON_COMPLIANT".
- **I3 — `containment_ok`:** gate the wipe prompt on containment actually succeeding. Note `lock
  device` only *queues* an MDM command on an offline device (connector reports queued, never
  "locked"), so treat a non-`success` status as uncontained → manual review, not a wipe prompt.
- **I8 — device_type:** drop the undeclared `device_type` from `redeploy_framework`; add
  `device_type ← resolve type` to `quarantine_device`. `redeploy management framework` is
  computer-only — this template is **scoped to computers** (documented in `README.md`); a mobile
  branch is a later enhancement.
- **Notes (I2):** every terminal path now writes a container note (no-device, no-drift,
  containment-failed, wipe-declined, wipe-queued). Use the same note mechanism as PR #11 for
  consistency. Word the wipe note "queued", never "wiped".

### Status (2026-07-06) — built, validated, run green
- **Built + imported clean:** `passed_validation: true`, no node warnings; the committed
  `.py`/`.json` are byte-for-byte identical to SOAR's canonical stored copy.
- **Live run 57 (green):** resolve → device_found → redeploy → blank push → **compliance read
  succeeded** (privilege granted — see below) → 0 records → `is_compliant` correctly routed to
  `note_no_drift`. Device-found gate, correction path, compliance read, and the safe no-drift path
  all verified live.
- **Privilege resolved:** granting **`Read Device Compliance Information`** (+ `Read Computers`)
  cleared the long-standing 403. The read now returns `status: success`.

### Still not exercised end-to-end
- **B2/I1 escalation branch + B1 wipe:** the test tenant returns **0 compliance records** for the
  test device (no compliance vendor), so nothing ever reports `NON_COMPLIANT` → the run never
  reaches quarantine → lock → prompt → wipe. `NON_COMPLIANT` is source-confirmed and `confirm` is
  wired to the device-id datapath (connector contract), but neither is fired on a live
  non-compliant device / real erase. Needs a device a compliance partner (e.g. Intune) reports as
  NON_COMPLIANT.

---

## Re-sync note (for maintainers)
**Mostly-canonical, NOT import-clean (corrected per PR #10 review I7).** The pair began as
SOAR's own VPE export (repo 2 `local`, playbook id 196), but the case-(d) empty-read guard on
node 7 (`is_compliant`) was patched into the graph outside a clean editor round-trip. Evidence
in the committed `.json`: node 7 carries `"warnings": {"config": ["Reconfigure invalid
datapath."]}`, and its third comparison uses a hand-minted key
`comparison_key_a65ee7ac-…` instead of the sibling `comparison_key_7_0/_7_1` pattern. The `.py`
(what actually runs) is correct, but the graph is **not** the pristine canonical export earlier
notes claimed — on the next VPE open the empty-read guard will likely need reconfiguring.
**Before merge, re-open in the VPE → resolve the node-7 warning → re-export → re-scrub → blank
the hash.** The `is_compliant` fail-safe truth table is otherwise intact — SOAR renders it as
`OR(compliance_state == COMPLIANT, status != success, summary.total == 0) → END; ELSE → contain`
(a failed/403/empty read never escalates). The old→new rename map below is kept only as history.

Two things about the committed files that are intentional, not drift:
- **`hash` is empty.** SOAR's export stamped a real hash, but it was computed over the graph
  with the real asset name; scrubbing that to `<your-jamf-asset>` (mandatory for a template)
  invalidates it, and no placeholder-graph hash can match a real instance anyway — SOAR
  recomputes on import. So `hash:""` is deliberate.
- **The `.py` is SOAR-generated** (per-block `collect2`/param loops, `Custom Code` stubs), so
  the earlier hand-authored `_dev()` helper and explanatory comments are gone by design.

If a future edit needs re-syncing again, repeat: VPE → save → export → **scrub the asset name**
→ blank the hash → commit.

| Old (auto-numbered) | New (descriptive) |
|---|---|
| `get_device_by_serial_1` | `resolve_device` |
| `redeploy_management_framework_1` | `redeploy_framework` |
| `send_blank_push_1` | `force_checkin` |
| `get_compliance_status_1` | `check_compliance` |
| `decision_1` | `is_compliant` |
| `add_to_static_group_1` | `quarantine_device` |
| `lock_device_1` | `lock_device` |
| `prompt_1` | `approve_wipe` |
| `decision_2` | `is_wipe_approved` |
| `wipe_device_1` | `wipe_device` |
