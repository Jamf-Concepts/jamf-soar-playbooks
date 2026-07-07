"""
Jamf - Lost or Stolen Device (macOS + mobile)

Responds to a device reported lost or stolen:
  resolve by serial -> (device found?) -> device_type?
      mobile   -> enable lost mode
      computer -> lock device
  -> containment note -> analyst approval gate -> wipe ONLY on approval.
A decline / timeout / no-device path just writes a note. Never auto-wipes.

Adaptation points (replace before use):
  - <your-jamf-asset>   : Jamf asset (this dev copy uses "test1").
  - approver            : prompt routes to the "Sarah" user in this dev copy;
                          switch to a security-analyst ROLE for distribution.
  - lock PIN "000000"   : replace with your 6-digit unlock PIN (computer lock).
  - lock-screen message : the lost/stolen message shown on the device.
Enrichment (#5 Device Enrichment Input) and quarantine (add to static group)
are deferred to v2.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'get_device_by_serial_1' block
    get_device_by_serial_1(container=container)

    return

@phantom.playbook_block()
def get_device_by_serial_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_serial_1() called")

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.serialNumber","artifact:*.id"])

    parameters = []

    # build parameters list for 'get_device_by_serial_1' call
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

    phantom.act("get device by serial", parameters=parameters, name="get_device_by_serial_1", assets=["test1"], callback=decision_2)

    return


@phantom.playbook_block()
def decision_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_2() called")

    # check for 'if' condition 1 - device found
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["get_device_by_serial_1:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
            ["get_device_by_serial_1:action_result.data.*.id", "!=", ""]
        ],
        name="decision_2:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        device_type(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2 - no device resolved
    code_3(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def device_type(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("device_type() called")

    # check for 'if' condition 1 - mobile device
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["get_device_by_serial_1:action_result.data.*.type", "==", "mobile"]
        ],
        conditions_dps=[
            ["get_device_by_serial_1:action_result.data.*.type", "==", "mobile"]
        ],
        name="device_type:condition_1",
        delimiter=None)

    # mobile -> enable lost mode
    if found_match_1:
        enable_lost_mode_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # else (computer) -> lock device
    lock_device_1(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def enable_lost_mode_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("enable_lost_mode_1() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'enable_lost_mode_1' call (mobile branch)
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_serial_1_result_item[0],
                "device_type": "mobile",
                "message": "This device has been reported lost or stolen. Please contact IT/Security.",
                "context": {'artifact_id': get_device_by_serial_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("enable lost mode", parameters=parameters, name="enable_lost_mode_1", assets=["test1"], callback=code_1)

    return


@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_device_1' call (computer branch)
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "pin": "000000",
                "message": "This device has been reported lost or stolen. Please contact IT/Security.",
                "device_id": get_device_by_serial_1_result_item[0],
                "device_type": "computer",
                "context": {'artifact_id': get_device_by_serial_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_device_1", assets=["test1"], callback=code_1)

    return


@phantom.playbook_block()
def code_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_1() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id", "get_device_by_serial_1:action_result.data.*.serial_number", "get_device_by_serial_1:action_result.data.*.type"], action_results=results)
    lk = phantom.collect2(container=container, datapath=["lock_device_1:action_result.status"], action_results=results)
    lm = phantom.collect2(container=container, datapath=["enable_lost_mode_1:action_result.status"], action_results=results)

    device_id = dev[0][0] if dev and dev[0] else None
    serial = dev[0][1] if dev and len(dev[0]) > 1 else None
    dtype = dev[0][2] if dev and len(dev[0]) > 2 else None
    lock_status = lk[0][0] if lk and lk[0] else None
    lost_status = lm[0][0] if lm and lm[0] else None

    lines = []
    lines.append("Lost or Stolen Device - containment outcomes:")
    lines.append("- Device: id {} (serial {}, type {})".format(device_id, serial, dtype))
    if dtype == "mobile":
        lines.append("- Enable Lost Mode (queued): {}".format(lost_status))
        if lost_status != "success":
            lines.append("WARNING: Enable Lost Mode did not succeed - review before approving a wipe.")
    else:
        lines.append("- Lock device (queued): {}".format(lock_status))
        if lock_status != "success":
            lines.append("WARNING: Lock device did not succeed - review before approving a wipe.")
    lines.append("MDM commands are QUEUED and apply when the device next checks in - containment is not guaranteed instant.")
    lines.append("An analyst approval is required before any wipe (irreversible).")

    phantom.add_note(container=container, title="Lost or Stolen Device - containment outcomes", content="\n".join(lines), note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_1_called", value="True")

    prompt_1(container=container)

    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")

    # set approver and message variables for phantom.prompt call
    # DEV: routes to the "Sarah" user; switch to a security-analyst ROLE for distribution.
    user = "Sarah"
    role = None
    message = """A device reported LOST or STOLEN has been contained. Approve a REMOTE WIPE?
