---
name: New Playbook
about: Propose a Splunk SOAR playbook template that orchestrates the Jamf SOAR app's actions
title: "[playbook] <scenario, e.g. Lost or stolen device>"
labels: playbook, backlog
assignees: ''
---

<!--
  Proposing as a non-engineer? You only need the first three sections
  ("Scenario / trigger", "Plain-English description", and "Customer-config
  points" if you know them). A maintainer will fill in the action chain,
  datapaths, and technical fields during triage. Don't delete the empty
  sections — leave them so the next person can complete them.
-->

## Scenario / trigger

<!-- What incident does this respond to, and what kicks it off? Example:
"A device is reported lost or stolen; analyst (or an alert) starts the
playbook." -->

## Plain-English description

<!-- Walk through what should happen, step by step, in plain English. Call out
where a human must approve before anything destructive happens. -->

---

## Technical fields (engineering fills in during triage)

### Action chain
<!-- The ordered list of Jamf SOAR app actions this playbook calls. Follow the
backbone: resolve device -> contain -> enrich/notify -> (timer) -> approval gate
-> destructive step. Reference actions by app + action name. -->

1. <!-- e.g. resolve device (Jamf app: `get computer detail`) -->
2.
3.

### Decision / approval gates
<!-- Where the playbook branches or pauses for a human. EVERY destructive step
(wipe/erase, mass group change) MUST be preceded by an analyst approval prompt —
this is non-negotiable. -->

- [ ] Analyst approval prompt present before every destructive step

### Datapaths between steps
<!-- How output from one block feeds the next. Example: step 1
`action_result.data.*.device_id` (contains: `jamf device id`) -> step 2 input
`device_id`. -->

| From step | Output datapath | contains | Into step | Input param |
|-----------|-----------------|----------|-----------|-------------|
|  |  |  |  |  |

### External tools used
<!-- Anything outside the Jamf app: Slack / chat, ticketing (e.g. Jira,
ServiceNow), IdP (e.g. Okta, Entra). Note the app/connector each needs. -->

- [ ] Slack / chat notification
- [ ] Ticketing
- [ ] Identity provider (IdP)
- [ ] Other:

### Customer-config points
<!-- Everything a customer must set when they adopt this template. Keep the
template generic — no real values here. -->

- Jamf asset name: `<your-jamf-asset>`
- Target static group(s): `<your-group-name>`
- Timer / hold duration:
- Approver(s) / role for the approval prompt:
- Notification channel:

### Acceptance criteria

- [ ] Playbook imports cleanly into SOAR (source-control sync or `.tgz`)
- [ ] Runs against the `jamf-splunk-soar` app with a configured Jamf asset
- [ ] Action blocks resolve by app + action name; datapaths wired correctly
- [ ] **Analyst approval gate present before every destructive step**
- [ ] No hardcoded environment specifics — placeholders only, config points marked
- [ ] `.tgz` export (if committed) scrubbed of environment specifics
- [ ] Documented (README "Planned playbook templates" / usage updated)

### Dependencies / blockers
<!-- Other issues this depends on, app actions that don't exist yet (file them
in `jamf-splunk-soar`), or external connector setup needed. -->
