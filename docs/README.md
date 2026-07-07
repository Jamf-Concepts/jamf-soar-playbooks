# Docs Changelog — jamf-soar-playbooks

Plain-English summary of every change made to the repo. Newest entries at the
top. Mirrors the technical change history in `CLAUDE.md` but written for
people who aren't deep in the playbooks.

---

## 2026-07-07 — Compromised User Device Sweep: review rework (PR #12)

Reworked after review (Sarah + Amanda) to fix the destructive spine. When a user
is flagged compromised, it finds their device(s) and contains each — adds it to a
**per-platform** quarantine group, locks it (Macs get a unique 6-digit PIN, shown
in the note), and sends a blank push. The containment note now reports the **real
per-device outcome** (✅ / failed) instead of claiming success unconditionally.

Before any wipe it pauses for an analyst, and the prompt now **enumerates every
device that would be erased** ("Wipe ALL N devices"), flagging any that failed
containment — so the approval scope matches what actually executes. Nothing wipes
without that explicit approval; a denial *or a timeout* routes to a clear note and
never wipes. (The wipe was previously inert — it sent `confirm: true`, which the
connector rejects; it's now wired to `confirm == device_id`, so it works — which
is exactly why the fleet-scope prompt had to land in the same change.)

Adopt it — set: `<your-jamf-asset>`, the per-platform quarantine groups
(`<your-computer-suspended-group-id>` / `<your-mobile-suspended-group-id>`), the
lock callback number (`<your-callback-number>`), and the approver role
(`<your-approver-role>`). It reads the username from `sourceUserName`.

## 2026-07-06 — FileVault Recovery Access: review fixes (leaked secret redacted, approval gate routing)

