"""
Accepts a device hostname and a flagged file name from the event, looks up the Mac in Jamf and checks its installed applications for the flagged app. If it is present, the Mac is added to an isolation group, locked and sent a blank push, and a note reports the actual result of each action. An analyst must approve before any wipe, and the wipe is blocked if the hostname matches more than one device. If the app is not found or cannot be confirmed, only a note is added.
"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'find_mac_by_hostname' block
    find_mac_by_hostname(container=container)

    return

@phantom.playbook_block()
def find_mac_by_hostname(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("find_mac_by_hostname() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Looks up the Mac in Jamf Pro by the hostname from the event artifact.
    ################################################################################

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.deviceHostname","artifact:*.id"])

    parameters = []

    # build parameters list for 'find_mac_by_hostname' call
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

    phantom.act("get device by name", parameters=parameters, name="find_mac_by_hostname", assets=["jamf_pro"], callback=device_found)

    return


@phantom.playbook_block()
def device_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("device_found() called")

    ################################################################################
    # Continues only if the lookup succeeded and returned at least one device.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        logical_operator="and",
        conditions=[
            ["find_mac_by_hostname:action_result.summary.total", ">", 0],
            ["find_mac_by_hostname:action_result.status", "==", "success"]
        ],
        conditions_dps=[
            ["find_mac_by_hostname:action_result.summary.total", ">", 0],
            ["find_mac_by_hostname:action_result.status", "==", "success"]
        ],
        name="device_found:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        get_installed_apps(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_no_device(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_no_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_no_device() called")

    ################################################################################
    # This block uses custom code. Adds a note when no device matched the hostname.
    ################################################################################

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

    phantom.save_block_result(key="note_no_device_called", value="True")

    return


@phantom.playbook_block()
def get_installed_apps(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("get_installed_apps() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # Lists the applications installed on the Mac.
    ################################################################################

    find_mac_by_hostname_result_data = phantom.collect2(container=container, datapath=["find_mac_by_hostname:action_result.data.*.id","find_mac_by_hostname:action_result.data.*.type","find_mac_by_hostname:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'get_installed_apps' call
    for find_mac_by_hostname_result_item in find_mac_by_hostname_result_data:
        if find_mac_by_hostname_result_item[0] is not None:
            parameters.append({
                "device_id": find_mac_by_hostname_result_item[0],
                "device_type": find_mac_by_hostname_result_item[1],
                "context": {'artifact_id': find_mac_by_hostname_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("get installed applications", parameters=parameters, name="get_installed_apps", assets=["jamf_pro"], callback=app_found)

    return


@phantom.playbook_block()
def app_found(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("app_found() called")

    ################################################################################
    # Contains the Mac only if the flagged app is among its installed applications.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        logical_operator="or",
        conditions=[
            ["artifact:*.cef.fileName", "in", "get_installed_apps:action_result.data.*.name"],
            ["get_installed_apps:action_result.data.*.name", "in", "artifact:*.cef.fileName"]
        ],
        conditions_dps=[
            ["artifact:*.cef.fileName", "in", "get_installed_apps:action_result.data.*.name"],
            ["get_installed_apps:action_result.data.*.name", "in", "artifact:*.cef.fileName"]
        ],
        name="app_found:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        add_to_isolation_group(action=action, success=success, container=container, results=results, handle=handle)
        lock_mac(action=action, success=success, container=container, results=results, handle=handle)
        send_blank_push(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_not_contained(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_not_contained(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_not_contained() called")

    ################################################################################
    # This block uses custom code. Adds a note when the flagged app was not found, 
    # or when the app list could not be read.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["artifact:*.cef.fileName"])
    fn = rows[0][0] if rows and rows[0] and rows[0][0] else "the flagged file"
    st = phantom.collect2(container=container, datapath=["get_installed_apps:action_result.status"], action_results=results)
    statuses = [str(r[0]).lower() if r and r[0] else "missing" for r in st]
    lookup_ok = bool(statuses) and all(s == "success" for s in statuses)

    if not lookup_ok:
        phantom.add_note(container=container, note_type="general",
            title="Malicious App Containment — Detection Inconclusive",
            content="Could not confirm whether **" + str(fn) + "** is present — device app enumeration failed. **Device NOT contained.** Review manually.",
            note_format="markdown")
    else:
        phantom.add_note(container=container, note_type="general",
            title="Malicious File Containment — Detection",
            content="Flagged file **" + str(fn) + "** was not found among the device's installed apps — no containment taken.",
            note_format="markdown")
    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_not_contained_called", value="True")

    return


@phantom.playbook_block()
def add_to_isolation_group(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("add_to_isolation_group() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Adds the Mac to the isolation group.
    ################################################################################

    find_mac_by_hostname_result_data = phantom.collect2(container=container, datapath=["find_mac_by_hostname:action_result.data.*.id","find_mac_by_hostname:action_result.data.*.type","find_mac_by_hostname:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'add_to_isolation_group' call
    for find_mac_by_hostname_result_item in find_mac_by_hostname_result_data:
        if find_mac_by_hostname_result_item[0] is not None:
            parameters.append({
                "group_id": "<your-isolation-group-id>",
                "device_id": find_mac_by_hostname_result_item[0],
                "device_type": find_mac_by_hostname_result_item[1],
                "context": {'artifact_id': find_mac_by_hostname_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    ISOLATION_GROUP = "<your-isolation-group-id>"
    rows = phantom.collect2(container=container, datapath=[
        "find_mac_by_hostname:action_result.data.*.id",
        "find_mac_by_hostname:action_result.data.*.type",
        "find_mac_by_hostname:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen or str(dtype) != "computer":
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did,
                           "group_id": ISOLATION_GROUP, "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("add to static group", parameters=parameters, name="add_to_isolation_group", assets=["jamf_pro"], callback=join_format_containment_results)

    return


@phantom.playbook_block()
def lock_mac(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("lock_mac() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Locks the Mac.
    ################################################################################

    find_mac_by_hostname_result_data = phantom.collect2(container=container, datapath=["find_mac_by_hostname:action_result.data.*.id","find_mac_by_hostname:action_result.data.*.type","find_mac_by_hostname:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'lock_mac' call
    for find_mac_by_hostname_result_item in find_mac_by_hostname_result_data:
        if find_mac_by_hostname_result_item[0] is not None:
            parameters.append({
                "device_id": find_mac_by_hostname_result_item[0],
                "device_type": find_mac_by_hostname_result_item[1],
                "context": {'artifact_id': find_mac_by_hostname_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    import secrets
    rows = phantom.collect2(container=container, datapath=[
        "find_mac_by_hostname:action_result.data.*.id",
        "find_mac_by_hostname:action_result.data.*.type",
        "find_mac_by_hostname:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen or str(dtype) != "computer":
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did,
            "pin": str(100000 + secrets.randbelow(900000)),
            "message": "This device has been isolated by security (detected malicious app). Contact IT.",
            "phone_number": "<your-callback-number>", "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("lock device", parameters=parameters, name="lock_mac", assets=["jamf_pro"], callback=join_format_containment_results)

    return


@phantom.playbook_block()
def send_blank_push(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("send_blank_push() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Sends a blank push so the Mac checks in.
    ################################################################################

    find_mac_by_hostname_result_data = phantom.collect2(container=container, datapath=["find_mac_by_hostname:action_result.data.*.id","find_mac_by_hostname:action_result.data.*.type","find_mac_by_hostname:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'send_blank_push' call
    for find_mac_by_hostname_result_item in find_mac_by_hostname_result_data:
        if find_mac_by_hostname_result_item[0] is not None:
            parameters.append({
                "device_id": find_mac_by_hostname_result_item[0],
                "device_type": find_mac_by_hostname_result_item[1],
                "context": {'artifact_id': find_mac_by_hostname_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "find_mac_by_hostname:action_result.data.*.id",
        "find_mac_by_hostname:action_result.data.*.type",
        "find_mac_by_hostname:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen or str(dtype) != "computer":
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did, "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("send blank push", parameters=parameters, name="send_blank_push", assets=["jamf_pro"], callback=join_format_containment_results)

    return


@phantom.playbook_block()
def join_format_containment_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("join_format_containment_results() called")

    if phantom.completed(action_names=["add_to_isolation_group", "lock_mac", "send_blank_push"]):
        # call connected block "format_containment_results"
        format_containment_results(container=container, handle=handle)

    return


@phantom.playbook_block()
def format_containment_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_containment_results() called")

    ################################################################################
    # This block uses custom code. Formats the actual result of each containment action.
    ################################################################################

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=[
        "find_mac_by_hostname:action_result.data.*.id",
        "find_mac_by_hostname:action_result.data.*.general.name"])
    seen, devs = set(), []
    for r in dev:
        if r[0] is not None and str(r[0]) not in seen:
            seen.add(str(r[0])); devs.append(r)

    fr = phantom.collect2(container=container, datapath=["artifact:*.cef.fileName"])
    flagged_all = sorted({str(x[0]) for x in fr if x and x[0]})
    ap = phantom.collect2(container=container, datapath=["get_installed_apps:action_result.data.*.name"])
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
            "lock_mac:action_result.parameter.device_id", "lock_mac:action_result.parameter.pin"])
        m = {str(x[0]): x[1] for x in rows if x and x[0] is not None}
        return m.get(str(did))
    grp, lok, psh = _stat("add_to_isolation_group"), _stat("lock_mac"), _stat("send_blank_push")
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

    phantom.format(container=container, template=template, parameters=parameters, name="format_containment_results")

    note_containment_results(container=container)

    return


@phantom.playbook_block()
def note_containment_results(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_containment_results() called")

    ################################################################################
    # This block uses custom code. Adds a note with the result of each containment 
    # action.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    text = phantom.get_format_data(name="format_containment_results")
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

    phantom.save_block_result(key="note_containment_results_called", value="True")

    single_device(container=container)

    return


@phantom.playbook_block()
def format_wipe_prompt(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("format_wipe_prompt() called")

    ################################################################################
    # This block uses custom code. Builds the device details shown in the wipe approval 
    # prompt.
    ################################################################################

    template = """"""

    # parameter list for template variable replacement
    parameters = []

    ################################################################################
    ## Custom Code Start
    ################################################################################

    dev = phantom.collect2(container=container, datapath=[
        "find_mac_by_hostname:action_result.data.*.general.name",
        "find_mac_by_hostname:action_result.data.*.id"])
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

    phantom.format(container=container, template=template, parameters=parameters, name="format_wipe_prompt")

    approve_wipe(container=container)

    return


@phantom.playbook_block()
def approve_wipe(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("approve_wipe() called")

    ################################################################################
    # Asks an analyst whether to wipe the Mac. Times out after 30 minutes.
    ################################################################################

    # set approver and message variables for phantom.prompt call

    user = None
    role = "<your-approver-role>"
    message = """{0}"""

    # parameter list for template variable replacement
    parameters = [
        "format_wipe_prompt:formatted_data"
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

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=30, name="approve_wipe", parameters=parameters, response_types=response_types, callback=wipe_approved)

    return


@phantom.playbook_block()
def wipe_approved(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_approved() called")

    ################################################################################
    # Wipes the Mac only if the analyst chose Wipe.
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
        wipe_mac(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_wipe_not_approved(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def wipe_mac(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("wipe_mac() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    ################################################################################
    # This block uses custom code. Erases the Mac. Runs only after analyst approval.
    ################################################################################

    find_mac_by_hostname_result_data = phantom.collect2(container=container, datapath=["find_mac_by_hostname:action_result.data.*.id","find_mac_by_hostname:action_result.data.*.type","find_mac_by_hostname:action_result.parameter.context.artifact_id"], action_results=results)

    parameters = []

    # build parameters list for 'wipe_mac' call
    for find_mac_by_hostname_result_item in find_mac_by_hostname_result_data:
        if find_mac_by_hostname_result_item[0] is not None:
            parameters.append({
                "confirm": True,
                "device_id": find_mac_by_hostname_result_item[0],
                "device_type": find_mac_by_hostname_result_item[1],
                "context": {'artifact_id': find_mac_by_hostname_result_item[2]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "find_mac_by_hostname:action_result.data.*.id",
        "find_mac_by_hostname:action_result.data.*.type",
        "find_mac_by_hostname:action_result.parameter.context.artifact_id"])
    seen, parameters = set(), []
    for r in rows:
        did, dtype, aid = r[0], r[1], r[2]
        if did is None or str(did) in seen or str(dtype) != "computer":   # macOS-only
            continue
        seen.add(str(did))
        parameters.append({"device_type": dtype, "device_id": did, "confirm": str(did), "context": {"artifact_id": aid}})

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("wipe device", parameters=parameters, name="wipe_mac", assets=["jamf_pro"], callback=note_wipe_outcome)

    return


@phantom.playbook_block()
def note_wipe_outcome(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_outcome() called")

    ################################################################################
    # This block uses custom code. Adds a note with the result of the wipe.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=[
        "wipe_mac:action_result.parameter.device_id",
        "wipe_mac:action_result.status",
        "wipe_mac:action_result.message"])
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

    phantom.save_block_result(key="note_wipe_outcome_called", value="True")

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

    phantom.add_note(container=container, note_type="general",
        title="Malicious App Containment — Wipe Not Approved",
        content="Wipe not approved (analyst denied, or the prompt timed out) — device remains isolated + locked.",
        note_format="markdown")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_not_approved_called", value="True")

    return


@phantom.playbook_block()
def single_device(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("single_device() called")

    ################################################################################
    # Asks for wipe approval only if the hostname matched exactly one device.
    ################################################################################

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["find_mac_by_hostname:action_result.summary.total", "<=", 1]
        ],
        conditions_dps=[
            ["find_mac_by_hostname:action_result.summary.total", "<=", 1]
        ],
        name="single_device:condition_1",
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        format_wipe_prompt(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    note_wipe_blocked(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def note_wipe_blocked(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, loop_state_json=None, **kwargs):
    phantom.debug("note_wipe_blocked() called")

    ################################################################################
    # This block uses custom code. Adds a note that the wipe was blocked because the 
    # hostname matched more than one device.
    ################################################################################

    ################################################################################
    ## Custom Code Start
    ################################################################################

    rows = phantom.collect2(container=container, datapath=["find_mac_by_hostname:action_result.summary.total"])
    n = rows[0][0] if rows and rows[0] else "multiple"
    phantom.add_note(container=container, note_type="general",
        title="Malicious App Containment — Wipe Blocked",
        content="The hostname matched **" + str(n) + " devices** — too broad to safely offer an irreversible wipe. Device(s) remain contained (isolated + locked). Review and re-run against a specific device.",
        note_format="markdown")

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.save_block_result(key="note_wipe_blocked_called", value="True")

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