"""
Jamf - IdP Breach Bulk Quarantine (batched up-front approval, no bulk wipe).

Responds to an identity-provider breach affecting many accounts/devices. Resolves the affected
device set, enriches lightly (compliance), then gates the ENTIRE bulk containment behind a single
up-front analyst approval that discloses the full blast radius. Only on approval does it contain
each device (add to quarantine group + lock + blank push). Bulk wipe is EXCLUDED by default — any
wipe is per-device and individually approved elsewhere.

Safety design (issue #6 + PR #12 review lessons):
- Approval is UP FRONT, before any containment (mass-scale action) — not just before a wipe.
- A batch-size cap gates the run so a runaway set can't be mass-actioned (fail-safe default 25).
- The approval prompt discloses scope: the full device list is posted as a note first, and the
  prompt states it will quarantine ALL listed devices (PR #12 C2 — scope shown == scope executed).
- Failed/empty resolution ends the run with a note — never reaches the approval/containment (C3).
- The final report is built from the REAL per-action statuses, not a hardcoded "done" line
  (PR #12 C1 — never report a failed contain as success).
- Computer vs mobile static groups are separate ID namespaces, so the quarantine group is chosen
  per device_type (PR #12 I1).

Customer-config points (replace before use):
- Jamf asset on every action block                 -> <your-jamf-asset>
- Computer quarantine static group id              -> <your-computer-quarantine-group>
- Mobile quarantine static group id                -> <your-mobile-quarantine-group>
- Per-device lock PIN (6 digits)                   -> <your-6-digit-pin>
- Lock return message / callback number            -> <your-return-message> / <your-callback-number>
- Approver role for the batched prompt             -> <your-security-analyst-role>
- Batch-size cap (hard safety limit)               -> MAX_DEVICES below (<max-devices-per-run>)
- Trigger reads usernames from artifact cef.sourceUserName.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


# Hard safety cap on how many devices one run may bulk-quarantine (<max-devices-per-run>).
MAX_DEVICES = 25


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    resolve_devices(container=container)

    return


@phantom.playbook_block()
def resolve_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("resolve_devices() called")

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceUserName","artifact:*.id"])

    parameters = []

    # one 'get device by username' call per affected username on the container
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "username": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    phantom.act("get device by username", parameters=parameters, name="resolve_devices", assets=["<your-jamf-asset>"], callback=devices_found)

    return


@phantom.playbook_block()
def devices_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("devices_found() called")

    # C3: only proceed if the resolve SUCCEEDED and actually returned a device id. Gating on
    # status=="success" AND id present matches the project fail-safe standard, so a failed read
    # (e.g. can't read mobile) or an unknown user never reaches the prompt or containment.
    found_match_1 = phantom.decision(
        container=container,
        logical_operator="and",
        conditions=[
            ["resolve_devices:action_result.status", "==", "success"],
            ["resolve_devices:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
            ["resolve_devices:action_result.status", "==", "success"],
            ["resolve_devices:action_result.data.*.id", "!=", ""]
        ],
        name="devices_found:condition_1",
        delimiter=None)

    if found_match_1:
        check_compliance(action=action, success=success, container=container, results=results, handle=handle)
        return

    note_no_devices(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_devices() called")

    phantom.add_note(
          container=container,
          title="IdP breach - no devices resolved",
          content=(
              "No Jamf devices resolved for the affected username(s), or the lookup failed. "
              "No containment was attempted. Verify the usernames / API-role read privileges and re-run."
          ),
          note_type="general",
      )

    phantom.save_block_result(key="note_no_devices_called", value="True")

    return


@phantom.playbook_block()
def check_compliance(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("check_compliance() called")

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # light enrichment: compliance status per resolved device (row-aligned id/type pairing)
    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_devices_result_item[0],
                "device_type": resolve_devices_result_item[1],
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    phantom.act("get compliance status", parameters=parameters, name="check_compliance", assets=["<your-jamf-asset>"], callback=build_quarantine_preview)

    return


@phantom.playbook_block()
def build_quarantine_preview(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("build_quarantine_preview() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Build the dry-run list (scope disclosure) BEFORE any approval, and post it as a note so the
    # analyst sees exactly which devices a "Yes" will quarantine (PR #12 C2 — scope shown). Surface
    # compliance state per device so the enrichment is actually visible to the approver.
    devices = phantom.collect2(
        container=container,
        datapath=["resolve_devices:action_result.data.*.id",
                  "resolve_devices:action_result.data.*.type",
                  "resolve_devices:action_result.data.*.general.name"],
        action_results=results)
    comp_rows = phantom.collect2(
        container=container,
        datapath=["check_compliance:action_result.data.*.device_id",
                  "check_compliance:action_result.data.*.compliance_state"],
        action_results=results)
    compliance = {str(c[0]): c[1] for c in comp_rows if c[0] is not None}

    # PR #15 review #1: reconcile INPUT usernames vs resolved, so a partial resolve failure
    # (some accounts 403 / zero-match in a multi-user breach) is surfaced, not silently dropped.
    # resolve runs once per username, so parameter.username + status + summary.total are per-user.
    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
    user_rows = phantom.collect2(container=container,
        datapath=["resolve_devices:action_result.parameter.username",
                  "resolve_devices:action_result.status",
                  "resolve_devices:action_result.summary.total"],
        action_results=results)
    usernames_in = sum(1 for r in user_rows if r[0] is not None)
    users_ok = sum(1 for r in user_rows if r[0] is not None and r[1] == "success" and _int(r[2]) > 0)
    users_failed = usernames_in - users_ok

    lines, count, skipped = [], 0, 0
    for d in devices:
        if d[0] is None:
            skipped += 1
            continue
        count += 1
        name = d[2] or "(unknown)"
        cstate = compliance.get(str(d[0]), "n/a")
        lines.append("- {0} | device_id {1} | {2} | compliance {3}".format(name, d[0], d[1] or "?", cstate))

    preview = "IdP breach - proposed bulk quarantine of {0} device(s):\n{1}".format(count, "\n".join(lines))
    preview += "\nAccounts: {0} username(s) in, {1} resolved to device(s), {2} failed/zero-match.".format(usernames_in, users_ok, users_failed)
    if users_failed:
        preview += "\nWARNING: {0} breached account(s) resolved to NO device and will NOT be contained - investigate manually.".format(users_failed)
    if skipped:
        preview += "\n({0} resolved record(s) had no device id and CANNOT be quarantined - investigate manually.)".format(skipped)
    phantom.add_note(
        container=container,
        title="IdP breach - proposed quarantine (review before approving)",
        content=preview,
        note_type="general",
        note_format="markdown",
    )
    phantom.save_block_result(key="device_count", value=str(count))

    # Hard safety cap on the AGGREGATE device count (PR-review C1). resolve runs once per username,
    # so the resolver's per-run summary.total does NOT bound a multi-user breach — gate the real
    # total instead, and fail safe (abort with a note) when it's exceeded.
    if count > MAX_DEVICES:
        note_batch_too_large(action=action, success=success, container=container, results=results, handle=handle)
        return

    ################################################################################
    ## Custom Code End
    ################################################################################

    approve_bulk_quarantine(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_batch_too_large(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_batch_too_large() called")

    phantom.add_note(
          container=container,
          title="IdP breach - batch too large, aborted",
          content=(
              "The affected device set exceeds the batch-size cap (MAX_DEVICES). Bulk quarantine "
              "was ABORTED and no containment was attempted, to prevent a runaway mass action. "
              "Re-scope the set, or raise the cap deliberately after review."
          ),
          note_type="general",
      )

    phantom.save_block_result(key="note_batch_too_large_called", value="True")

    return


@phantom.playbook_block()
def approve_bulk_quarantine(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_bulk_quarantine() called")

    user = None
    role = "<your-security-analyst-role>"
    message = """IdP breach response. This will QUARANTINE (add to group + lock + blank push) ALL devices listed in the case note titled "IdP breach - proposed quarantine (review before approving)" — read it for the exact device list and account reconciliation. This is a bulk containment action across every listed device. Bulk wipe is NOT part of this action. Approve bulk quarantine?"""

    parameters = []

    response_types = [
        {
            "prompt": "Approve bulk quarantine of ALL listed devices?",
            "options": {
                "type": "list",
                "required": True,
                "choices": [
                    "Yes",
                    "No"
                ],
            },
        }
    ]

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_bulk_quarantine", parameters=parameters, response_types=response_types, callback=is_quarantine_approved)

    return


@phantom.playbook_block()
def is_quarantine_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("is_quarantine_approved() called")

    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["approve_bulk_quarantine:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["approve_bulk_quarantine:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="is_quarantine_approved:condition_1",
        delimiter=None)

    if found_match_1:
        quarantine_add_group(action=action, success=success, container=container, results=results, handle=handle)
        return

    note_not_approved(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_not_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_not_approved() called")

    phantom.add_note(
          container=container,
          title="IdP breach - bulk quarantine NOT approved",
          content=(
              "The analyst declined the bulk quarantine, or the approval prompt timed out. "
              "No containment was performed. Follow up manually if the breach is confirmed."
          ),
          note_type="general",
      )

    phantom.save_block_result(key="note_not_approved_called", value="True")

    return


@phantom.playbook_block()
def quarantine_add_group(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_add_group() called")

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # I1: computer vs mobile static groups are separate ID namespaces -> pick the group per type.
    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            device_type = resolve_devices_result_item[1]
            group_id = "<your-computer-quarantine-group>" if device_type == "computer" else "<your-mobile-quarantine-group>"
            parameters.append({
                "device_id": resolve_devices_result_item[0],
                "device_type": device_type,
                "group_id": group_id,
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    phantom.act("add to static group", parameters=parameters, name="quarantine_add_group", assets=["<your-jamf-asset>"], callback=quarantine_lock)

    return


@phantom.playbook_block()
def quarantine_lock(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_lock() called")

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            parameters.append({
                "pin": "<your-6-digit-pin>",
                "message": "<your-return-message>",
                "device_id": resolve_devices_result_item[0],
                "device_type": resolve_devices_result_item[1],
                "phone_number": "<your-callback-number>",
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    phantom.act("lock device", parameters=parameters, name="quarantine_lock", assets=["<your-jamf-asset>"], callback=quarantine_push)

    return


@phantom.playbook_block()
def quarantine_push(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_push() called")

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_devices_result_item[0],
                "device_type": resolve_devices_result_item[1],
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    phantom.act("send blank push", parameters=parameters, name="quarantine_push", assets=["<your-jamf-asset>"], callback=report_results)

    return


@phantom.playbook_block()
def report_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("report_results() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # C1: build the outcome from REAL per-action statuses — never assert containment that failed.
    # Anything not exactly "success" (incl. None/unknown/missing) counts as not-ok, so a failed or
    # absent status can't be silently swallowed.
    def _counts(name):
        rows = phantom.collect2(container=container, datapath=[name + ":action_result.status"], action_results=results)
        ok = sum(1 for r in rows if r[0] == "success")
        not_ok = sum(1 for r in rows if r[0] != "success")
        return ok, not_ok, ok + not_ok

    # approved scope = devices the run intended to contain (non-null resolved ids)
    approved_rows = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id"], action_results=results)
    approved = sum(1 for r in approved_rows if r[0] is not None)

    # PR #15 review #1: also reconcile at the ACCOUNT level (input usernames vs resolved)
    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0
    user_rows = phantom.collect2(container=container,
        datapath=["resolve_devices:action_result.parameter.username",
                  "resolve_devices:action_result.status",
                  "resolve_devices:action_result.summary.total"],
        action_results=results)
    usernames_in = sum(1 for r in user_rows if r[0] is not None)
    users_ok = sum(1 for r in user_rows if r[0] is not None and r[1] == "success" and _int(r[2]) > 0)
    users_failed = usernames_in - users_ok
    acct = "Accounts: {0} username(s) in, {1} resolved, {2} failed/zero-match.".format(usernames_in, users_ok, users_failed)
    if users_failed:
        acct += " WARNING: {0} breached account(s) resolved to NO device and were NOT contained - investigate.".format(users_failed)

    add_ok, add_bad, add_n = _counts("quarantine_add_group")
    lock_ok, lock_bad, lock_n = _counts("quarantine_lock")
    push_ok, push_bad, push_n = _counts("quarantine_push")

    # reconcile: if any action touched fewer devices than were approved, surface the gap
    gaps = [nm for nm, n in (("add to static group", add_n), ("lock device", lock_n), ("send blank push", push_n)) if n < approved]
    recon = ""
    if gaps:
        recon = "\nWARNING: {0} device(s) were approved but these actions ran on fewer: {1} — the rest were dropped/not run; investigate.".format(approved, ", ".join(gaps))

    content = (
        "IdP breach bulk quarantine - results (from actual action statuses; {0} device(s) approved):\n"
        "{8}\n"
        "- add to static group (effective immediately): {1} ok, {2} failed/unknown\n"
        "- lock device (MDM command QUEUED - applies on next check-in, NOT confirmed on device): {3} queued-ok, {4} failed/unknown\n"
        "- send blank push (MDM command QUEUED): {5} queued-ok, {6} failed/unknown\n"
        "{7}"
        "\nAny failed/unknown count — or a queued command to an offline device — means those devices "
        "are NOT confirmed contained; review and remediate manually. (No Slack app in SOAR; this note "
        "is the notification.)"
    ).format(approved, add_ok, add_bad, lock_ok, lock_bad, push_ok, push_bad, recon, acct)

    phantom.add_note(
        container=container,
        title="IdP breach - bulk quarantine results",
        content=content,
        note_type="general",
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="report_results_called", value="True")

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    return
