# OUT-13 Editorial Video Candidate v1

## このスライスで変わったこと

OUT-12は実sourceを安全に解析・再encode・検証する一コマンド経路を確立したが、実captionの
意味単位に基づいて「何を残し、何を落としたか」を入力として固定する編集判断は持っていなかった。
OUT-13はOUT-12を書き換えず、`build-editorial-video-candidate`を後継CLIとして追加した。
source identity / SHA、source in/out、output order、section、editorial role、selection reason、
continuity evidence、transcript segment IDs、transition、omitted rangesを明示planからTimeline IRへ
運び、実字幕を焼き込んだ一本のreviewable MP4と同じpackageで追跡できる。

状態は`AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1`から
`EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1`へ進んだ。これは編集構成・字幕presentation・
画面/音声品質を同一MP4で判断できるinternal review surfaceが成立したという意味であり、作品の
rights、production subtitle/design/render、thumbnail、public/publishing/uploadの承認ではない。

## 実artifact

| 対象 | 実績 | 判断に使えること |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-001` | plan、media、readback、evidence、reviewを一つのidentityで参照できる |
| source | `youtube:7J5aS_pcBj4`; provider `https://www.youtube.com/watch?v=7J5aS_pcBj4`; SHA `e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`; 164.768798s; 1920x1080 | 既存local official creator sourceを再利用し、新規取得や別repo依存を増やしていない |
| authority | official JA JSON3 SHA `3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`; imported transcript SHA `ef928d4e3b47e5ab522cf8292d08fefdc81fcda9c904551941158814cdfb42d6`; rights snapshot SHA `e6ea94717b3bffceaa7cda9c608d2d2ecb6a0a46233958a9113f058c73464c12` | 文言・timing・cut根拠は追跡可能。speaker、歌唱、歌詞、rights適否は推定しない |
| timeline | 6 chronological non-contiguous cuts、4 semantic sections、6 omitted ranges（うちintentional 4）、mapping coverage 1.0 | 三等分命名やuniform samplingではなく、導入→対戦展開→最終戦→終結の根拠をcut単位で監査できる |
| final MP4 | 122.866016s、source利用率74.542%、H.264 High/AAC、1920x1080、73,776,611 bytes、SHA `84ed7aa6fc7aa1d478d7fa8f8783e349a5ffa56a7a59dc49c30daafa0791d7e2` | sourceより明確に短い一本を、video-first reviewで全体判断できる |
| manifest | 23 payloads、input fingerprint `051832b95969d8d3e35709f359e82dacb719552343ad40ec39ce35381685e3d8`、self-integrity SHA `8f0be672d847ea7b066a6ec932790f91601fd499956987813ec7edc42b0c02e8` | 同じsource/plan/settingsだけがresumeでき、古い別inputの再利用をfail closedにできる |

selected rangesは`2.453–17.167`、`24.041–49.566`、`50.868–79.163`、
`79.163–93.477`、`100.617–120.204`、`121.672–142.059`。待機beat、短い移動、
反復battle action、反復叫声、source head、creditsをomitted rangesとして残し、待機・反復の短縮で
原因と結果が失われない理由を各rangeへ結び付けた。

## 字幕presentation

selected source rangesのcontact sheetでsource-nativeの対話captionがないことを確認し、sidecarとの
二重表示を避けた。公式JSON3の文言・timingは保持し、provider由来の改行だけを空白へ正規化してから
Pillow font-bboxで再ラップする。resolved presentationは次の通り。

| 読み戻し面 | 実resolved value | 検証結果 |
|---|---|---|
| font | requested/resolved `Keifont`; local file `keifont.ttf`; 100px、line height 115px | global installなし。actual resolved fileのSHAをmanifest/readbackへ記録 |
| body / accent | white `#ffffff`; speaker identity未確認のためbadge非描画 | caption textからspeakerを推定せず、存在しないspeaker色分けを作らない |
| edge | black outline 8px、black shadow 2px | 明暗・高彩度frame上の白文字を維持 |
| safe area | left/right 106px、bottom 92px、safe width 1708px | overflow 0 |
| line break | measured Japanese wrap、最大2行、複数行8 cue | 77 cue、overlap/negative/orphan/violationはいずれも0 |

