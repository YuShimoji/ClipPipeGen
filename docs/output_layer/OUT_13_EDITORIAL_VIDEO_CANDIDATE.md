# OUT-13 Editorial Video Candidate v4

## 到達した状態

OUT-13 は candidate 004 の media-reviewable bytes を保ったまま、manifest-bearing directory を
schema / state / identity / parseability に関係なく永久に不変化し、source video から transcript
audio、provider video identity から exact caption JSON3 までの content-sensitive lineage を
fail closed で束ねる v4 contract へ進んだ。active artifact は
`clip-out13-editorial-video-candidate-v1-005`、state は
`OUT13_CANDIDATE_005_IMMUTABLE_TRANSITIVELY_LINEAGE_BOUND_REVIEWABLE_V1`。

これは exact MP4 を人間が編集判断できる内部レビュー gate を開く状態である。rights、
production subtitle/design/render、thumbnail、publishing、upload、public release の承認ではない。

> Current-host note (2026-07-24): 以下の005 package値はsource-host machine receiptである。
> 現在の`DESKTOP-U9P4LKJ` checkoutにはcandidate 004 / 005のplan、package、MP4、launcherがなく、
> local review / resumeは利用できない。current availabilityとnext actionは
> [RUNTIME_STATE.md](../RUNTIME_STATE.md)を優先する。

## v4 contract で閉じたこと

| rule | previous | replacement | reason | affected consumers | migration | rollback |
|---|---|---|---|---|---|---|
| artifact identity | module 固定 `...-001` | CLI 必須 `--artifact-id`、`...-NNN`形式 | 同じ ID の上書き・別入力混同を防ぐ | CLI、pipeline state、manifest、review、resume | 新規候補は新 ID を明示 | v1 package は historical receipt として読むだけ |
| successful output | 現行 schema/state の successful directory だけ保護 | `run_manifest.json`を含む directory は malformed / unknown / legacy / same-ID / cross-ID を問わず不変。promotion は空 path の原子的 reservation 後だけ実行 | legacy candidate と promotion race の上書きを防ぐ | renderer、resume、failure reconciliation | correction は successor identity を作る | package child の修復・追記・置換はしない |
| journal isolation | caller が任意 journal path を渡せた | deterministic sibling だけを許し、package 自身/配下、`..` alias、symlink/junction alias を write 前に拒否 | failure/resume receipt が successful package や別 target を汚染しない | resume、failure reconciliation | sibling `.run_journal`だけを使う | override で回避しない |
| package integrity | recursive file set と hash を検査 | symlink / junction / external target を build と validate の両方で拒否し、actual payload を package root 内 regular files に限定 | manifest 内 path が external bytes を間接参照することを防ぐ | manifest validator、resume | v4 manifest を新候補へ生成 | link を regular file としてコピーしない |
| audio lineage | energy envelope correlation / lag / RMS が合否へ寄与 | energy envelope は coarse lag 推定だけに使い、符号付き PCM waveform similarity、正 gain、gain-aligned NRMSE、全域 coverage を合否根拠にする | equal-energy 別波形、極性反転、時間並べ替え、無関係・切詰め audio を拒否 | authority binding、manifest、review | source-audio fetch receipt と full-coverage readback を記録 | threshold を実pair向けに弱めない |
| caption authority | generic non-repo handoff が provider identity evidence になり得た | exact `youtube:VIDEO_ID` namespace と、anonymous yt-dlp 取得の provider locator / language / format / exact local hash receipt を必須化 | plan fabricated evidence、generic handoff、別動画 caption を trust root にしない | caption readback、authority binding、review | `caption_acquisition_receipt` evidence を plan で指定 | credentials/cookies/OAuth/MFA を使わない |
| rights / font | snapshot / family 名を記録 | path/hash/source identity と resolved font file hash を固定 | silent fallback と stale snapshot を防ぐ | render、review、manifest | exact file bytes を入力 fingerprint へ追加 | fallback は拒否し新候補を作らない |
| cut evidence | evidence ID を含める | range 内 eligible transcript ID と完全一致、context refs は別欄 | arbitrary evidence 追加と途中分割を防ぐ | plan validator、Timeline IR | v2 plan へ明示移行 | unsupported plan は render 前 failure |
| omitted ranges | 説明付き range | sorted / non-overlap / selected range と disjoint / source complement 完全一致 | 未説明 source hole をなくす | plan validator、review | source 0–duration の補集合を列挙 | 不一致なら failure |
| caption boundaries | containment 中心 | split / duplicate / missing / unexpected / mapping coverage まで検証 | cut 境界で字幕 evidence を壊さない | caption readback、validation | v2 readback に counts を追加 | count 非ゼロは candidate 不成立 |
| observation claim | machine check と visual 記述が混在 | package は `visual_observation=unverified`、人間/Worker 観察は別 receipt | 未観察を観察済みにしない | review、handoff | sampled observation を文書で分離 | machine pass だけで visual acceptance しない |
| review UI | 大きい hero、詳細が初期展開 | compact summary、details 初期閉鎖、cut 前後 seek、mobile overflow 防止 | 長尺 candidate の判断摩擦を下げる | 人間 reviewer | v2 page を使う | v1 page は historical |

