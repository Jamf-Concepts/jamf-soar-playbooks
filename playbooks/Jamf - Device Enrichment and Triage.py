"""
Accepts a username from the event, finds the user's devices in Jamf, runs the Device Enrichment (Input) playbook on them and adds the resulting summary to the case as a note. Read-only; no changes are made to any device.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'find_devices_by_username' block
    find_devices_by_username(container=container)

    return

@phantom.playbook_block()
def find_devices_by_username(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("find_devices_by_username() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Looks up the user's devices in Jamf Pro by the username from the event artifact.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceUserName","artifact:*.id"])

    parameters = []

    # build parameters list for 'find_devices_by_username' call
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

    phantom.act("get device by username", parameters=parameters, name="find_devices_by_username", assets=["jamf_pro"], callback=devices_found)

    return


@phantom.playbook_block()
def note_enrichment_summary(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_enrichment_summary() called")

    ################################################################################
    # This block uses custom code. Adds the enrichment summary returned by the sub-playbook 
    # to the event as a note.
    ################################################################################

    id_value = container.get("id", None)
    run_device_enrichment_output_enrichment_summary = phantom.collect2(container=container, datapath=["run_device_enrichment:playbook_output:enrichment_summary"])

    run_device_enrichment_output_enrichment_summary_values = [item[0] for item in run_device_enrichment_output_enrichment_summary]

    ################################################################################
    ## Custom Code Start
    ################################################################################

     # flatten whatever nesting collect2 produced into one clean string
    def _flat(x):
        out = []
        if isinstance(x, (list, tuple)):
            for i in x:
                out.extend(_flat(i))
        elif x not in (None, ""):
            out.append(str(x))
        return out

    text = "\n".join(_flat(run_device_enrichment_output_enrichment_summary))

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

    phantom.save_block_result(key="note_enrichment_summary__inputs:0:run_device_enrichment:playbook_output:enrichment_summary", value=json.dumps(run_device_enrichment_output_enrichment_summary_values))
    phantom.save_block_result(key="note_enrichment_summary__inputs:1:container:id", value=json.dumps(id_value))

    phantom.save_block_result(key="note_enrichment_summary_called", value="True")

    return


@phantom.playbook_block()
def run_device_enrichment(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("run_device_enrichment() called")

    ################################################################################
    # Runs the Jamf - Device Enrichment (Input) playbook on the devices found.
    ################################################################################

    find_devices_by_username_result_data = phantom.collect2(container=container, datapath=["find_devices_by_username:action_result.data.*.id","find_devices_by_username:action_result.data.*.type"], action_results=results)

    find_devices_by_username_result_item_0 = [item[0] for item in find_devices_by_username_result_data]
    find_devices_by_username_result_item_1 = [item[1] for item in find_devices_by_username_result_data]

    inputs = {
        "device_id": find_devices_by_username_result_item_0,
        "device_type": find_devices_by_username_result_item_1,
    }

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    # call playbook "jamf-soar-playbooks/Jamf - Device Enrichment (Input)", returns the playbook_run_id
    playbook_run_id = phantom.playbook("jamf-soar-playbooks/Jamf - Device Enrichment (Input)", container=container, name="run_device_enrichment", callback=note_enrichment_summary, inputs=inputs)

    return


@phantom.playbook_block()
def devices_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("devices_found() called")

    ################################################################################
    # Continues only if Jamf Pro returned at least one device for the user.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["find_devices_by_username:action_result.summary.total", ">", 0]
        ],
        conditions_dps=[
            ["find_devices_by_username:action_result.summary.total", ">", 0]
        ],
        name="devices_found:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        run_device_enrichment(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_no_devices(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_devices() called")

    ################################################################################
    # This block uses custom code. Adds a note when no Jamf device was found for the 
    # user.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceUserName"])
    user = rows[0][0] if rows and rows[0] and rows[0][0] else "unknown"

    phantom.add_note(
        container=container,
        note_type="general",
        title="Jamf Device Enrichment",
        content="No Jamf device found for user **" + str(user) + "** — nothing to enrich.",
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_devices_called", value="True")

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