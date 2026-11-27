"""
Accepts a Mac serial number from the event and retrieves its FileVault recovery key, local user accounts and compliance status, then sets a recovery lock and locks the device. An analyst must approve before the device is wiped; a decline, a timeout or a serial with no matching device only adds a note. Use to secure access to a Mac after a compromise or during offboarding.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'find_mac_by_serial' block
    find_mac_by_serial(container=container)

    return

@phantom.playbook_block()
def find_mac_by_serial(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("find_mac_by_serial() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    #  Looks up the Mac in Jamf Pro by the serial number from the event artifact.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.serialNumber","artifact:*.id"])

    parameters = []

    # build parameters list for 'find_mac_by_serial' call
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

    phantom.act("get device by serial", parameters=parameters, name="find_mac_by_serial", assets=["jamf_pro"], callback=device_found)

    return


@phantom.playbook_block()
def get_filevault_key(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_filevault_key() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Retrieves the Mac's escrowed FileVault personal recovery key. The key is sensitive 
    # and is never written to a note.
    ################################################################################

    find_mac_by_serial_result_data = phantom.collect2(container=container, datapath=["find_mac_by_serial:action_result.data.*.id","find_mac_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_filevault_key' call
    for find_mac_by_serial_result_item in find_mac_by_serial_result_data:
        if find_mac_by_serial_result_item[0] is not None:
            parameters.append({
                "device_id": find_mac_by_serial_result_item[0],
                "context": {'artifact_id': find_mac_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get filevault recovery key", parameters=parameters, name="get_filevault_key", assets=["jamf_pro"], callback=get_local_accounts)

    return


@phantom.playbook_block()
def get_local_accounts(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_local_accounts() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Lists the Mac's local user accounts for the analyst.
    ################################################################################

    find_mac_by_serial_result_data = phantom.collect2(container=container, datapath=["find_mac_by_serial:action_result.data.*.id","find_mac_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_local_accounts' call
    for find_mac_by_serial_result_item in find_mac_by_serial_result_data:
        if find_mac_by_serial_result_item[0] is not None:
            parameters.append({
                "device_id": find_mac_by_serial_result_item[0],
                "context": {'artifact_id': find_mac_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get local user accounts", parameters=parameters, name="get_local_accounts", assets=["jamf_pro"], callback=get_compliance_status)

    return


@phantom.playbook_block()
def get_compliance_status(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Gets the Mac's compliance status from Jamf Pro for the analyst. 
    ################################################################################

    get_local_accounts_result_data = phantom.collect2(container=container, datapath=["get_local_accounts:action_result.parameter.device_id","get_local_accounts:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_compliance_status' call
    for get_local_accounts_result_item in get_local_accounts_result_data:
        if get_local_accounts_result_item[0] is not None:
            parameters.append({
                "device_id": get_local_accounts_result_item[0],
                "device_type": "computer",
                "context": {'artifact_id': get_local_accounts_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status", assets=["jamf_pro"], callback=set_recovery_lock)

    return


@phantom.playbook_block()
def set_recovery_lock(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("set_recovery_lock() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Sets a recovery lock so the Mac can't be started from recovery without the password. 
    # 
    ################################################################################

    find_mac_by_serial_result_data = phantom.collect2(container=container, datapath=["find_mac_by_serial:action_result.data.*.id","find_mac_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'set_recovery_lock' call
    for find_mac_by_serial_result_item in find_mac_by_serial_result_data:
        if find_mac_by_serial_result_item[0] is not None:
            parameters.append({
                "password": "<your-recovery-lock-password>",
                "device_id": find_mac_by_serial_result_item[0],
                "operation": "set",
                "device_type": "computer",
                "context": {'artifact_id': find_mac_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("set recovery lock", parameters=parameters, name="set_recovery_lock", assets=["jamf_pro"], callback=lock_mac)

    return


@phantom.playbook_block()
def lock_mac(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_mac() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Locks the Mac with the lock-screen message and PIN.
    ################################################################################

    find_mac_by_serial_result_data = phantom.collect2(container=container, datapath=["find_mac_by_serial:action_result.data.*.id","find_mac_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_mac' call
    for find_mac_by_serial_result_item in find_mac_by_serial_result_data:
        if find_mac_by_serial_result_item[0] is not None:
            parameters.append({
                "pin": "000000",
                "message": "<your-lock-screen-message>",
                "device_id": find_mac_by_serial_result_item[0],
                "device_type": "computer",
                "phone_number": "<your-support-phone>",
                "context": {'artifact_id': find_mac_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_mac", assets=["jamf_pro"], callback=note_step_outcomes)

    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")

    ################################################################################
    # Asks an analyst to approve wiping the Mac. Times out after 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<security-analyst-role>"
    message = """Approve device WIPE? This permanently ERASES the Mac and is IRREVERSIBLE.\n- FileVault recovery key escrowed in Jamf: {0}\n  - Set recovery lock queued: {1}\n  - Lock device queued: {2}"""

    # parameter list for template variable replacement
    parameters = [
        "get_filevault_key:action_result.summary.key_present",
        "set_recovery_lock:action_result.status",
        "lock_mac:action_result.status"
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_wipe", parameters=parameters, response_types=response_types, callback=wipe_approved)

    return


@phantom.playbook_block()
def wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_approved() called")

    ################################################################################
    # Wipes the Mac only if the analyst answered Yes. 
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
        name="wipe_approved:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_mac(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_wipe_not_approved(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_mac(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_mac() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Erases the Mac. Runs only after analyst approval. 
    ################################################################################

    find_mac_by_serial_result_data = phantom.collect2(container=container, datapath=["find_mac_by_serial:action_result.data.*.id","find_mac_by_serial:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_mac' call
    for find_mac_by_serial_result_item in find_mac_by_serial_result_data:
        if find_mac_by_serial_result_item[0] is not None:
            parameters.append({
                "confirm": find_mac_by_serial_result_item[0],
                "device_id": find_mac_by_serial_result_item[0],
                "device_type": "computer",
                "context": {'artifact_id': find_mac_by_serial_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_mac", assets=["jamf_pro"])

    return


@phantom.playbook_block()
def note_step_outcomes(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_step_outcomes() called")

    ################################################################################
    # This block uses custom code. Adds a note with the result of each step, including 
    # whether the FileVault key was retrieved, but never the key itself. 
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    fv = phantom.collect2(container=container, datapath=["get_filevault_key:action_result.status", "get_filevault_key:action_result.summary.key_present"], action_results=results)
    rl = phantom.collect2(container=container, datapath=["set_recovery_lock:action_result.status"], action_results=results)
    lk = phantom.collect2(container=container, datapath=["lock_mac:action_result.status"], action_results=results)
    cs = phantom.collect2(container=container, datapath=["get_compliance_status:action_result.status", "get_compliance_status:action_result.data.*.compliance_state"], action_results=results)
    lu = phantom.collect2(container=container, datapath=["get_local_accounts:action_result.status", "get_local_accounts:action_result.summary.total"], action_results=results)

    fv_status = fv[0][0] if fv else None
    key_present = fv[0][1] if fv and len(fv[0]) > 1 else None
    rl_status = rl[0][0] if rl else None
    lock_status = lk[0][0] if lk else None
    cs_status = cs[0][0] if cs else None
    cs_state = cs[0][1] if cs and len(cs[0]) > 1 else None
    lu_status = lu[0][0] if lu else None
    lu_total = lu[0][1] if lu and len(lu[0]) > 1 else None
       
    lines = []
    if fv_status != "success" or key_present not in (True, "True", "true"):
         lines.append("WARNING: a FileVault recovery key was NOT obtained (retrieval: {}, key escrowed: {}). Do NOT approve the wipe if the disk contents are still needed.".format(fv_status, key_present))
    if rl_status != "success" or lock_status != "success":
         lines.append("WARNING: securing the device did not fully succeed (set recovery lock: {}, lock device: {}). Review before approving the wipe.".format(rl_status, lock_status))

    lines.append("FileVault recovery access - step outcomes:")
    lines.append("- FileVault recovery key retrieval: {} (key escrowed in Jamf: {})".format(fv_status, key_present))
    lines.append("- Compliance status: {} ({})".format(cs_status, cs_state))
    lines.append("- Local user accounts: {} (count: {})".format(lu_status, lu_total))
    lines.append("- Set recovery lock (queued): {}".format(rl_status))
    lines.append("- Lock device (queued): {}".format(lock_status))
    lines.append("The FileVault recovery key is sensitive and is intentionally NOT included here.")
    lines.append("TODO: replace this note with a notification to a restricted security channel.")
      
    phantom.add_note(container=container, title="FileVault recovery access - step outcomes", content="\n".join(lines), note_type="general")


    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_step_outcomes_called", value="True")

    approve_wipe(container=container)

    return


@phantom.playbook_block()
def note_wipe_not_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_not_approved() called")

    ################################################################################
    # This block uses custom code. Adds a note saying the wipe was declined or the 
    # prompt timed out. 
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    resp = phantom.collect2(container=container, datapath=["approve_wipe:action_result.summary.responses.0"], action_results=results)
    answer = resp[0][0] if resp and resp[0] else None

    if answer in (None, ""):
        title = "FileVault recovery - wipe prompt timed out"
        content = ("The wipe approval prompt timed out with no response (treated as no-wipe). "
                     "The device remains contained (recovery lock + device lock queued); no erase was performed. "
                     "Re-run if a wipe is still required.")
    else:
          title = "FileVault recovery - wipe denied"
          content = ("The analyst declined the wipe at the approval prompt. "
                     "The device remains contained (recovery lock + device lock queued); no erase was performed.")

    phantom.add_note(container=container, title=title, content=content, note_type="general")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_not_approved_called", value="True")

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
            ["find_mac_by_serial:action_result.data.*.id", "!=", ""]
        ],
        conditions_dps=[
            ["find_mac_by_serial:action_result.data.*.id", "!=", ""]
        ],
        name="device_found:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        get_filevault_key(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_no_device(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_device() called")

    ################################################################################
    # This block uses custom code. Adds a note when no device matched the serial or 
    # the lookup failed.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    
    rows = phantom.collect2(container=container, datapath=["find_mac_by_serial:action_result.status"], action_results=results)
    lookup_status = rows[0][0] if rows and rows[0] else None

    if lookup_status == "success":
        title = "FileVault recovery - no device matched"
        content = ("No Jamf device matched the provided serial number. "
                     "No actions were taken. Verify the serial is correct and re-run.")
    else:
          title = "FileVault recovery - device lookup FAILED"
          content = ("The 'get device by serial' lookup did not succeed (status: {}). "
                     "No device was resolved and no actions were taken. This usually means a "
                     "Jamf asset / credential / privilege problem, NOT a wrong serial - check "
                     "the asset config and API role, then re-run.".format(lookup_status))

    phantom.add_note(container=container, title=title, content=content, note_type="general")


    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_device_called", value="True")

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