# Changelog — jamf-soar-playbooks

- 2026-11-26 — All eight playbooks ready for Splunk's community playbook checks: every block has a name, description and note; decision paths are labelled; action blocks use the Jamf Pro 2.0.0 app and the `jamf_pro` asset; each playbook has a canvas screenshot. Lost or Stolen Device, Compliance Drift and Malicious App now report a wipe or lookup result from one block instead of a decision plus two notes, keeping each within Splunk's 20-block limit. Behaviour is unchanged for a single matched device. With several matches, the wipe-outcome notes now say "queued" only if every wipe queued and otherwise list each device's result, and Malicious App reports "Detection Inconclusive" if any app lookup failed. The IdP Breach notes get back their full guidance text, lock PINs come from `secrets`, and the release-prep workflow now points sub-playbook calls at `community/<renamed playbook>`.
- 2026-11-25 — FileVault Recovery Access (macOS): added a description and setup notes in SOAR's format; design notes moved to docs/design-notes/.
- 2026-11-25 — Lost or Stolen Device: added a description and setup notes in SOAR's format; design notes moved to docs/design-notes/.
- 2026-07-08 — Docs now point to the connector's public documentation instead of its internal repo.
- 2026-07-07 — Added playbook: Malicious App or File Containment (macOS). Isolates and locks a Mac confirmed to have a flagged app installed; wipe requires analyst approval.
- 2026-07-07 — Added playbook: Lost or Stolen Device. Locks computers / enables Lost Mode on mobile devices; wipe requires analyst approval.
- 2026-07-07 — Added playbook: Compromised User Device Sweep. Quarantines and locks every device tied to a compromised user; wipe requires analyst approval.
- 2026-07-07 — Added playbook: IdP Breach Bulk Quarantine. Mass-quarantines devices affected by an identity-provider breach under a single up-front approval; does not wipe.
- 2026-07-06 — Added playbook: FileVault Recovery Access (macOS). Retrieves FileVault recovery access and secures a Mac; wipe requires analyst approval.
- 2026-07-06 — Added playbook: Compliance Drift and MDM Tamper Remediation. Attempts to re-correct a non-compliant device before quarantining it; wipe requires analyst approval.
- 2026-07-06 — Added playbook: Device Enrichment and Triage. Looks up a device and reports its status; read-only, no destructive actions.
- 2026-06-08 — Repo created.