This permanently ERASES the device and is IRREVERSIBLE.

Device id: {0}
Serial: {1}
Type: {2}
Lock device (computer) status: {3}
Enable lost mode (mobile) status: {4}

Approve only if the device is confirmed unrecoverable and a wipe is authorized."""

    # parameter list for template variable replacement
    parameters = [
        "get_device_by_serial_1:action_result.data.*.id",
        "get_device_by_serial_1:action_result.data.*.serial_number",
        "get_device_by_serial_1:action_result.data.*.type",
        "lock_device_1:action_result.status",
        "enable_lost_mode_1:action_result.status"
    ]

    # responses
    response_types = [
        {
            "prompt": "Proceed with wipe?",
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="prompt_1", parameters=parameters, response_types=response_types, callback=decision_1)

    return


@phantom.playbook_block()
def decision_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_1() called")

    # check for 'if' condition 1 - analyst approved
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["prompt_1:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["prompt_1:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="decision_1:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_device_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2 - declined / timed out
    code_2(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device_1() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.data.*.type","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device_1' call
    # confirm MUST equal device_id (connector's anti-fat-finger gate); device_type from the resolved device.
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "confirm": get_device_by_serial_1_result_item[0],
                "device_id": get_device_by_serial_1_result_item[0],
                "device_type": get_device_by_serial_1_result_item[1],
                "context": {'artifact_id': get_device_by_serial_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_device_1", assets=["test1"])

    return


@phantom.playbook_block()
def code_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_2() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    resp = phantom.collect2(container=container, datapath=["prompt_1:action_result.summary.responses.0"], action_results=results)
    answer = resp[0][0] if resp and resp[0] else None

    if answer in (None, ""):
        title = "Lost or Stolen Device - wipe prompt timed out"
        content = ("The wipe approval prompt timed out with no response (treated as no-wipe). "
                     "The device remains under the containment that was queued (lock or lost mode); no erase was performed. "
                     "Re-run if a wipe is still required.")
    else:
        title = "Lost or Stolen Device - wipe denied"
        content = ("The analyst declined the wipe at the approval prompt. "
                     "The device remains under the containment that was queued (lock or lost mode); no erase was performed.")

    phantom.add_note(container=container, title=title, content=content, note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_2_called", value="True")

    return


@phantom.playbook_block()
def code_3(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_3() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.status"], action_results=results)
    lookup_status = rows[0][0] if rows and rows[0] else None

    if lookup_status == "success":
        title = "Lost or Stolen Device - no device matched"
        content = ("No Jamf device matched the provided serial number. "
                     "No actions were taken. Verify the serial is correct and re-run.")
    else:
        title = "Lost or Stolen Device - device lookup FAILED"
        content = ("The 'get device by serial' lookup did not succeed (status: {}). "
                     "No device was resolved and no actions were taken. This usually means a "
                     "Jamf asset / credential / privilege problem, NOT a wrong serial - check "
                     "the asset config and API role, then re-run.".format(lookup_status))

    phantom.add_note(container=container, title=title, content=content, note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_3_called", value="True")

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
