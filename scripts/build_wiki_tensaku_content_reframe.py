from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EPISODE_ROOT = REPO_ROOT / "episodes/wiki_tensaku_family_20260804"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/content_planning/wiki_tensaku_content_reframe_v1"

WORK_ORDER_ID = "CPG-WIKI-CONTENT-REFRAME-001"
ARTIFACT_ID = "wiki-tensaku-content-reframe-v1-001"
AUDIENCE_PROMISE = (
    "配信を知らない視聴者でも、本人たちが非公式Wikiを読み、訂正し、忘れていた出来事や語録を"
    "再解釈する過程から、ファンの記録が本人像をどう作り直すかを4本で理解できる。"
)

EXPECTED_SOURCES: dict[str, dict[str, Any]] = {
    "1AcId5Yja10": {
        "source_id": "youtube:1AcId5Yja10",
        "duration_seconds": 5558,
        "media_relative_path": "corpus/materials/1AcId5Yja10/source_video.mp4",
        "media_bytes": 197_524_102,
        "media_sha256": "a994228674d0a6756f8747cf6a07b2cc4c4601fdbf98d5ca0bea3ee2f32060e7",
        "caption_relative_path": "corpus/captions/1AcId5Yja10.ja.json3",
        "caption_sha256": "f58c248f23b29845a94ae01b789f122c8759687125375a2650cc7a8074107e4f",
        "media_state": "exact_source_bytes_available",
        "acquisition_scope": "retained exact public-source bytes; no new acquisition",
        "content_topics": [
            "非公式Wikiと公式プロフィールの差",
            "大空スバルのプロフィール訂正",
            "忘れていた出来事と後年の達成",
            "語録・読み間違い・関係性",
        ],
    },
    "82iRbxjvbww": {
        "source_id": "youtube:82iRbxjvbww",
        "duration_seconds": 6418,
        "media_relative_path": None,
        "media_bytes": None,
        "media_sha256": None,
        "caption_relative_path": "corpus/captions/82iRbxjvbww.ja.json3",
        "caption_sha256": "42cc8ae804d8ca2d4e7a7185264a3d7930724a55f5162c09b1b4b86bbd37c3e3",
        "media_state": "exact_source_bytes_unavailable",
        "acquisition_scope": (
            "parked source gate; no guessed retrieval, cookies, OAuth, or anonymous retry"
        ),
        "content_topics": [
            "宝鐘マリンの語録と由来",
            "過去衣装・収益化判断の時代差",
            "友人の証言が自己認識を変える場面",
            "Wiki調査後のゲーム区間",
        ],
    },
    "Ocqg-RpQURY": {
        "source_id": "youtube:Ocqg-RpQURY",
        "duration_seconds": 3522,
        "media_relative_path": None,
        "media_bytes": None,
        "media_sha256": None,
        "caption_relative_path": "corpus/captions/Ocqg-RpQURY.ja.json3",
        "caption_sha256": "a383ad8a545fe9a24da142dace96fe19f05bf834a03e1e52616a5332db3c3992",
        "media_state": "exact_source_bytes_unavailable",
        "acquisition_scope": (
            "parked source gate; no guessed retrieval, cookies, OAuth, or anonymous retry"
        ),
        "content_topics": [
            "桃鈴ねねのページ構造と情報量",
            "家族由来の挨拶と忘れていた言葉",
            "言い間違いが共有言語になる過程",
            "みこ・スバルとの語録の交差",
        ],
    },
}

PROBES = [
    {
        "artifact_id": "clip-wiki-tensaku-family-turn-v1-001",
        "bytes": 21_800_858,
        "sha256": "1f965e537d5a767d8cfe5c456ed0481ea88a119743f207ada9764bbc0ebe3284",
    },
    {
        "artifact_id": "clip-wiki-tensaku-family-turn-v2-001",
        "bytes": 19_951_636,
        "sha256": "2736f6ec5b4a779a70c978d7815639802dee2d294220fdbb592edb9d75fe2dca",
    },
    {
        "artifact_id": "clip-wiki-tensaku-family-turn-v3-001",
        "bytes": 20_605_376,
        "sha256": "5abfd8e940bd8a2709e79aced38ab2e0e56b7f052f3d205512e082d2a8f8733b",
    },
    {
        "artifact_id": "clip-wiki-tensaku-family-turn-v4-001",
        "bytes": 18_884_819,
        "sha256": "5fea3d14e476871f239d1ab42283fedd83546daf98e8c5a27f625506ba69ca40",
    },
    {
        "artifact_id": "clip-wiki-tensaku-family-turn-v5-001",
        "bytes": 19_964_780,
        "sha256": "e192fcd6746d396c0c92b5952c274cf5afd07f47c0f5d3a17deecd33b658012c",
    },
]


