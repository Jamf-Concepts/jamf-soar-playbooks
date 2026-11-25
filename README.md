# Jamf SOAR Playbooks

A collection of **Splunk SOAR playbook templates** for the Jamf SOAR connector
app. These playbooks orchestrate the connector's actions (resolve a device,
contain it, enrich, notify, gate on an analyst, and — only then — take a
destructive step) into ready-to-adapt incident-response flows.

This repo is **not** a connector. It holds reusable playbooks that *call* the
Jamf SOAR app's actions. The companion connector app is documented at
[Jamf-Concepts/jamf-splunk-soar](https://github.com/Jamf-Concepts/jamf-splunk-soar).

> Status: **Pre-release / private development.** Early template PRs are merged
> or in review — see the status column in the table below.

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
| **Jamf SOAR connector app** | Installed in SOAR — see the [connector docs](https://github.com/Jamf-Concepts/jamf-splunk-soar) (coming to Splunkbase at release). The playbooks reference its actions by app + action name. |
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

> Each template lands via its own issue (`[playbook]` prefix) and PR — status
> is per row below. See [CONTRIBUTING.md](CONTRIBUTING.md).

Every template follows the same backbone: **resolve device → contain →
enrich / notify → (timer) → analyst approval gate → destructive step.**

| Scenario | Status | Notes |
|----------|--------|-------|
| Device enrichment & triage (read-only) | Merged (PR #9) | Reusable enrichment building block: resolve device → enrich → write a summary note. Ships as an Input sub-playbook (`Jamf - Device Enrichment (Input)`) the other templates call, plus a triage wrapper. No destructive step, so no approval gate. |
| Compliance drift / MDM tamper | Merged (PR #10) | Correct-first: redeploy the management framework + force a check-in, re-check compliance, and only contain (quarantine + lock) if still non-compliant. Wipe is gated behind an analyst approval prompt. |
| FileVault key / recovery access (macOS) | In review (PR #11) | Resolve a Mac by serial, retrieve the FileVault recovery key + context, secure (recovery lock + lock), then erase behind an analyst approval gate. |
| Compromised user | In review (PR #12) | Resolve the user's device(s) by username; contain each (per-platform quarantine group + lock + blank push) with honest per-device status; then an analyst prompt that enumerates the whole fleet before a gated wipe. |
| Lost / stolen device | Merged (PR #16) | Resolve a device by serial, branch on device type (mobile → enable lost mode / computer → lock device), write a containment note, hold at an analyst approval gate, then wipe **only** on approval. Decline / timeout / no-device paths just add a note. |
| **Identity-provider (IdP) breach** | **In review (PR #15)** | Bulk quarantine (add to group + lock + blank push) across the affected device set, behind a single **up-front** batched approval that discloses the full scope; hard batch-size cap; **bulk wipe excluded**. |
| Malicious app / file (macOS) | In review (#3) | Resolve by device name, confirm the flagged app is actually installed, isolate (static group) + lock + blank push with honest per-action status, then an analyst gate before wipe. One detection per container (guarded). |

---

## Installation & usage

> Detailed, per-playbook import/sync steps are still being written. The
> high-level shape below applies to every template.

High-level shape:

1. Install and configure the Jamf SOAR connector app in SOAR (see the
   [connector docs](https://github.com/Jamf-Concepts/jamf-splunk-soar); coming to
   Splunkbase at release), including a working Jamf asset.
2. Add this repo under **Administration → Source Control** (or import a
   playbook `.tgz`).
3. Point each playbook's action blocks at your configured Jamf asset.
4. Set your environment-specific config (asset name, target group names,
   timer durations) at the marked configuration points in the playbook.

---

## Links

- **Companion connector app (docs)** — <https://github.com/Jamf-Concepts/jamf-splunk-soar>
- **Splunk SOAR playbooks & source control** — <https://docs.splunk.com/Documentation/SOARonprem/current/Playbook/Overview>
- **Jamf Developer docs** — <https://developer.jamf.com/jamf-pro/docs>

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to propose a playbook, the
issue-first workflow, and the safety rules. Non-engineers (PMs, SEs) are
welcome to propose scenarios — there's a dedicated issue template for it.
