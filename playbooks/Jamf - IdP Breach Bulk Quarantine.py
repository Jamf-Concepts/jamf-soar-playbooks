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

    # C3: only proceed if the resolve actually returned devices. A failed read (e.g. can't read
    # mobile) or an unknown user returns no id -> end with a note, never reach containment.
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["resolve_devices:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
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
    # analyst sees exactly which devices a "Yes" will quarantine (PR #12 C2 — scope shown).
    devices = phantom.collect2(
        container=container,
        datapath=["resolve_devices:action_result.data.*.id",
                  "resolve_devices:action_result.data.*.type",
                  "resolve_devices:action_result.data.*.general.name"],
        action_results=results)

    lines, count = [], 0
    for d in devices:
        if d[0] is None:
            continue
        count += 1
        name = d[2] or "(unknown)"
        lines.append("- {0} | device_id {1} | {2}".format(name, d[0], d[1] or "?"))

    preview = "IdP breach — proposed bulk quarantine of {0} device(s):\n{1}".format(count, "\n".join(lines))
    phantom.add_note(
        container=container,
        title="IdP breach - proposed quarantine (review before approving)",
        content=preview,
        note_type="general",
        note_format="markdown",
    )
    phantom.save_block_result(key="device_count", value=str(count))

    ################################################################################
    ## Custom Code End
    ################################################################################

    within_batch_cap(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def within_batch_cap(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("within_batch_cap() called")

    # Hard safety cap: do not present a bulk-quarantine approval for a set larger than MAX_DEVICES.
    # Gates on the resolver's reported device total. For a single target (one username or one group)
    # this is the exact blast radius; for a multi-username set, scope the trigger to a pre-vetted
    # group (list group members) or tighten MAX_DEVICES deliberately.
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["resolve_devices:action_result.summary.total", "<=", MAX_DEVICES]
        ],
        conditions_dps=[
            ["resolve_devices:action_result.summary.total", "<=", MAX_DEVICES]
        ],
        name="within_batch_cap:condition_1",
        delimiter=None)

    if found_match_1:
        approve_bulk_quarantine(action=action, success=success, container=container, results=results, handle=handle)
        return

    note_batch_too_large(action=action, success=success, container=container, results=results, handle=handle)

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
    message = """IdP breach response. This will QUARANTINE (add to group + lock + blank push) ALL devices listed in the case note "IdP breach - proposed quarantine". This is a bulk containment action across every listed device. Bulk wipe is NOT part of this action. Approve bulk quarantine?"""

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
    def _counts(name):
        rows = phantom.collect2(container=container, datapath=[name + ":action_result.status"], action_results=results)
        ok = sum(1 for r in rows if r[0] == "success")
        fail = sum(1 for r in rows if r[0] not in ("success", None))
        return ok, fail

    add_ok, add_fail = _counts("quarantine_add_group")
    lock_ok, lock_fail = _counts("quarantine_lock")
    push_ok, push_fail = _counts("quarantine_push")

    content = (
        "IdP breach bulk quarantine — results (from actual action statuses):\n"
        "- add to static group: {0} succeeded, {1} failed\n"
        "- lock device: {2} succeeded, {3} failed\n"
        "- send blank push: {4} succeeded, {5} failed\n"
        "Any non-zero failure count means those devices are NOT fully contained — review and "
        "remediate manually. (No Slack app configured in SOAR; this note is the notification.)"
    ).format(add_ok, add_fail, lock_ok, lock_fail, push_ok, push_fail)

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