CLIP_SPECS: list[dict[str, Any]] = [
    {
        "clip_id": "CU-01",
        "episode_id": "E1",
        "chapter_number": 1,
        "chapter_title": "非公式Wikiは何を記録しているのか",
        "source_video_id": "1AcId5Yja10",
        "requested_start_seconds": 390,
        "requested_end_seconds": 510,
        "topic": "非公式Wikiの役割と公式情報との差",
        "speaker": "さくらみこ・大空スバル",
        "setup": "二人が非公式Wikiを開き、Wikipediaや公式プロフィールとは違う読み物だと確認する。",
        "core_statement": "ファンが選んだ出来事や言葉の熱量によって、同じ人物でもページの像が変わる。",
        "payoff_or_conclusion": "Wiki添削は誤字探しではなく、ファンが作った人物像を本人が読み返す企画だと定義する。",
        "required_prior_context": "番組開始と、今回読む対象が非公式Wikiであるという宣言。",
        "required_following_context": "別のページでは何が人物像として強調されるかを比較する。",
        "chapter_contribution": "シリーズ全体の観察レンズを提示する。",
        "transition_in": "完成品の先頭。題材と見方を最初に固定する。",
        "transition_out": "同じWikiでも人物ごとに記録のされ方が違う、という比較へ進む。",
        "selection_reason": "題材・話者・目的が一続きで説明され、初見視聴者の入口になる。",
        "exclusion_risk": "導入を短くしすぎると、単なるプロフィール読み上げに見える。",
        "viewer_question": "非公式Wikiを見ると本人の何が分かるのか。",
        "evidence": "二人がページの作成主体と公式情報との差を会話で確認する。",
        "interpretation": "ページは事実の羅列ではなく、ファンが残したい記憶の編集物である。",
        "conclusion": "以後の訂正・回想・語録を、人物像の更新として見る。",
    },
    {
        "clip_id": "CU-02",
        "episode_id": "E1",
        "chapter_number": 2,
        "chapter_title": "情報量が示す桃鈴ねね像",
        "source_video_id": "Ocqg-RpQURY",
        "requested_start_seconds": 390,
        "requested_end_seconds": 585,
        "topic": "ページ構造と人物像の強調点",
        "speaker": "さくらみこ・桃鈴ねね",
        "setup": "桃鈴ねねの非公式Wikiを上から確認し、衣装・来歴・好みの項目量を見る。",
        "core_statement": "ページの厚い箇所から、ファンが追ってきた変化やキャラクター像が見える。",
        "payoff_or_conclusion": "網羅量そのものではなく、何に記述が集まるかがその人の見え方を作る。",
        "required_prior_context": "CU-01で非公式Wikiをファン編集の人物記録と定義していること。",
        "required_following_context": "本人の自己紹介とWiki記述が一致するかを検証する。",
        "chapter_contribution": "人物ごとに異なるページ構造を比較可能にする。",
        "transition_in": "抽象的な定義から、実際のページ構造の違いへ移る。",
        "transition_out": "ページの強調点を、本人の訂正が最も多いプロフィール項目へ接続する。",
        "selection_reason": "ページ全体の見取り図から具体的な人物像まで会話が連続する。",
        "exclusion_risk": "後半の無関係な好物雑談まで延ばすと章の問いがぼやける。",
        "viewer_question": "ページの情報量は人物の何を強調するのか。",
        "evidence": "衣装、活動履歴、好きなものの項目を順に読み、記述量へ反応する。",
        "interpretation": "ファンの注目が集まった変化ほど、ページ上の人物像を強くする。",
        "conclusion": "次はページの記述と本人の認識がずれる箇所を確かめる。",
    },
    {
        "clip_id": "CU-03",
        "episode_id": "E1",
        "chapter_number": 3,
        "chapter_title": "プロフィール訂正で像が動く",
        "source_video_id": "1AcId5Yja10",
        "requested_start_seconds": 1530,
        "requested_end_seconds": 1905,
        "topic": "大空スバルのプロフィール訂正とアヒル像の由来",
        "speaker": "さくらみこ・大空スバル",
        "setup": "大空スバルの非公式プロフィールを開き、過去タグや身長などを本人が読み直す。",
        "core_statement": "本人が忘れた情報、現在は違う情報、ファンに定着したアヒル像が同じページに共存する。",
        "payoff_or_conclusion": "訂正してもファンの記憶は消えず、公式と非公式の間に現在の人物像ができる。",
        "required_prior_context": "ページ構造がファンの関心を可視化するというCU-02の結論。",
        "required_following_context": "次Episodeで、プロフィールより具体的な出来事の記憶へ進む。",
        "chapter_contribution": "シリーズの主題である『記録と本人認識の往復』を具体化する。",
        "transition_in": "ページの情報量から、情報の正しさと定着の仕方へ焦点を移す。",
        "transition_out": "訂正で終わらず、ページが忘れた出来事をどう呼び戻すかへ進む。",
        "selection_reason": "プロフィール、訂正、ミーム由来、受け止めまで因果が完結する。",
        "exclusion_risk": "アヒル像だけ抜くと、公式情報との比較と本人の受け止めが失われる。",
        "viewer_question": "本人が訂正すると、ファンが作った人物像はどう変わるのか。",
        "evidence": "忘れたタグ、身長の訂正、アヒル像の由来を本人たちが順に検証する。",
        "interpretation": "訂正は記録の否定ではなく、現在の本人像を重ねる更新である。",
        "conclusion": "人物像は公式説明とファンの記憶の往復で更新される。",
    },
    {
        "clip_id": "CU-04",
        "episode_id": "E2",
        "chapter_number": 1,
        "chapter_title": "古い挑戦が現在の達成へつながる",
        "source_video_id": "1AcId5Yja10",
        "requested_start_seconds": 2520,
        "requested_end_seconds": 2865,
        "topic": "忘れていた投稿と後年の目標達成",
        "speaker": "さくらみこ・大空スバル",
        "setup": "プロフィールからエピソード欄へ移り、本人も忘れた初期の投稿と企画を読む。",
        "core_statement": "当時は達成できなかった目標が、Wikiに残った記録を介して現在のアルバムやソロライブへつながる。",
        "payoff_or_conclusion": "アーカイブは失敗談を晒すだけでなく、時間を超えた達成の意味を可視化する。",
        "required_prior_context": "E1でWikiを人物像の更新装置として理解していること。",
        "required_following_context": "個人の出来事から、家族や仲間が覚えている言葉へ移る。",
        "chapter_contribution": "記録の時間軸が現在の解釈を変える例を示す。",
        "transition_in": "プロフィールの静的情報から、時間を持つ出来事へ移る。",
        "transition_out": "本人が忘れていても他者が覚えている記憶へ広げる。",
        "selection_reason": "過去の投稿、忘却、現在の達成、再解釈が一つの因果線になる。",
        "exclusion_risk": "古い投稿だけ抜くと失敗いじりになり、現在の達成という結論が消える。",
        "viewer_question": "忘れた過去の記録は、今の本人に何を返すのか。",
        "evidence": "初期投稿の目標と、後年のアルバム・ソロライブを会話で結び直す。",
        "interpretation": "Wikiは過去と現在を比較できる時間軸として機能する。",
        "conclusion": "古い記録の価値は、現在との接続で初めて生まれる。",
    },
    {
        "clip_id": "CU-05",
        "episode_id": "E2",
        "chapter_number": 2,
        "chapter_title": "家族が覚えていた挨拶",
        "source_video_id": "Ocqg-RpQURY",
        "requested_start_seconds": 2010,
        "requested_end_seconds": 2160,
        "topic": "家族由来の挨拶と言葉の再発見",
        "speaker": "さくらみこ・桃鈴ねね",
        "setup": "語録欄で『いらっしゃいニングビーム』を見つけ、由来を本人にたずねる。",
        "core_statement": "家族との日常で使っていた言葉がファンの記録に残り、本人はそこで初めて由来ごと思い出す。",
        "payoff_or_conclusion": "記録は本人だけでなく、周囲との関係を含む記憶を現在へ戻す。",
        "required_prior_context": "CU-04で古い記録が現在の意味を更新したこと。",
        "required_following_context": "記録が当時の規範や環境の違いまで映す例へ進む。",
        "chapter_contribution": "個人の記憶から関係性の記憶へ視野を広げる。",
        "transition_in": "公的な活動記録から、家庭内の小さな言葉へ縮尺を変える。",
        "transition_out": "個人的な記憶の復元から、時代背景を伴う記録の再解釈へ進む。",
        "selection_reason": "語句、由来、忘却、再使用の意思まで短い因果が完結する。",
        "exclusion_risk": "語句だけ抜くと意味不明な奇声になり、家族由来の価値が消える。",
        "viewer_question": "本人が忘れた言葉を、誰の記憶が残しているのか。",
        "evidence": "Wikiの語句から家族との使用場面を思い出し、また使いたいと話す。",
        "interpretation": "ファンの記録は本人の外側にある記憶も保存している。",
        "conclusion": "人物の来歴は、周囲との言葉の交換からも作られる。",
    },
    {
        "clip_id": "CU-06",
        "episode_id": "E2",
        "chapter_number": 3,
        "chapter_title": "昔の衣装を今の基準で読み直す",
        "source_video_id": "82iRbxjvbww",
        "requested_start_seconds": 2700,
        "requested_end_seconds": 2825,
        "topic": "過去衣装・収益化判断・配信環境の変化",
        "speaker": "さくらみこ・大空スバル・宝鐘マリン",
        "setup": "過去の衣装や露出についてのWiki記述から、当時の配信上の扱いを確認する。",
        "core_statement": "当時は許容された表現でも、現在の収益化やプラットフォーム基準では違う意味を持つ。",
        "payoff_or_conclusion": "Wikiの出来事は固定評価ではなく、時代と環境を添えて読み直す必要がある。",
        "required_prior_context": "過去と現在を接続して意味を更新するE2前半。",
        "required_following_context": "E3で、出来事から言葉そのものの継承へ焦点を移す。",
        "chapter_contribution": "記録の解釈に時代背景が必要だと示す。",
        "transition_in": "個人の記憶から、プラットフォーム環境という外部条件へ広げる。",
        "transition_out": "出来事をどう解釈するかから、言葉がどう残るかへ転じる。",
        "selection_reason": "過去の事実、現在の基準、参加者の解釈が同じ会話で閉じる。",
        "exclusion_risk": "衣装の一言だけでは扇情的になり、時代差という論点を失う。",
        "viewer_question": "過去の出来事を今の基準だけで評価してよいのか。",
        "evidence": "衣装、収益化、当時と現在の運用差を三人が順に結びつける。",
        "interpretation": "記録は出来事と同時に、その時代の制度も残す。",
        "conclusion": "Wiki添削には事実訂正だけでなく文脈の補足が必要になる。",
    },
    {
        "clip_id": "CU-07",
        "episode_id": "E3",
        "chapter_number": 1,
        "chapter_title": "語録欄はなぜ増殖するのか",
        "source_video_id": "1AcId5Yja10",
        "requested_start_seconds": 3180,
        "requested_end_seconds": 3490,
        "topic": "エピソード欄から語録欄への移行と量の意味",
        "speaker": "さくらみこ・大空スバル",
        "setup": "出来事欄を読み終え、警告されるほど大量の語録欄へ進む。",
        "core_statement": "語録は正しい名言集ではなく、反復され共有された言葉の履歴として増える。",
        "payoff_or_conclusion": "言葉の量は、ファンと配信者が共同で作った共有言語の厚みを示す。",
        "required_prior_context": "E2でWikiが出来事の時間軸を保存すると理解していること。",
        "required_following_context": "個々の読み間違いがどのように語録化するかを検証する。",
        "chapter_contribution": "語録を単発の面白発言ではなく蓄積として定義する。",
        "transition_in": "出来事の記憶から、繰り返される言葉の記憶へ移る。",
        "transition_out": "大量の語録の中から、意味が変わった具体例へ入る。",
        "selection_reason": "章移動、語録量への反応、語録の読み方までセットで提示される。",
        "exclusion_risk": "語録の一項目から始めると、なぜそれを読むかが視聴者に伝わらない。",
        "viewer_question": "なぜ言い間違いや口癖が大量に保存されるのか。",
        "evidence": "語録欄の量と注意書きを見て、二人が記憶の蓄積として反応する。",
        "interpretation": "反復と共有が、普通の発話を共同体の言葉へ変える。",
        "conclusion": "次章から語録化の具体的な仕組みを読む。",
    },
    {
        "clip_id": "CU-08",
        "episode_id": "E3",
        "chapter_number": 2,
        "chapter_title": "読み間違いに文脈を戻す",
        "source_video_id": "1AcId5Yja10",
        "requested_start_seconds": 3880,
        "requested_end_seconds": 4140,
        "topic": "読み間違いと語録化された場面の訂正",
        "speaker": "さくらみこ・大空スバル",
        "setup": "Wikiに並んだ読み間違いを一つずつ読み、元の場面を思い出す。",
        "core_statement": "文字だけでは誤りに見える発話も、当時の状況と反応を戻すと共有された笑いになる。",
        "payoff_or_conclusion": "語録の添削は正しい読みへの置換ではなく、成立した場面を保存する作業になる。",
        "required_prior_context": "CU-07で語録を共有言語の履歴と定義していること。",
        "required_following_context": "同じ間違いを複数人が共有する場合へ広げる。",
        "chapter_contribution": "語録にsetupとpayoffが不可欠だと実例で示す。",
        "transition_in": "語録欄全体の意味から、個別の発話と場面へズームする。",
        "transition_out": "個人の言い間違いから、参加者間で共有される言葉へ進む。",
        "selection_reason": "発話、誤り、元の文脈、現在の解釈が連続して読める。",
        "exclusion_risk": "誤読だけ切ると本人を笑うだけの素材になり、Wiki添削の意味が失われる。",
        "viewer_question": "語録を面白くしたのは言葉自体か、その場面か。",
        "evidence": "二人が語句を読み、当時の状況と反応を補って意味を再構成する。",
        "interpretation": "発話の価値は誤りではなく、共有された場面にある。",
        "conclusion": "文脈を戻すことで、語録は人物攻撃ではなく共同記憶になる。",
    },
    {
        "clip_id": "CU-09",
        "episode_id": "E3",
        "chapter_number": 3,
        "chapter_title": "同じ間違いが共有言語になる",
        "source_video_id": "Ocqg-RpQURY",
        "requested_start_seconds": 2350,
        "requested_end_seconds": 2850,
        "topic": "桃鈴ねねの言い間違いと参加者間の共有",
        "speaker": "さくらみこ・桃鈴ねね",
        "setup": "大量の言い間違いを読み、本人が覚えているかを確かめる。",
        "core_statement": "同じ間違いを他の参加者も使い、反復することで個人の失敗から集団の言葉へ変わる。",
        "payoff_or_conclusion": "Wikiは誰が最初に間違えたかより、どう共有されたかを残す場になる。",
        "required_prior_context": "CU-08で一つの語録に元場面の文脈を戻したこと。",
        "required_following_context": "由来を参加者同士で検証し、語録の境界が変わる例へ進む。",
        "chapter_contribution": "語録が個人から共同体へ移る過程を示す。",
        "transition_in": "一人の読み間違いから、複数人が反復する言葉へ広げる。",
        "transition_out": "共有された言葉の由来を、別の参加者も含めて検証する。",
        "selection_reason": "複数の例、記憶確認、他者の同種発話、共有の結論まで連続する。",
        "exclusion_risk": "例を一つだけ抜くと、反復が共有言語を作るという論旨を証明できない。",
        "viewer_question": "一人の言い間違いは、いつみんなの言葉になるのか。",
        "evidence": "複数の語句を読み、本人と周囲が同じ間違いを使った記憶を確認する。",
        "interpretation": "反復の主体が増えるほど、語句は共同体の識別子になる。",
        "conclusion": "語録の作者は一人ではなく、使い続けた参加者と視聴者でもある。",
    },
    {
        "clip_id": "CU-10",
        "episode_id": "E3",
        "chapter_number": 4,
        "chapter_title": "由来を本人たちが再検証する",
        "source_video_id": "82iRbxjvbww",
        "requested_start_seconds": 900,
        "requested_end_seconds": 1280,
        "topic": "宝鐘マリンの語録・由来・参加者による精度確認",
        "speaker": "さくらみこ・大空スバル・宝鐘マリン",
        "setup": "宝鐘マリンの語録を読み、誰がいつ使った言葉かを三人で確かめる。",
        "core_statement": "Wikiの一行を本人たちが照合すると、発話者や由来の境界が揺れ、より正確な共同記憶へ更新される。",
        "payoff_or_conclusion": "添削の価値は正解発表ではなく、複数の記憶を突き合わせる過程にある。",
        "required_prior_context": "CU-09で語録の作者が複数に広がったこと。",
        "required_following_context": "E4で、言葉の共有から人物同士の関係性そのものへ進む。",
        "chapter_contribution": "Wiki添削を共同検証のプロセスとして結論づける。",
        "transition_in": "二人の共有言語から、三人が由来を検証する場へ広げる。",
        "transition_out": "言葉の由来を超え、他者の証言が本人像をどう変えるかへ移る。",
        "selection_reason": "語録、由来仮説、参加者の照合、暫定結論が一続きになる。",
        "exclusion_risk": "単語だけ抜くと誰の何を検証しているか分からず、三人の役割も消える。",
        "viewer_question": "本人が複数いれば、Wikiの由来は正確になるのか。",
        "evidence": "三人が語録の使用者と由来を相互に確認し、記述の境界を修正する。",
        "interpretation": "複数視点の不一致こそ、記録を更新するための材料になる。",
        "conclusion": "Wiki添削は共同記憶を再編集する会話である。",
    },
    {
        "clip_id": "CU-11",
        "episode_id": "E4",
        "chapter_number": 1,
        "chapter_title": "友人が使うことで言葉が関係性になる",
        "source_video_id": "1AcId5Yja10",
        "requested_start_seconds": 4460,
        "requested_end_seconds": 4740,
        "topic": "みこ・スバル間の語録と宝鐘マリンの反応",
        "speaker": "さくらみこ・大空スバル（宝鐘マリンへの言及を含む）",
        "setup": "二人の間で共有される語録を読み、別の友人がその表現を後押しした場面を思い出す。",
        "core_statement": "言葉は本人の特徴だけでなく、誰が拾い、どう返したかという関係の形を残す。",
        "payoff_or_conclusion": "語録から読むべきなのは奇抜さではなく、参加者同士が作った応答の履歴である。",
        "required_prior_context": "E3で語録を共同記憶として理解していること。",
        "required_following_context": "友人の訪問や笑いが本人の自己評価を変える例へ進む。",
        "chapter_contribution": "共有言語を関係性の証拠として読み替える。",
        "transition_in": "言葉の由来から、その言葉を使う人間関係へ焦点を移す。",
        "transition_out": "言葉の応答から、行動による支えと自己認識へ進む。",
        "selection_reason": "語録と第三者の反応が、関係性の解釈までつながる。",
        "exclusion_risk": "語録の表面だけでは第三者の役割が消え、前Episodeと重複する。",
        "viewer_question": "共有された言葉から、誰と誰の関係が見えるのか。",
        "evidence": "二人が語録を読み、宝鐘マリンがその表現を受け止めた場面へ接続する。",
        "interpretation": "語録は話者の所有物ではなく、応答した関係者との共同成果である。",
        "conclusion": "関係性は呼び名や語録だけでなく、相手の自己像を変える力を持つ。",
    },
    {
        "clip_id": "CU-12",
        "episode_id": "E4",
        "chapter_number": 2,
        "chapter_title": "友人の反応が自己評価を変える",
        "source_video_id": "82iRbxjvbww",
        "requested_start_seconds": 2370,
        "requested_end_seconds": 2490,
        "topic": "宝鐘マリンの『虚無』と友人による回復",
        "speaker": "さくらみこ・大空スバル・宝鐘マリン",
        "setup": "Wikiの『虚無』という記述を読み、限界時の過ごし方と友人の訪問を話す。",
        "core_statement": "友人が来て笑ったという外部の反応が、本人には自分の価値を確かめる出来事として残る。",
        "payoff_or_conclusion": "Wikiの一項目から、本人の自己評価を支える関係の機能が見える。",
        "required_prior_context": "CU-11で言葉への応答を関係性の証拠として読んだこと。",
        "required_following_context": "複数ページを横断する語録から、family全体の結論へ進む。",
        "chapter_contribution": "他者の証言と行動が本人像を更新する核心例になる。",
        "transition_in": "言葉を拾う関係から、弱った時に支える関係へ深める。",
        "transition_out": "一つの支援関係から、三人のページにまたがる相互記録へ広げる。",
        "selection_reason": "用語定義、状態、友人の行動、本人の解釈が短い中で完結する。",
        "exclusion_risk": "『虚無』だけ抜くと状態の消費になり、友人の反応という結論を失う。",
        "viewer_question": "他者の証言は本人の自己認識をどう変えるのか。",
        "evidence": "Wikiの用語から、友人の訪問と笑いが本人を回復させた話へ進む。",
        "interpretation": "関係性は人物紹介の属性ではなく、自己評価を更新する出来事として記録される。",
        "conclusion": "Wikiに残る他者との場面が、本人像の一部を説明する。",
    },
    {
        "clip_id": "CU-13",
        "episode_id": "E4",
        "chapter_number": 3,
        "chapter_title": "ページをまたぐ言葉がfamilyを結ぶ",
        "source_video_id": "Ocqg-RpQURY",
        "requested_start_seconds": 3000,
        "requested_end_seconds": 3284,
        "topic": "複数メンバーに横断掲載された語録と更新の継続",
        "speaker": "さくらみこ・桃鈴ねね（大空スバルへの言及を含む）",
        "setup": "桃鈴ねねの語録欄で、さくらみこや大空スバルのページにも現れる言葉を見つける。",
        "core_statement": "同じ言葉が複数ページを横断し、日をまたいで反復されることで、人物単位のWikiが関係性の網になる。",
        "payoff_or_conclusion": "Wiki添削は一度の正誤判定で閉じず、配信と関係が続く限り更新される共同記録である。",
        "required_prior_context": "CU-12で他者との出来事が本人像を作ると理解していること。",
        "required_following_context": "family終幕。4本の問いと、未取得ソースを含む今後の更新条件を示す。",
        "chapter_contribution": "個別ページを横断し、Episode family全体を一つの結論に統合する。",
        "transition_in": "一対一の支援関係から、複数ページを結ぶ言葉のネットワークへ広げる。",
        "transition_out": "完成品では、4 Episodeの問いを回収し、記録は今後も更新されると閉じる。",
        "selection_reason": "横断語録、反復、残件、更新への言及までfamily結論に必要な流れがある。",
        "exclusion_risk": "横断語録だけ抜くと列挙で終わり、継続更新という結論に届かない。",
        "viewer_question": "別々の人物ページは、どこで一つの関係史になるのか。",
        "evidence": "複数ページに現れる同じ語句と反復を確認し、まだ多く残ると話す。",
        "interpretation": "人物ごとの記録は、共有された言葉を介して関係性のアーカイブになる。",
        "conclusion": "Wiki添削familyは、本人・仲間・ファンが更新し続ける人物史を読むシリーズである。",
    },
]


