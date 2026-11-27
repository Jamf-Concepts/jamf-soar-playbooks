# Contributing to jamf-soar-playbooks

Thanks for helping build the Jamf SOAR playbook library. This guide covers how
to propose a playbook, file issues, and submit pull requests. Engineers and
non-engineers are both welcome — if you can describe an incident-response
scenario in plain English, you can propose a playbook.

---

## Opening a GitHub issue

All work on this repo is tracked through GitHub Issues. **Propose before you
build** — open an issue first so the scenario gets discussed and the safety
review happens before anyone wires up action blocks. Search existing issues so
you don't duplicate one.

### For non-engineers (PMs, SEs, sales engineers)

You don't need to know the SOAR playbook editor or the Jamf API. Use the
**New Playbook** template and describe the scenario:

- What triggers the playbook (e.g. "a device is reported lost or stolen").
- What should happen, step by step, in plain English.
- Where a human should have to approve before anything destructive happens.

A maintainer will fill in the action chain, datapaths, and technical fields
during triage.

### For engineers

Use the same template, but fill in the technical fields yourself: the ordered
chain of Jamf app actions, the decision/approval gates, the datapaths wired
between steps, and any external tools (Slack, ticketing, IdP).

### Issue naming conventions

Use a prefix so the backlog is scannable:

| Prefix | Use for | Example |
|--------|---------|---------|
| `[playbook]` | A new playbook template | `[playbook] Lost or stolen device` |
| `[bug]` | A defect in an existing playbook | `[bug] Approval gate skipped on timeout` |
| `[research]` | An open question or spike | `[research] Can SOAR sync nested playbooks via git?` |
| `[docs]` | A documentation change | `[docs] Document source-control sync steps` |

Keep the title under ~70 characters and describe the *scenario / outcome*, not
the implementation (`[playbook] Lost or stolen device`, not
`[playbook] Add 6 action blocks and a prompt`).

### Labels

Apply labels when you file. Maintainers will adjust during triage.

- **Status** — `backlog`, `in-progress`, `in-review`, `done`
- **Type** — `playbook`, `bug`, `research`, `docs`

The **New Playbook** template applies `playbook, backlog` for you.

---

## How playbooks are managed

Playbooks in this repo are **git-synced into SOAR**. A customer adds this repo
under **Administration → Source Control** and SOAR keeps the playbooks in sync,
or they import a `.tgz` export. Because the repo *is* the source of truth, a
merged PR can change what's running in a customer's SOAR instance once they
sync — review accordingly.

### Keep templates generic

These are **templates**, not one customer's deployment. Do not hardcode
environment specifics:

- Action blocks use the generic asset name `jamf_pro` (the app name in lowercase with
  underscores, which Splunk's community playbook checks require). Never a real
  deployment's asset name.
- No real static-group names or IDs — call out where the customer sets theirs.
- No tenant URLs, label values, or analyst email addresses.

Mark each spot a customer must configure so it's obvious what to change.

### Safety rule (non-negotiable): analyst-in-the-loop

**Destructive steps must sit behind an analyst approval gate. Never fully
automate a wipe, erase, or mass group change.** Every destructive action in a
playbook must be preceded by a human-approval prompt. This is not optional and
a PR that automates a destructive step end-to-end will be rejected. (A
competitor once mass-unenrolled thousands of devices through an unattended
automation — we do not repeat that.)

---

## Submitting a pull request

1. **Open an issue first.** Every PR should reference an issue. This keeps the
   backlog accurate and ensures the scenario got a safety review.
2. **Create a feature branch off `main`:**
   ```
   git checkout -b playbook/lost-stolen-device
   git checkout -b bug/123-approval-gate
   git checkout -b docs/source-control-sync
   ```
3. **One playbook per PR.** Don't bundle multiple templates. Keep PRs small
   enough to review properly.
4. **Open the PR** with:
   - A title using the same prefix scheme as issues.
   - A body that links the issue (`Closes #42`), describes the scenario, lists
     the action chain, and confirms the approval gate is present on any
     destructive step.
   - The same labels as the linked issue.
5. **Move the issue to `in-review`** on the project board when the PR is open.
6. **Address review comments** in new commits — don't force-push during review.
7. Once approved, a maintainer will squash-merge and move the issue to `done`.

---

## Style notes

- Keep playbook and block names descriptive and scenario-led.
- No secrets, tenant URLs, or asset configs in commits. The `.gitignore`
  catches the common ones (`.env`, `*.asset.json`, `client_secret*.json`,
  `*.tgz`) but the responsibility is still yours.
- Scrub `.tgz` exports of environment specifics before committing or sharing.
