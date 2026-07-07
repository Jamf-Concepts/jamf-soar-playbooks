"""
Jamf - Lost or Stolen Device (macOS + mobile)

Responds to a device reported lost or stolen:
  resolve by serial -> (device found?) -> device_type?
      mobile   -> enable lost mode -> note -> approval gate -> wipe on approval
      computer -> lock device      -> note -> approval gate -> wipe on approval
A decline / timeout / no-device path just writes a note. Never auto-wipes.

Design notes:
- The two device-type branches each carry their OWN note -> prompt -> wipe tail and
  do NOT reconverge. Merging them onto one shared block makes SOAR insert a join that
  waits for BOTH branches; only one runs per device, so that join never completes and
  the note/prompt/wipe are skipped. Per-branch tails avoid the join.
- Block names follow SOAR's <type>_<n> convention with a UNIQUE id per type
  (decision_1..4, code_1..5, prompt_1..2, wipe_device_1..2); reusing an id within a
  type makes SOAR generate two functions with the same name (function-redefined).

Adaptation points (replace before use):
  - <your-jamf-asset>       : your configured Jamf asset (on all 5 action blocks).
  - <security-analyst-role> : the SOAR role the wipe-approval prompts route to.
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

    get_device_by_serial_1(container=container)

    return


@phantom.playbook_block()
def get_device_by_serial_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_serial_1() called")

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.serialNumber","artifact:*.id"])

    parameters = []

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

    phantom.act("get device by serial", parameters=parameters, name="get_device_by_serial_1", assets=["<your-jamf-asset>"], callback=decision_1)

    return


@phantom.playbook_block()
def decision_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_1() called")

    # device found?
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["get_device_by_serial_1:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
            ["get_device_by_serial_1:action_result.data.*.id", "!=", ""]
        ],
        name="decision_1:condition_1",
        delimiter=None)

    if found_match_1:
        decision_2(action=action, success=success, container=container, results=results, handle=handle)
        return

    code_5(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def decision_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_2() called")

    # device_type: mobile?
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["get_device_by_serial_1:action_result.data.*.type", "==", "mobile"]
        ],
        conditions_dps=[
            ["get_device_by_serial_1:action_result.data.*.type", "==", "mobile"]
        ],
        name="decision_2:condition_1",
        delimiter=None)

    # mobile -> enable lost mode branch
    if found_match_1:
        enable_lost_mode_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # else (computer) -> lock device branch
    lock_device_1(action=action, success=success, container=container, results=results, handle=handle)

    return


# ---------------------------------------------------------------------------
# MOBILE branch: enable lost mode -> code_1 -> prompt_1 -> decision_3 -> wipe_device_1 / code_2
# ---------------------------------------------------------------------------

@phantom.playbook_block()
def enable_lost_mode_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("enable_lost_mode_1() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

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

    phantom.act("enable lost mode", parameters=parameters, name="enable_lost_mode_1", assets=["<your-jamf-asset>"], callback=code_1)

    return


@phantom.playbook_block()
def code_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_1() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id", "get_device_by_serial_1:action_result.data.*.serial_number", "get_device_by_serial_1:action_result.data.*.type"], action_results=results)
    lm = phantom.collect2(container=container, datapath=["enable_lost_mode_1:action_result.status"], action_results=results)

    device_id = dev[0][0] if dev and dev[0] else None
    serial = dev[0][1] if dev and len(dev[0]) > 1 else None
    dtype = dev[0][2] if dev and len(dev[0]) > 2 else None
    lost_status = lm[0][0] if lm and lm[0] else None

    lines = []
    lines.append("Lost or Stolen Device - containment outcomes (mobile):")
    lines.append("- Device: id {} (serial {}, type {})".format(device_id, serial, dtype))
    lines.append("- Enable Lost Mode (queued): {}".format(lost_status))
    if lost_status != "success":
        lines.append("WARNING: Enable Lost Mode did not succeed - review before approving a wipe.")
    lines.append("MDM commands are QUEUED and apply when the device next checks in - containment is not guaranteed instant.")
    lines.append("An analyst approval is required before any wipe (irreversible).")

    phantom.add_note(container=container, title="Lost or Stolen Device - containment outcomes (mobile)", content="\n".join(lines), note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_1_called", value="True")

    prompt_1(container=container)

    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")

    # Wipe-approval routes to a SOAR role; set <security-analyst-role> to your analyst role.
    user = None
    role = "<security-analyst-role>"
    message = """A MOBILE device reported LOST or STOLEN has been placed in Lost Mode. Approve a REMOTE WIPE?
This permanently ERASES the device and is IRREVERSIBLE.

Device id: {0}
Serial: {1}
Type: {2}
Enable lost mode status: {3}

