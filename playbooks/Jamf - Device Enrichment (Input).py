"""
Accepts paired lists of Jamf device IDs and device types and collects device details, compliance status, group membership, installed applications, configuration profiles, local accounts and extension attributes. Returns a formatted enrichment summary as output. Read-only; no changes are made to the device.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'get_device_details' block
    get_device_details(container=container)
    # call 'get_configuration_profiles' block
    get_configuration_profiles(container=container)
    # call 'get_extension_attributes' block
    get_extension_attributes(container=container)
    # call 'get_installed_apps' block
    get_installed_apps(container=container)
    # call 'get_group_membership' block
    get_group_membership(container=container)
    # call 'get_compliance_status' block
    get_compliance_status(container=container)
    # call 'get_local_accounts' block
    get_local_accounts(container=container)

    return

@phantom.playbook_block()
def get_device_details(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_details() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Gets each device's inventory details from Jamf 
    # Pro.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_device_details' call
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

    assert len(playbook_input_device_id) == len(playbook_input_device_type), "device_id/device_type must be paired, equal-length lists"
    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device", parameters=parameters, name="get_device_details", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def get_installed_apps(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_installed_apps() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Lists the applications installed on each device.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_installed_apps' call
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

    assert len(playbook_input_device_id) == len(playbook_input_device_type), "device_id/device_type must be paired, equal-length lists"
    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get installed applications", parameters=parameters, name="get_installed_apps", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def get_group_membership(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_group_membership() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Lists the Jamf groups each device belongs to.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_group_membership' call
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

    assert len(playbook_input_device_id) == len(playbook_input_device_type), "device_id/device_type must be paired, equal-length lists"
    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]
    
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get group membership", parameters=parameters, name="get_group_membership", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def get_compliance_status(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Gets each device's compliance status from Jamf 
    # Pro.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_compliance_status' call
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

    assert len(playbook_input_device_id) == len(playbook_input_device_type), "device_id/device_type must be paired, equal-length lists"
    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get compliance status", parameters=parameters, name="get_compliance_status", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def get_configuration_profiles(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_configuration_profiles() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Lists the configuration profiles installed on each 
    # device.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_configuration_profiles' call
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

    assert len(playbook_input_device_id) == len(playbook_input_device_type), "device_id/device_type must be paired, equal-length lists"
    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get configuration profiles", parameters=parameters, name="get_configuration_profiles", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def get_local_accounts(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_local_accounts() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Lists each device's local user accounts.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])

    parameters = []

    # build parameters list for 'get_local_accounts' call
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

    phantom.act("get local user accounts", parameters=parameters, name="get_local_accounts", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def get_extension_attributes(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_extension_attributes() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Gets each device's extension attribute values from 
    # Jamf Pro.
    ################################################################################

    playbook_input_device_id = phantom.collect2(container=container, datapath=["playbook_input:device_id"])
    playbook_input_device_type = phantom.collect2(container=container, datapath=["playbook_input:device_type"])

    parameters = []

    # build parameters list for 'get_extension_attributes' call
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

    assert len(playbook_input_device_id) == len(playbook_input_device_type), "device_id/device_type must be paired, equal-length lists"
    parameters = [
        {"device_id": did[0], "device_type": dtype[0]}
        for did, dtype in zip(playbook_input_device_id, playbook_input_device_type)
        if did[0] is not None
    ]

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get extension attributes", parameters=parameters, name="get_extension_attributes", assets=["jamf_pro"], callback=join_format_enrichment_summary)

    return


@phantom.playbook_block()
def join_format_enrichment_summary(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_enrichment_summary() called")

    if phantom.completed(action_names=["get_device_details", "get_installed_apps", "get_group_membership", "get_compliance_status", "get_configuration_profiles", "get_local_accounts", "get_extension_attributes"]):
        # call connected block "format_enrichment_summary"
        format_enrichment_summary(container=container, handle=handle)

    return


@phantom.playbook_block()
def format_enrichment_summary(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_enrichment_summary() called")

    ################################################################################
    # This block uses custom code. Formats the results of every lookup into one enrichment 
    # summary, marking any lookup that failed.
    ################################################################################

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    ACTS = ["get_device_details","get_compliance_status","get_group_membership",
            "get_installed_apps","get_configuration_profiles",
            "get_local_accounts","get_extension_attributes"]

    def _ok(action):
        rows = phantom.collect2(container=container, datapath=[action + ":action_result.status"])
        vals = [str(r[0]).lower() for r in rows if r and r[0]]
        return bool(vals) and all(v == "success" for v in vals)

    st = {a: _ok(a) for a in ACTS}
    FAIL = "⚠️ not retrieved"

    def field(action, dp, join=False, empty="—"):
        if not st[action]:
            return FAIL
        rows = phantom.collect2(container=container, datapath=[dp])
        vals = [str(r[0]) for r in rows if r and r[0] not in (None, "")]
        if not vals:
            return "none" if join else empty
        return ", ".join(vals) if join else vals[0]

    name       = field("get_device_details", "get_device_details:action_result.data.*.general.name")
    serial     = field("get_device_details", "get_device_details:action_result.data.*.serial_number")
    user       = field("get_device_details", "get_device_details:action_result.data.*.username")
    compliance = field("get_compliance_status", "get_compliance_status:action_result.data.*.compliance_state")
    apps       = field("get_installed_apps", "get_installed_apps:action_result.summary.total", empty="0")
    groups     = field("get_group_membership", "get_group_membership:action_result.data.*.group_name", join=True)
    profiles   = field("get_configuration_profiles", "get_configuration_profiles:action_result.summary.total", empty="0")
    accounts   = field("get_local_accounts", "get_local_accounts:action_result.summary.total", empty="0")
    extattrs   = field("get_extension_attributes", "get_extension_attributes:action_result.summary.total", empty="0")

    ok = sum(st.values())
    summary = (
        "## Jamf Device Enrichment — " + name + "\n\n"
        + "_" + str(ok) + " of 7 lookups succeeded_\n\n"
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

    phantom.format(container=container, template=template, parameters=parameters, name="format_enrichment_summary")

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    format_enrichment_summary = phantom.get_format_data(name="format_enrichment_summary")

    output = {
        "enrichment_summary": format_enrichment_summary,
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