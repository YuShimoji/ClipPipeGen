# Wiki添削 Episode 1 integrated rough-cut preflight

Work Order: `CPG-WIKI-EP1-INTEGRATED-ROUGH-CUT-001`

Status: **BLOCKED_EXACT_SOURCE_MEDIA_REQUIRED**

Sの`content_continue`はproduction entryだけを許可した。human artistic acceptanceとfinal delivery acceptanceは未付与。mandatory preflightでCU-02のexact source mediaが解決できないため、MP4は生成していない。

## Episode 1 mapping

| Chapter | ClipUnit | Source/time | Media | Content connection |
|---:|---|---|---|---|
| 1 | `CU-01` 非公式Wikiは何を記録しているのか | `youtube:1AcId5Yja10` 390–510s | exact_media_ready | Wiki添削は誤字探しではなく、ファンが作った人物像を本人が読み返す企画だと定義する。 → 同じWikiでも人物ごとに記録のされ方が違う、という比較へ進む。 |
| 2 | `CU-02` 情報量が示す桃鈴ねね像 | `youtube:Ocqg-RpQURY` 390–585s | missing_exact_media_and_or_binding_receipt | 網羅量そのものではなく、何に記述が集まるかがその人の見え方を作る。 → ページの強調点を、本人の訂正が最も多いプロフィール項目へ接続する。 |
| 3 | `CU-03` プロフィール訂正で像が動く | `youtube:1AcId5Yja10` 1530–1905s | exact_media_ready | 訂正してもファンの記憶は消えず、公式と非公式の間に現在の人物像ができる。 → 訂正で終わらず、ページが忘れた出来事をどう呼び戻すかへ進む。 |

## Exact blocker

- `CU-02` requires `youtube:Ocqg-RpQURY` 390–585s.
- Expected media: `episodes/wiki_tensaku_family_20260804/corpus/materials/Ocqg-RpQURY/source_video.mp4` (missing).
- Expected receipt: `episodes/wiki_tensaku_family_20260804/corpus/materials/Ocqg-RpQURY/acquisition_receipt.json` (missing).
- Caption SHA-256: `a383ad8a545fe9a24da142dace96fe19f05bf834a03e1e52616a5332db3c3992` is present, but captions do not substitute for source video.

## Resume

Exact source bytes and a receipt binding source identity, byte size, and SHA-256 must be explicitly supplied at the recorded paths. This preflight performs no network acquisition.

Run: `uv run --no-project python scripts/preflight_wiki_tensaku_ep1_integrated_rough_cut.py`

Only `READY_TO_RENDER` permits the integrated renderer. Until then, `integrated_product_iteration=0`, score `82/100`, and no S MP4 review packet exists.

## Preserved probes

- `clip-wiki-tensaku-family-turn-v1-001`: 21800858 bytes / SHA-256 `1f965e537d5a767d8cfe5c456ed0481ea88a119743f207ada9764bbc0ebe3284`
- `clip-wiki-tensaku-family-turn-v2-001`: 19951636 bytes / SHA-256 `2736f6ec5b4a779a70c978d7815639802dee2d294220fdbb592edb9d75fe2dca`
- `clip-wiki-tensaku-family-turn-v3-001`: 20605376 bytes / SHA-256 `5abfd8e940bd8a2709e79aced38ab2e0e56b7f052f3d205512e082d2a8f8733b`
- `clip-wiki-tensaku-family-turn-v4-001`: 18884819 bytes / SHA-256 `5fea3d14e476871f239d1ab42283fedd83546daf98e8c5a27f625506ba69ca40`
- `clip-wiki-tensaku-family-turn-v5-001`: 19964780 bytes / SHA-256 `e192fcd6746d396c0c92b5952c274cf5afd07f47c0f5d3a17deecd33b658012c`
