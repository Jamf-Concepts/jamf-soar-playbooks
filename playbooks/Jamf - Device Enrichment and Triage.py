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

    phantom.act("get device by username", parameters=parameters, name="get_device_by_username_1", assets=["<your-jamf-asset>"], callback=playbook_jamf___device_enrichment__input__1)

    return


@phantom.playbook_block()
def code_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_1() called")

    id_value = container.get("id", None)
    playbook_jamf___device_enrichment__input__1_output_enrichment_summary = phantom.collect2(container=container, datapath=["playbook_jamf___device_enrichment__input__1:playbook_output:enrichment_summary"])

    playbook_jamf___device_enrichment__input__1_output_enrichment_summary_values = [item[0] for item in playbook_jamf___device_enrichment__input__1_output_enrichment_summary]

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

    text = "\n".join(_flat(playbook_jamf___device_enrichment__input__1_output_enrichment_summary))

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

    phantom.save_block_result(key="code_1__inputs:0:playbook_jamf___device_enrichment__input__1:playbook_output:enrichment_summary", value=json.dumps(playbook_jamf___device_enrichment__input__1_output_enrichment_summary_values))
    phantom.save_block_result(key="code_1__inputs:1:container:id", value=json.dumps(id_value))

    phantom.save_block_result(key="code_1_called", value="True")

    return


@phantom.playbook_block()
def playbook_jamf___device_enrichment__input__1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("playbook_jamf___device_enrichment__input__1() called")

    get_device_by_username_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_username_1:action_result.data.*.id","get_device_by_username_1:action_result.data.*.type"], action_results=results)

    get_device_by_username_1_result_item_0 = [item[0] for item in get_device_by_username_1_result_data]
    get_device_by_username_1_result_item_1 = [item[1] for item in get_device_by_username_1_result_data]

    inputs = {
        "device_id": get_device_by_username_1_result_item_0,
        "device_type": get_device_by_username_1_result_item_1,
    }

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    # call playbook "jamf-soar-playbooks/Jamf - Device Enrichment (Input)", returns the playbook_run_id
    playbook_run_id = phantom.playbook("jamf-soar-playbooks/Jamf - Device Enrichment (Input)", container=container, name="playbook_jamf___device_enrichment__input__1", callback=code_1, inputs=inputs)

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