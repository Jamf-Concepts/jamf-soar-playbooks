# Jamf SOAR Playbooks

A collection of **Splunk SOAR playbook templates** for the Jamf SOAR connector
app. These playbooks orchestrate the connector's actions (resolve a device,
contain it, enrich, notify, gate on an analyst, and — only then — take a
destructive step) into ready-to-adapt incident-response flows.

This repo is **not** a connector. It holds reusable playbooks that *call* the
Jamf SOAR app's actions. The companion connector app lives in
[`Jamf-Concepts/jamf-splunk-soar`](https://github.com/Jamf-Concepts/jamf-splunk-soar).

> Status: **Pre-release / private development.** Governance skeleton only —
> no playbooks have been built yet.

---

## Why this exists

The Jamf SOAR connector app gives you the building blocks — `lock device`,
`add to static group`, `wipe device`, and so on. But a building block isn't a
response. Analysts still have to wire those actions together, decide the order,
add the approval gates, and connect the enrichment and notification steps.

This repo ships those flows as **templates** so a customer doesn't start from a
blank canvas. Each playbook is a vetted chain that already encodes the safety
rules (most importantly: never auto-wipe — see below).

---

## Prerequisites

These playbooks do nothing on their own. To use them you need:

| Requirement | Detail |
|-------------|--------|
| **Splunk SOAR** | Cloud or On-prem. Playbooks run inside SOAR. |
| **Jamf SOAR connector app** | Installed in SOAR from [`Jamf-Concepts/jamf-splunk-soar`](https://github.com/Jamf-Concepts/jamf-splunk-soar). The playbooks reference its actions by app + action name. |
| **A configured Jamf asset** | An asset wired to the app with your Jamf Pro base URL + OAuth credentials. Without a working asset the actions have nothing to call. |

If the app isn't installed or the asset isn't configured, the playbooks will
fail to resolve their action blocks on import.

---

## Distribution model

Splunk SOAR manages playbooks in **git-backed repositories**, not inside the
connector app's `.tgz`. There are two supported ways to get these playbooks
into SOAR:

1. **Source-control repository (recommended).** In SOAR go to
   **Administration → Source Control** and add this repo as a source-control
   repository. SOAR clones it and keeps the playbooks in sync as the repo
   updates.
2. **`.tgz` export import.** Import an individual playbook from a `.tgz` export
   via the Playbooks UI. Use this for one-off sharing or air-gapped installs.

> Note: `.tgz` playbook exports can embed environment-specific details (asset
> names, group IDs, label values). Scrub those before sharing an export — see
> `CLAUDE.md` Gotchas.

---

## Planned playbook templates

> The first template has landed (in review). Each lands via its own issue
> (`[playbook]` prefix) and PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

Every template follows the same backbone: **resolve device → contain →
enrich / notify → (timer) → analyst approval gate → destructive step.**

| Scenario | Status | Notes |
|----------|--------|-------|
| **Device enrichment & triage (read-only)** | **In review (PR #9)** | Reusable enrichment building block: resolve device → enrich → write a summary note. Ships as an Input sub-playbook (`Jamf - Device Enrichment (Input)`) the other templates call, plus a triage wrapper. No destructive step, so no approval gate. |
| Lost / stolen device | Planned | Resolve device, lock + contain, notify, hold for analyst approval, then erase as a last resort. |
| Compromised user | Planned | Contain the user's enrolled devices, enrich with identity context, gate before destructive action. |
| Identity-provider (IdP) breach | Planned | Broad containment across affected accounts/devices; approval gate before any mass group change. |
| Malicious file | Planned | Locate affected device(s), contain, enrich the file verdict, remediate behind a gate. |

---

## Installation & usage

> Placeholder — step-by-step import/sync instructions will be added once the
> first playbook (lost / stolen device) lands.

High-level shape:

1. Install and configure the [Jamf SOAR connector app](https://github.com/Jamf-Concepts/jamf-splunk-soar)
   in SOAR, including a working Jamf asset.
2. Add this repo under **Administration → Source Control** (or import a
   playbook `.tgz`).
3. Point each playbook's action blocks at your configured Jamf asset.
4. Set your environment-specific config (asset name, target group names,
   timer durations) at the marked configuration points in the playbook.

---

## Links

- **Companion connector app** — <https://github.com/Jamf-Concepts/jamf-splunk-soar>
- **Splunk SOAR playbooks & source control** — <https://docs.splunk.com/Documentation/SOARonprem/current/Playbook/Overview>
- **Jamf Developer docs** — <https://developer.jamf.com/jamf-pro/docs>

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a playbook, the
issue-first workflow, and the safety rules. Non-engineers (PMs, SEs) are
welcome to propose scenarios — there's a dedicated issue template for it.
