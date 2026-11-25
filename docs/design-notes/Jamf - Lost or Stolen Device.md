# Jamf - Lost or Stolen Device: design notes

Developer notes for maintaining this playbook. Customer-facing setup is in the
playbook's **Notes** field in SOAR.

## Flow

```
resolve by serial -> (device found?) -> device_type?
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
- Block names follow SOAR's `<type>_<n>` convention with a unique id per type
  (`decision_1..4`, `code_1..5`, `prompt_1..2`, `wipe_device_1..2`). Reusing an id within a
  type makes SOAR generate two functions with the same name (function-redefined).
- Single-match assumption: a serial should resolve to one device. The containment,
  the wipe, and the disclosure note and prompt all act on every matched row, so if a serial
  ever matched more than one record the note warns and the wipe would erase all matches
  under one approval. Hard-gating to exactly one match (routing more than one to manual
  review) is a v2 item.
- `code_5` distinguishes a real "no device matched" from a partial lookup where one
  platform (computer or mobile) was skipped for auth (`get device by serial` is best-effort
  and returns success with `summary.skipped`), so a privilege gap isn't read as a clean miss.
- Enrichment (the Device Enrichment (Input) playbook) and quarantine (add to static group)
  are deferred to v2.
