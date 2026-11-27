"""
Accepts a device serial number from the event. Mobile devices are put into Lost Mode and computers are locked, and a note records the result. An analyst must then approve before the device is wiped; a decline, a timeout or a serial with no matching device only adds a note.
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
def find_device_by_serial(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("find_device_by_serial() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Looks up the device in Jamf Pro by the serial number from the event artifact.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.serialNumber","artifact:*.id"])

    parameters = []

    # build parameters list for 'find_device_by_serial' call
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

    phantom.act("get device by serial", parameters=parameters, name="find_device_by_serial", assets=["jamf_pro"], callback=device_found)

    return


@phantom.playbook_block()
def lock_computer(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_computer() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Locks the computer with the lock-screen message and PIN.
    ################################################################################

    find_device_by_serial_result_data = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.data.*.id","find_device_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_computer' call
    for find_device_by_serial_result_item in find_device_by_serial_result_data:
        if find_device_by_serial_result_item[0] is not None:
            parameters.append({
                "pin": "000000",
                "message": "This device has been reported lost or stolen. Please contact IT/Security.",
                "device_id": find_device_by_serial_result_item[0],
                "device_type": "computer",
                "context": {'artifact_id': find_device_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_computer", assets=["jamf_pro"], callback=note_computer_containment)

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
            ["find_device_by_serial:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
            ["find_device_by_serial:action_result.data.*.id", "!=", ""]
        ],
        name="device_found:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        device_type(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_lookup_failed(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_lookup_failed(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_lookup_failed() called")

    ################################################################################
    # This block uses custom code. Adds a note when no device matched, the lookup 
    # failed, or a platform was skipped.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.status", "find_device_by_serial:action_result.summary.skipped"], action_results=results)
    lookup_status = rows[0][0] if rows and rows[0] else None
    skipped = rows[0][1] if rows and len(rows[0]) > 1 else None

    if lookup_status != "success":
        title = "Lost or Stolen Device - device lookup FAILED"
        content = ("The 'get device by serial' lookup did not succeed (status: {}). "
                     "No device was resolved and no actions were taken. This usually means a "
                     "Jamf asset / credential / privilege problem, NOT a wrong serial - check "
                     "the asset config and API role, then re-run.".format(lookup_status))
    elif skipped:
        # get device by serial is best-effort across computer + mobile: it returns success even
        # when one platform was SKIPPED for auth/privilege (recorded in summary.skipped). Do NOT
        # report that as a clean "no device matched" - the lost/stolen device may be on the
        # skipped platform and is NOT contained.
        title = "Lost or Stolen Device - device lookup PARTIALLY failed (a platform was skipped)"
        content = ("The lookup succeeded on one platform but SKIPPED another due to a read/privilege "
                     "error ({}), and no device matched on the platform that WAS read. The lost/stolen "
                     "device may be on the SKIPPED platform and is NOT contained. Grant the API role "
                     "read access to the skipped platform, then re-run - do not assume the serial is wrong.".format(skipped))
    else:
        title = "Lost or Stolen Device - no device matched"
        content = ("No Jamf device matched the provided serial number (both platforms were read). "
                     "No actions were taken. Verify the serial is correct and re-run.")

    phantom.add_note(container=container, title=title, content=content, note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_lookup_failed_called", value="True")

    return


@phantom.playbook_block()
def device_type(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("device_type() called")

    ################################################################################
    # Sends mobile devices to Lost Mode and computers to lock.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["find_device_by_serial:action_result.data.*.type", "==", "mobile"]
        ],
        conditions_dps=[
            ["find_device_by_serial:action_result.data.*.type", "==", "mobile"]
        ],
        name="device_type:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        enable_lost_mode(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    lock_computer(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def enable_lost_mode(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("enable_lost_mode() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Puts the mobile device into Lost Mode with the lost or stolen message.
    ################################################################################

    find_device_by_serial_result_data = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.data.*.id","find_device_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'enable_lost_mode' call
    for find_device_by_serial_result_item in find_device_by_serial_result_data:
        if find_device_by_serial_result_item[0] is not None:
            parameters.append({
                "message": "This device has been reported lost or stolen. Please contact IT/Security.",
                "device_id": find_device_by_serial_result_item[0],
                "device_type": "mobile",
                "context": {'artifact_id': find_device_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("enable lost mode", parameters=parameters, name="enable_lost_mode", assets=["jamf_pro"], callback=note_mobile_containment)

    return


@phantom.playbook_block()
def note_mobile_containment(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_mobile_containment() called")

    ################################################################################
    # This block uses custom code. Adds a note with the Lost Mode result.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.data.*.id", "find_device_by_serial:action_result.data.*.serial_number", "find_device_by_serial:action_result.data.*.type"], action_results=results)
    lm = phantom.collect2(container=container, datapath=["enable_lost_mode:action_result.status"], action_results=results)

    matched = [d for d in dev if d and d[0] is not None]
    lost_status = lm[0][0] if lm and lm[0] else None

    lines = []
    lines.append("Lost or Stolen Device - containment outcomes (mobile):")
    # scope truthfulness: a serial should match one device, but enumerate ALL matches so the
    # analyst sees the full blast radius before approving (containment + wipe act on every match).
    if len(matched) > 1:
        lines.append("WARNING: {} devices matched this serial - ALL are contained and ALL will be wiped if approved. Review every device below before approving.".format(len(matched)))
    for d in matched:
        serial = d[1] if len(d) > 1 else None
        dtype = d[2] if len(d) > 2 else None
        lines.append("- device id {} (serial {}, type {})".format(d[0], serial, dtype))
    lines.append("- Enable Lost Mode - MDM command status: {}".format(lost_status))
    if lost_status != "success":
        lines.append("WARNING: Enable Lost Mode did not succeed - review before approving a wipe.")
    lines.append("MDM commands are QUEUED and apply when the device next checks in - containment is not guaranteed instant.")
    lines.append("An analyst approval is required before any wipe (irreversible).")

    phantom.add_note(container=container, title="Lost or Stolen Device - containment outcomes (mobile)", content="\n".join(lines), note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_mobile_containment_called", value="True")

    approve_mobile_wipe(container=container)

    return


@phantom.playbook_block()
def approve_mobile_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_mobile_wipe() called")

    ################################################################################
    # Asks an analyst to approve wiping the mobile device. Times out after 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<security-analyst-role>"
    message = """A MOBILE device reported LOST or STOLEN has been placed in Lost Mode. Approve a REMOTE WIPE?\nThis permanently ERASES the device and is IRREVERSIBLE.\n\nDevice id: {0}\nSerial: {1}\nType: {2}\nEnable lost mode status: {3}\n\nApprove only if the device is confirmed unrecoverable and a wipe is authorized."""

    # parameter list for template variable replacement
    parameters = [
        "find_device_by_serial:action_result.data.*.id",
        "find_device_by_serial:action_result.data.*.serial_number",
        "find_device_by_serial:action_result.data.*.type",
        "enable_lost_mode:action_result.status"
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_mobile_wipe", parameters=parameters, response_types=response_types, callback=mobile_wipe_approved)

    return


@phantom.playbook_block()
def mobile_wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("mobile_wipe_approved() called")

    ################################################################################
    # Wipes the mobile device only if the analyst answered Yes.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["approve_mobile_wipe:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["approve_mobile_wipe:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="mobile_wipe_approved:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_mobile_device(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_mobile_wipe_declined(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_mobile_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_mobile_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Erases the mobile device. Runs only after analyst approval.
    ################################################################################

    find_device_by_serial_result_data = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.data.*.id","find_device_by_serial:action_result.data.*.type","find_device_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_mobile_device' call
    for find_device_by_serial_result_item in find_device_by_serial_result_data:
        if find_device_by_serial_result_item[0] is not None:
            parameters.append({
                "confirm": find_device_by_serial_result_item[0],
                "device_id": find_device_by_serial_result_item[0],
                "device_type": find_device_by_serial_result_item[1],
                "context": {'artifact_id': find_device_by_serial_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_mobile_device", assets=["jamf_pro"], callback=note_mobile_wipe_outcome)

    return


@phantom.playbook_block()
def note_mobile_wipe_declined(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_mobile_wipe_declined() called")

    ################################################################################
    # This block uses custom code. Adds a note that the wipe was declined or the prompt 
    # timed out.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    resp = phantom.collect2(container=container, datapath=["approve_mobile_wipe:action_result.summary.responses.0"], action_results=results)
    lm = phantom.collect2(container=container, datapath=["enable_lost_mode:action_result.status"], action_results=results)
    answer = resp[0][0] if resp and resp[0] else None
    lost_status = lm[0][0] if lm and lm[0] else None

    # M1: only claim containment if enable-lost-mode actually succeeded; otherwise say so plainly.
    if lost_status == "success":
        contained = "the device remains in Lost Mode (queued)"
    else:
        contained = "WARNING: Lost Mode was NOT successfully enabled ({}) - the device may NOT be contained, follow up".format(lost_status)

    if answer in (None, ""):
        title = "Lost or Stolen Device - wipe prompt timed out (mobile)"
        content = ("The wipe approval prompt timed out with no response (treated as no-wipe). "
                     "No erase was performed; {}. Re-run if a wipe is still required.".format(contained))
    else:
        title = "Lost or Stolen Device - wipe denied (mobile)"
        content = ("The analyst declined the wipe at the approval prompt. "
                     "No erase was performed; {}.".format(contained))

    phantom.add_note(container=container, title=title, content=content, note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_mobile_wipe_declined_called", value="True")

    return


@phantom.playbook_block()
def note_computer_containment(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_computer_containment() called")

    ################################################################################
    # This block uses custom code. Adds a note with the lock result.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.data.*.id", "find_device_by_serial:action_result.data.*.serial_number", "find_device_by_serial:action_result.data.*.type"], action_results=results)
    lk = phantom.collect2(container=container, datapath=["lock_computer:action_result.status"], action_results=results)

    matched = [d for d in dev if d and d[0] is not None]
    lock_status = lk[0][0] if lk and lk[0] else None

    lines = []
    lines.append("Lost or Stolen Device - containment outcomes (computer):")
    # scope truthfulness: enumerate ALL matches so the analyst sees the full blast radius
    # before approving (containment + wipe act on every match).
    if len(matched) > 1:
        lines.append("WARNING: {} devices matched this serial - ALL are contained and ALL will be wiped if approved. Review every device below before approving.".format(len(matched)))
    for d in matched:
        serial = d[1] if len(d) > 1 else None
        dtype = d[2] if len(d) > 2 else None
        lines.append("- device id {} (serial {}, type {})".format(d[0], serial, dtype))
    lines.append("- Lock device - MDM command status: {}".format(lock_status))
    if lock_status != "success":
        lines.append("WARNING: Lock device did not succeed - review before approving a wipe.")
    lines.append("MDM commands are QUEUED and apply when the device next checks in - containment is not guaranteed instant.")
    lines.append("An analyst approval is required before any wipe (irreversible).")

    phantom.add_note(container=container, title="Lost or Stolen Device - containment outcomes (computer)", content="\n".join(lines), note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_computer_containment_called", value="True")

    approve_computer_wipe(container=container)

    return


@phantom.playbook_block()
def approve_computer_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_computer_wipe() called")

    ################################################################################
    # Asks an analyst to approve wiping the computer. Times out after 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<security-analyst-role>"
    message = """A COMPUTER reported LOST or STOLEN has been locked. Approve a REMOTE WIPE?\nThis permanently ERASES the device and is IRREVERSIBLE.\n\nDevice id: {0}\nSerial: {1}\nType: {2}\nLock device status: {3}\n\nApprove only if the device is confirmed unrecoverable and a wipe is authorized."""

    # parameter list for template variable replacement
    parameters = [
        "find_device_by_serial:action_result.data.*.id",
        "find_device_by_serial:action_result.data.*.serial_number",
        "find_device_by_serial:action_result.data.*.type",
        "lock_computer:action_result.status"
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_computer_wipe", parameters=parameters, response_types=response_types, callback=computer_wipe_approved)

    return


@phantom.playbook_block()
def computer_wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("computer_wipe_approved() called")

    ################################################################################
    # Wipes the computer only if the analyst answered Yes.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["approve_computer_wipe:action_result.summary.responses.0", "==", "Yes"]
        ],
        conditions_dps=[
            ["approve_computer_wipe:action_result.summary.responses.0", "==", "Yes"]
        ],
        name="computer_wipe_approved:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_computer(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_computer_wipe_declined(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_computer(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_computer() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Erases the computer. Runs only after analyst approval.
    ################################################################################

    find_device_by_serial_result_data = phantom.collect2(container=container, datapath=["find_device_by_serial:action_result.data.*.id","find_device_by_serial:action_result.data.*.type","find_device_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_computer' call
    for find_device_by_serial_result_item in find_device_by_serial_result_data:
        if find_device_by_serial_result_item[0] is not None:
            parameters.append({
                "confirm": find_device_by_serial_result_item[0],
                "device_id": find_device_by_serial_result_item[0],
                "device_type": find_device_by_serial_result_item[1],
                "context": {'artifact_id': find_device_by_serial_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_computer", assets=["jamf_pro"], callback=note_computer_wipe_outcome)

    return


@phantom.playbook_block()
def note_computer_wipe_declined(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_computer_wipe_declined() called")

    ################################################################################
    # This block uses custom code. Adds a note that the wipe of the computer was declined 
    # or the prompt timed out.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    resp = phantom.collect2(container=container, datapath=["approve_computer_wipe:action_result.summary.responses.0"], action_results=results)
    lk = phantom.collect2(container=container, datapath=["lock_computer:action_result.status"], action_results=results)
    answer = resp[0][0] if resp and resp[0] else None
    lock_status = lk[0][0] if lk and lk[0] else None

    # M1: only claim containment if the lock actually succeeded; otherwise say so plainly.
    if lock_status == "success":
        contained = "the device remains locked (queued)"
    else:
        contained = "WARNING: the lock did NOT succeed ({}) - the device may NOT be contained, follow up".format(lock_status)

    if answer in (None, ""):
        title = "Lost or Stolen Device - wipe prompt timed out (computer)"
        content = ("The wipe approval prompt timed out with no response (treated as no-wipe). "
                     "No erase was performed; {}. Re-run if a wipe is still required.".format(contained))
    else:
        title = "Lost or Stolen Device - wipe denied (computer)"
        content = ("The analyst declined the wipe at the approval prompt. "
                     "No erase was performed; {}.".format(contained))

    phantom.add_note(container=container, title=title, content=content, note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_computer_wipe_declined_called", value="True")

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
        find_device_by_serial(action=action, success=success, container=container, results=results, handle=handle)
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

    phantom.add_note(container=container,
        title="Lost or Stolen Device - no serial on the event",
        content=("The triggering event has no serial (artifact:*.cef.serialNumber is empty), so no device could be "
                 "resolved and no actions were taken. Add the device serial to the event and re-run - this is a "
                 "missing-input condition, NOT a Jamf asset / credential / privilege problem."),
        note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_serial_called", value="True")

    return


@phantom.playbook_block()
def note_mobile_wipe_outcome(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_mobile_wipe_outcome() called")

    ################################################################################
    # This block uses custom code. Adds a note saying whether the wipe of the mobile 
    # device was queued or failed.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["wipe_mobile_device:action_result.status", "wipe_mobile_device:action_result.message", "wipe_mobile_device:action_result.parameter.device_id"], action_results=results)
    outcomes = [(r[2], r[0], r[1]) for r in rows if r] or [(None, None, "no wipe result was returned")]
    failed = [o for o in outcomes if o[1] != "success"]

    if not failed:
        phantom.add_note(container=container,
            title="Lost or Stolen Device - wipe QUEUED (mobile)",
            content=("The remote WIPE (erase) was approved and the command was accepted / QUEUED for the mobile device. "
                     "MDM commands are queued and apply when the device next checks in - QUEUED is not confirmed-erased. "
                     "Track completion in the device's Jamf command history."),
            note_type="general")
    else:
        lines = ["- device {}: {} ({})".format(d, s, m) for d, s, m in outcomes]
        phantom.add_note(container=container,
            title="Lost or Stolen Device - wipe FAILED / NOT queued (mobile)",
            content=("The remote WIPE was approved but did NOT queue for every device. A device whose wipe did not queue is NOT being "
                     "erased and still holds data - investigate (enrollment / supervision / privilege / device state) and re-run.\n"
                     + "\n".join(lines)),
            note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_mobile_wipe_outcome_called", value="True")

    return


@phantom.playbook_block()
def note_computer_wipe_outcome(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_computer_wipe_outcome() called")

    ################################################################################
    # This block uses custom code. Adds a note saying whether the wipe of the computer 
    # was queued or failed.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["wipe_computer:action_result.status", "wipe_computer:action_result.message", "wipe_computer:action_result.parameter.device_id"], action_results=results)
    outcomes = [(r[2], r[0], r[1]) for r in rows if r] or [(None, None, "no wipe result was returned")]
    failed = [o for o in outcomes if o[1] != "success"]

    if not failed:
        phantom.add_note(container=container,
            title="Lost or Stolen Device - wipe QUEUED (computer)",
            content=("The remote WIPE (erase) was approved and the command was accepted / QUEUED for the computer device. "
                     "MDM commands are queued and apply when the device next checks in - QUEUED is not confirmed-erased. "
                     "Track completion in the device's Jamf command history."),
            note_type="general")
    else:
        lines = ["- device {}: {} ({})".format(d, s, m) for d, s, m in outcomes]
        phantom.add_note(container=container,
            title="Lost or Stolen Device - wipe FAILED / NOT queued (computer)",
            content=("The remote WIPE was approved but did NOT queue for every device. A device whose wipe did not queue is NOT being "
                     "erased and still holds data - investigate (enrollment / supervision / privilege / device state) and re-run.\n"
                     + "\n".join(lines)),
            note_type="general")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_computer_wipe_outcome_called", value="True")

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