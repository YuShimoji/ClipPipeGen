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

大きなZIPをtransport connectorへ渡す場合、operator wrapperは16MiBの
`<archive>.part0001`形式へ分割し、`<archive>.parts.json`へ各partと結合後archiveのSHAを固定する。
受領側では全partと結合後SHAを確認してから、元のarchive/receipt検証へ進む。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/operator/assemble_and_restore_private_artifact_transfer.ps1 `
  -PartsManifest C:\path\clip-example.zip.parts.json `
  -Receipt C:\path\clip-example.zip.receipt.json
```

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
照合する。単一large-file uploadがtransport中継timeoutになる場合も、16MiB partsを同じprivate
folderから取得して上記scriptで再構成できる。公開linkや「リンクを知っている全員」共有へ変更しない。

2026-08-05のfinal readbackではprivate folder `ClipPipeGen Private Artifact Handoffs`
（folder ID `1YPiWjsJLlK04GKbqj6gkgFz_iBaeW0ZB`）に、14 parts、parts manifest、receiptの
16 member / 224,909,222 bytesが揃った。part0001〜0013は各16,777,216 bytes、part0014は
6,800,437 bytes、manifestは4,134 bytes、receiptは843 bytes。全memberは`not_shared`で、
共有設定は変更していない。archive SHAは
`43331d7797faafc3aef7ba0ce538ca9ea8db1ff8ed168c76d4229a647c0e196d`、parts manifest self SHAは
`f452d1134fe2a9694ec04976993935b9099b8beb4227436d2b98910152d08b98`。

## Wiki artifact delta

既にfull-corpus bundleを受領済みの端末へ新しいreview artifactだけを渡す場合、source bytesを
重複させずcandidate-specific slice inputとartifact packageだけを固定する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/operator/build_wiki_tensaku_cross_device_bundle.ps1 `
  -ArtifactId clip-wiki-tensaku-family-turn-v2-001 `
  -PayloadMode artifact-delta
```

delta単体で最終MP4とreview pageは視聴できる。sourceから再renderする場合は、先に上記full-corpus
bundleをrestoreする。どちらも既存fileのconflict overwrite、共有設定変更、publicationを行わない。
