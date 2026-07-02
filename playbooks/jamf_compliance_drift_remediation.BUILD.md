# VPE Build Sheet — Jamf - Compliance Drift / MDM Tamper Remediation (Issue #4)

How to (re)build this template in SOAR's **Visual Playbook Editor (VPE)**. Action names,
parameters, and datapaths are **verified live** against the connector "Jamf Pro" v1.0.0.
Replace every `<...>` with your environment's value — no real asset names, group ids, PINs,
or serials belong in this file.

This sheet matches the committed `.py`/`.json` pair exactly: **12 nodes / 13 edges**. SOAR
playbooks must be authored in the VPE — build here, and SOAR generates valid files.

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
| 11 | **wipe_device** (action) | `wipe device` | `device_id` ← resolve id · `device_type` ← resolve type · `confirm` = `true` · `pin` = `<your-6-digit-pin>` |
| 12 | **on_finish** (END) | — | — |

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
- **IF** (path → block 7, contain) — BOTH conditions (AND):
  - `check_compliance:action_result.status` **==** `success`
  - `check_compliance:action_result.data.*.compliance_state` **!=** `COMPLIANT`
- **ELSE** (path → END): compliant, or the read failed/returned nothing.

> Confirm the exact non-compliant `compliance_state` token against a real device response.
> Once known, tighten the second condition to an explicit `==` on that value (e.g.
> `NOT_COMPLIANT`) so only a positively non-compliant read escalates.

**Block 10 — "is_wipe_approved"**
- **IF** (path → block 11, wipe): `approve_wipe:action_result.summary.responses.0` **==** `Yes`
- **ELSE** (path → END, denied/timed-out)

---

## Prompt config — Block 9 "approve_wipe"
- **Approver:** a role/user (use `<your-security-analyst-role>` or the container owner).
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
- Approver role: `<your-security-analyst-role>` (block 9)

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

## Re-sync note (for maintainers)
The committed `.json` has **already been regenerated** to match the `.py`: descriptive node
names, the `is_compliant` fail-safe (IF = `compliance_state == COMPLIANT` **OR**
`status != success` → END; ELSE → contain — no edge rewiring), the wipe `pin`, and the new
prompt text. `hash` is empty and `draft_mode:false` (matching the proven-importable export).

Because it was edited outside the editor, do one confirming pass before relying on it:
**open the playbook in the VPE → verify it loads and the diagram matches → run it once against a
test device (confirm it holds at the approval gate) → export.** The export recomputes the hash,
clears the draft flag, and becomes the authoritative pair. If it does *not* open, rebuild from
the block table above; the old→new rename map below is kept for reference.

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
