# OUT-08 private review package recovery

This recovery kit moves the already verified, Git-ignored OUT-08 review package from its last verified host to the current operator host. It does not rebuild either candidate, compare unlike source bytes, upload media, or make the package portable through Git.

The immutable identity is recorded in `out08_private_review_package_recovery_contract.json`: 17 package files, 16 manifest payloads, manifest self-integrity `22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4`, candidate hashes `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` and `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b`. `cut_009` remains rejected over 135.219–144.000 seconds, and candidate 02 may not extend beyond 135.219 seconds.

## Host-aware sequence

| Host and step | Command | Successful state | Failure handling |
| --- | --- | --- | --- |
| Any host: inspect | `uvx python -m src.cli.main recover-out08-private-review-package --format json probe` | Classifies the local package and port 8071; writes an ignored host receipt | `package_present_invalid` is fail-closed; do not overwrite it |
| Thank (`DESKTOP-H53P1T4`): export | `uvx python -m src.cli.main recover-out08-private-review-package --format json export --destination D:\private-transfer\out08-review.zip` | Deterministic ZIP containing the exact 17 files plus a sanitized receipt | Destination must be explicit, outside the repository, and absent |
| User-owned private channel | Copy `out08-review.zip` without modifying it | Archive arrives on Planner007 | This repository does not select or operate the transfer channel |
| Planner007: import | `uvx python -m src.cli.main recover-out08-private-review-package --format json import --archive D:\private-transfer\out08-review.zip --start-server` | Exact package is promoted atomically, revalidated, served, and probed | Unknown files, traversal, duplicates, case collisions, links, corruption, or any identity mismatch are rejected before promotion |

The PowerShell wrapper exposes the same operations:

```powershell
scripts\operator\out08_private_review_package_recovery.ps1 Probe
scripts\operator\out08_private_review_package_recovery.ps1 Export -Destination D:\private-transfer\out08-review.zip
scripts\operator\out08_private_review_package_recovery.ps1 Import -Archive D:\private-transfer\out08-review.zip -StartServer
```

Expected JSON status is `export_ready_for_private_copy` on Thank, then
`package_imported_atomically` (or `existing_valid_package_preserved`) on
Planner007. With `--start-server`, the receiving host receipt must finish with
`package_verified_exact`, `server_running_verified`, and
`exact_package_and_server_verified` before human review starts.

## Security and preservation guarantees

- Export validates the source package before and after writing, fixes ZIP timestamps and permissions, sorts entries, uses no compression variability, and refuses an in-repository or existing destination.
- Import accepts only the exact package allowlist plus `out08_private_transfer_receipt.json`. It rejects absolute or nested paths, `..`, backslashes, drive-qualified names, duplicate/case-colliding entries, directories, encrypted entries, symbolic links, non-regular entries, oversized content, CRC failure, and receipt/package identity mismatches.
- Import extracts into a new sibling staging directory. It promotes only after the full package contract passes. An existing invalid or different package is preserved and blocks import; an existing exact package is preserved and reused.
- Host receipts contain repository-relative paths and cryptographic identities, not absolute private paths. Both the package and receipt live under ignored `episodes/` storage.
- `--start-server` starts the repository's local byte-range server without opening a browser. Verification requires exact `index.html` bytes over HTTP 200 and an exact candidate byte range over HTTP 206.

Failures return `status=failed` plus a stable category. The categories identify
host mismatch/unknown state, missing or invalid package, unsafe or corrupt
archive, manifest/candidate/receipt/source identity mismatch, `cut_009`
overlap, unsafe existing package, port conflict, and server verification failure.
Do not bypass a category by copying files directly into the final package path.

## Still closed

The kit restores access only. Human playback/seek review, production acceptance, subtitle design acceptance, rights approval, public readiness, publishing acceptance, upload, OUT-07 thumbnail iteration, source-byte equivalence, and any media regeneration remain closed.

After import reports `package_verified_exact` and `server_running_verified`, the
single human question is:

> 追加Shorts候補ごとに、一本の編集単位として成立するか、テンポ・境界・字幕・音声に違和感があれば自由記述してください。