`SCHEMA_VERSION`、plan、manifest、pipeline version は v4 に上がった。module-level fixed
`ARTIFACT_ID`は除去し、現在 identity は CLI 引数と validated plan からだけ解決する。

## active artifact 005

| 対象 | exact result | 判断に使えること |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-005` | plan、media、readback、review を一つの immutable closed-package identity で参照 |
| source | `youtube:7J5aS_pcBj4`、SHA `6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`、35,281,366 bytes、164.768798s、1920x1080 | Thank 上の receipt / ledger と一致する実 bytes |
| authority | transcript `4a7b4fd8...3495`、provider JSON3 `3c15535f...9919`、rights `4302c4a1...bb8`、font `d5795bdf...ed6f` | source lineage と表示 bytes を監査可能。speaker / lyric / rights 適否は推定しない |
| audio lineage | video PCM `48f9d946...44b8`、audio PCM `f608fd1a...fcfcd`、coverage `0.999647612317`、signed similarity `0.947803984`、gain `0.943714876`、NRMSE `0.318853585`、lag `0.036312s` | content-sensitive waveform、正 gain、全域 residual と source-audio fetch receipt を監査 |
| caption lineage | provider video ID `7J5aS_pcBj4`、anonymous acquisition receipt `aeff5613...90e4`、provenance `e4680280...65e` | credential なしの provider 再取得と exact JSON3 SHA の一致を監査 |
| plan | exact input SHA `27ef1aa9d7aa29267e43d4b9b33dc17051acbf8f5b38dc4a3b50649e1ca6dac2` | 004 の cut / section / caption / typography / render contract は変えず identity / evidence schema だけを v4 化 |
| timeline | 7 chronological cuts、5 semantic sections、8 omitted ranges、128.795s、coverage 1.0 | 選択 range と source complement の全体を監査 |
| caption | provider sidecar 102 cues、split / duplicate / missing / unexpected / overlap / negative / orphan 0 | cut 境界で evidence を分割・重複・欠落させていない |
| final MP4 | H.264 High / AAC / yuv420p、1920x1080、128.833333s、82,594,810 bytes、SHA `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5` | exact human review target |
| manifest | 24 payload rows + excluded `run_manifest.json`、payload digest `8257a15c...c054`、fingerprint `bbeb2514...a6a0b`、self SHA `5d7550a7...d32b` | actual 25-file package の link-free closed-set integrity を検証 |
| package | 25 files / 87,123,995 bytes、tree digest `ed45fd4c486d1945dbbe32a8bfbbb218b9f6e1ff7263e83d0cdcf34c38e93040` | resume と rejected allocation の前後で complete tree が不変 |

selected source ranges は `2.453–17.167`、`22.606–24.041`、`25.109–49.566`、
`50.868–79.163`、`81.298–94.945`、`95.345–116.467`、`116.934–142.059`。
omitted ranges は source head、発話間 wait、重複 provider cues の bounded interval、短い action
beat、resolution 後 tail を source 0–164.768798s の完全な補集合として記録する。

## subtitle・media・review検証

Keifont の exact bytes を使い、100px、line height 115px、black outline 8px、shadow 2px、
最大2行で burn-in した。102 cue の mapping coverage は 1.0。full decode、faststart、
monotonic timestamps、A/V sync、loudness、cut 間 loudness、black/silence、caption containment、
source mapping、authority binding、subtitle presentation、explicit plan / omission checks は pass。

media readback は -14.48 LUFS、-1.88 dBTP、最大隣接 cut 差 1.85 LU、A/V duration delta
0.011333s、black / silence event 0。初回 render は 1 回、corrective render は 0 回。

review server は page 200、MP4 Range 206。browser smoke で横 overflow なし、4 evidence images
loaded、7 cut / 8 omission / 14 seek controls、video paused / muted / time 0 / readyState 4 /
1920x1080 / 128.833333s、console / media warning・error 0 を確認した。一方、package 内の
`visual_observation.status`は `unverified` のまま保持する。full decode と browser smoke は
人間が全編を視聴した証拠ではない。

## 実行・再開

新しい candidate は artifact ID と新しい空 output directory を必須にする。

```powershell
uvx --with Pillow python -m src.cli.main build-editorial-video-candidate `
  --artifact-id clip-out13-editorial-video-candidate-v1-005 `
  --source episodes\jp_pilot01_hololive_bancho_20260525\materials\src_video_jp_pilot01\source_video.mp4 `
  --source-identity youtube:7J5aS_pcBj4 `
  --editorial-plan episodes\out13_editorial_video_candidate_20260723\editorial_plan_input_v005.json `
  --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json `
  --caption-track episodes\jp_pilot01_hololive_bancho_20260525\source_subs\7J5aS_pcBj4.ja.json3 `
  --rights-manifest episodes\jp_pilot01_hololive_bancho_20260525\rights_manifest.json `
  --output-dir episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005 `
  --review-port 8076 --format json
```

