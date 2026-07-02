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

    phantom.act("get device by username", parameters=parameters, name="get_device_by_username_1", assets=["test 4"], callback=get_device_by_username_1_callback)

    return


@phantom.playbook_block()
def get_device_by_username_1_callback(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_username_1_callback() called")

    
    get_compliance_status_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    get_group_membership_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    get_installed_applications_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    get_configuration_profiles_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    get_local_user_accounts_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)
    get_extension_attributes_1(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=filtered_artifacts, filtered_results=filtered_results)


    return


@phantom.playbook_block()
def get_compliance_status_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_compliance_status_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_username_1_result_item[0],
                "device_type": get_device_by_username_1_result_item[1],
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status_1", assets=["test 4"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_installed_applications_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_installed_applications_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_installed_applications_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_username_1_result_item[0],
                "device_type": get_device_by_username_1_result_item[1],
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get installed applications", parameters=parameters, name="get_installed_applications_1", assets=["test 4"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_group_membership_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_group_membership_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_group_membership_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_username_1_result_item[0],
                "device_type": get_device_by_username_1_result_item[1],
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get group membership", parameters=parameters, name="get_group_membership_1", assets=["test 4"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_configuration_profiles_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_configuration_profiles_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_configuration_profiles_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_username_1_result_item[0],
                "device_type": get_device_by_username_1_result_item[1],
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get configuration profiles", parameters=parameters, name="get_configuration_profiles_1", assets=["test 4"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_local_user_accounts_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_local_user_accounts_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_local_user_accounts_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_username_1_result_item[0],
                "context": {'artifact_id': get_device_by_username_1_result_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get local user accounts", parameters=parameters, name="get_local_user_accounts_1", assets=["test 4"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_extension_attributes_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_extension_attributes_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.data.*.type","get_device_by_username_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_extension_attributes_1' call
    for get_device_by_username_1_result_item in get_device_by_username_1_result_data:
        if get_device_by_username_1_result_item[0] is not None:
            parameters.append({
                "device_id": get_device_by_username_1_result_item[0],
                "device_type": get_device_by_username_1_result_item[1],
                "context": {'artifact_id': get_device_by_username_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get extension attributes", parameters=parameters, name="get_extension_attributes_1", assets=["test 4"], callback=join_format_1)

    return


@phantom.playbook_block()
def join_format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_1() called")

    if phantom.completed(action_names=["get_compliance_status_1", "get_installed_applications_1", "get_group_membership_1", "get_configuration_profiles_1", "get_local_user_accounts_1", "get_extension_attributes_1"]):
        # call connected block "format_1"
        format_1(container=container, handle=handle)

    return


@phantom.playbook_block()
def format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_1() called")

    template = """## Jamf Device Enrichment — {0}\n- **Serial:** {1}\n- **User:** {2}\n- **Compliance:** {3}\n- **Group memberships:** {4}\n- **Installed apps:** {5}"""

    # parameter list for template variable replacement
    parameters = [
        "get_device_by_username_1:action_result.data.*.general.name",
        "get_device_by_username_1:action_result.data.*.serial_number",
        "get_device_by_username_1:action_result.parameter.username",
        "get_compliance_status_1:action_result.data.*.compliance_state",
        "get_group_membership_1:action_result.data.*.group_name",
        "get_installed_applications_1:action_result.summary.total"
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

    id_value = container.get("id", None)
    format_1 = phantom.get_format_data(name="format_1")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    text = format_1
    if isinstance(text, list):
        text = "\n".join(str(s) for s in text if s)

    phantom.add_note(
        container=container,
        note_type="general",
        title="Jamf Device Enrichment and Triage",
        content=text,
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_1__inputs:0:format_1:formatted_data", value=json.dumps(format_1))
    phantom.save_block_result(key="code_1__inputs:1:container:id", value=json.dumps(id_value))

    phantom.save_block_result(key="code_1_called", value="True")

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