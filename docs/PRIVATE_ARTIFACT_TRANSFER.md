# Private Artifact Transfer

`episodes/` の実mediaとreview packageをpublic Gitへ入れず、別端末へexact bytesで渡すための
private/offline transfer contract。SH-06のmanifest-only handoffを置き換えず、実体transportが
必要な場合だけ補完する。

## 何が解決されるか

Git cloneだけでは移らないsource bytes、caption sidecar、candidate-specific static input、
rendered MP4、review evidenceを、一つのZIPとSHA-256 receiptへ固定する。受領端末では全entryを
検証してからrepo-relativeな`episodes/` pathへ復元する。既存fileが同一SHAなら再利用し、
異なる場合は上書きせず停止する。

このtransportはprivate storage用であり、rights、production、公開、収益化、uploadの承認ではない。
Google Drive等へ置く場合も共有設定を変更せず、認証済みowner-only transportとして扱う。

## CLI

```powershell
uv run --offline --no-project --python 3.13 python -m src.cli.main `
  build-private-artifact-transfer `
  --bundle-id clip-example-private-transfer-v1-001 `
  --artifact-id clip-example-001 `
  --source-identity local:example `
  --repo-head (git rev-parse HEAD) `
  --include episodes/example/corpus `
  --include episodes/example/artifacts/clip-example-001 `
  --output episodes/example/transfers/clip-example-private-transfer-v1-001.zip
```

受領端末ではZIPと隣接receiptを取得後、次を実行する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/operator/restore_private_artifact_transfer.ps1 `
  -Archive C:\path\clip-example-private-transfer-v1-001.zip `
  -Receipt C:\path\clip-example-private-transfer-v1-001.zip.receipt.json
```

archiveはmanifest外entry、path traversal、case collision、secret-like path、reparse pointを拒否する。
payloadは`episodes/`配下だけに限定し、Git tracked stateを変更しない。

## Wiki family turn 001

Operator command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/operator/build_wiki_tensaku_cross_device_bundle.ps1
```

このbundleは次を含む。

- Wiki 001 exact retained source bytesとacquisition receipt
- Wiki 001/002/003のretained caption/corpus/static input evidence
- `clip-wiki-tensaku-family-turn-v1-001`の完全review packageと300秒MP4
- corpus inventory/receipt、watch/surface receipts、collector readback

diagnostic `audio_probe.wav`等の再生成可能scratchは含めない。Drive上ではfilenameとreceipt SHAを
照合し、公開linkや「リンクを知っている全員」共有へ変更しない。
