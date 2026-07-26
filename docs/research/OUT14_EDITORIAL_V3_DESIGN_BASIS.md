# OUT-14 editorial presentation v3 — pre-generation design basis

この記録は `CPG-OUT14-EDITORIAL-PRESENTATION-RECONSTRUCTION-V3 / attempt_id 1`
の最初の direction-generating mutation である。公開実例は、mission 専用の
fresh temporary Chrome user-data-dirを用い、Incognito、extensions disabled、
sync disabled、CDP cache disabled、signed-outで観測した。通常のDefault profile、
保存済みcookie、ログイン、履歴、Home、おすすめ欄は使っていない。

競合画像・映像・音声・字幕は保存、取得、download、repoへの収録をしていない。
下表はブラウザー上に一時表示されたactual surfaceの観測記録だけであり、
各実例のtitle、layout、copy、装飾を再利用する許可または根拠ではない。

## Actual-surface observation ledger

共通 `checked_at` は観測バッチを閉じた
`2026-07-27T04:49:56.606+09:00`。video surfaceはviewport
`1280x900`、zoom `100%`、thumbnail surfaceはviewport
`320x180`、zoom `100%`。全件のprofile modeは
`fresh-temporary-incognito`、account_stateは`signed_out`。

| URL | channel | title | timestamp | 観測surface | 観測限界 |
|---|---|---|---|---|---|
| https://www.youtube.com/watch?v=vscte5LUT0Q | ホロライブ毎日切り抜き | 「これ全体通知いくんだよ」深夜4時にDiscordを誤爆し全スタッフに謎の通知を送った大空スバル【大空スバル/切り抜き】#shorts | `00:13.862`, `00:24.138` | `320x180` thumbnail。縦型video上の固定hook、情報面、下部speech captionをactual decoded frameで観測。 | 冒頭24.1秒まで。静止的構成のため、長尺編集のtransition根拠には使わない。 |
| https://www.youtube.com/watch?v=3roZ4SVv5YU | ホロライブの部屋【切り抜きch】 | 【まとめ】人知れぬところでリスナー大絶賛の名言を残していた博衣こより【ホロライブ/ホロライブ切り抜き】 | `00:14.340`, `00:24.570` | `320x180` thumbnail。通常speech captionから中央の`ｗｗｗ` reactionへ切り替わるactual decoded frameを観測。 | 冒頭24.6秒まで。全編のrole coverageは未観測。 |
| https://www.youtube.com/watch?v=IywCDYmfBtM | ホロライブの部屋【切り抜きch】 | すいちゃんのVTuber業界ではありえない行動を見て改めて凄さを認識するさくらみこ【ホロライブ/ホロライブ切り抜き】 | `00:29.607`, `00:39.893` | `320x180` thumbnail。通常speech captionと、別人物の発話をspeech balloonと小さなidentity graphicで分離したactual decoded frameを観測。 | 冒頭39.9秒まで。identityの正しさは当該動画の表示範囲だけを観測。 |
| https://www.youtube.com/watch?v=qHL0Bxbnie8 | ホロライブの部屋【切り抜きch】 | 『ホロぐらおかしいのでは？』と聞いたスタッフからの返事が狂気過ぎたと語る大空スバル【ホロライブ/ホロライブ切り抜き】 | `00:14.513`, `00:24.789` | `320x180` thumbnail。`ｗｗｗ` reaction、source人物の挿入、下部speech captionへ進むactual decoded frameを観測。 | 冒頭24.8秒まで。挿入素材の権利状態や制作方法は観測対象外。 |
| https://www.youtube.com/watch?v=YecJTYBbmTM | せんぱい【ホロライブ切り抜き】 | 【厳選】笑いどころを凝縮したラミィちゃんと雪民さんの濃過ぎる大喜利雑談まとめｗｗｗ【ホロライブ/切り抜き/hololive/雪花ラミィ/雑談/大喜利/演出切り抜き】 | `00:14.506`, `00:24.724` | `320x180` thumbnail。人物とgraphic primitiveで説明を保持する画面から、speech balloonを持つ会話画面へ切り替わるactual decoded frameを観測。 | 冒頭24.7秒まで。外部graphicやportraitをv3へ転用しない。 |
| https://www.youtube.com/watch?v=Zln8EAie3_c | せんぱい【ホロライブ切り抜き】 | 公式マスコット面接で“リッキー＆ブッキー”がライン際でやりたい放題した結果ｗｗｗ【ホロライブ/切り抜き/hololive/鷹嶺ルイ/白上フブキ/響咲リオナ/ホロライブランド】 | `00:14.786`, `00:25.167` | `320x180` thumbnail。単独人物のspeech画面から、複数人物を前後分離しpunchline captionを置く画面へのactual decoded cutを観測。 | 冒頭25.2秒まで。人物asset、costume、copy、layoutは参照実装しない。 |
| https://www.youtube.com/watch?v=aKq9PlmBgJg | ホロライブ切り抜きch / 永遠の闇 | ツボに入ったら笑いが止まらないお嬢のクセになる爆笑シーン11連発まとめ【ホロライブ切り抜き/百鬼あやめ | `00:14.392`, `00:24.941`, `00:47.565` | `320x180` thumbnail。色付きspeaker cue、複数人物の常設分離、末尾`w`付きreaction captionをactual decoded frameで観測。 | 冒頭47.6秒まで。speaker identityは表示上のcueだけを観測。 |
| https://www.youtube.com/watch?v=nTjuOBvPhyk | ホロライブ切り抜きch / 永遠の闇 | ツボって笑いから抜け出せないぺこらの面白可愛い爆笑シーン13連発【兎田ぺこら/ホロライブ切り抜き】 | `00:13.963`, `00:24.276`, `00:54.420` | `320x180` thumbnail。通常speech caption、結果graphicを重ねたbeat、末尾`w`付きreaction captionをactual decoded frameで観測。 | 冒頭54.4秒まで。ゲーム画面内UIとcreator-added graphicの制作系統は判定しない。 |
| https://www.youtube.com/watch?v=Vdd_WvohXg8 | ホロライブ毎日切り抜き | 「僕とじゃ楽しくないってこと？」猫又おかゆが妬いてスバルに拗ねるかわいい瞬間【白上フブキ/切り抜き】#shorts | `00:13.799`, `00:24.002` | `320x180` thumbnail。縦型summary hookと複数人物を含むsource/game surfaceのactual decoded frameを観測。 | 冒頭24.0秒まで。source内speaker表示とcreator-added captionを完全には分離できないため、speaker stylingの正例には使わない。 |

