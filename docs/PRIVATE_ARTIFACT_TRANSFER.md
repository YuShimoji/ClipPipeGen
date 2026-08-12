# Private Artifact Transfer

`episodes/` の実 media と review package を public Git に入れず、別端末へ exact bytes で渡す
ための private/offline transfer contract。既存の manifest-only handoff を置き換えず、実体の
transport が必要な場合だけ補完する。

## 解消する摩擦と残す境界

Git clone だけでは移らない source bytes、caption sidecar、rendered MP4、review evidence を、
一つの immutable ZIP と隣接する SHA-256 receipt へ固定する。受領端末では全 entry と receipt
identity を検証してから repo-relative な `episodes/` path へ復元する。既存 file が同一 SHA
なら再利用し、異なる場合は一件も復元する前に fail closed する。

この transport は private storage 用であり、rights、production、公開、収益化、publishing、
upload の承認ではない。Google Drive 等へ置く場合も共有設定を変更せず、owner-only または
明示的に承認された private transfer として扱う。本 CLI 自体は Drive への書込みを行わない。

## 作成

include と output は repository-relative かつ `episodes/` 配下に限定される。`.env*`、OAuth
token、cookie、repository/runtime metadata、reparse point は拒否する。output と receipt は
既存 file を上書きしない。

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

作成処理は ZIP 内の manifest self-integrity と全 payload hash を再検証してから、ZIP と
receipt を確定する。receipt の確定に失敗した場合は、今回だけが生成した未対の ZIP を残さない。

## 検証と復元

ZIP と同名の `.receipt.json` を取得し、ファイル名を保ったまま次を実行する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  scripts/operator/restore_private_artifact_transfer.ps1 `
  -Archive C:\path\clip-example-private-transfer-v1-001.zip `
  -Receipt C:\path\clip-example-private-transfer-v1-001.zip.receipt.json
```

検証は次を fail closed で照合する。

- archive SHA/size と receipt の exact identity
- manifest SHA/self-integrity、bundle/artifact/source/repo identity
- payload file count/byte size と各 member の SHA/size
- manifest 外 member、path traversal、case collision、secret-like path
- restore 先の reparse point と既存 file の SHA conflict

全 archive 検証と既存 target の preflight が通るまで復元を開始しない。Git tracked state、
Drive、共有設定、外部公開先は変更しない。
