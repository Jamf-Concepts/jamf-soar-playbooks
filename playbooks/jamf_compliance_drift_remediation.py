"""
Jamf - Compliance Drift / MDM Tamper Remediation (correct-first, gated wipe).

v2 (PR #10 review): device-found gate, positive NON_COMPLIANT match with a
manual-review note for compliant/unknown/failed reads, containment-success gate
before the wipe prompt, a note on every terminal path, and the wipe `confirm`
wired to the resolved device id (the connector requires confirm == device_id).
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'resolve_device' block
    resolve_device(container=container)

    return

@phantom.playbook_block()
def resolve_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("resolve_device() called")

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.serialNumber","artifact:*.id"])

    parameters = []

    # build parameters list for 'resolve_device' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "serial_number": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device by serial", parameters=parameters, name="resolve_device", assets=["<your-jamf-asset>"], callback=device_found)

    return


@phantom.playbook_block()
def device_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("device_found() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["resolve_device:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
            ["resolve_device:action_result.data.*.id", "!=", ""]
        ],
        name="device_found:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        redeploy_framework(action=action, success=success, container=container, results=results, handle=handle)
        return

    # call connected blocks for the else condition 2
    note_no_device(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_device() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - no device found",
          content=(
              "No Jamf device matched the serial from the event. "
              "Playbook stopped; no correction or containment was attempted. "
              "Verify the serial and re-run."
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_device_called", value="True")

    return


@phantom.playbook_block()
def redeploy_framework(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("redeploy_framework() called")

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'redeploy_framework' call
    # NOTE (I8): 'redeploy management framework' is a computer-only action and does not
    # declare device_type — do not pass it. This template is scoped to computers.
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_device_result_item[0],
                "context": {'artifact_id': resolve_device_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("redeploy management framework", parameters=parameters, name="redeploy_framework", assets=["<your-jamf-asset>"], callback=force_checkin)

    return


@phantom.playbook_block()
def force_checkin(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("force_checkin() called")

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'force_checkin' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_device_result_item[0],
                "device_type": resolve_device_result_item[1],
                "context": {'artifact_id': resolve_device_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("send blank push", parameters=parameters, name="force_checkin", assets=["<your-jamf-asset>"], callback=check_compliance)

    return


@phantom.playbook_block()
def check_compliance(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("check_compliance() called")

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'check_compliance' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_device_result_item[0],
                "device_type": resolve_device_result_item[1],
                "context": {'artifact_id': resolve_device_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="check_compliance", assets=["<your-jamf-asset>"], callback=is_compliant)

    return


@phantom.playbook_block()
def is_compliant(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("is_compliant() called")

    # Positive match (B2/I1): escalate ONLY on a present, successful, NON_COMPLIANT read.
    # complianceState enum is UNKNOWN / NON_COMPLIANT / COMPLIANT (jamf_client.py). Anything
    # else — COMPLIANT, UNKNOWN, None, empty, or a failed/403 read — falls to the else path
    # (note_no_drift → END), so a failed read never escalates and UNKNOWN never over-escalates.
    found_match_1 = phantom.decision(
        container=container,
        logical_operator="and",
        conditions=[
            ["check_compliance:action_result.status", "==", "success"],
            ["check_compliance:action_result.data.*.compliance_state", "==", "NON_COMPLIANT"]
        ],
        conditions_dps=[
            ["check_compliance:action_result.status", "==", "success"],
            ["check_compliance:action_result.data.*.compliance_state", "==", "NON_COMPLIANT"]
        ],
        name="is_compliant:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        quarantine_device(action=action, success=success, container=container, results=results, handle=handle)
        return

    # call connected blocks for the else condition 2
    note_no_drift(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_drift(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_drift() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - no containment taken",
          content=(
              "The device is COMPLIANT, its state is UNKNOWN/None, there was no compliance data, "
              "or the compliance read failed (e.g. 403). No containment was taken. "
              "Open a manual review if drift is still suspected."
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_drift_called", value="True")

    return


@phantom.playbook_block()
def quarantine_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_device() called")

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'quarantine_device' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_device_result_item[0],
                "device_type": resolve_device_result_item[1],
                "group_name": "<your-quarantine-group>",
                "context": {'artifact_id': resolve_device_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add to static group", parameters=parameters, name="quarantine_device", assets=["<your-jamf-asset>"], callback=lock_device)

    return


@phantom.playbook_block()
def lock_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device() called")

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_device' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "pin": "<your-6-digit-pin>",
                "message": "<your-return-message>",
                "device_id": resolve_device_result_item[0],
                "device_type": resolve_device_result_item[1],
                "phone_number": "<your-callback-number>",
                "context": {'artifact_id': resolve_device_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_device", assets=["<your-jamf-asset>"], callback=containment_ok)

    return


@phantom.playbook_block()
def containment_ok(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("containment_ok() called")

    # I3: only prompt for the irreversible wipe if containment actually succeeded. A lock on an
    # offline device only QUEUES an MDM command (never a confirmed "locked"), so a non-success
    # status means the device may be uncontained → route to a manual-review note, not the prompt.
    found_match_1 = phantom.decision(
        container=container,
        logical_operator="and",
        conditions=[
            ["quarantine_device:action_result.status", "==", "success"],
            ["lock_device:action_result.status", "==", "success"]
        ],
        conditions_dps=[
            ["quarantine_device:action_result.status", "==", "success"],
            ["lock_device:action_result.status", "==", "success"]
        ],
        name="containment_ok:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        approve_wipe(action=action, success=success, container=container, results=results, handle=handle)
        return

    # call connected blocks for the else condition 2
    note_containment_failed(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_containment_failed(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_containment_failed() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - containment did not succeed",
          content=(
              "Quarantine and/or lock did not report success (a failure, or a queued MDM command "
              "on an offline device). The device may be UNCONTAINED. "
              "Manual review required before any wipe; the wipe prompt was NOT shown."
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_containment_failed_called", value="True")

    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")

    # set approver and message variables for phantom.prompt call

    user = None
    role = "Administrator"
    message = """Device is still reported NON_COMPLIANT after automated correction, and containment (quarantine + lock) completed successfully. Approve device WIPE? This ERASES the device and is IRREVERSIBLE."""

    # parameter list for template variable replacement
    parameters = []

    # responses
    response_types = [
        {
            "prompt": "Approve device WIPE? (irreversible)",
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_wipe", parameters=parameters, response_types=response_types, callback=is_wipe_approved)

    return


@phantom.playbook_block()
def is_wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("is_wipe_approved() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["approve_wipe:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["approve_wipe:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="is_wipe_approved:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_device(action=action, success=success, container=container, results=results, handle=handle)
        return

    # call connected blocks for the else condition 2
    note_wipe_declined(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_wipe_declined(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_declined() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - wipe NOT approved",
          content=(
              "The analyst declined the wipe, or the approval prompt timed out. "
              "The device remains quarantined + locked; no erase was performed. "
              "Follow up manually."
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_declined_called", value="True")

    return


@phantom.playbook_block()
def wipe_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device() called")

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device' call
    # B1: the connector's wipe gate requires confirm == device_id, so confirm is wired to the
    # SAME resolved device-id value as device_id (a truthy flag is rejected as WIPE_NOT_CONFIRMED).
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "pin": "<your-6-digit-pin>",
                "confirm": resolve_device_result_item[0],
                "device_id": resolve_device_result_item[0],
                "device_type": resolve_device_result_item[1],
                "context": {'artifact_id': resolve_device_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_device", assets=["<your-jamf-asset>"], callback=note_wipe_queued)

    return


@phantom.playbook_block()
def note_wipe_queued(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_queued() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - ERASE command queued",
          content=(
              "An ERASE_DEVICE MDM command was QUEUED for the device (not a confirmed erase). "
              "The device wipes on its next check-in."
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_queued_called", value="True")

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    return