Two fixes from the review of the FileVault Recovery Access playbook (PR #11), plus a re-sync
with `main`:

- **Removed a real secret left in the docs.** The maintainer notes (`CLAUDE.md`) still spelled out
  a real recovery-lock password, a device serial, and other test values that had already been
  swapped for placeholders everywhere else. They're now described without printing the values.
  Because the password was also committed to git history, rotating it on the Jamf side is tracked
  as a follow-up (**issue #14**) — the connector repo is confirmed clean, and for a private repo
  rotating the credential is the accepted mitigation (no history rewrite needed).
- **Fixed the approval-prompt routing.** The "approve the wipe?" prompt was pointed at a *user* slot
  holding a placeholder, which wouldn't resolve to a real person on import — so the safety gate
  could fail to reach anyone. It now routes by **role**, so on import you just point it at your
  security-analyst role.

Also merged in the Compliance Drift template (now landed on `main`) so the shared docs line up —
that template is now **merged**, FileVault is **in review**.

## 2026-07-06 — v3: re-review fixes (false "wipe queued" note, no-serial guard, prompt wording)

Ron's re-review confirmed every prior fix landed and flagged one real bug plus two cheap items;
all fixed, re-imported, and re-run (green):

- **No more false "device is being erased" note.** Previously the "ERASE queued" note posted even
  if the wipe *failed* (e.g. an HTTP 500 on a user-enrolled Mac). Now a `wipe_ok` check only posts
  it on success; a failed wipe writes a "NOT queued — device still quarantined + locked, manual
  intervention required" note instead.
- **No silent dead-end on a missing serial.** If the triggering event has no serial number, the
  playbook now stops with a clear note instead of quietly doing nothing.
- **Clearer approval wording.** The wipe prompt now says quarantine and lock were *queued* (a lock
  is an async command — queued, not confirmed applied) rather than "completed successfully," so the
  analyst isn't misled before authorizing an irreversible erase.
- Dropped a stray erase PIN that modern Macs don't use.

Re-imported to SOAR (validated clean) and re-run against the test device — same correct healthy
path as before, with the new serial guard passing through as expected. The two new failure-path
notes only fire on a failed wipe / missing serial, which the healthy test device doesn't produce.

## 2026-07-06 — Renamed the playbook to the standard `Jamf - <Scenario>` format

Renamed the files from `jamf_compliance_drift_remediation.*` to
**`Jamf - Compliance Drift and MDM Tamper Remediation.*`** so they match the naming standard
(and the sibling templates like `Jamf - FileVault Recovery Access (macOS)`) and the name shown
in SOAR. The scenario had a slash ("Compliance Drift / MDM Tamper"), which can't go in a
filename, so it's reworded to "and". No behaviour changed — same graph and logic, new name.

## 2026-07-06 — v2 rebuild: all review logic fixed, validated, and run live (green)

Rebuilt the playbook to fix every logic issue the reviews raised, imported it into SOAR, and
**ran it live against the test device — it passed.**

What changed in the playbook (now 19 steps, up from 12):
- **The wipe can now actually fire.** The erase's safety `confirm` value is now wired to the
  device's own ID (the connector demands they match) instead of a plain "true" that it always
  rejected.
- **It only escalates on a real "not compliant" answer.** Before, anything that wasn't a clean
  "compliant" could push toward containment. Now it acts only when the device is *positively*
  reported NON_COMPLIANT; compliant / unknown / no-data / failed-read all stop safely with a note.
- **It won't ask to wipe an uncontained device.** A new check confirms quarantine *and* lock both
  succeeded before the analyst is ever shown the wipe prompt.
- **A "no device found" early exit** and **a note on every ending** (no device, no drift,
  containment failed, wipe declined, wipe queued) so a run is never silent.
- Scoped to computers (the correction step is computer-only), which is now stated for adopters.

The live run (against the test Mac): looked up the device → redeployed management → sent a blank
push → **read compliance successfully** (this had been failing with a permissions error every
prior run; granting the *Read Device Compliance Information* privilege fixed it) → the device came
back with no compliance records, so it correctly **stopped with a "no containment taken" note**
instead of escalating. That exercises the device-found gate, the correction path, the now-working
compliance read, and the safe "no drift" path.

Still not exercised live: quarantine → lock → approval → wipe. The test tenant has no compliance
partner reporting on the device, so it never returns a NON_COMPLIANT result to drive that path;
the wipe fix is confirmed against the connector's rules but hasn't been fired on a real erase.

The committed files stay generic (placeholders only); the real test values used for the run live
only in a local test bundle that is never committed.

## 2026-07-06 — PR #10 deep-pass review: more doc-only fixes; logic still deferred

A second reviewer's deep pass (at head `1632612`) re-confirmed the logic findings and added a
few doc/graph-integrity ones. Verified each against the files, fixed the doc-only ones, left all
playbook-logic changes for the VPE session:

- **BUILD.md no longer teaches the broken wipe wiring (I6).** The block-11 row previously said
  `confirm` = "checkbox on / boolean True"; corrected it to wire `confirm` to the resolved
  device-id datapath (the connector requires `confirm == device_id`), with a prominent note that
  the committed files still carry the broken value and it must be fixed in the VPE before merge.
- **Walked back the "canonical export" claim (I7).** Confirmed the committed `.json`'s
  `is_compliant` node carries an editor warning (`"Reconfigure invalid datapath."`) and a
  hand-minted comparison key — the case-(d) guard was patched in outside a clean editor
  round-trip, so the graph is not import-clean. BUILD.md + CLAUDE.md now say so and call for a
  VPE re-open/re-export before merge.
- **Surfaced the computer-only scope for adopters (I8).** `playbooks/README.md` now warns that
  the template targets computers (redeploy is computer-only; quarantine omits `device_type`), so
  a mobile device gets half-applied containment until `device_type` branching is added.

Still deferred to the VPE + live re-verify: B1 (wire `confirm` to device_id), B2/I1 (positively
match NON_COMPLIANT; route UNKNOWN/None to manual review), I3 (gate wipe on containment success),
I4/I5 (device-found + wipe-declined/timeout notes), I8 wiring, and the approver-role placeholder.

## 2026-07-06 — PR #10 second review (Sarah): doc-only fixes; logic deferred

Sarah's review found two critical logic issues (C1 the wipe can't fire; C2 a failed compliance
read ends silently) plus several important ones. Those are **playbook-logic** changes that must
be made in the Visual Playbook Editor and re-verified live, so they are **deferred** — not fixed
in this pass. What *was* fixed here is doc-only, and only where verified against the connector
source:

- **Corrected wrong wipe-`confirm` guidance (C1).** Confirmed in `jamf_connector.py:1674-1680`
  that the connector requires `confirm` to *exactly equal the `device_id` string*. Our docs
  previously told maintainers to "change it to string `'true'`" — which still ≠ device_id and
  would never fire. Docs now record the real bug and the correct fix (wire `confirm` to the
  resolved device-id datapath) as a pending VPE edit.
- **Fixed the API-privilege table (I5).** `lock`, `wipe`, and `send blank push` all queue via
  `/api/v2/mdm/commands`, so they need the **v2 "Send MDM command information in Jamf Pro API"**
  privilege — not the Classic per-command privileges we'd listed; added the missing blank-push
  row. Verified against `jamf_connector.py:1576-1577`.
- **Walked back the "verified end-to-end" overclaim (I5).** The live run's `get compliance
  status` actually 403'd and only the wipe-*deny* path ran; corrected the two spots that implied
  a clean full pass.

The remaining findings (C1 code fix, C2, I1 positive NON_COMPLIANT match, I2 terminal-path
notes, I3 gate-on-containment-success, I4 device_type branching, approver-role placeholder) are
tracked for the next VPE session.

## 2026-07-06 — PR #10 review fixes (docs only)

Ron's review approved-with-changes; addressed all three items (no playbook logic changed):

- **Blocking — root `README.md` was out of sync.** It still said "no playbooks have been
  built yet" and its "Planned playbook templates" table didn't list this one. Flipped the
  status note and added a **Compliance drift / MDM tamper — In review (PR #10)** row.
- **Nit — enrichment stage noted as deferred.** `playbooks/README.md` now states the issue-#4
  enrichment step (`get configuration profiles` / `get extension attributes`) is intentionally
  left out pending the reusable enrichment engine in PR #9, and reiterates that `update
  inventory` is permanently dropped (connector rejects it for computers).
- **Nit — snake_case filename explained.** Added a one-line note that the on-disk filenames are
  `snake_case` on purpose (the `/` in a `Jamf - <Scenario>` name makes SOAR treat it as a
  subdirectory on export), while the display name inside SOAR still reads `Jamf - <Scenario>`.

---

## 2026-07-06 — First playbook merged: Device Enrichment & Triage (PR #9)

The first real playbook merged to `main` (PR #9, issue #5). It's **read-only** — it looks a
device up and writes a tidy summary note onto the case; it doesn't change anything, so there's
no approval gate needed.

It's built in two pieces on purpose:

- **`Jamf - Device Enrichment (Input)`** — the reusable "engine." Hand it a device and it gathers
  everything (device details, compliance, groups, installed apps, config profiles, local
  accounts, extension attributes), formats a summary, and hands it back. The other playbooks call
  this instead of each rebuilding the same lookups.
- **`Jamf - Device Enrichment and Triage`** — the entry point. It finds the device (by username),
  calls the engine, and writes the summary as a note on the case.

Things to know when adopting it:

- Set your Jamf asset where it says `<your-jamf-asset>`.
- After importing, re-point the wrapper's sub-playbook block to your copy of the engine (SOAR ties
  sub-playbooks to a specific repo; naming your Source Control repo `jamf-soar-playbooks` makes the
  built-in reference line up).
- It finds devices by **username** (`sourceUserName`); serial / name / MAC and mobile-only steps
  are planned next.
- If you call the enrichment engine directly, pass `device_id` and `device_type` as **paired,
  equal-length lists** — the engine assumes they line up and fails loudly if they don't.

*(Carried over into this branch during the rebase onto main.)*

---

## 2026-07-03 — Closed the "empty compliance read" edge case (#10)

The review found one real logic gap: if the compliance check ever came back "successful but
with no records," the playbook would have treated that as non-compliant and escalated to
quarantine + lock. Added a guard so a **success-with-zero-records** read now ends the run
safely instead. Escalation to containment now requires a genuine, present, non-compliant
result — a failed read, a permission-denied read, and an empty read all stop the flow.

Done in SOAR's editor and re-exported. (One hiccup: the editor kept dropping either the new
condition or the block's name between saves, so the final file was assembled from the good
export with the block name restored — the behaviour and wiring are unchanged.) The irreversible
wipe is still gated behind explicit analyst approval, untouched.

---

## 2026-07-03 — PR-review doc fixes (#10)

A final review pass before marking PR #10 ready caught three documentation problems (no
playbook logic changed):

- **Fixed a wrong claim about the wipe `confirm` value.** Earlier notes said SOAR's export
  stores `confirm` as a boolean. In fact the graph file (`.json`) stores it as the text
  `"true"`, and only SOAR's generated Python file uses a boolean. Corrected the docs and
  flagged that neither form has been tested on an actual wipe (we've never let one run).
- **Scrubbed real environment details** that had crept into the internal change log — a test
  device serial, real asset names, an internal host address, and a graph fingerprint — since
  this repo mirrors a public project. Replaced with generic phrasing.
- **Corrected the build sheet** so its decision-block instructions match the exact form the
  committed playbook uses, and fixed the approver setting (it ships as `Administrator`, not a
  placeholder). Also noted a known edge case: if the compliance check ever returns "success
  but no data," the current logic would still escalate — worth tightening when we learn the
  real non-compliant value.

---

## 2026-07-03 — Re-synced the Compliance Drift template from SOAR's canonical export (#4)

Opened the playbook in SOAR's Visual Playbook Editor, saved and **exported** it, and
replaced the repo's `.py` / `.json` with what SOAR actually produces. Why: the previous
`.json` had been hand-edited programmatically, so it wasn't byte-for-byte what the editor
generates. Now the repo holds SOAR's own canonical graph and code.

What this changed and what we checked:
- **Safety logic verified intact after the round-trip.** SOAR expresses the compliance
  decision as "if compliant *or* the read failed → stop; otherwise quarantine" — which is
  exactly our fail-safe: a failed / permission-denied compliance read still never escalates
  toward the wipe. The wipe still fires only on an explicit `Yes` at the approval prompt.
- **Scrubbed a leaked asset name.** SOAR's export baked in the real test-environment asset
  name; replaced every occurrence with the `<your-jamf-asset>` placeholder so the template
  stays generic.
- **The `.py` is now SOAR-generated**, so the hand-written helper and explanatory comments
  are gone (SOAR writes its own per-block boilerplate). Same behaviour, just SOAR's style.
- **About the integrity "hash":** SOAR stamps a hash over the graph, but that graph includes
  the asset name — and a shareable template must use a placeholder, not a real asset. So no
  committed hash can ever match a real deployment; SOAR recomputes it on import anyway. We
  therefore left the hash blank (the state we already proved imports cleanly), rather than
  ship a hash that wouldn't match the placeholder graph.

Net: the repo now mirrors SOAR's real output (layout, decision wiring, code style), with the
one unavoidable generic-template differences (placeholder asset, blank hash) clearly recorded.

---

## 2026-07-02 — PR review fixes on the Compliance Drift template (#4)

Ran a full multi-agent PR review on the #4 template before opening the PR and fixed
what it found:

- **Scrubbed a leak.** The build sheet (`.BUILD.md`) still named a real Jamf asset
  and a real device serial. Replaced both with `<...>` placeholders — templates must
  stay generic.
- **Made a dangerous edge case safe.** The compliance check now only escalates to
  "quarantine + lock" when the read actually *succeeds and* says non-compliant. Before,
  a permission error / 403 (which this repo documents as a real possibility) was silently
  treated as "non-compliant" and pushed the device toward containment. A failed read now
  ends the run safely.
- **Renamed the blocks** to plain descriptive verbs (`resolve_device`, `check_compliance`,
  `approve_wipe`, …) per the agreed convention, instead of the auto-numbered defaults, and
  fixed the docs that pointed at old/nonexistent block names.
- **Regenerated the build sheet** to match the real 12-step playbook (earlier it described
  an older 20-step design with steps that were since dropped, including one action the
  connector rejects for computers).
- Added the 6-digit PIN to the wipe step (computers need it, same as lock) and reworded the
  approval prompt so it says containment was *queued* rather than asserting it as done.

The `.json` diagram was also regenerated to match (new block names, the fail-safe check, the
wipe PIN, the new prompt), so SOAR runs the fixed playbook without a manual rebuild. Because
it was edited outside the editor, it's marked draft: open it once in SOAR's editor and run it
once to confirm it loads and the wipe gate still holds — then export to lock it in.

---

## 2026-06-30 — First playbook template: Compliance Drift / MDM Tamper

Added the first real playbook template under `playbooks/` (issue #4), on the
`playbook/compliance-drift-remediation` branch:

- **`Jamf - Compliance Drift and MDM Tamper Remediation.py` / `.json`** — responds to a device
  flagged as non-compliant or MDM-tampered. Unlike a "contain first" flow, this
  one **tries to fix the device first** (re-establish MDM control and force a
  check-in), then **checks compliance**. If the device is healthy again, it just
  stops. Only if it's *still* broken does it quarantine and lock the device — and
  a full wipe happens **only** after an analyst clicks Approve on a prompt that
  spells out the wipe is permanent and irreversible.
- **`playbooks/README.md`** — an index of templates and how to adapt them.

Everything in the template is a clearly-marked placeholder (Jamf asset,
quarantine group, PIN, approver role) — no real names, no
secrets. It follows the naming/safety conventions agreed in issue #8.

One caveat: the `.py` (the actual logic) is complete and syntax-checked, but the
paired `.json` (the visual diagram SOAR draws) is a best-effort version that
should be opened and re-saved once in SOAR's Visual Playbook Editor to tidy up
the layout.

**Update (2026-07-01):** we checked the template against the *real* Jamf connector
that's actually installed in the SOAR test environment (not a guess) and corrected
the data wiring: the connector returns a device's id as `id` (not `jamf_device_id`),
its type as `type`, and compliance as a `compliance_state` text field (not a
true/false `compliant`); the "flag" attribute uses `ea_id`; and the wipe safety
`confirm` is a text value. The action names we used were already right. The
playbook's logic still passes its flow test after the fixes.

**Update (2026-07-01) — rebuilt and proven working live.** The first hand-written
version wouldn't open in SOAR's Visual Playbook Editor (the file format for the
decision/prompt/note blocks is too intricate to write by hand). We rebuilt it by
copying the structure of an already-working playbook, then **ran it live in the SOAR
test environment against the real Jamf tenant** (look up device → redeploy management
→ force check-in → check compliance → quarantine → lock), it **paused for analyst
approval before the wipe**, and we **denied, so nothing was erased**. That proves the
control flow and the safety gate. **Caveat (PR #10 review):** this was not a clean
end-to-end pass — `get compliance status` returned **HTTP 403** (the test API role
lacks the conditional-access privilege), and only the wipe-*deny* path was exercised.
The compliance read and the actual wipe path remain unverified live.

Two things we learned and wrote down so nobody trips on them:
- **Prerequisites matter.** Each action needs specific Jamf API permissions (there's a
  table in `playbooks/README.md`), plus real values for the quarantine group and a
  6-digit lock PIN. Missing permissions show up as "403" errors at run time.
- **Playbooks are built in SOAR's editor, then saved to git** — not written by hand.
  There's now a step-by-step build sheet (`playbooks/…​.BUILD.md`) for recreating it.

The committed template keeps generic `<placeholders>` (no real asset names, group
names, or PINs) so it's safe to share; real values live only in the SOAR instance.

---

---

## 2026-07-03 — FileVault Recovery Access: serial now pulled from the event + distribution PR

Two things:
- **The Mac's serial is no longer hardcoded.** The resolve step now reads the
  serial straight from the incoming SOAR event (`artifact:*.cef.serialNumber`),
  the same pattern the sibling Compliance Drift / MDM Tamper playbook (issue #4)
  uses — so the template works on whatever device the event is about, instead of
  a fixed test serial.
- **Distribution PR opened.** The generic, ready-to-share version (placeholder
  asset/approver/passwords, no real values) goes to `main` via its own branch,
  while the working copy stays runnable in SOAR for testing. This keeps the
  live playbook and the shareable template from stepping on each other.

Still to finish: the secure-notification step (still a placeholder note) and
friendlier block names.

---

## 2026-07-02 — First playbook: Jamf - FileVault Recovery Access (macOS)

The first real playbook is in (issue #7): **Jamf - FileVault Recovery Access
(macOS)**. It gives IT/security secured recovery access to a Mac — after a
compromise or during employee offboarding:

1. **Resolve** the Mac by serial number; if none matches, it stops with a note.
2. **Enrich** — pull the FileVault recovery key (sensitive!), local user
   accounts, and compliance status.
3. **Secure** — set a recovery lock, then lock the device.
4. **Note / notify** — record what happened (today a note; meant to become a
   restricted-channel Slack alert — see below).
5. **Ask a human** — an analyst approval prompt before any wipe.
6. **Only on "Yes"** — wipe the device (offboarding erase). A "No" just leaves a
   note. It never wipes on its own.

Cleanups done this session:
- **Renamed** the playbook to drop a `/` in its title (the slash was accidentally
  creating a folder inside the repo).
- **Made it generic** — swapped one environment's specifics for clearly-marked
  placeholders: the dev asset name, the approver, and a **real recovery-lock
  password and test phone number** that had been left in. The wipe prompt now
  spells out that the erase is permanent and irreversible.

Still to finish (per issue #7):
- **Build the real notify step.** Right now step 4 is just a note with a "replace
  me" reminder; it needs to send to a restricted channel (the recovery key must
  never go to a broad channel).
- **Wire the serial to the event** instead of a fixed placeholder — waiting on a
  shared decision about device-identifier fields (issue #8).
- **Friendlier block names** (a tidy-up best done in the SOAR editor).

---

## 2026-06-08 — Repo skeleton created

This is the very first version of the repo. Nothing here runs yet — it's a
governance scaffold so people know what this repo is for, how to propose a
playbook, and the safety rules before any actual playbooks land.

What was added:

- **README.md** — Explains what the repo is (a library of Splunk SOAR playbook
  *templates* for the Jamf SOAR connector app), the prerequisites (the
  `jamf-splunk-soar` app installed in SOAR plus a configured Jamf asset), and
  how the playbooks get into SOAR (added as a git source-control repository, or
  imported as a `.tgz` export). Lists the four planned scenarios with lost /
  stolen device marked as first. Install/usage steps are placeholders for now.
- **CONTRIBUTING.md** — How to propose a playbook (issue first), the
  `[playbook]` title prefix, that playbooks are git-synced into SOAR, a reminder
  to keep template asset/group names generic, the non-negotiable
  analyst-in-the-loop safety rule, and the PR workflow (one playbook per PR,
  reference an issue). Non-engineers welcome.
- **CLAUDE.md** — Technical notes for future maintainers and AI assistants:
  how each playbook is a SOAR playbook synced via git, the dependency on the
  connector app's actions and datapaths, known gotchas, decisions log, and
  change history.
- **.gitignore** — Files git should never track: secrets (`.env`, asset configs,
  client-secret JSON), SOAR playbook export artifacts (`.tgz` / `.tar.gz`),
  Python build junk (playbooks can contain custom code blocks), OS and editor
  junk, logs, and a local `personal/` scratch folder.
- **Issue template** (in `.github/ISSUE_TEMPLATE/`):
  - `new-playbook.md` — Use when you want to propose a playbook. Captures the
    scenario/trigger, a plain-English description, the ordered chain of Jamf app
    actions, decision/approval gates, datapaths between steps, external tools,
    customer-config points, and acceptance criteria.

What's intentionally **not** here yet:

- No actual playbooks. The first one (lost / stolen device) will be added via
  its own issue and PR. We didn't want to commit empty playbook stubs that go
  stale.
- No license file. The repo is private; a license will be added before any
  public release.
- No SOAR source-control sync instructions beyond the high-level shape — those
  will be fleshed out alongside the first real playbook.
