# First Slice — Material Sourcing + Thumbnail 最小実証

Slice 1 のスコープ・ファイル構成・CLI 導線・受け入れ条件を定める。

## ゴール

1本の元動画 URL に対して、以下の流れを通す：

1. 仮の `rights_manifest` を作成し、`compliance_check.status` を記録する
2. サムネ用の人物画像／背景画像を `material_ledger` に登録（sidecar 強制）
3. 透過PNG を外部処理で生成して受け取り、ledger に登録
4. YMM4 で人手 authoring 済みの `thumbnail base template.ymmp` の slot を audit
5. CLI で `thumbnail_patch_input.json` を渡して slot patch を実行
6. patched ymmp を YMM4 で開き、人手で構図・配色を最終確認・書き出し
7. 全工程の readback／manifest が連結された状態で残る

## Slice 1 では実装しない（後続 feature として扱う）

- 元動画／音声取得（Slice 1 では未実装。現在は INT-02a で fake source audio 契約、INT-02c でローカル media の source audio 正規化、INT-02e で `yt-dlp-audio` source audio URL fetch を actual smoke まで完了。INT-02f で `fetch-source-video --mode local-media-video` による local source video 登録と FFprobe metadata readback まで完了。OUT-01 で source video + source audio + edit_pack から tiny diagnostic rendered video proof まで完了。URL video fetch / production render は後続）
- 背景切り抜き API 呼び出し（未実装、INT-03/INT-04 で起票。Slice 1 は透過PNG の受け取りのみ）
- 動画 cut detection・字幕生成（Slice 1 では未実装。現在は ED-02 / ED-04 の transcript-based CLI を実装済み）
- YouTube upload（PB-* / INT-01）
- GUI — Slice 1 後の SH-03 / SH-03b / SH-03c で実装済

## ファイル構成（Slice 1 後の状態）

```
ClipPipeGen/
├── README.md
├── CLAUDE.md
├── AGENTS.md
├── .claude/
│   └── CLAUDE.md
├── .gitignore
├── docs/
│   ├── INVARIANTS.md
│   ├── LANES.md
│   ├── AUTOMATION_BOUNDARY.md
│   ├── RUNTIME_STATE.md
│   ├── FEATURE_REGISTRY.md
│   ├── FIRST_SLICE.md
│   └── SCHEMAS/v1/
│       ├── rights_manifest.md
│       ├── material_ledger.md
│       ├── material_sidecar.md
│       └── thumbnail_patch_input.md
├── config/
│   └── nlmytgen_path.json.example
├── src/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── init_episode.py        # 新 episode の skeleton 作成
│   │   ├── validate_rights.py     # rights_manifest validate
│   │   ├── set_compliance.py      # compliance_check.status を更新（人手判断結果の記録）
│   │   ├── register_material.py   # 素材登録（sidecar 必須）
│   │   ├── audit_material_ledger.py  # material_ledger 整合性チェック
│   │   ├── audit_thumbnail.py     # NLMYTGen audit-thumbnail-template bridge
│   │   └── patch_thumbnail.py     # NLMYTGen patch-thumbnail-template bridge
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── rights_manifest.py     # CR-01 schema＋validator
│   │   ├── material_ledger.py     # MS-01 schema＋validator＋CRUD
│   │   ├── material_sidecar.py    # MS-02 schema＋validator
│   │   ├── thumbnail_patch.py     # TH-01 入力構築＋result parsing
│   │   └── nlmytgen_bridge.py     # NLMYTGen subprocess wrapper
│   └── integrations/
│       └── (Slice 1 では空。後続スライスで埋める)
├── tests/
│   ├── test_rights_manifest.py
│   ├── test_material_ledger.py
│   ├── test_material_sidecar.py
│   ├── test_thumbnail_patch.py
│   └── test_nlmytgen_bridge.py    # subprocess は mock する
├── episodes/
│   └── (Slice 1 中の手動作業 episode が入る)
├── materials/
│   └── (素材ディレクトリ。各素材は <id>/ 配下に file + sidecar.json)
└── templates/
    └── thumbnail/
        └── (YMM4 で人手 authoring した base template ymmp を配置)
```

## CLI 設計（Slice 1）

すべて `python -m clippipegen.cli.main <subcommand>` 形式。

### `init-episode`

```
clippipe init-episode --episode-id ep_20260506_hololive_sample_001
```

`episodes/<episode_id>/` を作成。`rights_manifest.json` skeleton を書き出す（status=`pending`）。

### `validate-rights`

```
clippipe validate-rights --rights-manifest episodes/<id>/rights_manifest.json
```

schema 構造と CR-01 バリデーション規則をチェック。`compliance_check.status` の値はチェックしない（pending でも validate は通る）。

### `set-compliance`

```
clippipe set-compliance \
  --rights-manifest episodes/<id>/rights_manifest.json \
  --status passed \
  --checked-by user:thankyoukass
```

rights / compliance の状態を記録する。VOD 状態や `third_party_ip[].permitted=false` は review notes / warnings に残すが、`status=passed` をブロックしない。

### `register-material`

```
clippipe register-material \
  --episode-id ep_20260506_hololive_sample_001 \
  --kind character_image \
  --subkind transparent_png \
  --file materials/mat_001/character_pekora_transparent.png \
  --sidecar materials/mat_001/sidecar.json \
  --intended-use thumbnail
```

