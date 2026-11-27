# Jamf SOAR Playbooks

A collection of **Splunk SOAR playbook templates** for the Jamf SOAR connector
app. These playbooks orchestrate the connector's actions (resolve a device,
contain it, enrich, notify, gate on an analyst, and — only then — take a
destructive step) into ready-to-adapt incident-response flows.

This repo is **not** a connector. It holds reusable playbooks that *call* the
Jamf SOAR app's actions. The companion connector app is documented at
[Jamf-Concepts/jamf-splunk-soar](https://github.com/Jamf-Concepts/jamf-splunk-soar).

The Jamf SOAR connector app gives you the building blocks — `lock device`,
`add to static group`, `wipe device`, and so on. But a building block isn't a
response. Analysts still have to wire those actions together, decide the order,
add the approval gates, and connect the enrichment and notification steps.

This repo ships those flows as **templates** so a customer doesn't start from a
blank canvas. Each playbook is a vetted chain that already encodes the safety
rules (most importantly: never auto-wipe — see below).

## Prerequisites

These playbooks do nothing on their own. To use them you need:

| Requirement | Detail |
|-------------|--------|
| **Splunk SOAR** | Cloud or On-prem. Playbooks run inside SOAR. |
| **Jamf SOAR connector app** | Installed in SOAR — see the [connector docs](https://github.com/Jamf-Concepts/jamf-splunk-soar) (coming to Splunkbase at release). The playbooks reference its actions by app + action name. |
| **A configured Jamf asset** | An asset wired to the app with a Jamf Account integration's Client ID, secret, region and Tenant ID. The integration needs the capabilities listed under [Required Jamf capabilities](#required-jamf-capabilities). Without a working asset the actions have nothing to call. |

If the app isn't installed or the asset isn't configured, the playbooks will
fail to resolve their action blocks on import.

## Distribution model

Splunk SOAR manages playbooks in **git-backed repositories**, not inside the
connector app's `.tgz`. There are two supported ways to get these playbooks
into SOAR:

1. **Source-control repository (recommended).** In SOAR go to
   **Administration → Source Control** and add this repo as a source-control
   repository. SOAR clones it and keeps the playbooks in sync as the repo
   updates.
2. **`.tgz` export import.** Import an individual playbook from a `.tgz` export
   via the Playbooks UI. Use this for one-off sharing or air-gapped installs.

> Note: `.tgz` playbook exports can embed environment-specific details (asset
> names, group IDs, label values). Scrub those before sharing an export.

## Playbook templates

Every template follows the same backbone: **resolve device → contain →
enrich / notify → (timer) → analyst approval gate → destructive step.**

| Playbook | Scenario | Backbone |
|----------|----------|----------|
| `Jamf - Device Enrichment (Input)` + `Jamf - Device Enrichment and Triage` | Read-only enrichment/triage | resolve → enrich (Input sub-playbook) → summary note (no destructive step) |
| `Jamf - Compliance Drift and MDM Tamper Remediation` | Device flagged non-compliant / MDM-tampered | resolve → **correct-first** → check → contain-if-needed → approval gate → wipe |
| `Jamf - IdP Breach Bulk Quarantine` | IdP breach — mass affected device set | resolve set → devices-found gate → enrich → **up-front batched approval (full scope) + batch cap** → contain loop (add group / lock / blank push) → results note. **No bulk wipe.** |
| `Jamf - FileVault Recovery Access (macOS)` | Secured recovery access after a compromise or offboarding | resolve by serial → enrich (recovery key, local users, compliance) → recovery lock + lock → note → approval gate → wipe |
| `Jamf - Compromised User Device Sweep` | One compromised user, all their devices | resolve by username → contain each (group + blank push + lock) → note → fleet-wide approval gate → wipe |
| `Jamf - Lost or Stolen Device` | Device reported lost or stolen (computer or mobile) | resolve by serial → branch on `device_type` (mobile: lost mode / computer: lock) → note → approval gate → wipe |
| `Jamf - Malicious App or File Containment (macOS)` | Malicious app/file detected on a Mac | resolve by device name → confirm the flagged app is installed → isolate (group + lock + blank push) → approval gate → wipe |

### `Jamf - IdP Breach Bulk Quarantine`
The **highest-risk** template: it mass-quarantines every device caught in an IdP breach, so the
gate is stricter than the others. Resolves the affected set (`get device by username` over the
container's `cef.sourceUserName` values), enriches with compliance, posts a **dry-run note listing
every device**, then a **single up-front approval** authorizes the whole batch (scope shown =
scope executed). A **hard batch-size cap** (`MAX_DEVICES`, default 25) aborts a runaway set. On
approval it loops containment — add to a quarantine static group (chosen per `device_type`, since
computer vs mobile groups are separate ID namespaces), lock, blank push — then writes a results
note built from the **real per-action statuses** (a failed contain is never reported as success).
**Bulk wipe is excluded**; any erase is per-device and separately approved. Failed/empty resolve
and a declined approval each end with a note.

Flow: `resolve_devices` → `devices_found?` → `check_compliance` → `build_quarantine_preview`
(posts the dry-run note **and** enforces the aggregate batch cap: over-cap → `note_batch_too_large`)
→ `approve_bulk_quarantine` → `is_quarantine_approved?` → `quarantine_add_group` →
`quarantine_lock` → `quarantine_push` → `report_results`.

**Customer-config:** a Jamf Pro asset named `jamf_pro` (or change the asset on each action block); computer + mobile quarantine groups
(`<your-computer-quarantine-group>` / `<your-mobile-quarantine-group>`); lock PIN
(`<your-6-digit-pin>`); approver role (`<your-security-analyst-role>`); batch cap (`MAX_DEVICES`).

> **`.py`/`.json` note:** the per-`device_type` group choice, the real-status results summary,
> the aggregate batch-cap check, and the compliance-in-preview live in the hand-authored `.py`
> (the reviewable source of truth). The `.json` graph carries single-value placeholders and stub
> code nodes — if rebuilding in the VPE, re-add that custom code.

### `Jamf - Compliance Drift and MDM Tamper Remediation`
Apple/MDM-unique template (no shipped SOAR equivalent). Leads with **non-destructive
correction** — redeploy the management framework and send a blank push to force an MDM
check-in — then **checks compliance**. Only if the read *succeeds and* the device is
*still* non-compliant does it contain (quarantine group + lock); a wipe happens **only**
behind an analyst approval prompt whose text states the action is irreversible. Escalation is a
**positive match** — `is_compliant` contains only on `status == success` AND
`compliance_state == NON_COMPLIANT`; a COMPLIANT / UNKNOWN / None / empty / failed (403) read
all end the run safely at `note_no_drift` rather than escalating.

Flow (v3, block names in order): `has_serial?` → `resolve_device` → `device_found?` →
`redeploy_framework` → `force_checkin` → `check_compliance` → `is_compliant?` →
`quarantine_device` → `lock_device` → `containment_ok?` → `approve_wipe` → `is_wipe_approved?`
→ `wipe_device` → `note_wipe_outcome`. Every terminal path writes a container note (`has_serial` no →
`note_no_serial`; `device_found` no → `note_no_device`; `is_compliant` else → `note_no_drift`;
`containment_ok` no → `note_containment_failed`; `is_wipe_approved` no → `note_wipe_declined`;
`wipe_device` → `note_wipe_outcome`, which reads the wipe status and writes "ERASE queued" only when
the wipe succeeded and "ERASE NOT queued" otherwise), so a failed erase never reports as queued. That
block replaces the former `wipe_ok` decision and its two note blocks, keeping the playbook under Splunk's
20-block limit. The wipe prompt
is shown only if `containment_ok` confirms quarantine AND lock both succeeded.

> **Deferred — enrichment stage.** Issue #4 also calls for an enrichment step
> (`get configuration profiles`, `get extension attributes`) alongside the correction
> steps. It's intentionally left out here: the reusable enrichment engine ships in the
> `Jamf - Device Enrichment (Input)` sub-playbook. A follow-up
> can wire that Input sub-playbook in rather than re-implementing the lookups. The `update
> inventory` correction step is permanently dropped — the connector rejects it for computers
> (macOS recon is policy-based).

> **Scope — computers (macOS) only, for now (PR #10 review I8).** The correction path
> (`redeploy management framework`) is a computer-only action, and `quarantine_device` doesn't
> set `device_type`, so it targets the computer namespace. Running this against a **mobile**
> device gives half-applied containment. `device_type` branching (redeploy for computers only;
> `device_type` on quarantine) is a planned enhancement — until then, scope this template to
> computers.

**Customer-config points** (replace the `<...>` placeholders on import):
- Jamf asset — a Jamf Pro asset named `jamf_pro` (or change the asset on each action block)
- Quarantine static group — `group_name` on `quarantine_device`
- Lock PIN — `<your-6-digit-pin>` on `lock_device` (the `wipe_device` erase PIN was dropped — modern Macs don't use it)
- Lock return message + callback number — on `lock_device`
- Approver role — on `approve_wipe` (default `Administrator`)

**Datapaths (verified against the live connector "Jamf Pro" v1.0.0):** the resolver
returns the device id at `action_result.data.*.id` and type at `action_result.data.*.type`.
`get compliance status` returns `action_result.data.*.compliance_state` — enum
`UNKNOWN / NON_COMPLIANT / COMPLIANT`. **Verified live 2026-07-06:** with compliance
read access granted, the read succeeds (run 57 returned 0 records for a
test device with no compliance vendor, which correctly routed to `note_no_drift`). The literal
`NON_COMPLIANT` token is confirmed from the connector source but not yet observed on a live
non-compliant device. **Wipe `confirm` (B1, fixed):** wired to `resolve_device:action_result.data.*.id`
— the connector requires `confirm == device_id`, so a truthy flag would be rejected
(`WIPE_NOT_CONFIRMED`). Not yet fired end-to-end (no non-compliant device in the test tenant).

### `Jamf - FileVault Recovery Access (macOS)`
Secured recovery access to a Mac after a compromise or during offboarding. Resolves the device by
serial (`artifact:*.cef.serialNumber`), then retrieves recovery context: the FileVault personal
recovery key, local user accounts, and compliance status. It secures the Mac (set recovery lock,
lock device), adds a note, and holds at an analyst approval gate. The wipe runs **only** on
approval; a decline or a no-device path just adds a note.

Flow: `find mac by serial` → `device found` → `get filevault key` → `get local accounts` →
`get compliance status` → `set recovery lock` → `lock mac` → `note step outcomes` →
`approve wipe` → `wipe approved` → `wipe mac`.

> **The FileVault recovery key is sensitive.** Never route it to a broad channel or a
> container note. The notify step ships as a plain note — replace it with a restricted-channel
> notifier before use.

**Customer-config:** a Jamf Pro asset named `jamf_pro` (or change the asset on each action block); approver role (`<security-analyst-role>`);
recovery-lock password (`<your-recovery-lock-password>`, prefer a secret); lock-screen message
and support phone (`<your-lock-screen-message>` / `<your-support-phone>`); lock PIN (defaults to
`000000` — replace with a chosen 6-digit PIN).

### `Jamf - Compromised User Device Sweep`
Contains every device belonging to one compromised user. Resolves devices by username
(`artifact:*.cef.sourceUserName`), then for each device adds it to a suspended group (chosen per
`device_type`, since computer and mobile group IDs are separate namespaces), sends a blank push,
and locks it. It posts a containment summary with per-device status, then a single approval prompt
that enumerates the whole fleet before any wipe. The wipe runs only on approval and sets
`confirm` to the device ID, as the connector requires.

**Customer-config:** a Jamf Pro asset named `jamf_pro` (or change the asset on each action block); computer and mobile suspended groups
(`<your-computer-suspended-group-id>` / `<your-mobile-suspended-group-id>`); callback number
(`<your-callback-number>`); approver role (`<your-approver-role>`).

### `Jamf - Lost or Stolen Device`
Responds to a device reported lost or stolen. Resolves by serial, then branches on `device_type`:
a mobile device gets **lost mode**; a computer gets **lock device**. Each branch writes a note,
holds at an analyst approval gate, and wipes only on approval. A decline, timeout, or no-device
path just writes a note.

- **Per-branch tails.** The two branches each carry their own note → prompt → wipe tail and do
  not reconverge. A shared tail makes SOAR insert a join that waits for both branches; only one
  runs per device, so the join would never complete and the note, prompt, and wipe would be skipped.
- **Single-match assumption.** A serial should resolve to one device. Containment, the wipe, and
  the disclosure note and prompt all act on every matched row, so a serial matching more than one
  record would be erased under one approval. The note warns when that happens; hard-gating to
  exactly one match is not implemented.
- **One block per wipe result.** `note mobile wipe outcome` / `note computer wipe outcome` read the
  wipe status and write the "queued" or "failed" note, which keeps the playbook at Splunk's
  20-block limit.
- **Partial lookups.** `get device by serial` is best-effort and returns success with
  `summary.skipped` when one platform was skipped for auth. The no-device path distinguishes that
  from a clean miss, so a privilege gap isn't read as "no such device".

Enrichment (the Device Enrichment Input sub-playbook) and quarantine (add to static group) are
not included.

**Customer-config:** a Jamf Pro asset named `jamf_pro` (or change the asset on all five action blocks); approver role
(`<security-analyst-role>`); lock PIN (`000000` — replace with a 6-digit PIN); lock-screen message.

### `Jamf - Malicious App or File Containment (macOS)`
Contains a Mac after a malicious app or file detection. Resolves the device by name
(`artifact:*.cef.deviceHostname`), then reads its installed applications and checks that the
flagged file name (`artifact:*.cef.fileName`) matches one. If the app is not installed, or the
installed-apps read fails, the run ends with a note and takes no containment. If it is installed,
the playbook isolates the device (static group, lock, blank push) with an honest per-action status,
then holds at an analyst approval gate before any wipe. Each container should carry one detection.

**Customer-config:** a Jamf Pro asset named `jamf_pro` (or change the asset on each action block); isolation group (`<your-isolation-group-id>`);
callback number (`<your-callback-number>`); approver role (`<your-approver-role>`).

## Required Jamf capabilities

The connector authenticates as a **Jamf Account integration** (Jamf Account → **Integrations**)
and each action needs specific **capabilities** on it. A missing capability returns **HTTP 403
`BAD_PERMISSIONS`**, and the gateway doesn't name the capability it wanted, so grant these up
front. The per-action matrix is in the connector's
[Configuring Jamf API access](https://github.com/Jamf-Concepts/jamf-splunk-soar/blob/main/docs/configuring-jamf-api-access.md)
guide. Jamf Pro **11.30 or later** is required.

| Template | Capabilities to grant |
|----------|-----------------------|
| `Jamf - Device Enrichment and Triage` (read-only) | `devices:read`, `device-compliance-information:read` |
| `Jamf - Compliance Drift and MDM Tamper Remediation` | `devices:read`, `device-compliance-information:read`, `device-actions:execute`, `computer-check-in:read`, `device-groups:read`, `device-groups:update`, `destructive-device-actions:execute` |
| `Jamf - IdP Breach Bulk Quarantine` | `devices:read`, `device-compliance-information:read`, `device-groups:read`, `device-groups:update`, `device-actions:execute`, `destructive-device-actions:execute` |
| `Jamf - FileVault Recovery Access (macOS)` | `devices:read`, `device-compliance-information:read`, `disk-encryption-recovery-key:read`, `recovery-lock:execute`, `destructive-device-actions:execute` |
| `Jamf - Compromised User Device Sweep` | `devices:read`, `device-groups:read`, `device-groups:update`, `device-actions:execute`, `destructive-device-actions:execute` |
| `Jamf - Lost or Stolen Device` | `devices:read`, `devices:create`, `destructive-device-actions:execute` |
| `Jamf - Malicious App or File Containment (macOS)` | `devices:read`, `device-groups:read`, `device-groups:update`, `device-actions:execute`, `destructive-device-actions:execute` |

> **`lock device` needs `destructive-device-actions:execute`, the same capability as
> `wipe device`.** Every template that locks a device therefore needs it, including
> `Jamf - IdP Breach Bulk Quarantine`, which never wipes. The playbook's approval gate is the only
> control between a contained device and an erase, so keep that gate in place.
>
> `disk-encryption-recovery-key:read` and `recovery-lock:execute` expose sensitive material —
> grant them deliberately. `enable lost mode` only takes effect on a **supervised** mobile device.

**Required config values (not capabilities) — replace before running:**
- `lock device` needs a real **6-digit `pin`** (the code to unlock the Mac afterward); the
  `<your-6-digit-pin>` placeholder fails connector validation.
- `add to static group` needs a real `group_name` (an existing static group).
- `send blank push` / `get compliance status` etc. take the resolver's `device_id` (`data.*.id`).

> **Note:** `lock device` and `wipe device` are **queued MDM commands** and, on a real
> device, actually lock/erase it. Test against a spare/test device — never a production Mac.

**Safety:** the `approve_wipe → is_wipe_approved` gate must never be removed. The wipe
is reached only on an explicit `Yes` response; a timeout, `No`, or no response never wipes.

## Authoring notes

Each playbook is a `.py` + `.json` pair. The pairs are normally generated by the Visual Playbook
Editor (VPE). When a template is hand-authored, the `.py` is the reviewable source of truth; the
`.json` is a best-effort VPE graph that should be opened and re-saved in the editor to
canonicalize its layout, ports, and hash.

## Installation & usage

> Detailed, per-playbook import/sync steps are still being written. The
> high-level shape below applies to every template.

High-level shape:

1. Install and configure the Jamf SOAR connector app in SOAR (see the
   [connector docs](https://github.com/Jamf-Concepts/jamf-splunk-soar); coming to
   Splunkbase at release), including a working Jamf asset.
2. Add this repo under **Administration → Source Control** (or import a
   playbook `.tgz`).
3. Point each playbook's action blocks at your configured Jamf asset.
4. Set your environment-specific config (asset name, target group names,
   timer durations) at the marked configuration points in the playbook.

## Links

- **Companion connector app (docs)** — <https://github.com/Jamf-Concepts/jamf-splunk-soar>
- **Splunk SOAR playbooks & source control** — <https://docs.splunk.com/Documentation/SOARonprem/current/Playbook/Overview>
- **Jamf Developer docs** — <https://developer.jamf.com/jamf-pro/docs>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a playbook, the
issue-first workflow, and the safety rules. 

## Feedback and Questions
