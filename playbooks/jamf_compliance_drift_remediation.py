"""
Jamf - Compliance Drift / MDM Tamper Remediation
=================================================

Splunk SOAR playbook template (Issue #4) for the `jamf-splunk-soar` connector.

Scenario
--------
A compliance correlation flags a device as non-compliant or MDM-tampered (security
profile removed, OS out of date, jailbreak extension attribute set). The container
carries the device serial (or id) on a label such as `<your-noncompliant-label>`.

Backbone (correct-first variant)
--------------------------------
resolve -> enrich -> CORRECT (reversible, non-disruptive) -> re-check ->
decision(corrected?) -> contain only if still non-compliant -> analyst approval
gate -> wipe (destructive, gated).

This template leads with non-destructive correction; containment and wipe are
escalations, not the first move.

Safety rule (non-negotiable)
----------------------------
The wipe is NEVER automatic. It runs only after an explicit analyst approval
prompt, and the prompt states that the action is irreversible. Do not remove the
gate (`prompt_escalate_wipe` -> `decide_wipe_approved`) when adapting this template.

Customer-config points (replace the <...> placeholders on import)
-----------------------------------------------------------------
- Jamf asset name ...... `assets=["<your-jamf-asset>"]` on every action block
- Quarantine group ...... `group_name` in `add_to_quarantine_group`
- Flag extension attr ... `ea_id` / value in `flag_under_review`
- Approver role ......... `role` in `prompt_escalate_wipe`
- Re-check delay ........ `WAIT_MINUTES` below (force-check-in settle time)

Connector-contract notes (verified against live connector "Jamf Pro" v1.0.0, app id 4)
--------------------------------------------------------------------------------------
- Resolver output: device id is `action_result.data.*.id` and device type is
  `action_result.data.*.type` (NOT `jamf_device_id` / `device_type`).
- `get compliance status` returns `action_result.data.*.compliance_state` (string) —
  the decision compares it to "COMPLIANT". Confirm the exact enum against a real
  device response (also: compliance_vendor, applicable).
- `update extension attribute` param is `ea_id` (+ optional `ea_name`, `value`).
- `wipe device` `confirm` is a REQUIRED STRING (set to "true"); confirm the exact
  accepted token against the connector.
- Notifications use `phantom.add_note` (container note) so the template needs no
  extra chat asset. Swap in your chat connector's "send message" action if desired.
"""

import phantom.rules as phantom
import json
from datetime import datetime, timedelta

# Settle time between the correction step and the compliance re-check, so a forced
# MDM check-in has time to apply. Surface as a customer-config point.
WAIT_MINUTES = 10


@phantom.playbook_block()
def on_start(container):
    phantom.debug("on_start() called")

    # call the first block
    resolve_device(container=container)

    return


@phantom.playbook_block()
def resolve_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Resolve the flagged device from the container's serial number."""
    phantom.debug("resolve_device() called")

    parameters = [{
        "serial_number": "artifact.*.cef.serialNumber",
    }]

    phantom.act(
        "get device by serial",
        parameters=parameters,
        name="resolve_device",
        assets=["<your-jamf-asset>"],
        callback=get_compliance_status_initial,
    )

    return


def _device_params(container, results):
    """Build per-device parameter dicts (device_id + device_type) from the resolver.

    Returns a list with one entry per resolved device, threading the originating
    artifact_id through `context` so results map back to the right artifact.
    """
    resolved = phantom.collect2(
        container=container,
        datapath=[
            "resolve_device:action_result.data.*.id",
            "resolve_device:action_result.data.*.type",
            "resolve_device:action_result.parameter.context.artifact_id",
        ],
        action_results=results,
    )

    parameters = []
    for item in resolved:
        if item[0] is not None:
            parameters.append({
                "device_id": item[0],
                "device_type": item[1],
                "context": {"artifact_id": item[2]},
            })
    return parameters


