"""
Accepts a device serial number from the event and attempts to restore MDM control by redeploying the management framework and forcing a check-in, then re-checks compliance. If the device is still non-compliant, it is quarantined and locked, and an analyst is asked to approve before any wipe. A note is added on every outcome. Computers only.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'has_serial' block
    has_serial(container=container)

    return

@phantom.playbook_block()
def resolve_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("resolve_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Looks up the computer in Jamf Pro by the serial number from the event artifact.
    ################################################################################

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

    phantom.act("get device by serial", parameters=parameters, name="resolve_device", assets=["jamf_pro"], callback=device_found)

    return


@phantom.playbook_block()
def redeploy_framework(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("redeploy_framework() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Redeploys the Jamf management framework to restore MDM control.
    ################################################################################

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'redeploy_framework' call
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

    phantom.act("redeploy management framework", parameters=parameters, name="redeploy_framework", assets=["jamf_pro"], callback=force_checkin)

    return


@phantom.playbook_block()
def force_checkin(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("force_checkin() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Sends a blank push so the computer checks in.
    ################################################################################

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

    phantom.act("send blank push", parameters=parameters, name="force_checkin", assets=["jamf_pro"], callback=check_compliance)

    return


@phantom.playbook_block()
def check_compliance(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("check_compliance() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Gets the computer's compliance status after the redeploy.
    ################################################################################

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

    phantom.act("get compliance status", parameters=parameters, name="check_compliance", assets=["jamf_pro"], callback=is_compliant)

    return


@phantom.playbook_block()
def is_compliant(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("is_compliant() called")

    ################################################################################
    # Contains the computer only if it is still non-compliant.
    ################################################################################

    # check for 'if' condition 1
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

    # check for 'else' condition 2
    note_no_drift(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def quarantine_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Adds the computer to the quarantine group.
    ################################################################################

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'quarantine_device' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_device_result_item[0],
                "group_name": "<your-quarantine-group>",
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

    phantom.act("add to static group", parameters=parameters, name="quarantine_device", assets=["jamf_pro"], callback=lock_device)

    return


@phantom.playbook_block()
def lock_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Locks the computer with the lock-screen message and PIN.
    ################################################################################

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

    phantom.act("lock device", parameters=parameters, name="lock_device", assets=["jamf_pro"], callback=containment_ok)

    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")

    ################################################################################
    # Asks an analyst to approve wiping the computer. Times out after 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "Administrator"
    message = """Device is still reported NON_COMPLIANT after automated correction. Quarantine and lock were QUEUED (lock is an async MDM command — queued, not confirmed applied). Approve device WIPE? This ERASES the device and is IRREVERSIBLE."""

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

    ################################################################################
    # Wipes the computer only if the analyst answered Yes.
    ################################################################################

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

    # check for 'else' condition 2
    note_wipe_declined(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Erases the computer. Runs only after analyst approval.
    ################################################################################

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
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

    phantom.act("wipe device", parameters=parameters, name="wipe_device", assets=["jamf_pro"], callback=note_wipe_outcome)

    return


@phantom.playbook_block()
def device_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("device_found() called")

    ################################################################################
    # Continues only if Jamf Pro returned a matching device.
    ################################################################################

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

    # check for 'else' condition 2
    note_no_device(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_device() called")

    ################################################################################
    # This block uses custom code. Adds a note when no device matched the serial.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - no device found",
          content=(
              "No Jamf device matched the serial from the event. "
              "Playbook stopped; no correction or containment was attempted. "
              "Verify the serial and re-run. "
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_device_called", value="True")

    return


@phantom.playbook_block()
def note_no_drift(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_drift() called")

    ################################################################################
    # This block uses custom code. Adds a note that the computer is compliant, so 
    # no containment was taken.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - no containment taken",
          content=(
              "The device is COMPLIANT, its state is UNKNOWN/None, there was no compliance data, "
              "or the compliance read failed (e.g. 403). No containment was taken. "
              "Open a manual review if drift is still suspected. "
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_drift_called", value="True")

    return


@phantom.playbook_block()
def containment_ok(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("containment_ok() called")

    ################################################################################
    # Asks for wipe approval only if both the quarantine and the lock succeeded.
    ################################################################################

    # check for 'if' condition 1
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

    # check for 'else' condition 2
    note_containment_failed(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_containment_failed(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_containment_failed() called")

    ################################################################################
    # This block uses custom code. Adds a note when the quarantine or the lock did 
    # not succeed.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - containment did not succeed",
          content=(
              "Quarantine and/or lock did not report success (a failure, or a queued MDM command "
              "on an offline device). The device may be UNCONTAINED. "
              "Manual review required before any wipe; wipe prompt was NOT shown. "
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_containment_failed_called", value="True")

    return


@phantom.playbook_block()
def note_wipe_declined(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_declined() called")

    ################################################################################
    # This block uses custom code. Adds a note that the wipe was declined or the prompt 
    # timed out.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - wipe NOT approved",
          content=(
              "The analyst declined the wipe, or the approval prompt timed out. "
              "The device remains quarantined + locked; no erase was performed. "
              "Follow up manually. "
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_declined_called", value="True")

    return


@phantom.playbook_block()
def note_wipe_outcome(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_outcome() called")

    ################################################################################
    # This block uses custom code. Adds a note saying whether the erase command was 
    # queued or failed.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["wipe_device:action_result.status", "wipe_device:action_result.message", "wipe_device:action_result.parameter.device_id"], action_results=results)
    outcomes = [(r[2], r[0], r[1]) for r in rows if r] or [(None, None, "no wipe result was returned")]
    failed = [o for o in outcomes if o[1] != "success"]

    if not failed:
        phantom.add_note(
              container=container,
              title="Compliance drift - ERASE command queued",
              content=(
                  "An ERASE_DEVICE MDM command was QUEUED for the device (not a confirmed erase). "
                  "The device wipes on its next check-in. "
              ),
              note_type="general",
          )
    else:
        lines = ["- device {}: {} ({})".format(d, s, m) for d, s, m in outcomes]
        phantom.add_note(
              container=container,
              title="Compliance drift - ERASE command NOT queued",
              content=(
                  "The wipe action returned an error - the ERASE command was NOT queued for every device. "
                  "The device is still quarantined + locked. Manual intervention required.\n"
                  + "\n".join(lines)
              ),
              note_type="general",
          )
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_outcome_called", value="True")

    return


@phantom.playbook_block()
def has_serial(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("has_serial() called")

    ################################################################################
    # Continues only if the event has a serial number.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["artifact:*.cef.serialNumber", "!=", ""]
        ],
        conditions_dps=[
            ["artifact:*.cef.serialNumber", "!=", ""]
        ],
        name="has_serial:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        resolve_device(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_no_serial(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_serial(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_serial() called")

    ################################################################################
    # This block uses custom code. Adds a note that the event had no serial number.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="Compliance drift - no serial on artifact",
          content=(
              "The triggering artifact carried no serialNumber, so no device could be resolved. "
              "Playbook stopped; nothing was attempted. Map the event's serial to cef.serialNumber. "
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_serial_called", value="True")

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