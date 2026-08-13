# Editorial Form Variants

`select-editorial-form`は、編集形式を暗黙のdefaultへまとめず、stable variant IDで
明示選択する構造検証入口である。media取得・render・creative judgement・rights・
production・publicationは行わない。

## Family registry

| variant_id | primary axis | entry path |
|---|---|---|
| `common_context_argument` | evidence-grounded argument | 既存`build-common-context-probe`を変更せず使用 |
| `evidence_linked_comparison` | concurrent evidence comparison | 既存`build-evidence-linked-comparison`を変更せず使用 |
| `activity_chronology` | observable activity chronology | `select-editorial-form --variant activity_chronology`でplanを検証しnormalized IRを生成 |

このregistryはglobal defaultを新設・変更しない。既存build command、各形式のschema、
既存callerはそのままで、`activity_chronology`もfamily唯一の形式にはしない。

## activity_chronology contract

入力schemaは`clippipegen.editorial_form_plan.v1`、出力IRは
`clippipegen.editorial_form_ir.v1`。accepted media一例の人物・日付・source range・
unit数・引用数・duration・fade・hashはgrammarへ固定しない。

- `primary_axis`は`observable_activity_chronology`。
- 各unitは一つの`topic`、一つのsource surface、一つのsource/time attributionを持つ。
- `context.source_in/source_out`はselected source rangeを包含し、context basisを保持する。
- unitはISO date/datetimeの`timepoint`順に並び、後戻りしない。
- 接続根拠は映像と順序、または直接帰属できる引用。`subtitle_only`は禁止。
- ordinary temporal bridgeはsame day / next day / within one week / one week laterの
  relationと短いcaption一件まで。より長い時間関係または48文字を越えるcaptionには
  明示的`structural_justification`が必要で、caption例外も160文字を上限とする。
- quoteを使う場合はtext、attribution、source locator、選択範囲内のsource timeを持つ。
- abstract growth thesis、同時collageで作る抽象接続、字幕密度で隠す接続をprimaryにしない。
- 説明を足すより、活動映像・順序・直接引用だけで読める構造を優先する。

例:

```powershell
uv run python -m src.cli.main select-editorial-form `
  --variant activity_chronology `
  --plan path\to\activity-plan.json `
  --output path\to\normalized-activity-ir.json `
  --format json
```

出力先は既存fileを上書きしない。失敗時はcreative rejectionを推定せず、
`rule`と`locator`（unitまたはsource locator）を返す。

## Artifact and acceptance boundary

このcapabilityの根拠となったexact activity artifactは
`clip-s2-subaru-activity-chronology-v2-001`、MP4 SHA-256
`8f7930ae89e8a397f8343f5745e2d2e105dea3f70988daf2f487f8fe5e4b1544`。
Mission authority上のexact artifact review stateは、汎用variant IRへ継承しない。

rejectされた比較predecessor
`clip-s2-subaru-evidence-linked-comparison-v1-002`、MP4 SHA-256
`a959dc50a0b1b36d37644195fab9105403afdbc7e5f60dfc42ca90c70c72d00f`
もimmutable referenceとして隔離し、`activity_chronology`選択により昇格・変更しない。

normalized IRの`capability_boundaries`はhuman creative acceptance、production
readiness、rights clearance、publication/uploadをすべてfalseに固定する。repository
capabilityのtechnical validationは、個別artifactの受入やproduction readinessではない。
