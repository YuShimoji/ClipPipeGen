# Invariants

破ってはいけない条件・責務境界を保持する正本。実装済み/未実装の区別を明確にし、未実装機能を禁止扱いにしない。

## North Star

- **Python は制作接着層**：元動画 URL／素材／rights 記録／EDL／字幕案／manifest／slot patch／publishing metadata を episode 単位でつなぐ。
- **外部素材取得・背景切り抜き・upload は通常の integration 候補**。未実装なら未実装として扱い、方針上の禁止にしない。
- **STT と素材取得を混ぜない**。`transcribe-audio` はローカル音声ファイルから `transcript.json` を作る。URL / VOD 取得は INT-02 `asset_fetch` として別に扱う。
- **FFmpeg / yt-dlp を core に漏らさない**。実 downloader は `src/integrations/asset_fetch/` に閉じ込める。FFmpeg は source audio 正規化だけ、yt-dlp は元 media 取得だけ。Editing core / STT / render / GUI から直接呼ばない。
- **rights / license / restriction は readback**。`pending` / `unverified` / `unknown` / `fair_use_claimed` / `denied` などの値だけで local CLI を停止しない。
- **外部ツール境界は明示する**。YMM4、外部 NLE、YouTube API、背景切り抜き API などは integration / bridge / handoff として扱う。

## Production Value North Star

- 制作価値は **「元動画と素材を、字幕／配置／サムネ／投稿準備まで詰まらず運べる」** ことで測る。
- preflight が通る・schema が validate する・テストが通るは接続証跡であり、成果そのものではない。
- レーン横断の成果は `episode_pack.{id, rights_manifest, material_ledger, edit_pack, thumbnail_patch, publish_draft}` がすべて連結された状態で測る。

## 責務境界

- **Compliance / Rights は記録層**。`compliance_check.status` は判断材料として表示するが、他レーンの local CLI gate にしない。
- **Material Sourcing は横断レイヤー**。Editing／Thumbnail／Compliance がそれぞれ素材要求を出し、Material Sourcing が一元的に台帳化する。動画編集配下に置かない。
- **Editing は transcript／cut EDL／字幕案／配置データまで**。動画ファイルの cut 実行・concat・字幕焼き込みは外部 NLE／YMM4／人手で行う。
- **Thumbnail は YMM4 サムネテンプレへの slot patch を先行実装済み**。完全自動合成や画像レンダリングは必要になった時点で feature として起票する。
- **Publishing は metadata／thumbnail 設定／upload receipt を扱う候補レーン**。visibility の扱いは CLI/GUI 実装時の引数仕様として決める。

## Integrations 隔離

外部 API・AI・取得系は **`src/integrations/` の中に隔離**する。本体ロジックは integration 結果を受け取るだけ。

- `src/integrations/youtube/` — OAuth・videos.insert・thumbnails.set
- `src/integrations/asset_fetch/` — source audio/video 取得 adapter（INT-02a は fake WAV generator、INT-02c は local-media-audio FFmpeg normalize、INT-02d は yt-dlp-audio spec only。INT-02e は source audio URL fetch 限定の yt-dlp-audio actual smoke まで完了。VOD / source video 取得拡張は後続）
- future `src/integrations/stt/` — STT engine wrapper（URL / VOD 取得は含めない）
- `src/integrations/bg_removal/` — 背景切り抜き API（外部送信を伴う）

本体ロジックは integration 結果を受け取る。外部送信・認証・課金・provider 固有処理は integration 配下に寄せる。

## NLMYTGen との関係

- **NLMYTGen のファイルは読まない・書かない・編集しない**。
- 再利用は CLI subprocess 経由のみ：`patch-thumbnail-template` / `audit-thumbnail-template` / 字幕表示幅計測。
- shared package 化は先回しでやらない。CLI bridge で運用感を見てから判断する。
- NLMYTGen 側の E-01（YouTube投稿）への依存を作らない。本リポ独自の `src/integrations/youtube/` を持つ。NLMYTGen 側で E-01 が successor-lane で起票されるかは本リポの判断対象外。

## Prohibited Interpretations / Shortcuts

- **未実装を禁止として書かない**。理由: roadmap 判断と safety gate が混ざると、後続エージェントが実装可能な integration を避ける。
- **rights / sidecar の値だけで実行を止めない**。理由: 本ツールは記録と接続を担い、最終判断をデータ値に過剰委譲しない。
- **外部 integration を pipeline 本体に直書きしない**。理由: 認証・課金・provider 固有差分を integration 境界で交換可能にする。
- **NLMYTGen の docs／runtime-state／INVARIANTS／コードを編集しない**。再利用は CLI 経由のみ。理由: NLMYTGen は別リポであり、本リポの変更範囲外。
- **shared package を先回しで作らない**。理由: 再利用パターンが固まる前の抽象化は死荷重になる。CLI subprocess で 2-3 個の実例が出てから判断する。

## Rights Readback（非ブロック仕様）

`rights_manifest.compliance_check.status` は episode の状態記録であり、CLI 実行の hard gate ではない。

- `set-compliance --status passed` は VOD 状態や third_party_ip の値で失敗しない。
- 旧 auto-fail 条件は `warnings[]` / GUI の review notes として残す。
- thumbnail patch / material registration / future publishing integration は、ファイル存在・schema・hash などの整合性を検証し、rights status だけでは停止しない。
- bypass flag は不要。hard gate が存在しないため。

## 運用ルール

- ユーザーが一度説明した非交渉条件は本ファイルに固定する。
- 理由を「Why:」として 1 行残す。後でエッジケース判断ができるようにする。
- 日付固定の宣言（「2026-xx-xx 固定」等）は使わない。状態は [docs/RUNTIME_STATE.md](RUNTIME_STATE.md) に置く。

## 意思決定注記の最小仕様

対象: 新方針採用 / 方針撤回 / 主軸・slice・next_action 変更 / FEATURE status 遷移。
形式: `根拠: <源1> [+ <源2>]`
許容源: canonical docs 参照 / FEATURE ID / DECISION LOG 行。
禁止源: 「経験的に」「一般に」「安全上」など verifiable でない抽象文言。
