# CLAUDE.md

Splunk SOAR playbook templates (`.py` + `.json` pairs in `playbooks/`) that call the
actions of the `jamf-splunk-soar` connector app. This repo is not a connector. The
README is the reference for what each template does and what it needs.

## Rules

- **Never auto-wipe.** Every wipe/erase sits behind an analyst approval prompt that is
  reached only on an explicit yes. Do not remove or bypass that gate.
- **Keep templates generic.** Every customer value is a `<...>` placeholder: no real
  asset names, group IDs, tenant URLs, approver names, or secrets. Scrub `.tgz`/export
  files before committing; they embed asset names and group IDs.
- **Work on a feature branch and open a PR.** Never commit to `main`.
- **`git fetch` before editing a playbook on a shared branch.** SOAR source control
  pushes VPE saves to the same branches, so a local checkout can be badly stale.

## Gotchas

- Playbooks reference connector actions by **app + action name** and chain on their
  output datapaths. Renaming an action or changing its datapaths in the connector breaks
  the playbooks.
- Required Jamf capabilities per action are in the connector repo's
  `docs/configuring-jamf-api-access.md`. `lock device` needs
  `destructive-device-actions:execute`, the same as `wipe device`.
- `wipe device` requires `confirm` to equal the target `device_id` string exactly; a
  truthy flag is rejected (`WIPE_NOT_CONFIRMED`). Wire `confirm` to the same datapath
  as `device_id`.
- The Input sub-playbook `Jamf - Device Enrichment (Input)` takes `device_id` and
  `device_type` as paired, equal-length lists and `zip`s them. SOAR would otherwise
  loop over every combination and hit the wrong devices.
- Branches that run one-or-the-other must not reconverge on a shared block: SOAR inserts
  a join that waits for both and the tail never runs. Give each branch its own tail
  (see `Jamf - Lost or Stolen Device`).
- A `/` in a playbook name becomes a directory separator on export. Avoid it.