### 構造読戻し

この表は装飾やcopyの採用表ではなく、各actual surfaceで観測できた構造と、
観測できなかった範囲を分離するためのreadbackである。thumbnail copyは文章を転記せず、
階層数と役割だけを記録した。

| video | thumbnail copy hierarchy | 人物／対象の分離 | speaker／quote cue | reaction typography／motion | transition／explanation |
|---|---|---|---|---|---|
| `vscte5LUT0Q` | 縦型hook 1階層＋source面 | 単独人物と情報面 | 下部speech。引用分離は観測せず | reactionは観測範囲外。motion判定不能 | 冒頭24.1秒は固定的。長尺bridge根拠にしない |
| `3roZ4SVv5YU` | 人物＋短い主hook | 人物とsource背景 | 通常speech | 中央`ｗｗｗ`へrole変更。小幅motion有無は判定不能 | reaction beatへのcutを観測。説明surfaceは未観測 |
| `IywCDYmfBtM` | 人物関係を主従2階層 | 主話者と引用対象を別領域化 | speech balloon＋小identity cue | 強いreactionは未観測 | 通常speechからquote surfaceへの意味transition |
| `qHL0Bxbnie8` | 主hook＋人物 | source人物挿入を別面化 | 通常speech | `ｗｗｗ`を通常speechと別role化。motion判定不能 | reaction→挿入→speechのcut。素材権利は判定外 |
| `YecJTYBbmTM` | 人物＋状況graphic | 人物とgraphic primitive | speech balloonで会話差 | 笑いcopyはtitle側のみ、動画motionは未確定 | graphic説明→会話surfaceのsection cut |
| `Zln8EAie3_c` | 複数人物＋punchline | 前後レイヤーで人物分離 | speaker色/name cueは限定的 | punchlineを通常speechより強調 | 単独→複数人物のsemantic cut。素材は非採用 |
| `aKq9PlmBgJg` | 複数人物＋短いreaction | 常設の人物分離 | 色付きspeaker cue | 末尾`w`付きreaction。motionはactual範囲で断定せず | 複数episode間のcutを観測。説明cardは未観測 |
| `nTjuOBvPhyk` | 人物＋結果graphic | source/gameとcreator graphic | 通常speech | 末尾`w`付きreaction | 通常speech→結果graphic→reactionのbeat change |
| `Vdd_WvohXg8` | 縦型summary hook | 複数人物とgame surface | source表示とcreator captionを分離不能 | reaction roleは観測範囲外 | 冒頭24.0秒のみ。speaker design basisから除外 |