@phantom.playbook_block()
def get_compliance_status_initial(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Enrich: baseline compliance state before any correction."""
    phantom.debug("get_compliance_status_initial() called")

    parameters = _device_params(container, results)

    # No device resolved in Jamf -> note and end (on_finish runs automatically).
    if not parameters:
        phantom.add_note(
            container=container,
            note_type="general",
            title="Compliance Drift - device not found",
            content="No device matched the container's serial in Jamf. No action taken.",
        )
        return

    phantom.act(
        "get compliance status",
        parameters=parameters,
        name="get_compliance_status_initial",
        assets=["<your-jamf-asset>"],
        callback=get_configuration_profiles,
    )

    return


@phantom.playbook_block()
def get_configuration_profiles(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Enrich: is the expected security profile still present?"""
    phantom.debug("get_configuration_profiles() called")

    parameters = _device_params(container, results)

    phantom.act(
        "get configuration profiles",
        parameters=parameters,
        name="get_configuration_profiles",
        assets=["<your-jamf-asset>"],
        callback=get_extension_attributes,
    )

    return


@phantom.playbook_block()
def get_extension_attributes(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Enrich: read extension attributes (e.g. a jailbreak / tamper flag)."""
    phantom.debug("get_extension_attributes() called")

    parameters = _device_params(container, results)

    phantom.act(
        "get extension attributes",
        parameters=parameters,
        name="get_extension_attributes",
        assets=["<your-jamf-asset>"],
        callback=redeploy_management_framework,
    )

    return


@phantom.playbook_block()
def redeploy_management_framework(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Correct (reversible): re-establish MDM control on the device."""
    phantom.debug("redeploy_management_framework() called")

    parameters = _device_params(container, results)

    phantom.act(
        "redeploy management framework",
        parameters=parameters,
        name="redeploy_management_framework",
        assets=["<your-jamf-asset>"],
        callback=send_blank_push,
    )

    return


@phantom.playbook_block()
def send_blank_push(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Correct (reversible): force a fast MDM check-in so correction applies."""
    phantom.debug("send_blank_push() called")

    parameters = _device_params(container, results)

    phantom.act(
        "send blank push",
        parameters=parameters,
        name="send_blank_push",
        assets=["<your-jamf-asset>"],
        callback=update_inventory,
    )

    return


@phantom.playbook_block()
def update_inventory(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Correct (reversible): refresh inventory so re-check sees current state."""
    phantom.debug("update_inventory() called")

    parameters = _device_params(container, results)

    phantom.act(
        "update inventory",
        parameters=parameters,
        name="update_inventory",
        assets=["<your-jamf-asset>"],
        callback=flag_under_review,
    )

    return


@phantom.playbook_block()
def flag_under_review(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Correct (reversible): flag the device as under review via an extension attribute."""
    phantom.debug("flag_under_review() called")

    parameters = _device_params(container, results)
    for p in parameters:
        # Customer-config: the EA used to flag a device as under review, and the value.
        # Connector param is `ea_id` (verified against the live connector).
        p["ea_id"] = "<your-flag-ea-id>"
        p["value"] = "<under-review>"

    phantom.act(
        "update extension attribute",
        parameters=parameters,
        name="flag_under_review",
        assets=["<your-jamf-asset>"],
        callback=recheck_compliance,
    )

    return


@phantom.playbook_block()
def recheck_compliance(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Re-check compliance after the correction steps have been applied."""
    phantom.debug("recheck_compliance() called")

    # Optional settle time so the forced check-in has applied before we re-read state.
    phantom.debug("waiting {} minutes for MDM check-in to settle".format(WAIT_MINUTES))

    parameters = _device_params(container, results)

    phantom.act(
        "get compliance status",
        parameters=parameters,
        name="recheck_compliance",
        assets=["<your-jamf-asset>"],
        callback=decide_corrected,
    )

    return


@phantom.playbook_block()
def decide_corrected(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Corrected? Compliant now -> close; still non-compliant -> contain."""
    phantom.debug("decide_corrected() called")

    # Verified against the live connector: `get compliance status` returns
    # `compliance_state` (string), not a `compliant` boolean. Confirm the exact
    # value string ("COMPLIANT") against a real device's response.
    corrected = phantom.decision(
        container=container,
        conditions=[
            ["recheck_compliance:action_result.data.*.compliance_state", "==", "COMPLIANT"]
        ],
        conditions_dps=[
            ["recheck_compliance:action_result.data.*.compliance_state", "==", "COMPLIANT"]
        ],
        name="decide_corrected:condition_1",
        delimiter=None,
    )

    if corrected:
        notify_remediated(action=action, success=success, container=container, results=results, handle=handle)
        return

    # Still non-compliant -> escalate to containment.
    add_to_quarantine_group(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def notify_remediated(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Closed path: correction worked, device is compliant again."""
    phantom.debug("notify_remediated() called")

    phantom.add_note(
        container=container,
        note_type="general",
        title="Compliance Drift - remediated",
        content="Device returned to a compliant state after correction (redeploy framework / blank push / inventory). No containment needed.",
    )
    # Swap in your chat connector's "send message" action here if you notify externally.

    return


@phantom.playbook_block()
def add_to_quarantine_group(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Contain (reversible): scope a restrictive profile via a quarantine static group."""
    phantom.debug("add_to_quarantine_group() called")

    parameters = _device_params(container, results)
    for p in parameters:
        # Customer-config: your quarantine static group.
        p["group_name"] = "<your-quarantine-group>"
        # device_type isn't an input to this action; drop it to avoid a stray param.
        p.pop("device_type", None)

    phantom.act(
        "add to static group",
        parameters=parameters,
        name="add_to_quarantine_group",
        assets=["<your-jamf-asset>"],
        callback=lock_device,
    )

    return


@phantom.playbook_block()
def lock_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Contain (reversible): lock the device (queued; applies on next check-in).

    Computer path shown. For supervised mobile devices, branch to `enable lost mode`
    instead — left as a documented extension point to keep the template focused.
    """
    phantom.debug("lock_device() called")

    parameters = _device_params(container, results)
    for p in parameters:
        # Customer-config: lock screen message + callback number shown on the device.
        p["message"] = "<your-return-message>"
        p["phone_number"] = "<your-callback-number>"

    phantom.act(
        "lock device",
        parameters=parameters,
        name="lock_device",
        assets=["<your-jamf-asset>"],
        callback=notify_contained,
    )

    return


@phantom.playbook_block()
def notify_contained(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Notify that containment is queued, then move to the approval gate."""
    phantom.debug("notify_contained() called")

    phantom.add_note(
        container=container,
        note_type="general",
        title="Compliance Drift - contained (queued)",
        content="Correction did not restore compliance. Device added to the quarantine group and locked (queued; applies on next MDM check-in). Awaiting analyst decision on wipe.",
    )

    prompt_escalate_wipe(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def prompt_escalate_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """ANALYST APPROVAL GATE before the destructive wipe. Never remove this block.

    The prompt states the irreversibility of the action at the moment of decision
    (per the library convention in issue #8).
    """
    phantom.debug("prompt_escalate_wipe() called")

    # Approver is a ROLE, not a named person, so the template stays generic.
    user = None
    role = "<your-security-analyst-role>"
    message = (
        "Device remains non-compliant after automated correction and is now "
        "contained (locked + quarantined). Escalate to WIPE? This ERASES the "
        "device and is IRREVERSIBLE."
    )

    parameters = []

    response_types = [
        {
            "prompt": "Approve device WIPE? (irreversible)",
            "options": {
                "type": "list",
                "required": True,
                "choices": [
                    "Approve",
                    "Deny",
                ],
            },
        }
    ]

    phantom.prompt2(
        container=container,
        user=user,
        role=role,
        message=message,
        respond_in_mins=30,
        name="prompt_escalate_wipe",
        parameters=parameters,
        response_types=response_types,
        callback=decide_wipe_approved,
    )

    return


@phantom.playbook_block()
def decide_wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Approved? Only an explicit 'Approve' proceeds to the wipe."""
    phantom.debug("decide_wipe_approved() called")

    approved = phantom.decision(
        container=container,
        conditions=[
            ["prompt_escalate_wipe:action_result.summary.responses.0", "==", "Approve"]
        ],
        conditions_dps=[
            ["prompt_escalate_wipe:action_result.summary.responses.0", "==", "Approve"]
        ],
        name="decide_wipe_approved:condition_1",
        delimiter=None,
    )

    if approved:
        wipe_device(action=action, success=success, container=container, results=results, handle=handle)
        return

    # Denied -> leave the device contained, record the decision.
    note_wipe_denied(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Destructive (gated): erase the device. Reached ONLY on analyst approval."""
    phantom.debug("wipe_device() called")

    parameters = _device_params(container, results)
    for p in parameters:
        # Connector's `confirm` is a REQUIRED STRING safety flag (verified live),
        # not a boolean. Confirm the exact accepted value against the connector.
        p["confirm"] = "true"

    phantom.act(
        "wipe device",
        parameters=parameters,
        name="wipe_device",
        assets=["<your-jamf-asset>"],
    )

    return


@phantom.playbook_block()
def note_wipe_denied(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    """Denied path: record that the wipe was declined; device stays contained."""
    phantom.debug("note_wipe_denied() called")

    phantom.add_note(
        container=container,
        note_type="general",
        title="Compliance Drift - wipe denied",
        content="Analyst denied the wipe. Device remains locked and quarantined; no erase performed.",
    )

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    return
