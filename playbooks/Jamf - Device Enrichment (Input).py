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
    # call 'get_local_user_accounts_1' block
    get_local_user_accounts_1(container=container)

    return

@phantom.playbook_block()
def get_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_device_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        for playbook_input_device_type_item in playbook_input_device_type:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_id": playbook_input_device_id_item[0],
                    "device_type": playbook_input_device_type_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device", parameters=parameters, name="get_device_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_installed_applications_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_installed_applications_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_installed_applications_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        for playbook_input_device_type_item in playbook_input_device_type:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_id": playbook_input_device_id_item[0],
                    "device_type": playbook_input_device_type_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get installed applications", parameters=parameters, name="get_installed_applications_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_group_membership_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_group_membership_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_group_membership_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        for playbook_input_device_type_item in playbook_input_device_type:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_id": playbook_input_device_id_item[0],
                    "device_type": playbook_input_device_type_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]
    
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get group membership", parameters=parameters, name="get_group_membership_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_compliance_status_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_compliance_status_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        for playbook_input_device_type_item in playbook_input_device_type:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_id": playbook_input_device_id_item[0],
                    "device_type": playbook_input_device_type_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def get_configuration_profiles_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_configuration_profiles_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_configuration_profiles_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        for playbook_input_device_type_item in playbook_input_device_type:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_id": playbook_input_device_id_item[0],
                    "device_type": playbook_input_device_type_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

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

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_extension_attributes_1' call
    for playbook_input_device_id_item in playbook_input_device_id:
        for playbook_input_device_type_item in playbook_input_device_type:
            if playbook_input_device_id_item[0] is not None:
                parameters.append({
                    "device_id": playbook_input_device_id_item[0],
                    "device_type": playbook_input_device_type_item[0],
                })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get extension attributes", parameters=parameters, name="get_extension_attributes_1", assets=["<your-jamf-asset>"], callback=join_format_1)

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

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    def _first(dp, default="—"):
        rows = phantom.collect2(container=container, datapath=[dp])
        vals = [str(r[0]) for r in rows if r and r[0] not in (None, "")]
        return vals[0] if vals else default

    def _join(dp, default="none"):
        rows = phantom.collect2(container=container, datapath=[dp])
        vals = [str(r[0]) for r in rows if r and r[0] not in (None, "")]
        return ", ".join(vals) if vals else default

    name       = _first("get_device_1:action_result.data.*.general.name")
    serial     = _first("get_device_1:action_result.data.*.serial_number")
    user       = _first("get_device_1:action_result.data.*.username")
    compliance = _first("get_compliance_status_1:action_result.data.*.compliance_state")
    apps       = _first("get_installed_applications_1:action_result.summary.total", "0")
    groups     = _join("get_group_membership_1:action_result.data.*.group_name")
    profiles   = _first("get_configuration_profiles_1:action_result.summary.total", "0")
    accounts   = _first("get_local_user_accounts_1:action_result.summary.total", "0")
    extattrs   = _first("get_extension_attributes_1:action_result.summary.total", "0")

    summary = (
        "## Jamf Device Enrichment — " + name + "\n\n"
        + "- **Serial:** " + serial + "\n"
        + "- **User:** " + user + "\n"
        + "- **Compliance:** " + compliance + "\n"
        + "- **Group memberships:** " + groups + "\n"
        + "- **Installed apps:** " + apps + "\n"
        + "- **Configuration profiles:** " + profiles + "\n"
        + "- **Local user accounts:** " + accounts + "\n"
        + "- **Extension attributes:** " + extattrs
    )
    template = summary.replace("{", "{{").replace("}", "}}")
    parameters = []

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