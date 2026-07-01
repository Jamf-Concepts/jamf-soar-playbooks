# VPE Build Sheet — Jamf - Compliance Drift / MDM Tamper Remediation (Issue #4)

How to recreate this template in SOAR's **Visual Playbook Editor (VPE)**. Action names,
parameters, and datapaths are **verified live** against the connector "Jamf Pro" v1.0.0
(app id 4 / your dev app id 6, asset `jamf_amanda`).

The paired `.py` / `.json` in this folder hold the same logic, but SOAR playbooks must be
authored in the VPE — build here, and SOAR generates valid files automatically.

---

## 0. Create the playbook
- SOAR → **Playbooks → + Playbook**.
- Name: **`Jamf - Compliance Drift / MDM Tamper Remediation`**
- Type: **Automation** · Operates on label: **`<your-noncompliant-label>`** (e.g. `jamf_noncompliant_device`)
- You start with a **START** block on the canvas. Build left→right, connecting each block's
  output dot to the next block's input dot.

## VPE mechanics (quick reference)
- **Add a block:** drag from the START/out dot, or click **+**. Pick the block type:
  **Action** (a connector action), **Decision**, **Prompt**, or **Utility** (add note).
- **Action block:** choose app **Jamf Pro** (asset **`jamf_amanda`**), then the action.
  Fill each parameter — click the field → **Datapath** to reference an earlier block's output.
- **Datapath format:** `<block_name>:action_result.data.*.<field>`. The resolver's device id is
  `...data.*.id` and type is `...data.*.type` (NOT `jamf_device_id`).
- Connect blocks by dragging between the dots. Decisions/prompts have multiple out-paths.

---

## The blocks (in order)

| # | Block (type) | Action / config | Key parameters |
|---|---|---|---|
| 1 | **START** | on_start | — |
| 2 | **Resolve device** (action) | `get device by serial` | `serial_number` ← `artifact:*.cef.serialNumber` |
| 3 | **Get compliance (baseline)** (action) | `get compliance status` | `device_id` ← `resolve:...data.*.id` · `device_type` ← `resolve:...data.*.type` |
| 4 | *Get config profiles* (action, **optional**) | `get configuration profiles` | `device_id` ← resolve id · `device_type` ← resolve type |
| 5 | *Get extension attrs* (action, **optional**) | `get extension attributes` | `device_id` ← resolve id · `device_type` ← resolve type |
| 6 | **Redeploy framework** (action) | `redeploy management framework` | `device_id` ← resolve id · `device_type` ← resolve type |
| 7 | **Send blank push** (action) | `send blank push` | `device_id` ← resolve id · `device_type` ← resolve type |
| 8 | **Update inventory** (action) | `update inventory` | `device_id` ← resolve id · `device_type` ← resolve type |
| 9 | **Flag under review** (action) | `update extension attribute` | `device_id` ← resolve id · `device_type` ← resolve type · `ea_id` = `<your-flag-ea-id>` · `value` = `<under-review>` |
| 10 | **Re-check compliance** (action) | `get compliance status` | `device_id` ← resolve id · `device_type` ← resolve type |
| 11 | **Corrected?** (decision) | see conditions below | branches to 12 (compliant) or 13 (not) |
| 12 | **Note: remediated** (utility → add note) | title/content below | → END |
| 13 | **Add to quarantine group** (action) | `add to static group` | `device_id` ← resolve id · `group_name` = `<your-quarantine-group>` |
| 14 | **Lock device** (action) | `lock device` | `device_id` ← resolve id · `device_type` ← resolve type · `message` = `<your-return-message>` · `phone_number` = `<your-callback-number>` |
| 15 | **Note: contained (queued)** (utility → add note) | title/content below | → 16 |
| 16 | **Approve wipe?** (prompt) | approval gate, config below | → 17 |
| 17 | **Approved?** (decision) | see conditions below | branches to 18 (approved) or 19 (denied) |
| 18 | **Wipe device** (action) | `wipe device` | `device_id` ← resolve id · `device_type` ← resolve type · `confirm` = `true` | → END |
| 19 | **Note: wipe denied** (utility → add note) | title/content below | → END |
| 20 | **END** | on_finish | — |

> **Optional-for-v1:** blocks 4 and 5 are context enrichment only (nothing downstream depends
> on them). Skip them for a first working build if you want fewer blocks; add later.

---

## Decision configs

**Block 11 — "Corrected?"**
- **IF** (path → block 12, remediated): `re_check_compliance:action_result.data.*.compliance_state` **==** `COMPLIANT`
- **ELSE** (path → block 13, contain)

**Block 17 — "Approved?"**
- **IF** (path → block 18, wipe): `approve_wipe:action_result.summary.responses.0` **==** `Yes`
- **ELSE** (path → block 19, denied)

> Confirm the exact `compliance_state` value against a real device response (we expect
> `COMPLIANT`); adjust if the connector returns a different token.

---

## Prompt config — Block 16 "Approve wipe?"
- **Approver:** a role/user (use `<your-security-analyst-role>` or the container owner).
- **Response time:** 30 minutes.
- **Response 1 (required, yes/no):**
  - Prompt text: **"Device remains non-compliant after automated correction and is contained (locked + quarantined). Approve device WIPE? This ERASES the device and is IRREVERSIBLE."**
  - Options: **Yes / No**

---

## Add-note (utility) contents
- **Block 12 (remediated):** title `Compliance Drift - remediated` · content: "Device returned to a compliant state after correction. No containment needed."
- **Block 15 (contained):** title `Compliance Drift - contained (queued)` · content: "Correction did not restore compliance. Quarantined + locked (queued). Awaiting analyst decision on wipe."
- **Block 19 (wipe denied):** title `Compliance Drift - wipe denied` · content: "Analyst denied the wipe. Device remains locked and quarantined; no erase performed."

---

## Customer-config placeholders to fill (per environment)
- Jamf asset: **`jamf_amanda`** (or `<your-jamf-asset>`)
- Trigger label: `<your-noncompliant-label>`
- Quarantine static group: `<your-quarantine-group>` (block 13)
- Flag extension attribute id + value: `<your-flag-ea-id>` / `<under-review>` (block 9)
- Lock message + callback number: `<your-return-message>` / `<your-callback-number>` (block 14)
- Approver role: `<your-security-analyst-role>` (block 16)

## Prerequisite (Jamf side)
`get compliance status` needs the API role to have the **conditional-access / device-compliance
read** privilege, or it returns HTTP 403. (Granted 2026-07-01.)

## Save & test
1. **Save** the playbook (VPE compiles it — fixes any block errors it flags).
2. **Run** on a container with a `serialNumber` artifact (test value: `HC2F60R07T`).
3. Watch it execute block-by-block in the debugger. Destructive `wipe device` only fires
   after **Yes** at the prompt.