同じ exact candidate の整合確認は末尾へ `--resume`を加える。実runは render 非実行、
`editorial_plan` / `caption_presentation` / `render` / `media_validation` / `review_package` の
5 cache hits、同じ final / manifest SHA と package-tree digest 前後一致を確認した。resume readback と
rejected allocation failure は package 外の
`episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005.run_journal\`
にだけ書かれる。成功済み candidate に `--force`は使わない。

レビュー入口:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\open_preview.ps1
```

package は `episodes/`配下の same-machine ignored artifact で、Git clone 間では portable ではない。
別hostでは exact inputs / plan / package を承認済み private transfer で回収して hash 照合するか、
別 artifact ID で再生成する。`git ls-files episodes`は空を維持する。

## 001–004 の履歴

- `...-001`は別 source-host の exact inputs / final SHA `84ed7aa6...791d7e2`へ結び付く historical
  receipt。この Thank checkout の active candidate とは呼ばない。
- `...-002`は Thank 上の初回 immutable rebuild。media bytes は成立したが、caption mode を
  `official_sidecar`と表示し、review の plan SHA が入力 bytes ではなく packaged
  reserialization を指したため、人間受理対象から外した。
- `...-003`は上の事実表現を訂正した media-reviewable successor。package immutability と transitive
  lineage が未完了だったため、accepted / rejected とはせず 26-file technical predecessor evidence
  として開始時 inventory のまま保存した。
- `...-004`は cut selection、sections、captions、typography、render settings を変えず、closed package
  と transitive lineage を修復した。final MP4、SRT、ASS、subtitle presentation は 003 と byte-identical。
  Timeline IR は schema version だけが変わり、編集 mapping は同一。
- `...-004`は verdict 未記録の parallel human-review target として開始時 tree digest
  `970297cd...829`のまま保持した。005 は同じ final MP4 / SRT / ASS / subtitle presentation を持ち、
  strong immutability、content-sensitive audio、canonical caption receipt だけを修復する。

## 次の判断境界

次の consumer は exact candidate 005 を全編視聴する人間 reviewer である。candidate 004 は
parallel target として verdict 未記録で保持する。`accept`なら internal
editorial acceptance だけを candidate SHA へ bindする。`repair`なら cut / caption / timestamp と
観察事実を限定し、006 以降の successor identity で直す。`reject`なら理由と reuse 禁止範囲を残す。
どの判断も rights、production、thumbnail、publishing、upload、public release を自動で開かない。
