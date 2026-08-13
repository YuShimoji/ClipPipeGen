# Portable review proof intake

`verify-portable-review-proof` は、親 Coordinator から別送される project ZIP と
ZIP 外の manifest を受領した後、既知の review proof identity を機械的に照合する。
opening、endpoint、subtitle/source/cut/causal route の採否は判断しない。

current exact expectation は
`docs/review_intake/clip-wiki-integrated-subtitle-cut-proof-v1-001.expected.json`。
70 個の `package/` file、69 payload を閉じる live manifest self SHA、review HTML、
4 本の MP4 の SHA-256 と byte size を固定している。manifest 全行の path / SHA /
byte size も package の実 bytes と照合する。ZIP がより広い project snapshot を含む場合も、検証後に
展開するのはこの `package/` 70 files だけである。既存の展開先は上書きしない。

## ZIP 外 manifest

転送元は ZIP と同じ場所に次の JSON を置く。archive の値は転送後の実 bytes から
計算し、`artifact_id` と package count は tracked expectation に合わせる。

```json
{
  "schema_version": "clippipegen.portable_review_outer_manifest.v1",
  "artifact_id": "clip-wiki-integrated-subtitle-cut-proof-v1-001",
  "archive_name": "ClipPipeGen-portable.zip",
  "archive_byte_size": 123456,
  "archive_sha256": "<64 lowercase hex>",
  "package_root": "package",
  "package_file_count": 70
}
```

## 受領側の実行

GUI や media player を起動せずに verify と展開を行う例：

```powershell
python -m src.cli.main verify-portable-review-proof `
  --archive C:\path\to\ClipPipeGen-portable.zip `
  --outer-manifest C:\path\to\ClipPipeGen-portable.outer-manifest.json `
  --expected docs\review_intake\clip-wiki-integrated-subtitle-cut-proof-v1-001.expected.json `
  --extract-to C:\path\to\clip-wiki-proof-review `
  --review-contract docs\review_intake\clip-wiki-integrated-subtitle-cut-proof-v1-001.review-contract.json `
  --handoff-dir C:\path\to\clip-wiki-proof-handoff `
  --reply-destination video-coordinator:CURRENT_TASK `
  --format json
```

合格時の JSON は、絶対 `review_entrypoint`、`review_open_command`、自動で browser を
開かない `review_server_restart_command` を返す。この工程は identity/integrity の
受入だけであり、実見、creative acceptance、production/public/publishing acceptance
を代替しない。ZIP または外側 manifest が未着なら再生成や Drive 探索へ逸れず、
transfer source boundary としてその二点の受領を待つ。

`--review-contract`、`--handoff-dir`、`--reply-destination` は
`--extract-to` と同時に指定する。exact verification と新規directoryへの展開が両方
成功した場合だけ、handoff directoryへ `verification_receipt.json`、
`coordinator_review_packet.json`、`coordinator_review_packet.md` をatomicに出力する。
packetはopening、endpoint、subtitle behavior、overall winnerを別dimensionとして示し、
`ACCEPT` / `REPAIR` / `REJECT` の一回答だけをCoordinatorへ返す形にする。未着、hash不一致、
既存出力先、別artifact contractではpacketを作らない。
`video-coordinator:CURRENT_TASK` はportable sourceへ固定する実IDではなく、callerが
実行時のCoordinator destinationへ置換するplaceholderである。実destinationは
task-owned ignored/generated handoff packetにだけ記録する。
