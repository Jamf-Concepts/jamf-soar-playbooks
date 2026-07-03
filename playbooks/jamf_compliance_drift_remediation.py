"""
Jamf - Compliance Drift / MDM Tamper Remediation (correct-first, gated wipe).
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

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

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

    phantom.act("get device by serial", parameters=parameters, name="resolve_device", assets=["<your-jamf-asset>"], callback=redeploy_framework)

    return


@phantom.playbook_block()
def redeploy_framework(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("redeploy_framework() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'redeploy_framework' call
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

    phantom.act("redeploy management framework", parameters=parameters, name="redeploy_framework", assets=["<your-jamf-asset>"], callback=force_checkin)

    return


@phantom.playbook_block()
def force_checkin(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("force_checkin() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

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

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

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

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        logical_operator="or",
        conditions=[
            ["check_compliance:action_result.data.*.compliance_state", "==", "COMPLIANT"],
            ["check_compliance:action_result.status", "!=", "success"],
            ["check_compliance:action_result.summary.total", "==", 0]
        ],
        conditions_dps=[
            ["check_compliance:action_result.data.*.compliance_state", "==", "COMPLIANT"],
            ["check_compliance:action_result.status", "!=", "success"],
            ["check_compliance:action_result.summary.total", "==", 0]
        ],
        name="is_compliant:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        return

    # check for 'else' condition 2
    quarantine_device(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def quarantine_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'quarantine_device' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "device_id": resolve_device_result_item[0],
                "group_name": "<your-quarantine-group>",
                "context": {'artifact_id': resolve_device_result_item[1]},
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

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

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

    phantom.act("lock device", parameters=parameters, name="lock_device", assets=["<your-jamf-asset>"], callback=approve_wipe)

    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")

    # set approver and message variables for phantom.prompt call

    user = None
    role = "Administrator"
    message = """Device is still reported non-compliant after automated correction. Quarantine + lock were queued (verify they applied). Approve device WIPE? This ERASES the device and is IRREVERSIBLE."""

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

    return


@phantom.playbook_block()
def wipe_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    resolve_device_result_data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id","resolve_device:action_result.data.*.type","resolve_device:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device' call
    for resolve_device_result_item in resolve_device_result_data:
        if resolve_device_result_item[0] is not None:
            parameters.append({
                "pin": "<your-6-digit-pin>",
                "confirm": True,
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

    phantom.act("wipe device", parameters=parameters, name="wipe_device", assets=["<your-jamf-asset>"])

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