EPISODE_SPECS = [
    {
        "episode_id": "E1",
        "title": "Wikiが作る人物像",
        "thesis": "非公式Wikiは事実一覧ではなく、ファンの注目と本人の訂正が往復する人物像である。",
        "viewer_question": "ページを読むと、公式プロフィールだけでは見えない何が分かるのか。",
        "setup": "非公式Wikiの作成主体と公式情報との差を説明する。",
        "evidence": "ページ構造の比較と大空スバルのプロフィール訂正を並べる。",
        "interpretation": "記述の量とずれが、ファンの人物理解を可視化する。",
        "conclusion": "人物像は公式と非公式のどちらか一方ではなく、往復で更新される。",
        "transition_to_next": "静的プロフィールから、忘れていた出来事の時間軸へ進む。",
        "clip_ids": ["CU-01", "CU-02", "CU-03"],
    },
    {
        "episode_id": "E2",
        "title": "記録が呼び戻す出来事と記憶",
        "thesis": "Wikiに残った出来事は、現在の達成・家族の記憶・時代背景を添えて初めて意味を持つ。",
        "viewer_question": "本人も忘れた過去は、今の本人に何を返すのか。",
        "setup": "古い投稿を現在の達成と接続する。",
        "evidence": "活動目標、家族由来の言葉、過去衣装と制度差を比較する。",
        "interpretation": "記録は過去を固定せず、現在から再解釈する材料になる。",
        "conclusion": "事実訂正だけでなく、時間と環境の文脈を戻すことが添削になる。",
        "transition_to_next": "出来事の履歴から、反復される言葉の履歴へ進む。",
        "clip_ids": ["CU-04", "CU-05", "CU-06"],
    },
    {
        "episode_id": "E3",
        "title": "語録・言い間違いが共有言語になる",
        "thesis": "語録は失言集ではなく、場面・反復・複数人の照合で共同記憶になった言葉である。",
        "viewer_question": "一度の発話は、どうしてファンと仲間の共有言語になるのか。",
        "setup": "語録欄の量と読み方を定義する。",
        "evidence": "読み間違いの元場面、複数人の反復、三人による由来検証をつなぐ。",
        "interpretation": "言葉の価値は誤りではなく、誰がどう応答し共有したかにある。",
        "conclusion": "Wiki添削は語録の正解発表ではなく、共同記憶の再編集である。",
        "transition_to_next": "共有言語から、それを生む人間関係と自己認識へ進む。",
        "clip_ids": ["CU-07", "CU-08", "CU-09", "CU-10"],
    },
    {
        "episode_id": "E4",
        "title": "他者の証言が本人像を更新する",
        "thesis": "人物像は本人の説明だけでなく、友人が拾った言葉・支えた行動・横断する記録から作られる。",
        "viewer_question": "他者との関係は、Wiki上の本人像をどう変えるのか。",
        "setup": "友人が語録を拾う場面から始める。",
        "evidence": "友人による回復と、複数ページを横断する語録を接続する。",
        "interpretation": "関係性は人物の属性ではなく、相互に自己像を変える履歴である。",
        "conclusion": "Wiki添削familyは、本人・仲間・ファンが更新し続ける人物史を読む。",
        "transition_to_next": "family終幕。未取得ソースを解消した後に統合rough cutへ進む。",
        "clip_ids": ["CU-11", "CU-12", "CU-13"],
    },
]