通常発話`caption_0025`、長文2行`caption_0062`、0.534s短時間cue`caption_0039`をfinal
videoからPNG抽出し、contact sheetへまとめた。source-selected contact sheetと並べることで、burn-in後の
可読性と二重表示の不存在を一つのreview入口から比較できる。

## media・review検証

shipping codec、source-native aspect、duration/start、monotonic timestamps、faststart、full decode、
A/V sync、loudness、cut間loudness delta、black/silence、caption containment、source mappingの13基礎
checkに、explicit plan、cut/omission、shortening、caption evidence、subtitle presentationを加えた19項目が
passした。A/V duration deltaは0.003016s、integrated loudnessは-14.61 LUFS、true peakは-1.58 dBTP、
最大隣接cut差は0.94 LU、0.5s以上のblack eventと1.0s以上のsilence eventは0だった。

localhost reviewはpage 200 / MP4 Range 206、clean openで`paused=true` / `muted=true` /
`currentTime=0` / `readyState=4` / media errorなし。cut_002 seekは14.714sへ一致した。1440px desktopと
390px mobileでdocument overflowなし、console error/warning 0、展開したmachine validation 19項目の
表示を確認し、検証serverは終了した。

初回はprovider改行を固定改行として再ラップした1 cueが3行となり、presentation preflightでrender前に
停止した。failure evidenceを先に永続化するよう修正し、provider layout whitespaceの正規化と
`measured_width_by_line`を使う実幅検査を追加した。その結果、長文2 cueが3行になることを正しく検知し、
OUT-13専用の100px two-line scaleへ因果的に調整した。再実行後は77 cueすべてが最大2行・safe-area内で
passし、実renderと全後段検証まで完走した。

## 実行・再開

> 2026-07-23 current-checkout note: 以下はsource-hostで成立したhistorical command contract。
> current checkoutには`editorial_plan_input.json`とOUT-13 packageがなく、source/transcript/rights
> SHAも上記contractと一致しない。exact recoveryまたはnew identity rebuildを行うまで、旧command、
> localhost URL、`--resume`を現在利用可能とは扱わない。live authorityは
> [RUNTIME_STATE.md](../RUNTIME_STATE.md)と[CURRENT_HANDOFF.md](../CURRENT_HANDOFF.md)。

新規生成または入力変更後の明示再生成:

```powershell
uvx --with Pillow python -m src.cli.main build-editorial-video-candidate `
  --source episodes\jp_pilot01_hololive_bancho_20260525\materials\src_video_jp_pilot01\source_video.mp4 `
  --source-identity youtube:7J5aS_pcBj4 `
  --editorial-plan episodes\out13_editorial_video_candidate_20260722\editorial_plan_input.json `
  --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json `
  --caption-track episodes\jp_pilot01_hololive_bancho_20260525\source_subs\7J5aS_pcBj4.ja.json3 `
  --rights-manifest episodes\jp_pilot01_hololive_bancho_20260525\rights_manifest.json `
  --output-dir episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate `
  --force --review-port 8076 --format json
```

同一inputの整合確認と高速再開は`--force`を`--resume`へ替える。実runでは0.328s、render非実行、
同一video/manifest SHAを確認した。レビューを開く単一入口は次のcommandで、serverを閉じる時は
foreground PowerShellで`Ctrl+C`を使う。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate\review\open_preview.ps1
```

packageは`episodes/`配下のsame-machine ignored artifactであり、Git clone間ではportableではない。
tracked code/docs/testsだけを別hostへ持ち出した場合は、同一source/caption/transcript/rights/plan bytesを
用意して再生成する。`git ls-files episodes`は0件を維持する。

## 次の判断境界

次のconsumerはこの一本を見て編集構成、字幕presentation、画面・音声品質をまとめて判断するhuman
reviewである。ここでinternal editorial acceptanceを得てもrightsやproduction利用は自動で開かない。
production subtitle/render gateへ進む場合は、rights snapshotの判断、subtitle designのproduction採用、
public-ready renderの受理を別スライスで明示的に扱う。thumbnail、publishing、uploadは引き続き対象外。