ledger に追加。sidecar 構造・hash・透過PNG 整合性の検証を含む。`source.kind == "unverified"` 等は metadata として保持し、後段の thumbnail / publishing を止めない。

### `audit-material-ledger`

```
clippipe audit-material-ledger --episode-id ep_20260506_hololive_sample_001
```

ledger 全体の整合性（hash／sidecar／compliance_link）を検証。

### `audit-thumbnail`

```
clippipe audit-thumbnail \
  --base-template templates/thumbnail/hololive_clip_v1.ymmp
```

NLMYTGen の `audit-thumbnail-template` を subprocess で呼び、slot 一覧と健全性を返す。

### `patch-thumbnail`

```
clippipe patch-thumbnail \
  --input episodes/<id>/thumbnail_patch_input.json \
  --output-result episodes/<id>/thumbnail_patch_result.json
```

Slice 1 の中心 CLI。流れ：

1. rights manifest readback（rights_manifest.compliance_check.status を記録）
2. material validation（sidecar schema / file resolution）
3. NLMYTGen `audit-thumbnail-template` で slot 健全性確認
4. NLMYTGen `patch-thumbnail-template` を subprocess 呼び出し
5. patched ymmp の slot 値を再 read（readback match）
6. `thumbnail_patch_result.json` を書き出し

## NLMYTGen CLI bridge

### config 設計

`config/nlmytgen_path.json`（リポルートに置く、`.gitignore` 対象）：

```json
{
  "nlmytgen_root": "c:/Users/thank/Storage/Media Contents Projects/NLMYTGen",
  "python_executable": "python",
  "verified_at": "2026-05-06"
}
```

`config/nlmytgen_path.json.example` をリポにコミットし、ユーザーがコピーして自環境に合わせる。

### subprocess 呼び出し

`src/pipeline/nlmytgen_bridge.py`：

```python
def call_nlmytgen(subcommand: str, args: list[str]) -> dict:
    """
    NLMYTGen の CLI を subprocess で呼び、stdout JSON を返す。
    NLMYTGen が見つからない／異常終了したら例外で止める（silent fallback しない）。
    """
    ...
```

呼び出し対象（Slice 1）:

- `nlmytgen audit-thumbnail-template`
- `nlmytgen patch-thumbnail-template`

NLMYTGen 側 CLI の正確なコマンド名は実装時に NLMYTGen の CLI 仕様（`docs/dev/CLI_REFERENCE.md`）を参照（読み取りのみ、編集なし）。

## GUI 最小導線

**Slice 1 では GUI は作らない**。CLI のみ。

理由：

- Slice 1 の目的は schema・readback・bridge の運用感確認。GUI は設計コストが大きい
- CLI で運用感を見てから、後続スライスで GUI を起こす方が無駄が少ない
- ユーザーが CLI を使う前提のドメインに馴染んでいる（NLMYTGen と同じ運用）

後続スライスで GUI を検討する際は、SH-03 として FEATURE_REGISTRY に起票し、技術選定（Electron / Web / Tauri 等）から始める。

## 受け入れ条件（Slice 1）

以下が全て通ったら Slice 1 は done：

- [ ] `init-episode` で `rights_manifest` skeleton が生成される
- [ ] `validate-rights` が schema 違反を検出する（unit test 含む）
- [ ] `set-compliance --status passed` が review notes を warnings に残しつつ成功する（VOD not public 等）
- [ ] `register-material` が sidecar なしで失敗する
- [ ] `audit-material-ledger` が hash 不一致／sidecar 違反を検出する
- [ ] NLMYTGen の `audit-thumbnail-template` を subprocess で呼べる
- [ ] NLMYTGen の `patch-thumbnail-template` を subprocess で呼べる
- [ ] `patch-thumbnail` が rights status によらず実行され、status を readback に残す
- [ ] `patch-thumbnail` が `thumbnail_use=denied` 素材でも実行される
- [ ] `patch-thumbnail` で patched ymmp が生成され、readback match する
- [ ] 1 episode 分の手動 walkthrough（実 YMM4 base template ymmp に対する patch）が成功する
- [ ] tests が通る（mock subprocess を含む）

## 実装境界（Slice 1 で壊しやすいところ）

| 操作 | リスク | 対策 |
|---|---|---|
| `patch-thumbnail` の readback miss を warning で通す | 想定と違う ymmp が出来る | readback miss は error として fail。warning にしない |
| NLMYTGen subprocess の silent fallback | NLMYTGen が古い／壊れていても進む | 見つからない／バージョン不一致は exit 1 で止める |
| sidecar 必須の例外 flag 追加（`--skip-sidecar`） | hash / file 解決の追跡性が落ちる | sidecar は構造・追跡用 artifact として維持する |

## Slice 1 の DoD（Definition of Done）と DoR（Definition of Ready）

### DoR（着手前）

- [ ] ユーザーが本文書を review し、Slice 1 のスコープに同意
- [ ] `proposed → approved`：CR-01, MS-01, MS-02, MS-03, TH-01, SH-01
- [ ] NLMYTGen 側 CLI コマンド名を `docs/dev/CLI_REFERENCE.md` で確認（assistant が read-only で確認、結果を本文書に追記）
- [ ] YMM4 で動作する base template ymmp（slot に `Remark=thumb.*.<id>` あり）が用意できる見込みがあること（実物は実装中／後で作成可）

### DoD（完了条件）

上記「受け入れ条件」全項目が ✓。
