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

Turn 2 deltaの2026-08-06 final readbackは4 member / 21,334,932 bytes、全member `not_shared`。
archiveは21,332,844 bytes、SHA
`4710c08c15157773982ff0d9ce2aa53265352c4ecfacb5828b885b4bf625bba0`、24 payload files、
repo head `dd758bd007868b73cd21f66820be5a6403b87200`へbindする。memberは次の通り。

| member | bytes | SHA-256 | Drive file ID |
|---|---:|---|---|
| `part0001` | 16,777,216 | `f3b31f86b2525e3bf621f5d74906d40c78a50530beb2f75b07d2d423214f6157` | `1YJj0njYKPmJJ7s-58WjAH5izlDLcIgW9` |
| `part0002` | 4,555,628 | `9958417a0d829a67260215c3a4801f3303222ce5da9cc5739225984f29c49a46` | `15Dki5jk9qTBeyAf0ww5STEmbRSMdrTaj` |
| `parts.json` | 1,247 | `532f952ec20770086f2679ceb1ab55971ba50acd5bad596ad032e59d65890f42` | `1gx2Z8QfmRR2wezbEasdsQkncYZ9tO5Qc` |
| `receipt.json` | 841 | `0b03ad44c5103bfb9f29fc25bdf5cc69e66a83b794ed1cbc07555cca7e4aaf65` | `1Kxdj9SWHogae1xehFLvo-XK1fuzsqpgW` |

parts manifest self SHAは`b9333b8f24d68eea4c70e5b13487cab9b42dc4c152ac6cb6e35850b4aa18f48c`。
folder全体は20 member / 246,244,154 bytes（full-corpus 16 + Turn 2 delta 4）。

## Wiki Turn 3 artifact delta

Turn 3は同じ`artifact-delta` modeで生成し、既存source bundleを重複させない。
2026-08-06 final readbackは4 member / 21,985,477 bytes、全member `not_shared`。
archiveは21,983,389 bytes、SHA
`59efb0174571607d521d7964f941525d4e3764fee710ef02ffea64eb70e6409a`、24 payload files、
repo head `49dd7bf1886bee0c275c01fb97297b91a4019c01`へbindする。

| member | bytes | SHA-256 | Drive file ID |
|---|---:|---|---|
| `part0001` | 16,777,216 | `28d42a56b789bebc8ebc485b6ee02f0e12a164384ad84cccdad82f44d3f552d7` | `1cpS7al_FR67QItkk-e3fGJXZqkAVEXZt` |
| `part0002` | 5,206,173 | `cf46a7b3100d9b90e6a18fa3f22f2775dcbdb1a71b26c7935ab9adbf383c31b7` | `1wUhp63T3WKW1f1ubuGYo-_yAbPMmlQde` |
| `parts.json` | 1,247 | `8f52e615985ccf3b63747ff7a706407a548d93005b78b98b002cc3497c6a3e6a` | `1Y1o-GOj5LpQvBZjiI72qX58MevM7TRCW` |
| `receipt.json` | 841 | `d601e1842fc5ddc5f8a94cbffc0addeaa71bb0534c66a26c8f5c51a01adf6408` | `1zbrvkiEM_PHa8fBpLvj1FbwHnLuAuLar` |

parts manifest self SHAは`51c92590f187fbbef8495faeefcc234a5219b65ef7b598e072255c18ef00e8b4`。
folder全体は24 member / 268,229,631 bytes（full-corpus 16 + Turn 2 delta 4 + Turn 3 delta 4）。
`not_shared`はowner private storage状態を示すだけで、recipient download/restore完了の証拠ではない。
