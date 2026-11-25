# Jamf - FileVault Recovery Access (macOS): design notes

Developer notes for maintaining this playbook. Customer-facing setup is in the
playbook's **Notes** field in SOAR.

## Flow

```
resolve by serial (from the event artifact) -> (device found?)
  -> retrieve recovery context: FileVault personal recovery key [SENSITIVE],
     local user accounts, compliance status
  -> secure: set recovery lock, lock device
  -> note (notify) -> analyst approval gate -> wipe device only on approval
```

A decline, a timeout or a no-device path only adds a note.

## Design notes

- The serial is read from `artifact:*.cef.serialNumber` in a code block (`collect2`), not
  through the visual datapath picker, which stores a non-standard CEF field as a literal.
- The FileVault recovery key is sensitive. `code_1` writes only whether the key was
  retrieved and escrowed (`summary.key_present`), never the key itself. Keep it that way
  and never route the key to a broad channel or note.
- `code_1` is the notify step and is a note today. Replace it with a restricted-channel
  notifier if your process needs one.
- If the key was not obtained, the note warns the analyst not to approve the wipe while the
  disk contents are still needed.
