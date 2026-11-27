"""
Accepts a username from the event, finds every Jamf-managed device for that user, then quarantines, locks and sends a blank push to each, reporting the actual result per device in a note. An analyst is shown the full list of devices and must approve before any of them are wiped. Nothing is wiped without approval.
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
    # Looks up every Jamf device for the username in the event artifact.
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
def add_to_suspended_group(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("add_to_suspended_group() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Adds each device to the computer or mobile suspended 
    # group.
    ################################################################################

    find_devices_by_username_result_data = phantom.collect2(container=container, datapath=["find_devices_by_username:action_result.data.*.id","find_devices_by_username:action_result.data.*.type","find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'add_to_suspended_group' call
    for find_devices_by_username_result_item in find_devices_by_username_result_data:
        if find_devices_by_username_result_item[0] is not None:
            parameters.append({
                "group_id": "",
                "device_id": find_devices_by_username_result_item[0],
                "device_type": find_devices_by_username_result_item[1],
                "context": {'artifact_id': find_devices_by_username_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    COMPUTER_GROUP = "<your-computer-suspended-group-id>"
    MOBILE_GROUP   = "<your-mobile-suspended-group-id>"
    rows = phantom.collect2(container=container, datapath=[
        "find_devices_by_username:action_result.data.*.id",
        "find_devices_by_username:action_result.data.*.type",
        "find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        gid = COMPUTER_GROUP if str(dtype) == "computer" else MOBILE_GROUP
        parameters.append({
            "device_type": dtype, 
            "device_id": did, 
            "group_id": gid,
            "context": {"artifact_id": aid}
        })

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add to static group", parameters=parameters, name="add_to_suspended_group", assets=["jamf_pro"], callback=join_format_containment_results)

    return


@phantom.playbook_block()
def send_blank_push(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("send_blank_push() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Sends a blank push to each device so it checks 
    # in.
    ################################################################################

    find_devices_by_username_result_data = phantom.collect2(container=container, datapath=["find_devices_by_username:action_result.data.*.id","find_devices_by_username:action_result.data.*.type","find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'send_blank_push' call
    for find_devices_by_username_result_item in find_devices_by_username_result_data:
        if find_devices_by_username_result_item[0] is not None:
            parameters.append({
                "device_id": find_devices_by_username_result_item[0],
                "device_type": find_devices_by_username_result_item[1],
                "context": {'artifact_id': find_devices_by_username_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "find_devices_by_username:action_result.data.*.id",
        "find_devices_by_username:action_result.data.*.type",
        "find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did,
                           "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("send blank push", parameters=parameters, name="send_blank_push", assets=["jamf_pro"], callback=join_format_containment_results)

    return


@phantom.playbook_block()
def lock_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_devices() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Locks each device.
    ################################################################################

    find_devices_by_username_result_data = phantom.collect2(container=container, datapath=["find_devices_by_username:action_result.data.*.id","find_devices_by_username:action_result.data.*.type","find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_devices' call
    for find_devices_by_username_result_item in find_devices_by_username_result_data:
        if find_devices_by_username_result_item[0] is not None:
            parameters.append({
                "pin": "",
                "message": "",
                "device_id": find_devices_by_username_result_item[0],
                "device_type": find_devices_by_username_result_item[1],
                "phone_number": "",
                "context": {'artifact_id': find_devices_by_username_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################


    import secrets
    rows = phantom.collect2(container=container, datapath=[
        "find_devices_by_username:action_result.data.*.id",
        "find_devices_by_username:action_result.data.*.type",
        "find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        p = {
            "device_type": dtype, "device_id": did,
             "message": "This device has been locked by security. Contact IT.",
             "phone_number": "<your-callback-number>", "context": {"artifact_id": aid}
        }
        if str(dtype) == "computer":
            p["pin"] = str(100000 + secrets.randbelow(900000))
        parameters.append(p)

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_devices", assets=["jamf_pro"], callback=join_format_containment_results)

    return


@phantom.playbook_block()
def join_format_containment_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_containment_results() called")

    if phantom.completed(action_names=["add_to_suspended_group", "send_blank_push", "lock_devices"]):
        # call connected block "format_containment_results"
        format_containment_results(container=container, handle=handle)

    return


@phantom.playbook_block()
def format_containment_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_containment_results() called")

    ################################################################################
    # This block uses custom code. Formats the actual result of each containment action 
    # for each device.
    ################################################################################

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev_raw = phantom.collect2(container=container, datapath=[
        "find_devices_by_username:action_result.data.*.id",
        "find_devices_by_username:action_result.data.*.general.name",
        "find_devices_by_username:action_result.data.*.type"])
    seen, dev = set(), []
    for r in dev_raw:
        if r[0] is not None and str(r[0]) not in seen:
            seen.add(str(r[0])); dev.append(r)

    def _stat(action):
        rows = phantom.collect2(container=container, datapath=[
            action + ":action_result.parameter.device_id", action + ":action_result.status"])
        return {str(x[0]): str(x[1]).lower() for x in rows if x and x[0] is not None}
    def _pin(did):
        rows = phantom.collect2(container=container, datapath=[
            "lock_devices:action_result.parameter.device_id", "lock_devices:action_result.parameter.pin"])
        m = {str(x[0]): x[1] for x in rows if x and x[0] is not None}
        return m.get(str(did))

    grp, lok, psh = _stat("add_to_suspended_group"), _stat("lock_devices"), _stat("send_blank_push")
    def mark(m, did):
        s = m.get(str(did))
        return "✅" if s == "success" else ("⚠️ FAILED" if s else "— not attempted")

    blocks = []
    for r in dev:
        did, name, dtype = r[0], r[1], r[2]
        line = "  - Lock: " + mark(lok, did)
        if lok.get(str(did)) == "success" and _pin(did):
            line += "  (unlock PIN: " + str(_pin(did)) + ")"
        blocks.append("**" + str(name) + "**  (" + str(dtype) + ", id " + str(did) + ")\n"
                      + "  - Quarantine group: " + mark(grp, did) + "\n"
                      + line + "\n  - Blank push: " + mark(psh, did))
    summary = ("## Compromised User — Containment\n\n"
               + ("\n\n".join(blocks) if blocks else "_No devices resolved._")
               + "\n\n_MDM actions are queued — they apply on the device's next check-in._")
    template = summary.replace("{", "{{").replace("}", "}}")
    parameters = []

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="format_containment_results")

    note_containment_results(container=container)

    return


@phantom.playbook_block()
def note_containment_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_containment_results() called")

    ################################################################################
    # This block uses custom code. Adds a note with the containment result for each 
    # device.
    ################################################################################

    format_containment_results = phantom.get_format_data(name="format_containment_results")

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

    text = "\n".join(_flat(format_containment_results))

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

    phantom.save_block_result(key="note_containment_results__inputs:0:format_containment_results:formatted_data", value=json.dumps(format_containment_results))

    phantom.save_block_result(key="note_containment_results_called", value="True")

    format_wipe_prompt(container=container)

    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")

    ################################################################################
    # Shows the analyst every device and asks whether to wipe them. Times out after 
    # 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<your-approver-role>"
    message = """Compromised-user containment complete.\\n\\n{0}"""

    # parameter list for template variable replacement
    parameters = [
        "format_wipe_prompt:formatted_data"
    ]

    # responses
    response_types = [
        {
            "prompt": "Wipe ALL the devices listed above? This is irreversible.",
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_wipe", parameters=parameters, response_types=response_types, callback=wipe_approved)

    return


@phantom.playbook_block()
def wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_approved() called")

    ################################################################################
    # Wipes the devices only if the analyst chose Wipe.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["approve_wipe:action_result.summary.responses.0", "==", "Wipe"]
        ],
        conditions_dps=[
            ["approve_wipe:action_result.summary.responses.0", "==", "Wipe"]
        ],
        name="wipe_approved:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_devices(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_wipe_not_approved(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_devices(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_devices() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Erases each device. Runs only after analyst approval.
    ################################################################################

    find_devices_by_username_result_data = phantom.collect2(container=container, datapath=["find_devices_by_username:action_result.data.*.id","find_devices_by_username:action_result.data.*.type","find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_devices' call
    for find_devices_by_username_result_item in find_devices_by_username_result_data:
        if find_devices_by_username_result_item[0] is not None:
            parameters.append({
                "pin": "",
                "confirm": True,
                "device_id": find_devices_by_username_result_item[0],
                "device_type": find_devices_by_username_result_item[1],
                "context": {'artifact_id': find_devices_by_username_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "find_devices_by_username:action_result.data.*.id",
        "find_devices_by_username:action_result.data.*.type",
        "find_devices_by_username:action_result.parameter.context.artifact_id"], action_results=results)
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        parameters.append({
            "device_type": dtype, "device_id": did,
            "confirm": str(did),          # connector requires confirm == device_id
            "context": {"artifact_id": aid},
        })

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_devices", assets=["jamf_pro"], callback=note_wipe_outcome)

    return


@phantom.playbook_block()
def note_wipe_not_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_not_approved() called")

    ################################################################################
    # This block uses custom code. Adds a note that the wipe was not approved or the 
    # prompt timed out.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(
        container=container,
        note_type="general",
        title="Wipe not approved",
        content="Wipe not approved (analyst denied, or the prompt timed out) — devices remain contained (quarantined + locked).",
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_not_approved_called", value="True")

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
        add_to_suspended_group(action=action, success=success, container=container, results=results, handle=handle)
        send_blank_push(action=action, success=success, container=container, results=results, handle=handle)
        lock_devices(action=action, success=success, container=container, results=results, handle=handle)
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
        title="Compromised User Device Sweep",
        content="No Jamf devices found for user **" + str(user) + "** — nothing to contain.",
        note_format="markdown",
    )

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_no_devices_called", value="True")

    return


@phantom.playbook_block()
def note_wipe_outcome(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_outcome() called")

    ################################################################################
    # This block uses custom code. Adds a note with the result of the wipe for each 
    # device.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "wipe_devices:action_result.parameter.device_id",
        "wipe_devices:action_result.status",
        "wipe_devices:action_result.message"
    ])
    if not rows:
        body = "_Wipe was not executed._"
    else:
        seen, lines = set(), []
        for r in rows:
            did = r[0]
            if did is None or str(did) in seen:
                continue
            seen.add(str(did))
            icon = "✅ queued" if str(r[1]).lower() == "success" else "⚠️ FAILED"
            lines.append("- Device id " + str(did) + ": " + icon + (" — " + str(r[2]) if r[2] else ""))
        body = "## Wipe outcome\n\n" + "\n".join(lines)
    phantom.add_note(
        container=container, note_type="general",
        title="Compromised User — Wipe Outcome", content=body, note_format="markdown")
    
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_outcome_called", value="True")

    return


@phantom.playbook_block()
def format_wipe_prompt(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_wipe_prompt() called")

    ################################################################################
    # This block uses custom code. Lists every device that would be wiped, for the 
    # approval prompt.
    ################################################################################

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    ids = phantom.collect2(container=container, datapath=[
        "find_devices_by_username:action_result.data.*.id",
        "find_devices_by_username:action_result.data.*.general.name"])
    def _stat(a):
        rows = phantom.collect2(container=container, datapath=[
            a + ":action_result.parameter.device_id", a + ":action_result.status"])
        return {str(x[0]): str(x[1]).lower() for x in rows if x and x[0] is not None}
    grp, lok = _stat("add_to_suspended_group"), _stat("lock_devices")
    seen, lines = set(), []
    for r in ids:
        did = r[0]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        ok = grp.get(str(did)) == "success" and lok.get(str(did)) == "success"
        lines.append("• " + str(r[1]) + " (id " + str(did) + ")" + ("" if ok else "  ⚠️ NOT fully contained"))
    scope = ("⚠️ You are about to WIPE ALL " + str(len(lines)) + " device(s) — IRREVERSIBLE:\n"
             + "\n".join(lines)
             + "\n\n(⚠️-flagged devices failed containment — review before wiping.)")
    template = scope.replace("{", "{{").replace("}", "}}")
    parameters = []
    
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="format_wipe_prompt")

    approve_wipe(container=container)

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