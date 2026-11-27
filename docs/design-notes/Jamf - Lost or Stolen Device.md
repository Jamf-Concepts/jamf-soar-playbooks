# Jamf - Lost or Stolen Device: design notes

Developer notes for maintaining this playbook. Customer-facing setup is in the
playbook's **Notes** field in SOAR.

## Flow

```
has serial? -> find device by serial -> device found? -> device type?
    mobile   -> enable lost mode -> note -> approval gate -> wipe on approval
    computer -> lock device      -> note -> approval gate -> wipe on approval
```

A decline, a timeout or a no-device path only writes a note. The playbook never wipes
without approval.

## Design notes

- The two device-type branches each carry their **own** note -> prompt -> wipe tail and
  do not reconverge. Merging them onto one shared block makes SOAR insert a join that
  waits for both branches; only one runs per device, so that join never completes and
  the note, prompt and wipe are skipped. Per-branch tails avoid the join.
- Every block has a custom name (lowercase, at most four words, as Splunk's playbook
  checks require). SOAR builds each block's function name from its custom name, so names
  must be unique, and renaming a block renames its function. The editor updates its own
  generated code but **not** hand-written custom code, so after a rename, update any
  `<block>:action_result` datapaths in the code blocks by hand.
- Each wipe's result is reported by one code block (`note mobile wipe outcome`,
  `note computer wipe outcome`) that reads the wipe status and writes either the "queued" or
  the "failed / not queued" note. This used to be a decision plus two note blocks per branch;
  merging them keeps the playbook at the 20-block limit.
- Single-match assumption: a serial should resolve to one device. The containment,
  the wipe, and the disclosure note and prompt all act on every matched row, so if a serial
  ever matched more than one record the note warns and the wipe would erase all matches
  under one approval. Hard-gating to exactly one match (routing more than one to manual
  review) is a v2 item.
- `note lookup failed` distinguishes a real "no device matched" from a partial lookup where one
  platform (computer or mobile) was skipped for auth (`get device by serial` is best-effort
  and returns success with `summary.skipped`), so a privilege gap isn't read as a clean miss.
- Enrichment (the Device Enrichment (Input) playbook) and quarantine (add to static group)
  are deferred to v2.
