"""

"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'get_device_by_name_1' block
    get_device_by_name_1(container=container)

    return

@phantom.playbook_block()
def get_device_by_name_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_device_by_name_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.deviceHostname","artifact:*.id"])

    parameters = []

    # build parameters list for 'get_device_by_name_1' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "device_name": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get device by name", parameters=parameters, name="get_device_by_name_1", assets=["<your-jamf-asset>"], callback=decision_1)

    return


@phantom.playbook_block()
def decision_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_1() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["get_device_by_name_1:action_result.summary.total", ">", 0]
        ],
        conditions_dps=[
            ["get_device_by_name_1:action_result.summary.total", ">", 0]
        ],
        name="decision_1:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        get_installed_applications_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    code_1(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def code_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_1() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["artifact:*.cef.deviceHostname"])
    host = rows[0][0] if rows and rows[0] and rows[0][0] else "unknown"
    phantom.add_note(
        container=container, note_type="general",
        title="Malicious File Containment",
        content="No Jamf device found matching host **" + str(host) + "** — no action taken.",
        note_format="markdown")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_1_called", value="True")

    return


@phantom.playbook_block()
def get_installed_applications_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_installed_applications_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_name_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_name_1:action_result.data.*.type","get_device_by_name_1:action_result.data.*.id","get_device_by_name_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_installed_applications_1' call
    for get_device_by_name_1_result_item in get_device_by_name_1_result_data:
        if get_device_by_name_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_name_1_result_item[0],
                "device_id": get_device_by_name_1_result_item[1],
                "context": {'artifact_id': get_device_by_name_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get installed applications", parameters=parameters, name="get_installed_applications_1", assets=["<your-jamf-asset>"], callback=decision_2)

    return


@phantom.playbook_block()
def decision_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_2() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["artifact:*.cef.fileName", "in", "get_installed_applications_1:action_result.data.*.name"]
        ],
        conditions_dps=[
            ["artifact:*.cef.fileName", "in", "get_installed_applications_1:action_result.data.*.name"]
        ],
        name="decision_2:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        add_to_static_group_1(action=action, success=success, container=container, results=results, handle=handle)
        lock_device_1(action=action, success=success, container=container, results=results, handle=handle)
        send_blank_push_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    code_2(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def code_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_2() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["artifact:*.cef.fileName"])
    fn = rows[0][0] if rows and rows[0] and rows[0][0] else "the flagged file"
    phantom.add_note(container=container, note_type="general",
        title="Malicious File Containment — Detection",
        content="Flagged file **" + str(fn) + "** was not found among the device's installed apps — no containment taken.",
        note_format="markdown")
    
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_2_called", value="True")

    return


@phantom.playbook_block()
def add_to_static_group_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("add_to_static_group_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_name_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_name_1:action_result.data.*.type","get_device_by_name_1:action_result.data.*.id","get_device_by_name_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'add_to_static_group_1' call
    for get_device_by_name_1_result_item in get_device_by_name_1_result_data:
        if get_device_by_name_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_name_1_result_item[0],
                "device_id": get_device_by_name_1_result_item[1],
                "group_id": 3,
                "context": {'artifact_id': get_device_by_name_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    ISOLATION_GROUP = "<your-isolation-group-id>"
    rows = phantom.collect2(container=container, datapath=[
        "get_device_by_name_1:action_result.data.*.id",
        "get_device_by_name_1:action_result.data.*.type",
        "get_device_by_name_1:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did,
                           "group_id": ISOLATION_GROUP, "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add to static group", parameters=parameters, name="add_to_static_group_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def lock_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_name_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_name_1:action_result.data.*.type","get_device_by_name_1:action_result.data.*.id","get_device_by_name_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_device_1' call
    for get_device_by_name_1_result_item in get_device_by_name_1_result_data:
        if get_device_by_name_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_name_1_result_item[0],
                "device_id": get_device_by_name_1_result_item[1],
                "context": {'artifact_id': get_device_by_name_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    import random
    rows = phantom.collect2(container=container, datapath=[
        "get_device_by_name_1:action_result.data.*.id",
        "get_device_by_name_1:action_result.data.*.type",
        "get_device_by_name_1:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did,
            "pin": str(random.randint(100000, 999999)),
            "message": "This device has been isolated by security (detected malicious app). Contact IT.",
            "phone_number": "<your-callback-number>", "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_device_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def send_blank_push_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("send_blank_push_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_name_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_name_1:action_result.data.*.type","get_device_by_name_1:action_result.data.*.id","get_device_by_name_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'send_blank_push_1' call
    for get_device_by_name_1_result_item in get_device_by_name_1_result_data:
        if get_device_by_name_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_name_1_result_item[0],
                "device_id": get_device_by_name_1_result_item[1],
                "context": {'artifact_id': get_device_by_name_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "get_device_by_name_1:action_result.data.*.id",
        "get_device_by_name_1:action_result.data.*.type",
        "get_device_by_name_1:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did, "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("send blank push", parameters=parameters, name="send_blank_push_1", assets=["<your-jamf-asset>"], callback=join_format_1)

    return


@phantom.playbook_block()
def join_format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_1() called")

    if phantom.completed(action_names=["add_to_static_group_1", "lock_device_1", "send_blank_push_1"]):
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

    dev = phantom.collect2(container=container, datapath=[
        "get_device_by_name_1:action_result.data.*.id",
        "get_device_by_name_1:action_result.data.*.general.name"])
    seen, devs = set(), []
    for r in dev:
        if r[0] is not None and str(r[0]) not in seen:
            seen.add(str(r[0])); devs.append(r)

    fr = phantom.collect2(container=container, datapath=["artifact:*.cef.fileName"])
    flagged_all = sorted({str(x[0]) for x in fr if x and x[0]})
    ap = phantom.collect2(container=container, datapath=["get_installed_applications_1:action_result.data.*.name"])
    app_names = [str(a[0]) for a in ap if a and a[0]]
    confirmed = sorted({f for f in flagged_all for a in app_names if f in a or a in f})
    flagged = ", ".join(confirmed) or "(none matched)"

    hosts = {str(r[0]) for r in phantom.collect2(container=container, datapath=["artifact:*.cef.deviceHostname"]) if r and r[0]}
    multi_warn = ""
    if len(hosts) > 1 or len(flagged_all) > 1:
        multi_warn = ("\n\n> ⚠️ **Multiple detections in this container** (" + str(len(hosts))
            + " host(s), " + str(len(flagged_all)) + " flagged file(s)). This playbook handles "
            "**one detection per container** — review manually; the wipe step is blocked.")

    def _stat(a):
        rows = phantom.collect2(container=container, datapath=[
            a + ":action_result.parameter.device_id", a + ":action_result.status"])
        return {str(x[0]): str(x[1]).lower() for x in rows if x and x[0] is not None}
    def _pin(did):
        rows = phantom.collect2(container=container, datapath=[
            "lock_device_1:action_result.parameter.device_id", "lock_device_1:action_result.parameter.pin"])
        m = {str(x[0]): x[1] for x in rows if x and x[0] is not None}
        return m.get(str(did))
    grp, lok, psh = _stat("add_to_static_group_1"), _stat("lock_device_1"), _stat("send_blank_push_1")
    def mark(m, did):
        s = m.get(str(did))
        return "✅" if s == "success" else ("⚠️ FAILED" if s else "— not attempted")

    blocks = []
    for r in devs:
        did, name = r[0], r[1]
        line = "  - Lock: " + mark(lok, did)
        if lok.get(str(did)) == "success" and _pin(did):
            line += "  (unlock PIN: " + str(_pin(did)) + ")"
        blocks.append("**" + str(name) + "**  (id " + str(did) + ")\n"
            + "  - Isolation group: " + mark(grp, did) + "\n"
            + line + "\n  - Blank push: " + mark(psh, did))
    summary = ("## Malicious App Containment\n\n**Flagged app:** " + flagged + multi_warn + "\n\n"
        + ("\n\n".join(blocks) if blocks else "_No devices._")
        + "\n\n_MDM actions are queued — they apply on the device's next check-in._")
    template = summary.replace("{", "{{").replace("}", "}}")
    parameters = []

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="format_1")

    code_3(container=container)

    return


@phantom.playbook_block()
def code_3(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_3() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    text = phantom.get_format_data(name="format_1")
    def _flat(x):
        out = []
        if isinstance(x, (list, tuple)):
            for i in x:
                out.extend(_flat(i))
        elif x not in (None, ""):
            out.append(str(x))
        return out
    phantom.add_note(container=container, note_type="general",
        title="Malicious App Containment", content="\n".join(_flat(text)), note_format="markdown")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_3_called", value="True")

    format_2(container=container)

    return


@phantom.playbook_block()
def format_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_2() called")

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=[
        "get_device_by_name_1:action_result.data.*.general.name",
        "get_device_by_name_1:action_result.data.*.id"])
    seen, names = set(), []
    for r in dev:
        did = r[1]
        if did is None or str(did) in seen:
            continue
        seen.add(str(did)); names.append(str(r[0]) + " (id " + str(did) + ")")
    fr = phantom.collect2(container=container, datapath=["artifact:*.cef.fileName"])
    flg = ", ".join(sorted({str(x[0]) for x in fr if x and x[0]})) or "flagged app"
    scope = ("A malicious app (" + flg + ") was confirmed on:\n" + "\n".join("• " + n for n in names)
             + "\n\n⚠️ WIPE is IRREVERSIBLE.")
    template = scope.replace("{", "{{").replace("}", "}}")
    parameters = []

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="format_2")

    prompt_1(container=container)

    return


@phantom.playbook_block()
def prompt_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("prompt_1() called")

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<your-approver-role>"
    message = """{0}"""

    # parameter list for template variable replacement
    parameters = [
        "format_2:formatted_data"
    ]

    # responses
    response_types = [
        {
            "prompt": "Wipe the device(s) listed above? This is irreversible.",
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="prompt_1", parameters=parameters, response_types=response_types, callback=decision_3)

    return


@phantom.playbook_block()
def decision_3(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("decision_3() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["prompt_1:action_result.summary.responses.0", "==", "Wipe"]
        ],
        conditions_dps=[
            ["prompt_1:action_result.summary.responses.0", "==", "Wipe"]
        ],
        name="decision_3:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        wipe_device_1(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    code_5(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_device_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_device_1() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    get_device_by_name_1_result_data = phantom.collect2(container=container, datapath=["get_device_by_name_1:action_result.data.*.type","get_device_by_name_1:action_result.data.*.id","get_device_by_name_1:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_device_1' call
    for get_device_by_name_1_result_item in get_device_by_name_1_result_data:
        if get_device_by_name_1_result_item[1] is not None:
            parameters.append({
                "device_type": get_device_by_name_1_result_item[0],
                "device_id": get_device_by_name_1_result_item[1],
                "confirm": True,
                "context": {'artifact_id': get_device_by_name_1_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    hosts = {str(r[0]) for r in phantom.collect2(container=container, datapath=["artifact:*.cef.deviceHostname"]) if r and r[0]}
    files = {str(r[0]) for r in phantom.collect2(container=container, datapath=["artifact:*.cef.fileName"]) if r and r[0]}
    parameters = []
    if len(hosts) <= 1 and len(files) <= 1:          # one-detection guard — no wipe if multiple
        rows = phantom.collect2(container=container, datapath=[
            "get_device_by_name_1:action_result.data.*.id",
            "get_device_by_name_1:action_result.data.*.type",
            "get_device_by_name_1:action_result.parameter.context.artifact_id"])
        seen = set()
        for r in rows:
            did, dtype, aid = r[0], r[1], r[2]
            if did is None or str(did) in seen:
                continue
            seen.add(str(did))
            parameters.append({"device_type": dtype, "device_id": did,
                "confirm": str(did), "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_device_1", assets=["<your-jamf-asset>"], callback=code_4)

    return


@phantom.playbook_block()
def code_4(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_4() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "wipe_device_1:action_result.parameter.device_id",
        "wipe_device_1:action_result.status",
        "wipe_device_1:action_result.message"])
    if not rows:
        body = "_Wipe not executed (no approval, or blocked — multiple detections)._"
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
    phantom.add_note(container=container, note_type="general",
        title="Malicious App Containment — Wipe Outcome", content=body, note_format="markdown")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_4_called", value="True")

    return


@phantom.playbook_block()
def code_5(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("code_5() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    phantom.add_note(container=container, note_type="general",
        title="Malicious App Containment — Wipe Not Approved",
        content="Wipe not approved (analyst denied, or the prompt timed out) — device remains isolated + locked.",
        note_format="markdown")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="code_5_called", value="True")

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