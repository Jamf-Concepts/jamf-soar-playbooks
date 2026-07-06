"""

"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'get_device_by_username_1' block
    get_device_by_username_1(container=container)

    return

@phantom.playbook_block()
def get_device_by_username_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_username_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceUserName","artifact:*.id"])

    parameters = []

    # build parameters list for 'get_device_by_username_1' call
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

    phantom.act("get device by username", parameters=parameters, name="get_device_by_username_1", assets=["<your-jamf-asset>"], callback=get_device_by_username_1_callback)

    return


@phantom.playbook_block()
def get_device_by_username_1_callback(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_username_1_callback() called")

    
    add_to_static_group_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    send_blank_push_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    lock_device_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)


    return


@phantom.playbook_block()
def add_to_static_group_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("add_to_static_group_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'add_to_static_group_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_username_1_result_item[0],
                "device_id": get_device_by_username_1_result_item[1],
                "group_id": "<your-suspended-group-id>",
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add to static group", parameters=parameters, name="add_to_static_group_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def send_blank_push_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("send_blank_push_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'send_blank_push_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_username_1_result_item[0],
                "device_id": get_device_by_username_1_result_item[1],
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("send blank push", parameters=parameters, name="send_blank_push_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_device_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_username_1_result_item[0],
                "device_id": get_device_by_username_1_result_item[1],
                "message": "This device has been locked by security. Contact IT.",
                "pin": "<lock-pin>",
                "phone_number": "<your-callback-number>",
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_device_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def join_format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_1() called")

    if phantom.completed(action_names=["add_to_static_group_1", "send_blank_push_1", "lock_device_1"]):
        # call connected block "format_1"
        format_1(container=container, handle=handle)

    return


@phantom.playbook_block()
def format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_1() called")

    template = """## Compromised User — Device Contained\n\n- **User:** {0}\n- **Device:** {1} ({2})\n- **Actions taken:** added to quarantine group, locked, blank push sent"""

    # parameter list for template variable replacement
    parameters = [
        "get_device_by_username_1:action_result.data.*.username",
        "get_device_by_username_1:action_result.data.*.general.name",
        "get_device_by_username_1:action_result.data.*.serial_number"
    ]

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="format_1")

    code_1(container=container)

    return


@phantom.playbook_block()
def code_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_1() called")

    format_1 = phantom.get_format_data(name="format_1")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    def _flat(x):
        out = []
        if isinstance(x, (list, tuple)):
            for i in x:
                out.extend(_flat(i))
        elif x not in (None, ""):
            out.append(str(x))
        return out

    text = "\n".join(_flat(format_1))

    phantom.add_note(
        container=container,
        note_type="general",
        title="Compromised User — Device Contained",
        content=text,
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_1__inputs:0:format_1:formatted_data", value=json.dumps(format_1))

    phantom.save_block_result(key="code_1_called", value="True")

    prompt_1(container=container)

    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<your-approver-role>"
    message = """Compromised-user containment complete for {0} (device {1})."""

    # parameter list for template variable replacement
    parameters = [
        "get_device_by_username_1:action_result.parameter.username",
        "get_device_by_username_1:action_result.data.*.general.name"
    ]

    # responses
    response_types = [
        {
            "prompt": "Wipe this device? This is irreversible.",
            "options": {
                "type": "list",
                "required": True,
                "choices": [
                    "Wipe",
                    "Do not wipe"
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
            ["prompt_1:action_result.summary.responses.0", "==", "Wipe"]
        ],
        conditions_dps=[
            ["prompt_1:action_result.summary.responses.0", "==", "Wipe"]
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

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_username_1_result_item[0],
                "device_id": get_device_by_username_1_result_item[1],
                "confirm": True,
                "pin": "<lock-pin>",
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
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

    phantom.add_note(
        container=container,
        note_type="general",
        title="Wipe denied",
        content="Analyst denied wipe — device remains contained (locked + quarantined).",
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_2_called", value="True")

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