ACCEPTANCE_UNITS = [
    ("final deliverable topology", 8, 1.0, "4本のテーマ別Episode familyと視聴順を固定"),
    ("source corpus inventory", 10, 1.0, "既知3配信のexact/ unavailable laneと処理範囲を固定"),
    ("thematic clustering", 12, 1.0, "配信内容から導出した4クラスタをsource横断で固定"),
    ("Episode/Chapter map", 12, 1.0, "4 Episode・13 chapterの論旨と遷移を固定"),
    ("context-complete ClipUnits", 18, 1.0, "13/13でsetup/core/payoff/前後文脈/遷移を固定"),
    ("continuous rough-cut/edit script", 14, 1.0, "13 ClipUnitを連続する編集台本へ接続"),
    ("S content review", 8, 0.0, "Coordinator経由のcontent verdict待ち"),
    ("integrated render", 8, 0.0, "本Work OrderではMP4生成禁止"),
    ("technical QA", 4, 0.0, "統合render前のためfinal media QAは未開始"),
    ("final content acceptance", 6, 0.0, "明示的human content acceptanceなし"),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def clean_caption_text(event: dict[str, Any]) -> str:
    text = "".join(str(segment.get("utf8") or "") for segment in event.get("segs") or [])
    return " ".join(text.split())


def caption_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, event in enumerate(payload.get("events") or []):
        text = clean_caption_text(event)
        if not text:
            continue
        start = float(event.get("tStartMs") or 0) / 1000.0
        duration = float(event.get("dDurationMs") or 0) / 1000.0
        result.append(
            {
                "event_index": index,
                "event_id": f"json3_event_{index:04d}",
                "start_seconds": round(start, 3),
                "end_seconds": round(start + duration, 3),
                "text": text,
            }
        )
    return result


def excerpt(events: list[dict[str, Any]], start_index: int, count: int = 2) -> str:
    value = " / ".join(item["text"] for item in events[start_index : start_index + count])
    return value if len(value) <= 96 else value[:95] + "…"


def caption_readback(
    events: list[dict[str, Any]], start_seconds: float, end_seconds: float
) -> dict[str, Any]:
    selected = [
        item
        for item in events
        if item["start_seconds"] >= start_seconds and item["start_seconds"] < end_seconds
    ]
    if not selected:
        raise ValueError(f"no caption event in range {start_seconds}-{end_seconds}")
    middle = max(0, len(selected) // 2 - 1)
    payoff_start = max(0, len(selected) - 2)
    return {
        "event_count": len(selected),
        "first_event_id": selected[0]["event_id"],
        "last_event_id": selected[-1]["event_id"],
        "aligned_start_seconds": selected[0]["start_seconds"],
        "aligned_end_seconds": selected[-1]["end_seconds"],
        "setup_excerpt": excerpt(selected, 0),
        "core_excerpt": excerpt(selected, middle),
        "payoff_excerpt": excerpt(selected, payoff_start),
        "note": "短いcaption readback。話者帰属と編集適合はS content review対象。",
    }


def merge_ranges(ranges: list[tuple[float, float]]) -> list[tuple[float, float]]:
    merged: list[list[float]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(round(start, 6), round(end, 6)) for start, end in merged]


def range_duration(ranges: list[tuple[float, float]]) -> float:
    return round(sum(end - start for start, end in ranges), 6)


def complement_ranges(
    ranges: list[tuple[float, float]], duration_seconds: float
) -> list[tuple[float, float]]:
    cursor = 0.0
    result: list[tuple[float, float]] = []
    for start, end in merge_ranges(ranges):
        bounded_start = max(0.0, min(duration_seconds, start))
        bounded_end = max(0.0, min(duration_seconds, end))
        if bounded_start > cursor:
            result.append((round(cursor, 6), round(bounded_start, 6)))
        cursor = max(cursor, bounded_end)
    if cursor < duration_seconds:
        result.append((round(cursor, 6), round(duration_seconds, 6)))
    return result


def selected_ranges_from_pack(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    if payload.get("source_identity") != "youtube:1AcId5Yja10":
        raise ValueError(f"unexpected edit-pack source identity: {path}")
    selected_ids = set(payload.get("selected_cut_ids") or [])
    selected = [item for item in payload.get("cut_candidates") or [] if item.get("id") in selected_ids]
    if len(selected) != len(selected_ids):
        raise ValueError(f"selected cut id missing from candidates: {path}")
    return selected


def verify_sources() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    inventory_path = EPISODE_ROOT / "corpus/corpus_inventory.json"
    inventory = load_json(inventory_path)
    inventory_videos = {item["video_id"]: item for item in inventory.get("videos") or []}
    if set(inventory_videos) != set(EXPECTED_SOURCES):
        raise ValueError("corpus inventory video identities changed")

    source_records: list[dict[str, Any]] = []
    events_by_source: dict[str, list[dict[str, Any]]] = {}
    for video_id, expected in EXPECTED_SOURCES.items():
        inventory_item = inventory_videos[video_id]
        if int(inventory_item.get("duration_seconds") or 0) != expected["duration_seconds"]:
            raise ValueError(f"duration identity changed: {video_id}")

        caption_path = EPISODE_ROOT / expected["caption_relative_path"]
        caption_hash = sha256_file(caption_path)
        if caption_hash != expected["caption_sha256"]:
            raise ValueError(f"caption identity changed: {video_id}")
        events = caption_events(load_json(caption_path))
        events_by_source[video_id] = events

        media_record: dict[str, Any]
        if expected["media_relative_path"]:
            media_path = EPISODE_ROOT / expected["media_relative_path"]
            if media_path.stat().st_size != expected["media_bytes"]:
                raise ValueError(f"source byte size changed: {video_id}")
            if sha256_file(media_path) != expected["media_sha256"]:
                raise ValueError(f"source hash changed: {video_id}")
            media_record = {
                "state": expected["media_state"],
                "repo_relative_ignored_path": display_path(media_path),
                "bytes": expected["media_bytes"],
                "sha256": expected["media_sha256"],
            }
        else:
            media_record = {
                "state": expected["media_state"],
                "repo_relative_ignored_path": None,
                "bytes": None,
                "sha256": None,
            }

        source_records.append(
            {
                "source_id": expected["source_id"],
                "title": inventory_item["title"],
                "duration_seconds": expected["duration_seconds"],
                "provenance": {
                    "authoritative_channel_id": inventory["inclusion_criteria"]["authoritative_channel_id"],
                    "authoritative_surface": inventory_item["authoritative_surface"],
                    "inventory_path": display_path(inventory_path),
                    "inventory_sha256": sha256_file(inventory_path),
                    "corpus_completeness_claim": (
                        "known public authoritative stream surface under the recorded title rule only; "
                        "does not claim private, deleted, future, or off-rule streams"
                    ),
                },
                "media": media_record,
                "captions": {
                    "state": "exact_caption_bytes_available_automatic_unreviewed",
                    "repo_relative_ignored_path": display_path(caption_path),
                    "bytes": caption_path.stat().st_size,
                    "sha256": caption_hash,
                    "normalized_text_event_count": len(events),
                },
                "acquisition_scope": expected["acquisition_scope"],
                "processed_media_ranges": [],
                "unprocessed_media_ranges": [],
                "content_topics": expected["content_topics"],
            }
        )
    return source_records, events_by_source


def verify_probes_and_ranges() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[tuple[float, float]]]:
    reclassified: list[dict[str, Any]] = []
    probe_cuts: list[dict[str, Any]] = []
    all_ranges: list[tuple[float, float]] = []

    baseline_id = "clip-wiki-tensaku-longform-v1-001"
    pack_ids = [baseline_id] + [item["artifact_id"] for item in PROBES]
    for artifact_id in pack_ids:
        pack_path = EPISODE_ROOT / f"artifacts/{artifact_id}/edit_pack.json"
        selected = selected_ranges_from_pack(pack_path)
        for item in selected:
            value = (float(item["source_start_seconds"]), float(item["source_end_seconds"]))
            all_ranges.append(value)
            if artifact_id != baseline_id:
                probe_cuts.append(
                    {
                        "probe_artifact_id": artifact_id,
                        "cut_id": item["id"],
                        "source_timestamp": {
                            "start_seconds": value[0],
                            "end_seconds": value[1],
                        },
                    }
                )

    for probe in PROBES:
        video_path = EPISODE_ROOT / f"artifacts/{probe['artifact_id']}/final_video.mp4"
        if video_path.stat().st_size != probe["bytes"]:
            raise ValueError(f"probe byte size changed: {probe['artifact_id']}")
        if sha256_file(video_path) != probe["sha256"]:
            raise ValueError(f"probe hash changed: {probe['artifact_id']}")
        reclassified.append(
            {
                **probe,
                "repo_relative_ignored_path": display_path(video_path),
                "turn_class": "SOURCE_SELECTION_AND_RENDER_PROBE",
                "product_authority": "non-final",
                "technical_evidence": "preserved",
                "human_artistic_acceptance": "revise",
                "final_product_status": "not accepted",
                "receipt_rewrite": False,
            }
        )
    return reclassified, probe_cuts, all_ranges


def build_clip_units(events_by_source: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for spec in CLIP_SPECS:
        source_id = spec["source_video_id"]
        readback = caption_readback(
            events_by_source[source_id],
            float(spec["requested_start_seconds"]),
            float(spec["requested_end_seconds"]),
        )
        source_expected = EXPECTED_SOURCES[source_id]
        item = dict(spec)
        item["source_id"] = source_expected["source_id"]
        item["source_timestamp"] = {
            "requested_start_seconds": spec["requested_start_seconds"],
            "requested_end_seconds": spec["requested_end_seconds"],
            "caption_aligned_start_seconds": readback["aligned_start_seconds"],
            "caption_aligned_end_seconds": readback["aligned_end_seconds"],
            "requested_duration_seconds": spec["requested_end_seconds"]
            - spec["requested_start_seconds"],
        }
        item["source_identity"] = {
            "media_state": source_expected["media_state"],
            "media_sha256": source_expected["media_sha256"],
            "caption_sha256": source_expected["caption_sha256"],
        }
        item["caption_readback"] = readback
        item["context_overlap_classification"] = (
            "no_planned_clipunit_overlap; context-preserving overlap remains allowed if S requests it"
        )
        for obsolete in ("source_video_id", "requested_start_seconds", "requested_end_seconds"):
            item.pop(obsolete)
        result.append(item)
    return result


def classify_probe_cuts(
    probe_cuts: list[dict[str, Any]], clip_units: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reusable: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    source_one_units = [item for item in clip_units if item["source_id"] == "youtube:1AcId5Yja10"]
    for cut in probe_cuts:
        start = cut["source_timestamp"]["start_seconds"]
        end = cut["source_timestamp"]["end_seconds"]
        overlap_ids: list[str] = []
        overlap_seconds = 0.0
        for clip in source_one_units:
            clip_start = clip["source_timestamp"]["requested_start_seconds"]
            clip_end = clip["source_timestamp"]["requested_end_seconds"]
            overlap = max(0.0, min(end, clip_end) - max(start, clip_start))
            if overlap > 0:
                overlap_ids.append(clip["clip_id"])
                overlap_seconds += overlap
        if overlap_ids:
            reusable.append(
                {
                    **cut,
                    "status": "proposed_for_contextual_reuse",
                    "overlapping_clip_units": overlap_ids,
                    "overlap_seconds": round(overlap_seconds, 6),
                    "reason": (
                        "旧25秒窓のままでは採用しない。context-complete ClipUnitの内部素材としてのみ再編集候補。"
                    ),
                }
            )
        else:
            excluded.append(
                {
                    **cut,
                    "status": "excluded_from_current_assembly",
                    "reason": (
                        "現在の4 Episodeのthesis-bearing ClipUnit外。setup/core/payoffと隣接関係を新たに"
                        "立証しない限り持ち越さない。"
                    ),
                }
            )
    return reusable, excluded


def build_episode_map(clip_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clip_index = {item["clip_id"]: item for item in clip_units}
    result: list[dict[str, Any]] = []
    for episode in EPISODE_SPECS:
        chapters: list[dict[str, Any]] = []
        for clip_id in episode["clip_ids"]:
            clip = clip_index[clip_id]
            chapters.append(
                {
                    "chapter_number": clip["chapter_number"],
                    "title": clip["chapter_title"],
                    "clip_id": clip_id,
                    "thesis": clip["chapter_contribution"],
                    "viewer_question": clip["viewer_question"],
                    "setup": clip["setup"],
                    "evidence": clip["evidence"],
                    "interpretation": clip["interpretation"],
                    "conclusion": clip["conclusion"],
                    "transition_to_next": clip["transition_out"],
                }
            )
        result.append({**episode, "chapters": chapters})
    return result


def build_rough_cut(clip_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "order": index,
            "episode_id": clip["episode_id"],
            "chapter_number": clip["chapter_number"],
            "clip_id": clip["clip_id"],
            "bridge_in": clip["transition_in"],
            "source_action": f"{clip['source_id']} {clip['source_timestamp']['requested_start_seconds']:.0f}–{clip['source_timestamp']['requested_end_seconds']:.0f}s を文脈単位で使用",
            "setup_read": clip["setup"],
            "core_read": clip["core_statement"],
            "interpretation_read": clip["interpretation"],
            "payoff_read": clip["payoff_or_conclusion"],
            "bridge_out": clip["transition_out"],
            "render_readiness": clip["source_identity"]["media_state"],
        }
        for index, clip in enumerate(clip_units, start=1)
    ]


def build_plan() -> dict[str, Any]:
    source_records, events_by_source = verify_sources()
    probes, probe_cuts, all_used_ranges = verify_probes_and_ranges()
    clip_units = build_clip_units(events_by_source)
    reusable, excluded = classify_probe_cuts(probe_cuts, clip_units)

    source_one_merged = merge_ranges(all_used_ranges)
    source_one_complement = complement_ranges(source_one_merged, 5558)
    for source in source_records:
        if source["source_id"] == "youtube:1AcId5Yja10":
            source["processed_media_ranges"] = {
                "selected_range_count_baseline_plus_turns_1_to_5": len(all_used_ranges),
                "merged_ranges": [
                    {"start_seconds": start, "end_seconds": end}
                    for start, end in source_one_merged
                ],
                "unique_seconds": range_duration(source_one_merged),
                "share_of_source_percent": round(range_duration(source_one_merged) / 5558 * 100, 2),
                "metric_role": "technical support only; not product progress",
            }
            source["unprocessed_media_ranges"] = {
                "ranges": [
                    {"start_seconds": start, "end_seconds": end}
                    for start, end in source_one_complement
                ],
                "unique_seconds": range_duration(source_one_complement),
            }
        else:
            source["processed_media_ranges"] = {
                "selected_range_count": 0,
                "merged_ranges": [],
                "unique_seconds": 0,
                "reason": "exact source bytes unavailable; static caption planning is not processed media",
            }
            source["unprocessed_media_ranges"] = {
                "ranges": "entire exact-media lane unavailable",
                "unique_seconds": source["duration_seconds"],
            }

    episodes = build_episode_map(clip_units)
    thematic_clusters = [
        {
            "cluster_id": episode["episode_id"],
            "name": episode["title"],
            "derived_from_source_evidence": episode["evidence"],
            "central_question": episode["viewer_question"],
            "clip_ids": episode["clip_ids"],
            "source_representation": sorted(
                {next(item["source_id"] for item in clip_units if item["clip_id"] == clip_id) for clip_id in episode["clip_ids"]}
            ),
            "coverage_status": "reviewable_content_design",
            "measurement_note": "topic/source representation; not time percentage",
        }
        for episode in episodes
    ]

    acceptance = [
        {
            "unit": name,
            "weight": weight,
            "score": score,
            "weighted_points": weight * score,
            "evidence": evidence,
        }
        for name, weight, score, evidence in ACCEPTANCE_UNITS
    ]
    acceptance_total = sum(item["weighted_points"] for item in acceptance)

    return {
        "schema_version": "clippipegen.wiki_tensaku_content_reframe.v1",
        "work_order_id": WORK_ORDER_ID,
        "artifact_id": ARTIFACT_ID,
        "artifact_class": "diagnostic_pre_render_content_design",
        "finished_video": False,
        "generated_mp4_count": 0,
        "human_artistic_acceptance": "revise",
        "audience_promise": AUDIENCE_PROMISE,
        "classification_correction": {
            "process_turn_count": 8,
            "artifact_producing_turn_count": 5,
            "technically_closed_D_S_cycles": 4,
            "integrated_product_iterations": 0,
            "content_accepted_deliverables": 0,
            "coverage_is_project_progress": False,
            "overlap_policy": (
                "overlap 0 is not an absolute quality rule; context-preserving overlap is allowed and labeled, "
                "harmful redundancy is rejected"
            ),
        },
        "final_deliverable_proposal": {
            "selected_topology": "thematic_episode_family",
            "planned_final_artifact_count": 4,
            "family_index_is_final_mp4": False,
            "rationale": (
                "三配信に反復する編集構造を4つの問いで横断でき、2本のsource-byte gateを隠さずに"
                "理解可能な視聴順を保てる。1本masterは欠損laneで構成が歪み、旧300秒turn方式は"
                "隣接関係と全体像を失うため採用しない。"
            ),
            "prohibited_topology": "per-turn disconnected 300-second outputs",
            "deferred_alternative": (
                "全source bytesが揃いS review後、4 Episodeを連続再生するmaster indexは検討可能。"
            ),
        },
        "corpus_inventory": {
            "known_source_count": len(source_records),
            "exact_media_source_count": sum(
                item["media"]["state"] == "exact_source_bytes_available" for item in source_records
            ),
            "missing_exact_media_source_count": sum(
                item["media"]["state"] == "exact_source_bytes_unavailable" for item in source_records
            ),
            "exact_caption_source_count": len(source_records),
            "sources": source_records,
        },
        "thematic_cluster_map": thematic_clusters,
        "episode_chapter_map": episodes,
        "family_viewing_order": [
            {
                "order": index,
                "episode_id": episode["episode_id"],
                "title": episode["title"],
                "why_here": episode["transition_to_next"] if index < 4 else episode["conclusion"],
            }
            for index, episode in enumerate(episodes, start=1)
        ],
        "narrative_assembly_ir": {
            "clip_unit_count": len(clip_units),
            "setup_complete_count": sum(bool(item["setup"]) for item in clip_units),
            "core_complete_count": sum(bool(item["core_statement"]) for item in clip_units),
            "payoff_complete_count": sum(bool(item["payoff_or_conclusion"]) for item in clip_units),
            "transition_in_complete_count": sum(bool(item["transition_in"]) for item in clip_units),
            "transition_out_complete_count": sum(bool(item["transition_out"]) for item in clip_units),
            "clip_units": clip_units,
        },
        "continuous_rough_cut_edit_script": build_rough_cut(clip_units),
        "probe_reclassification": probes,
        "turn_1_to_5_reuse_review": {
            "probe_cut_count": len(probe_cuts),
            "proposed_for_contextual_reuse_count": len(reusable),
            "excluded_from_current_assembly_count": len(excluded),
            "reuse_rule": "旧25秒窓をstandalone採用せず、拡張ClipUnit内部でのみ再編集する。",
            "proposed_for_contextual_reuse": reusable,
            "excluded_from_current_assembly": excluded,
        },
        "acceptance_score": {
            "fixed_weight_total": 100,
            "earned_points": acceptance_total,
            "units": acceptance,
            "interpretation": (
                "pre-render units 1–6のみ。S review、integrated render、final media QA、human acceptanceは未加点。"
            ),
        },
        "pre_render_validation": {
            "source_identity_verified_count": len(source_records),
            "exact_media_identity_verified_count": sum(
                item["media"]["state"] == "exact_source_bytes_available"
                for item in source_records
            ),
            "explicit_unavailable_media_lane_count": sum(
                item["media"]["state"] == "exact_source_bytes_unavailable"
                for item in source_records
            ),
            "immutable_probe_hash_and_size_verified_count": len(probes),
            "immutable_probe_receipt_rewrite_count": 0,
            "clipunit_required_field_complete_count": len(clip_units),
            "clipunit_setup_core_payoff_complete_count": len(clip_units),
            "clipunit_transition_in_out_complete_count": len(clip_units),
            "fixed_25_second_window_count": sum(
                item["source_timestamp"]["requested_duration_seconds"] == 25
                for item in clip_units
            ),
            "continuous_rough_cut_step_count": len(clip_units),
            "generated_mp4_count": 0,
            "validation_boundary": (
                "content-design completeness and exact identity only; S content fit, integrated media QA, "
                "human acceptance, rights, production, and publication remain separate"
            ),
        },
        "s_content_review_packet": {
            "route": "return_to_Coordinator; do_not_contact_S_directly",
            "requested_verdicts": [
                "content_continue",
                "content_bounded_repair",
                "content_reframe",
            ],
            "review_questions": [
                "audience promiseは初見視聴者にWiki添削の趣旨を一文で伝えるか",
                "4 Episodeのテーマ順は、人物像→記憶→共有言語→関係性の論理を保つか",
                "13 ClipUnitは各々setup/core/payoffと前後接続を満たすか",
                "Turn1–5の20 reuse候補は拡張文脈内だけで使う方針が妥当か",
                "source bytes未提供2 laneを残したままrenderへ進まず、取得gateを維持すべきか",
            ],
            "decision_boundary": (
                "content_continueのみ次のintegrated rough-cut実装へ進む。bounded repair/reframeは"
                "指定範囲だけ設計を修正し、MP4は作らない。"
            ),
            "non_inferences": [
                "technical decode/test/coverage/overlapからcontent acceptanceを推論しない",
                "rights/production/publication/monetization/deliveryを推論しない",
                "unavailable source bytesをcaptionだけでrender-readyと扱わない",
            ],
        },
        "open_gates": [
            {
                "gate": "S content review",
                "owner": "Coordinator-routed S",
                "next_move": "このpacketへcontent verdictを返す",
            },
            {
                "gate": "youtube:82iRbxjvbww exact source bytes",
                "owner": "authorized source provider/user",
                "next_move": "exact bytesの明示提供。推測取得・cookies/OAuth・anonymous retryなし",
            },
            {
                "gate": "youtube:Ocqg-RpQURY exact source bytes",
                "owner": "authorized source provider/user",
                "next_move": "exact bytesの明示提供。推測取得・cookies/OAuth・anonymous retryなし",
            },
            {
                "gate": "human content acceptance and rights/publication chain",
                "owner": "human authority",
                "next_move": "integrated renderとtechnical QA後に別判断",
            },
        ],
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Wiki添削 Content Reframe v1",
        "",
        "> **診断用・pre-render。完成動画ではありません。**",
        "",
        f"Work Order: `{plan['work_order_id']}` / artifact: `{plan['artifact_id']}`",
        "",
        "## 視聴者への約束",
        "",
        plan["audience_promise"],
        "",
        "## 最終形",
        "",
        f"**4本のテーマ別Episode family**。{plan['final_deliverable_proposal']['rationale']}",
        "",
        "| 順 | Episode | 問い | Chapter |",
        "|---:|---|---|---:|",
    ]
    for order, episode in enumerate(plan["episode_chapter_map"], start=1):
        lines.append(
            f"| {order} | {episode['episode_id']} {episode['title']} | {episode['viewer_question']} | {len(episode['chapters'])} |"
        )
    lines += [
        "",
        "## コーパスとrender gate",
        "",
        "| Source | Duration | Exact media | Exact captions | Topic |",
        "|---|---:|---|---|---|",
    ]
    for source in plan["corpus_inventory"]["sources"]:
        lines.append(
            f"| `{source['source_id']}` | {source['duration_seconds']}s | {source['media']['state']} | "
            f"{source['captions']['sha256'][:12]}… | {' / '.join(source['content_topics'][:2])} |"
        )
    lines += [
        "",
        "## Episode / Chapter map",
        "",
    ]
    for episode in plan["episode_chapter_map"]:
        lines += [
            f"### {episode['episode_id']} {episode['title']}",
            "",
            f"**Thesis:** {episode['thesis']}",
            "",
            f"**Viewer question:** {episode['viewer_question']}",
            "",
        ]
        for chapter in episode["chapters"]:
            lines += [
                f"#### {episode['episode_id']}-{chapter['chapter_number']:02d} {chapter['title']} (`{chapter['clip_id']}`)",
                "",
                f"- Setup: {chapter['setup']}",
                f"- Evidence: {chapter['evidence']}",
                f"- Interpretation: {chapter['interpretation']}",
                f"- Conclusion: {chapter['conclusion']}",
                f"- Transition: {chapter['transition_to_next']}",
                "",
            ]
    reuse = plan["turn_1_to_5_reuse_review"]
    lines += [
        "## Turn1–5の扱い",
        "",
        "5本はすべて `SOURCE_SELECTION_AND_RENDER_PROBE` / non-final / human revise。既存receiptは書き換えていません。",
        "",
        f"旧60カットのうち {reuse['proposed_for_contextual_reuse_count']} 件は拡張ClipUnit内部の再編集候補、"
        f"{reuse['excluded_from_current_assembly_count']} 件は現assemblyから除外です。25秒窓のstandalone再利用はしません。",
        "",
        "## 完全性と現在の得点",
        "",
        f"ClipUnit {plan['narrative_assembly_ir']['clip_unit_count']} / setup {plan['narrative_assembly_ir']['setup_complete_count']} / "
        f"core {plan['narrative_assembly_ir']['core_complete_count']} / payoff {plan['narrative_assembly_ir']['payoff_complete_count']} / "
        f"transition in/out {plan['narrative_assembly_ir']['transition_in_complete_count']}/{plan['narrative_assembly_ir']['transition_out_complete_count']}。",
        "",
        f"固定weight score: **{plan['acceptance_score']['earned_points']}/100**。S review以降は未加点です。",
        "",
        "## 次の判断",
        "",
        "CoordinatorからSへcontent review packetを渡し、`content_continue` の場合だけ次のintegrated rough-cutへ進みます。"
        "2本のexact source bytesが未提供の間は、そのlaneをrender-readyとみなしません。",
        "",
        "完全なClipUnit、source timestamp map、caption readback、rough-cut script、全reuse/exclusion理由、S packetは同ディレクトリのJSONが正本です。",
        "",
    ]
    return "\n".join(lines)


def render_html(plan: dict[str, Any]) -> str:
    episode_cards = []
    for episode in plan["episode_chapter_map"]:
        chapter_rows = "".join(
            f"<li><b>{html.escape(chapter['clip_id'])}</b> {html.escape(chapter['title'])}"
            f"<span>{html.escape(chapter['transition_to_next'])}</span></li>"
            for chapter in episode["chapters"]
        )
        episode_cards.append(
            f"<article><div class='ep'>{html.escape(episode['episode_id'])}</div>"
            f"<h2>{html.escape(episode['title'])}</h2>"
            f"<p class='question'>{html.escape(episode['viewer_question'])}</p>"
            f"<p>{html.escape(episode['thesis'])}</p><ol>{chapter_rows}</ol></article>"
        )
    source_rows = "".join(
        f"<tr><td><code>{html.escape(source['source_id'])}</code></td>"
        f"<td>{source['duration_seconds']}s</td>"
        f"<td class={'ok' if source['media']['state']=='exact_source_bytes_available' else 'block'}>"
        f"{html.escape(source['media']['state'])}</td>"
        f"<td>{source['captions']['normalized_text_event_count']}</td></tr>"
        for source in plan["corpus_inventory"]["sources"]
    )
    score_rows = "".join(
        f"<tr><td>{html.escape(item['unit'])}</td><td>{item['weight']}</td><td>{item['score']}</td>"
        f"<td>{item['weighted_points']}</td></tr>"
        for item in plan["acceptance_score"]["units"]
    )
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wiki添削 Content Reframe</title>
<style>
:root{{--ink:#17211b;--muted:#657168;--paper:#f5f2e8;--card:#fffdf6;--green:#1d6048;--amber:#a65d18;--line:#d9d3c2}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}
header{{min-height:92vh;padding:5vw;display:grid;grid-template-columns:1.05fr 1.95fr;gap:4vw;align-items:center;background:linear-gradient(135deg,#e9f2e7,#f5f2e8 52%,#f4e4cf)}}
.kicker{{font-weight:800;letter-spacing:.13em;color:var(--green)}} h1{{font-size:clamp(2.3rem,6vw,6.2rem);line-height:.92;margin:.2em 0}}
.promise{{font-size:clamp(1.08rem,2vw,1.55rem);max-width:36em}} .status{{display:inline-block;padding:.45rem .75rem;background:#fff1d5;border:1px solid #e0b765;border-radius:999px;font-weight:750}}
.rail{{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}} article{{background:rgba(255,253,246,.94);border:1px solid var(--line);border-radius:18px;padding:1.25rem;box-shadow:0 14px 35px #4b4b3f12}}
.ep{{font-weight:900;color:var(--green)}} article h2{{margin:.15rem 0;font-size:1.2rem}} .question{{font-weight:750}} ol{{padding-left:1.2rem}} li{{margin:.5rem 0}} li span{{display:block;color:var(--muted);font-size:.88rem}}
main{{max-width:1180px;margin:auto;padding:4rem 2rem}} section{{margin-bottom:4rem}} .grid{{display:grid;grid-template-columns:1fr 1fr;gap:2rem}}
table{{width:100%;border-collapse:collapse;background:var(--card)}} th,td{{padding:.7rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} .ok{{color:var(--green);font-weight:800}} .block{{color:var(--amber);font-weight:800}}
.metric{{font-size:3rem;font-weight:900;color:var(--green)}} .note{{color:var(--muted)}} code{{font-size:.84em}} @media(max-width:850px){{header,.grid{{grid-template-columns:1fr}}.rail{{grid-template-columns:1fr}}}}
</style></head><body>
<header><div><div class="kicker">DIAGNOSTIC · PRE-RENDER</div><h1>Wiki添削を<br>物語に戻す</h1>
<p class="promise">{html.escape(plan['audience_promise'])}</p>
<p class="status">完成動画ではない · human revise · MP4 0</p>
<p class="note">旧300秒turn topologyを終了し、全コーパスを4つの問いで横断する。</p></div>
<div class="rail">{''.join(episode_cards)}</div></header>
<main><section class="grid"><div><h2>なぜEpisode familyか</h2><p>{html.escape(plan['final_deliverable_proposal']['rationale'])}</p>
<p><b>視聴順:</b> 人物像 → 記憶 → 共有言語 → 関係性</p></div>
<div><div class="metric">{plan['narrative_assembly_ir']['clip_unit_count']}/13</div><p>ClipUnitのsetup/core/payoff/transitionが完備。</p>
<p>Turn1–5 reuse候補 {plan['turn_1_to_5_reuse_review']['proposed_for_contextual_reuse_count']} / 除外 {plan['turn_1_to_5_reuse_review']['excluded_from_current_assembly_count']}。旧25秒窓はstandalone不採用。</p></div></section>
<section><h2>Source readiness</h2><table><thead><tr><th>Source</th><th>Duration</th><th>Exact media</th><th>Caption events</th></tr></thead><tbody>{source_rows}</tbody></table>
<p class="note">未提供2 laneはcaptionでcontent designのみ。推測取得・cookies/OAuth・anonymous retryなし。</p></section>
<section><h2>固定weight acceptance</h2><table><thead><tr><th>Unit</th><th>Weight</th><th>Score</th><th>Points</th></tr></thead><tbody>{score_rows}</tbody></table>
<p class="metric">{plan['acceptance_score']['earned_points']}/100</p><p>S content review、integrated render、final media QA、human acceptanceは0のまま。</p></section>
<section><h2>次のgate</h2><p>このentrypointとJSON正本をCoordinator経由でSへ渡す。<code>content_continue</code> の場合だけ、source gateを満たしたlaneからintegrated rough-cutへ進む。</p>
<p class="note">Work Order {html.escape(plan['work_order_id'])} · artifact {html.escape(plan['artifact_id'])}</p></section></main>
</body></html>"""


def write_outputs(plan: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = "wiki_tensaku_content_reframe_v1"
    s_packet = {
        "schema_version": "clippipegen.wiki_tensaku_s_content_review_packet.v1",
        "work_order_id": plan["work_order_id"],
        "artifact_id": plan["artifact_id"],
        "human_artistic_acceptance": plan["human_artistic_acceptance"],
        "audience_promise": plan["audience_promise"],
        "selected_topology": plan["final_deliverable_proposal"],
        "episode_chapter_map": plan["episode_chapter_map"],
        "clipunit_completeness": {
            key: value
            for key, value in plan["narrative_assembly_ir"].items()
            if key != "clip_units"
        },
        "clipunit_ids": [
            item["clip_id"] for item in plan["narrative_assembly_ir"]["clip_units"]
        ],
        "probe_reuse_review": {
            key: value
            for key, value in plan["turn_1_to_5_reuse_review"].items()
            if key
            in {
                "probe_cut_count",
                "proposed_for_contextual_reuse_count",
                "excluded_from_current_assembly_count",
                "reuse_rule",
            }
        },
        "acceptance_score": plan["acceptance_score"],
        "review_packet": plan["s_content_review_packet"],
        "canonical_ir_path": display_path(DEFAULT_OUTPUT_DIR / f"{stem}.json"),
        "human_entrypoint": display_path(DEFAULT_OUTPUT_DIR / f"{stem}.html"),
    }
    payloads = {
        f"{stem}.json": json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        f"{stem}.md": render_markdown(plan),
        f"{stem}.html": render_html(plan),
        f"{stem}.s_review_packet.json": json.dumps(s_packet, ensure_ascii=False, indent=2)
        + "\n",
    }
    for name, value in payloads.items():
        (output_dir / name).write_text(value, encoding="utf-8", newline="\n")
    members = []
    for name in payloads:
        path = output_dir / name
        members.append(
            {
                "path": display_path(DEFAULT_OUTPUT_DIR / name),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    receipt = {
        "schema_version": "clippipegen.wiki_tensaku_content_reframe_receipt.v1",
        "work_order_id": WORK_ORDER_ID,
        "artifact_id": ARTIFACT_ID,
        "artifact_class": "diagnostic_pre_render_content_design",
        "members": members,
        "generated_mp4_count": 0,
        "immutable_probe_count_verified": len(PROBES),
        "source_identity_count_verified": len(EXPECTED_SOURCES),
    }
    receipt_path = output_dir / f"{stem}.receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Wiki添削 pre-render content reframe packet")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify live evidence and require generated output bytes to match tracked output",
    )
    args = parser.parse_args()

    plan = build_plan()
    if args.check:
        temp_dir = args.output_dir.parent / f".{args.output_dir.name}.check"
        if temp_dir.exists():
            raise ValueError(f"check directory already exists: {temp_dir}")
        write_outputs(plan, temp_dir)
        expected_names = {
            "wiki_tensaku_content_reframe_v1.json",
            "wiki_tensaku_content_reframe_v1.md",
            "wiki_tensaku_content_reframe_v1.html",
            "wiki_tensaku_content_reframe_v1.s_review_packet.json",
            "wiki_tensaku_content_reframe_v1.receipt.json",
        }
        try:
            for name in expected_names:
                if (temp_dir / name).read_bytes() != (args.output_dir / name).read_bytes():
                    raise ValueError(f"tracked output is stale: {name}")
        finally:
            for path in temp_dir.iterdir():
                path.unlink()
            temp_dir.rmdir()
        print(
            json.dumps(
                {
                    "status": "verified",
                    "artifact_id": ARTIFACT_ID,
                    "clip_units": len(plan["narrative_assembly_ir"]["clip_units"]),
                    "score": plan["acceptance_score"]["earned_points"],
                    "generated_mp4_count": 0,
                },
                ensure_ascii=False,
            )
        )
        return 0

    receipt = write_outputs(plan, args.output_dir)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
