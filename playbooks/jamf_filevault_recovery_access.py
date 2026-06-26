"""

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

    parameters = []

    parameters.append({
        "serial_number": "HNWYQ246Q2",
    })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device by serial", parameters=parameters, name="get_device_by_serial_1", assets=["test1"], callback=get_filevault_recovery_key_1)

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

    phantom.act("get filevault recovery key", parameters=parameters, name="get_filevault_recovery_key_1", assets=["test1"], callback=get_local_user_accounts_1)

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

    phantom.act("get local user accounts", parameters=parameters, name="get_local_user_accounts_1", assets=["test1"], callback=get_compliance_status_1)

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

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status_1", assets=["test1"], callback=set_recovery_lock_1)

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
                "password": "TestRecovery123",
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

    phantom.act("set recovery lock", parameters=parameters, name="set_recovery_lock_1", assets=["test1"], callback=lock_device_1)

    return


@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    set_recovery_lock_1_result_data = phantom.collect2(container=container, datapath=["set_recovery_lock_1:action_result.data.*.device_id","set_recovery_lock_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_device_1' call
    for set_recovery_lock_1_result_item in set_recovery_lock_1_result_data:
        if set_recovery_lock_1_result_item[0] is not None:
            parameters.append({
                "pin": "000000",
                "message": "SOAR test lock ",
                "device_id": set_recovery_lock_1_result_item[0],
                "device_type": "computer",
                "phone_number": "555-0100",
                "context": {'artifact_id': set_recovery_lock_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_device_1", assets=["test1"], callback=prompt_1)

    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")

    # set approver and message variables for phantom.prompt call

    user = "Sarah"
    role = None
    message = """ Wipe this Mac? (offboarding erase)"""

    # parameter list for template variable replacement
    parameters = []

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

    phantom.act("wipe device", parameters=parameters, name="wipe_device_1", assets=["test1"])

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