"""
Jamf - Compliance Drift / MDM Tamper Remediation
Correct-first: resolve -> correct (redeploy management framework + blank push) ->
re-check compliance -> if still non-compliant: contain (quarantine + lock) -> analyst
approval prompt (irreversible warning) -> gated wipe. Never auto-wipe.
Block names match the VPE graph (auto-numbered) so the .py and .json stay in sync.
"""

import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')
    get_device_by_serial_1(container=container)
    return


@phantom.playbook_block()
def get_device_by_serial_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_serial_1() called")
    parameters = [{"serial_number": "artifact:*.cef.serialNumber"}]
    phantom.act("get device by serial", parameters=parameters, name="get_device_by_serial_1", assets=["<your-jamf-asset>"], callback=redeploy_management_framework_1)
    return


def _dev(container, results):
    data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id", "get_device_by_serial_1:action_result.data.*.type"], action_results=results)
    return [{"device_id": r[0], "device_type": r[1]} for r in data if r[0] is not None]


@phantom.playbook_block()
def redeploy_management_framework_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("redeploy_management_framework_1() called")
    phantom.act("redeploy management framework", parameters=_dev(container, results), name="redeploy_management_framework_1", assets=["<your-jamf-asset>"], callback=send_blank_push_1)
    return


@phantom.playbook_block()
def send_blank_push_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("send_blank_push_1() called")
    # 'update inventory' removed — connector rejects it for computers (macOS recon
    # runs on-device via policy, not MDM). redeploy + blank push force a check-in.
    phantom.act("send blank push", parameters=_dev(container, results), name="send_blank_push_1", assets=["<your-jamf-asset>"], callback=get_compliance_status_1)
    return


@phantom.playbook_block()
def get_compliance_status_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_compliance_status_1() called")
    phantom.act("get compliance status", parameters=_dev(container, results), name="get_compliance_status_1", assets=["<your-jamf-asset>"], callback=decision_1)
    return


@phantom.playbook_block()
def decision_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_1() called")
    # Corrected? compliant now -> end; still non-compliant -> contain
    matched = phantom.decision(
        container=container,
        conditions=[["get_compliance_status_1:action_result.data.*.compliance_state", "==", "COMPLIANT"]],
        name="decision_1:condition_1",
    )
    if matched:
        return  # remediated -> on_finish
    add_to_static_group_1(action=action, success=success, container=container, results=results, handle=handle)
    return


@phantom.playbook_block()
def add_to_static_group_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("add_to_static_group_1() called")
    data = phantom.collect2(container=container, datapath=["get_device_by_serial_1:action_result.data.*.id"], action_results=results)
    parameters = [{"device_id": r[0], "group_name": "<your-quarantine-group>"} for r in data if r[0] is not None]
    phantom.act("add to static group", parameters=parameters, name="add_to_static_group_1", assets=["<your-jamf-asset>"], callback=lock_device_1)
    return


@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")
    params = _dev(container, results)
    for p in params:
        p["pin"] = "<your-6-digit-pin>"   # computers require a 6-digit unlock pin
        p["message"] = "<your-return-message>"
        p["phone_number"] = "<your-callback-number>"
    phantom.act("lock device", parameters=params, name="lock_device_1", assets=["<your-jamf-asset>"], callback=prompt_1)
    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")
    message = ("Device remains non-compliant after automated correction and is contained "
               "(locked + quarantined). Approve device WIPE? This ERASES the device and is IRREVERSIBLE.")
    response_types = [{
        "prompt": "Approve device WIPE? (irreversible)",
        "options": {"type": "list", "required": True, "choices": ["Yes", "No"]},
    }]
    phantom.prompt2(container=container, user=None, role="Administrator", message=message,
                    respond_in_mins=30, name="prompt_1", parameters=[], response_types=response_types, callback=decision_2)
    return


@phantom.playbook_block()
def decision_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_2() called")
    approved = phantom.decision(
        container=container,
        conditions=[["prompt_1:action_result.summary.responses.0", "==", "Yes"]],
        name="decision_2:condition_1",
    )
    if approved:
        wipe_device_1(action=action, success=success, container=container, results=results, handle=handle)
    return


@phantom.playbook_block()
def wipe_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device_1() called")
    params = _dev(container, results)
    for p in params:
        p["confirm"] = "true"
    phantom.act("wipe device", parameters=params, name="wipe_device_1", assets=["<your-jamf-asset>"])
    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")
    return
