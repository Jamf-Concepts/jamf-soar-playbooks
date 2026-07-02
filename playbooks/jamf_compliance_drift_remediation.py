"""
Jamf - Compliance Drift / MDM Tamper Remediation
Correct-first: resolve -> correct (redeploy management framework + blank push) ->
re-check compliance -> if still non-compliant: contain (quarantine + lock) -> analyst
approval prompt (irreversible warning) -> gated wipe. Never auto-wipe.

Block names are descriptive verbs (issue #8 convention), not auto-numbered.
NOTE: the paired .json still carries the old auto-numbered node ids; it must be
re-opened in the VPE, renamed to match these names, and re-exported so the two
stay in sync (see jamf_compliance_drift_remediation.BUILD.md for the rename map).
"""

import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')
    resolve_device(container=container)
    return


@phantom.playbook_block()
def resolve_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("resolve_device() called")
    parameters = [{"serial_number": "artifact:*.cef.serialNumber"}]
    phantom.act("get device by serial", parameters=parameters, name="resolve_device", assets=["<your-jamf-asset>"], callback=redeploy_framework)
    return


def _dev(container, results):
    data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id", "resolve_device:action_result.data.*.type"], action_results=results)
    return [{"device_id": r[0], "device_type": r[1]} for r in data if r[0] is not None]


@phantom.playbook_block()
def redeploy_framework(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("redeploy_framework() called")
    phantom.act("redeploy management framework", parameters=_dev(container, results), name="redeploy_framework", assets=["<your-jamf-asset>"], callback=force_checkin)
    return


@phantom.playbook_block()
def force_checkin(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("force_checkin() called")
    # 'update inventory' removed — connector rejects it for computers (macOS recon
    # runs on-device via policy, not MDM). redeploy + blank push force a check-in.
    phantom.act("send blank push", parameters=_dev(container, results), name="force_checkin", assets=["<your-jamf-asset>"], callback=check_compliance)
    return


@phantom.playbook_block()
def check_compliance(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("check_compliance() called")
    phantom.act("get compliance status", parameters=_dev(container, results), name="check_compliance", assets=["<your-jamf-asset>"], callback=is_compliant)
    return


@phantom.playbook_block()
def is_compliant(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("is_compliant() called")
    # Fail-safe: only CONTAIN when the compliance read SUCCEEDED and positively reports
    # a non-compliant device. A failed/403 read (documented INVALID_PRIVILEGE case) or an
    # empty/unknown value falls through to on_finish and is NEVER treated as non-compliant —
    # a missing signal must not silently escalate toward containment/wipe.
    # NOTE: the non-compliant enum value is not yet confirmed against the live connector; we
    # escalate on "not COMPLIANT" gated by a successful read. Once the exact non-compliant
    # token is known, tighten the second condition to an explicit equality.
    escalate = phantom.decision(
        container=container,
        conditions=[
            ["check_compliance:action_result.status", "==", "success"],
            ["check_compliance:action_result.data.*.compliance_state", "!=", "COMPLIANT"],
        ],
        name="is_compliant:condition_1",
    )
    if escalate:
        quarantine_device(action=action, success=success, container=container, results=results, handle=handle)
    return  # compliant OR failed/empty read -> on_finish (safe)


@phantom.playbook_block()
def quarantine_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("quarantine_device() called")
    data = phantom.collect2(container=container, datapath=["resolve_device:action_result.data.*.id"], action_results=results)
    parameters = [{"device_id": r[0], "group_name": "<your-quarantine-group>"} for r in data if r[0] is not None]
    phantom.act("add to static group", parameters=parameters, name="quarantine_device", assets=["<your-jamf-asset>"], callback=lock_device)
    return


@phantom.playbook_block()
def lock_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device() called")
    params = _dev(container, results)
    for p in params:
        p["pin"] = "<your-6-digit-pin>"   # computers require a 6-digit unlock pin
        p["message"] = "<your-return-message>"
        p["phone_number"] = "<your-callback-number>"
    phantom.act("lock device", parameters=params, name="lock_device", assets=["<your-jamf-asset>"], callback=approve_wipe)
    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")
    # Message states what was ATTEMPTED, not asserted fact — the containment steps are queued
    # MDM commands and are not confirmed applied at prompt time.
    message = ("Device is still reported non-compliant after automated correction. Quarantine + "
               "lock were queued (verify they applied). Approve device WIPE? This ERASES the "
               "device and is IRREVERSIBLE.")
    response_types = [{
        "prompt": "Approve device WIPE? (irreversible)",
        "options": {"type": "list", "required": True, "choices": ["Yes", "No"]},
    }]
    phantom.prompt2(container=container, user=None, role="Administrator", message=message,
                    respond_in_mins=30, name="approve_wipe", parameters=[], response_types=response_types, callback=is_wipe_approved)
    return


@phantom.playbook_block()
def is_wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("is_wipe_approved() called")
    # Fail-safe: wipe requires an explicit "Yes". Timeout / "No" / no response all fall through
    # to on_finish and never wipe.
    approved = phantom.decision(
        container=container,
        conditions=[["approve_wipe:action_result.summary.responses.0", "==", "Yes"]],
        name="is_wipe_approved:condition_1",
    )
    if approved:
        wipe_device(action=action, success=success, container=container, results=results, handle=handle)
    return


@phantom.playbook_block()
def wipe_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device() called")
    params = _dev(container, results)
    for p in params:
        p["confirm"] = "true"
        p["pin"] = "<your-6-digit-pin>"   # computer erase requires a 6-digit pin (same as lock)
    phantom.act("wipe device", parameters=params, name="wipe_device", assets=["<your-jamf-asset>"])
    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")
    return
