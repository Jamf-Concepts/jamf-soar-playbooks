# Changelog — jamf-soar-playbooks

- 2026-07-08 — Docs now point to the connector's public documentation instead of its internal repo.
- 2026-07-07 — Added playbook: Malicious App or File Containment (macOS). Isolates and locks a Mac confirmed to have a flagged app installed; wipe requires analyst approval.
- 2026-07-07 — Added playbook: Lost or Stolen Device. Locks computers / enables Lost Mode on mobile devices; wipe requires analyst approval.
- 2026-07-07 — Added playbook: Compromised User Device Sweep. Quarantines and locks every device tied to a compromised user; wipe requires analyst approval.
- 2026-07-07 — Added playbook: IdP Breach Bulk Quarantine. Mass-quarantines devices affected by an identity-provider breach under a single up-front approval; does not wipe.
- 2026-07-06 — Added playbook: FileVault Recovery Access (macOS). Retrieves FileVault recovery access and secures a Mac; wipe requires analyst approval.
- 2026-07-06 — Added playbook: Compliance Drift and MDM Tamper Remediation. Attempts to re-correct a non-compliant device before quarantining it; wipe requires analyst approval.
- 2026-07-06 — Added playbook: Device Enrichment and Triage. Looks up a device and reports its status; read-only, no destructive actions.
- 2026-06-08 — Repo created.
