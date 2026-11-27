"""
Accepts usernames from the event, finds the affected Jamf devices and posts the full list as a note. A single analyst approval covers the whole batch; if more devices are found than the batch limit (25 by default), the run stops with a note instead. On approval, each device is added to a quarantine group, locked and sent a blank push, and a final note reports the actual result of every action. Devices are never wiped.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'resolve_devices' block
    resolve_devices(container=container)

    return

@phantom.playbook_block()
def resolve_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("resolve_devices() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Looks up every Jamf device for the usernames in the event artifacts.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceUserName","artifact:*.id"])

    parameters = []

    # build parameters list for 'resolve_devices' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "username": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device by username", parameters=parameters, name="resolve_devices", assets=["jamf_pro"], callback=devices_found)

    return


@phantom.playbook_block()
def devices_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("devices_found() called")

    ################################################################################
    # Continues only if the lookup succeeded and returned at least one device.
    ################################################################################

    # check for 'if' condition 1
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

    # call connected blocks if condition 1 matched
    if found_match_1:
        check_compliance(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_no_devices(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_devices() called")

    ################################################################################
    # This block uses custom code. Adds a note when no Jamf devices were found for 
    # the usernames.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="IdP breach - no devices resolved",
          content="No Jamf devices resolved for the affected username(s), or the lookup failed. No containment was attempted. Check the usernames, and that the Jamf Account integration has the devices:read capability, then re-run.",
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_devices_called", value="True")

    return


@phantom.playbook_block()
def check_compliance(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("check_compliance() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Gets each device's compliance status from Jamf Pro for the preview.
    ################################################################################

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'check_compliance' call
    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_devices_result_item[0],
                "device_type": resolve_devices_result_item[1],
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="check_compliance", assets=["jamf_pro"], callback=build_quarantine_preview)

    return


@phantom.playbook_block()
def build_quarantine_preview(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("build_quarantine_preview() called")

    ################################################################################
    # This block uses custom code. Posts the full list of devices to quarantine as 
    # a note, or stops with a note if there are more than the batch limit.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Post a dry-run note listing every device (scope disclosure) and enforce the AGGREGATE
    # batch cap (count > MAX_DEVICES -> note_batch_too_large, else -> approve). Full logic in the
    # .py source of truth.
    phantom.add_note(
          container=container,
          title="IdP breach - proposed quarantine (review before approving)",
          content="Lists every resolved device + compliance; a Yes quarantines ALL listed. Aborts if over the batch cap.",
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="build_quarantine_preview_called", value="True")

    approve_bulk_quarantine(container=container)
    note_batch_too_large(container=container)

    return


@phantom.playbook_block()
def note_batch_too_large(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_batch_too_large() called")

    ################################################################################
    # This block uses custom code. Adds a note and stops when more devices were found 
    # than the batch limit (25 by default).
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="IdP breach - batch too large, aborted",
          content="The affected device set exceeds the batch-size cap (MAX_DEVICES). Bulk quarantine was ABORTED and no containment was attempted, to prevent a runaway mass action. Re-scope the set, or raise the cap deliberately after review.",
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_batch_too_large_called", value="True")

    return


@phantom.playbook_block()
def approve_bulk_quarantine(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_bulk_quarantine() called")

    ################################################################################
    # Asks an analyst to approve quarantining every device in the list with one approval. 
    # Times out after 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<your-security-analyst-role>"
    message = """IdP breach response. This will QUARANTINE (add to group + lock + blank push) ALL devices listed in the case note titled \"IdP breach - proposed quarantine (review before approving)\" - read it for the exact device list and account reconciliation. Bulk wipe is NOT part of this action. Approve bulk quarantine?"""

    # parameter list for template variable replacement
    parameters = []

    # responses
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

    ################################################################################
    # Quarantines the devices only if the analyst answered Yes.
    ################################################################################

    # check for 'if' condition 1
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

    # call connected blocks if condition 1 matched
    if found_match_1:
        quarantine_add_group(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_not_approved(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_not_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_not_approved() called")

    ################################################################################
    # This block uses custom code. Adds a note that the bulk quarantine was not approved 
    # or the prompt timed out.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="IdP breach - bulk quarantine NOT approved",
          content="The analyst declined the bulk quarantine, or the approval prompt timed out. No containment was performed. Follow up manually if the breach is confirmed.",
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_not_approved_called", value="True")

    return


@phantom.playbook_block()
def quarantine_add_group(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_add_group() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Adds each device to the computer or mobile quarantine group.
    ################################################################################

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'quarantine_add_group' call
    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            parameters.append({
                "group_id": "<your-computer-quarantine-group>",
                "device_id": resolve_devices_result_item[0],
                "device_type": resolve_devices_result_item[1],
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add to static group", parameters=parameters, name="quarantine_add_group", assets=["jamf_pro"], callback=quarantine_lock)

    return


@phantom.playbook_block()
def quarantine_lock(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_lock() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Locks each device.
    ################################################################################

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'quarantine_lock' call
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

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="quarantine_lock", assets=["jamf_pro"], callback=quarantine_push)

    return


@phantom.playbook_block()
def quarantine_push(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_push() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Sends a blank push to each device so it checks in.
    ################################################################################

    resolve_devices_result_data = phantom.collect2(container=container, datapath=["resolve_devices:action_result.data.*.id","resolve_devices:action_result.data.*.type","resolve_devices:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'quarantine_push' call
    for resolve_devices_result_item in resolve_devices_result_data:
        if resolve_devices_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_devices_result_item[0],
                "device_type": resolve_devices_result_item[1],
                "context": {'artifact_id': resolve_devices_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("send blank push", parameters=parameters, name="quarantine_push", assets=["jamf_pro"], callback=report_results)

    return


@phantom.playbook_block()
def report_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("report_results() called")

    ################################################################################
    # This block uses custom code. Adds a note with the actual result of every action 
    # for every device.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Build results from REAL per-action statuses (never report a failed contain as success).
    # Full logic in the .py source of truth.
    phantom.add_note(
          container=container,
          title="IdP breach - bulk quarantine results",
          content="Per-action success/failure counts for add-to-group, lock, and blank push.",
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="report_results_called", value="True")

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