Approve only if the device is confirmed unrecoverable and a wipe is authorized."""

    parameters = [
        "get_device_by_serial_1:action_result.data.*.id",
        "get_device_by_serial_1:action_result.data.*.serial_number",
        "get_device_by_serial_1:action_result.data.*.type",
        "enable_lost_mode_1:action_result.status"
    ]

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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="prompt_1", parameters=parameters, response_types=response_types, callback=decision_3)

    return


@phantom.playbook_block()
def decision_3(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_3() called")

    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["prompt_1:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["prompt_1:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="decision_3:condition_1",
        delimiter=None)

    if found_match_1:
        wipe_device_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    code_2(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device_1() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.data.*.type","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

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

    phantom.act("wipe device", parameters=parameters, name="wipe_device_1", assets=["<your-jamf-asset>"])

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
        title = "Lost or Stolen Device - wipe prompt timed out (mobile)"
        content = ("The wipe approval prompt timed out with no response (treated as no-wipe). "
                     "The device remains in Lost Mode (queued); no erase was performed. "
                     "Re-run if a wipe is still required.")
    else:
        title = "Lost or Stolen Device - wipe denied (mobile)"
        content = ("The analyst declined the wipe at the approval prompt. "
                     "The device remains in Lost Mode (queued); no erase was performed.")

    phantom.add_note(container=container, title=title, content=content, note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_2_called", value="True")

    return


# ---------------------------------------------------------------------------
# COMPUTER branch: lock device -> code_3 -> prompt_2 -> decision_4 -> wipe_device_2 / code_4
# ---------------------------------------------------------------------------

@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

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

    phantom.act("lock device", parameters=parameters, name="lock_device_1", assets=["<your-jamf-asset>"], callback=code_3)

    return


@phantom.playbook_block()
def code_3(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_3() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id", "get_device_by_serial_1:action_result.data.*.serial_number", "get_device_by_serial_1:action_result.data.*.type"], action_results=results)
    lk = phantom.collect2(container=container, datapath=["lock_device_1:action_result.status"], action_results=results)

    device_id = dev[0][0] if dev and dev[0] else None
    serial = dev[0][1] if dev and len(dev[0]) > 1 else None
    dtype = dev[0][2] if dev and len(dev[0]) > 2 else None
    lock_status = lk[0][0] if lk and lk[0] else None

    lines = []
    lines.append("Lost or Stolen Device - containment outcomes (computer):")
    lines.append("- Device: id {} (serial {}, type {})".format(device_id, serial, dtype))
    lines.append("- Lock device (queued): {}".format(lock_status))
    if lock_status != "success":
        lines.append("WARNING: Lock device did not succeed - review before approving a wipe.")
    lines.append("MDM commands are QUEUED and apply when the device next checks in - containment is not guaranteed instant.")
    lines.append("An analyst approval is required before any wipe (irreversible).")

    phantom.add_note(container=container, title="Lost or Stolen Device - containment outcomes (computer)", content="\n".join(lines), note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_3_called", value="True")

    prompt_2(container=container)

    return


@phantom.playbook_block()
def prompt_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_2() called")

    # Wipe-approval routes to a SOAR role; set <security-analyst-role> to your analyst role.
    user = None
    role = "<security-analyst-role>"
    message = """A COMPUTER reported LOST or STOLEN has been locked. Approve a REMOTE WIPE?
This permanently ERASES the device and is IRREVERSIBLE.

Device id: {0}
Serial: {1}
Type: {2}
Lock device status: {3}

Approve only if the device is confirmed unrecoverable and a wipe is authorized."""

    parameters = [
        "get_device_by_serial_1:action_result.data.*.id",
        "get_device_by_serial_1:action_result.data.*.serial_number",
        "get_device_by_serial_1:action_result.data.*.type",
        "lock_device_1:action_result.status"
    ]

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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="prompt_2", parameters=parameters, response_types=response_types, callback=decision_4)

    return


@phantom.playbook_block()
def decision_4(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_4() called")

    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["prompt_2:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["prompt_2:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="decision_4:condition_1",
        delimiter=None)

    if found_match_1:
        wipe_device_2(action=action, success=success, container=container, results=results, handle=handle)
        return

    code_4(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device_2() called")

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.data.*.type","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

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

    phantom.act("wipe device", parameters=parameters, name="wipe_device_2", assets=["<your-jamf-asset>"])

    return


@phantom.playbook_block()
def code_4(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_4() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    resp = phantom.collect2(container=container, datapath=["prompt_2:action_result.summary.responses.0"], action_results=results)
    answer = resp[0][0] if resp and resp[0] else None

    if answer in (None, ""):
        title = "Lost or Stolen Device - wipe prompt timed out (computer)"
        content = ("The wipe approval prompt timed out with no response (treated as no-wipe). "
                     "The device remains locked (queued); no erase was performed. "
                     "Re-run if a wipe is still required.")
    else:
        title = "Lost or Stolen Device - wipe denied (computer)"
        content = ("The analyst declined the wipe at the approval prompt. "
                     "The device remains locked (queued); no erase was performed.")

    phantom.add_note(container=container, title=title, content=content, note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_4_called", value="True")

    return


# ---------------------------------------------------------------------------
# No-device / lookup-failed path
# ---------------------------------------------------------------------------

@phantom.playbook_block()
def code_5(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_5() called")

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

    phantom.save_block_result(key="code_5_called", value="True")

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