横断して採用するのは、`normal / quote / reaction / explanation`を同型にしないこと、
material jumpを知覚可能にすること、thumbnailをsetup＋consequenceの二意味単位にすることだけ。
各channel固有の文字、色、portrait、speech balloon、layout、motionはv3へ持ち込まない。

## Predeclared direction signature

`CPG-OUT14-V3-DIRSIG-20260727-A`

このsignatureは実装前に固定する。v3は以下を同時に満たす。

1. **Thumbnail — discovery/relation-led**
   - 選定案は「遊びのプロフィール変更」から「スタッフ全体への予期しない到達」へ進む
     setup＋consequenceの二単位構成。
   - reaction-led案はrunner-upに残す。
   - source-derived frame/crop/montageとcreator text/graphic primitiveだけを使う。
   - raw screenshot一枚構成、全幅半透明黒帯、外部portrait、生成画像は使わない。

2. **Caption hierarchy — five explicit roles**
   - `normal_speech`: 大空スバルの現在発話。下部、最大2行、phrase-aware。
   - `quoted_speech`: 証拠でidentityを確定できた引用だけ。name cue、quote frame、
     member accentを持ち、通常speechと同型にしない。
   - `laughter_reaction`: mildは`(笑)`、strongは`ｗｗｗ`。強い笑いの一部だけ、
     deterministicな1–4px micro-motionを許す。
   - `punchline_emphasis`: 短い語句だけ。通常caption全文へ常用しない。
   - `creator_explanation`: source footageまたはsource-derived stillをanchorにし、
     compact panelとepisode accentで説明する。full black＋white textを使わない。

3. **Speaker truth**
   - narrating Subaru、verified quoted identity、paraphrase、creator explanationを
     manifest上で別roleにする。
   - identity不明またはparaphraseを、Holomemのverbatim live speechとして演出しない。
   - portraitを追加しない。

4. **Transitions**
   - 8 boundaryを同一scene omission、semantic beat、time jump、
     explanation/ending、intentional hard cutへ分類する。
   - `~02:48`と`~06:27`を含むmaterial jumpには可視または可聴のbridgeを与える。
   - 全boundaryへ同じfadeを適用しない。

5. **Timing**
   - v2で受理されたperceptual timingをbaselineとし、layout-only cueは時刻不変。
   - merge/splitはcanonical word timingだけから決める。
   - unaffected cueのonset/end deltaは`0`、changed cueのmedianは
     `-100..+100ms`、p95 absolute deltaは`<=300ms`をgateにする。

6. **Review order**
   - selected `320x180` / `160x90`、runner-up、full video、changed probesの順。
   - `1280x720`はzoom確認用に限定する。

このsignatureはpublic実例のcopyやlayoutを複製する指示ではない。v2のhuman verdictを
cause-owned requirementsへ変換し、v3固有のsource bytesとcanonical timingにだけ適用する。
