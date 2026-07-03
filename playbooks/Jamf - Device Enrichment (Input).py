"""

"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'get_device_1' block
    get_device_1(container=container)
    # call 'get_configuration_profiles_1' block
    get_configuration_profiles_1(container=container)
    # call 'get_extension_attributes_1' block
    get_extension_attributes_1(container=container)
    # call 'get_installed_applications_1' block
    get_installed_applications_1(container=container)
    # call 'get_group_membership_1' block
    get_group_membership_1(container=container)
    # call 'get_compliance_status_1' block
    get_compliance_status_1(container=container)
    # call 'decision_1' block
    decision_1(container=container)

    return

@phantom.playbook_block()
def get_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])
    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_device_1' call
    for playbook_input_device_type_item in playbook_input_device_type:
        for playbook_input_device_id_item in playbook_input_device_id:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_type": playbook_input_device_type_item[0],
                    "device_id": playbook_input_device_id_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device", parameters=parameters, name="get_device_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_installed_applications_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_installed_applications_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])
    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_installed_applications_1' call
    for playbook_input_device_type_item in playbook_input_device_type:
        for playbook_input_device_id_item in playbook_input_device_id:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_type": playbook_input_device_type_item[0],
                    "device_id": playbook_input_device_id_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get installed applications", parameters=parameters, name="get_installed_applications_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_group_membership_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_group_membership_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])
    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_group_membership_1' call
    for playbook_input_device_type_item in playbook_input_device_type:
        for playbook_input_device_id_item in playbook_input_device_id:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_type": playbook_input_device_type_item[0],
                    "device_id": playbook_input_device_id_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get group membership", parameters=parameters, name="get_group_membership_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_compliance_status_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])
    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_compliance_status_1' call
    for playbook_input_device_type_item in playbook_input_device_type:
        for playbook_input_device_id_item in playbook_input_device_id:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_type": playbook_input_device_type_item[0],
                    "device_id": playbook_input_device_id_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_configuration_profiles_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_configuration_profiles_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])
    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_configuration_profiles_1' call
    for playbook_input_device_type_item in playbook_input_device_type:
        for playbook_input_device_id_item in playbook_input_device_id:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_type": playbook_input_device_type_item[0],
                    "device_id": playbook_input_device_id_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get configuration profiles", parameters=parameters, name="get_configuration_profiles_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_local_user_accounts_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_local_user_accounts_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_local_user_accounts_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        if playbook_input_device_id_item[0] is not None:
            parameters.append({
                "device_id": playbook_input_device_id_item[0],
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get local user accounts", parameters=parameters, name="get_local_user_accounts_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_extension_attributes_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_extension_attributes_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])
    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_extension_attributes_1' call
    for playbook_input_device_type_item in playbook_input_device_type:
        for playbook_input_device_id_item in playbook_input_device_id:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_type": playbook_input_device_type_item[0],
                    "device_id": playbook_input_device_id_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get extension attributes", parameters=parameters, name="get_extension_attributes_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def decision_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_1() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["playbook_input:device_type", "==", "computer"]
        ],
        conditions_dps=[
            ["playbook_input:device_type", "==", "computer"]
        ],
        name="decision_1:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        get_local_user_accounts_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    join_format_1(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def join_format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_1() called")

    if phantom.completed(action_names=["get_device_1", "get_installed_applications_1", "get_group_membership_1", "get_compliance_status_1", "get_configuration_profiles_1", "get_local_user_accounts_1", "get_extension_attributes_1"]):
        # call connected block "format_1"
        format_1(container=container, handle=handle)

    return


@phantom.playbook_block()
def format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_1() called")

    template = """## Jamf Device Enrichment — {0}\n\n- **Serial:** {1}\n- **User:** {2}\n- **Compliance:** {3}\n- **Group memberships:** {4}\n- **Installed apps:** {5}"""

    # parameter list for template variable replacement
    parameters = [
        "get_device_1:action_result.data.*.general.name",
        "get_device_1:action_result.data.*.serial_number",
        "get_device_1:action_result.data.*.username",
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

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    format_1 = phantom.get_format_data(name="format_1")

    output = {
        "enrichment_summary": format_1,
    }

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_playbook_output_data(output=output)

    return