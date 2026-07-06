"""Jamf - FileVault Recovery Access (macOS) - playbook #7.

Secured recovery access to a Mac after a compromise or during offboarding.
Flow: resolve by serial (from the event artifact) -> (device found?) -> retrieve
recovery context (FileVault personal recovery key [SENSITIVE], local user
accounts, compliance status) -> secure (set recovery lock, lock device) ->
note/notify -> analyst approval gate -> wipe device ONLY on approval; a decline
or no-device path just adds a note.

Template notes (replace before use):
- Jamf asset on every action block         -> <your-jamf-asset>
- Approval-prompt approver (user or role)   -> <security-analyst-role>
- Recovery-lock password (prefer a secret)  -> <your-recovery-lock-password>
- Lock-screen message / support phone       -> <your-lock-screen-message> / <your-support-phone>
- Lock PIN defaults to 000000               -> replace with a chosen 6-digit unlock PIN
- The FileVault recovery key is SENSITIVE   -> never route it to a broad channel/note.
- Resolve reads the serial from artifact:*.cef.serialNumber.
- code_1 is the notify step (a note) -> replace with a restricted-channel notifier.
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

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

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

    phantom.act("get device by serial", parameters=parameters, name="get_device_by_serial_1", assets=["<your-jamf-asset>"], callback=decision_2)

    return


@phantom.playbook_block()
def get_filevault_recovery_key_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_filevault_recovery_key_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_filevault_recovery_key_1' call
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_serial_1_result_item[0],
                "context": {'artifact_id': get_device_by_serial_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get filevault recovery key", parameters=parameters, name="get_filevault_recovery_key_1", assets=["<your-jamf-asset>"], callback=get_local_user_accounts_1)

    return


@phantom.playbook_block()
def get_local_user_accounts_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_local_user_accounts_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_local_user_accounts_1' call
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_serial_1_result_item[0],
                "context": {'artifact_id': get_device_by_serial_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get local user accounts", parameters=parameters, name="get_local_user_accounts_1", assets=["<your-jamf-asset>"], callback=get_compliance_status_1)

    return


@phantom.playbook_block()
def get_compliance_status_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_local_user_accounts_1_result_data = phantom.collect2(container=container, datapath=["get_local_user_accounts_1:action_result.parameter.device_id","get_local_user_accounts_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_compliance_status_1' call
    for get_local_user_accounts_1_result_item in get_local_user_accounts_1_result_data:
        if get_local_user_accounts_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_local_user_accounts_1_result_item[0],
                "device_type": "computer",
                "context": {'artifact_id': get_local_user_accounts_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status_1", assets=["<your-jamf-asset>"], callback=set_recovery_lock_1)

    return


@phantom.playbook_block()
def set_recovery_lock_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("set_recovery_lock_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'set_recovery_lock_1' call
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "password": "<your-recovery-lock-password>",
                "device_id": get_device_by_serial_1_result_item[0],
                "operation": "set",
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

    phantom.act("set recovery lock", parameters=parameters, name="set_recovery_lock_1", assets=["<your-jamf-asset>"], callback=lock_device_1)

    return


@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_device_1' call
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "pin": "000000",
                "message": "<your-lock-screen-message>",
                "device_id": get_device_by_serial_1_result_item[0],
                "device_type": "computer",
                "phone_number": "<your-support-phone>",
                "context": {'artifact_id': get_device_by_serial_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_device_1", assets=["<your-jamf-asset>"], callback=code_1)

    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")

    # set approver and message variables for phantom.prompt call

    user = "<security-analyst-role>"
    role = None
    message = """Approve device WIPE? This permanently ERASES the Mac and is IRREVERSIBLE.\n- FileVault recovery key escrowed in Jamf: {0}\n  - Set recovery lock queued: {1}\n  - Lock device queued: {2}"""

    # parameter list for template variable replacement
    parameters = [
        "get_filevault_recovery_key_1:action_result.summary.key_present",
        "set_recovery_lock_1:action_result.status",
        "lock_device_1:action_result.status"
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

    # check for 'if' condition 1
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

    # check for 'else' condition 2
    code_2(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_serial_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id","get_device_by_serial_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device_1' call
    for get_device_by_serial_1_result_item in get_device_by_serial_1_result_data:
        if get_device_by_serial_1_result_item[0] is not None:
            parameters.append({
                "confirm": get_device_by_serial_1_result_item[0],
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

    phantom.act("wipe device", parameters=parameters, name="wipe_device_1", assets=["<your-jamf-asset>"])

    return


@phantom.playbook_block()
def code_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_1() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    fv = phantom.collect2(container=container, datapath=["get_filevault_recovery_key_1:action_result.status", "get_filevault_recovery_key_1:action_result.summary.key_present"], action_results=results)
    rl = phantom.collect2(container=container, datapath=["set_recovery_lock_1:action_result.status"], action_results=results)
    lk = phantom.collect2(container=container, datapath=["lock_device_1:action_result.status"], action_results=results)

    fv_status = fv[0][0] if fv else None
    key_present = fv[0][1] if fv and len(fv[0]) > 1 else None
    rl_status = rl[0][0] if rl else None
    lock_status = lk[0][0] if lk else None

    lines = []
    if fv_status != "success" or key_present not in (True, "True", "true"):
          lines.append("WARNING: a FileVault recovery key was NOT obtained (retrieval: {}, key escrowed: {}). Do NOT approve the wipe if the disk contents are still needed.".format(fv_status,
  key_present))
    if rl_status != "success" or lock_status != "success":
          lines.append("WARNING: securing the device did not fully succeed (set recovery lock: {}, lock device: {}). Review before approving the wipe.".format(rl_status, lock_status))

    lines.append("FileVault recovery access - step outcomes:")
    lines.append("- FileVault recovery key retrieval: {} (key escrowed in Jamf: {})".format(fv_status, key_present))
    lines.append("- Set recovery lock (queued): {}".format(rl_status))
    lines.append("- Lock device (queued): {}".format(lock_status))
    lines.append("The FileVault recovery key is sensitive and is intentionally NOT included here.")
    lines.append("TODO: replace this note with a notification to a restricted security channel.")

    phantom.add_note(container=container, title="FileVault recovery access - step outcomes", content="\n".join(lines), note_type="general")


    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_1_called", value="True")

    prompt_1(container=container)

    return


@phantom.playbook_block()
def code_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_2() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
          container=container,
          title="FileVault recovery - wipe NOT approved",
          content=(
              "The analyst declined the wipe at the approval prompt. "
              "The device remains secured (recovery lock + device lock queued); no erase was performed."
          ),
          note_type="general",
      )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_2_called", value="True")

    return


@phantom.playbook_block()
def decision_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_2() called")

    # check for 'if' condition 1
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
        get_filevault_recovery_key_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    code_3(action=action, success=success, container=container, results=results, handle=handle)

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