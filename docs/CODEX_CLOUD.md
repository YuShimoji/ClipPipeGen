# ClipPipeGen の Cloud 開発

CloudではCLI、Editing core、素材台帳、権利readback、字幕案、GUIコードを編集し、同梱fixtureで検証する。PC内の `episodes/` はGitに含まれないため、既存の実動画をCloudの入力として推定しない。

## 環境を準備する

ChatGPTの「設定 → Codex Cloud → 環境」で `Media Contents Projects` を作成し、今回指定された `YuShimoji/NLMYTGen`、`YuShimoji/ClipPipeGen`、`YuShimoji/FastFictionFactory` だけを選ぶ。各タスクの対象は明示する。他リポジトリのソースをimport/copyせず、NLMYTGenの再利用は既存のCLI subprocess境界を使う。

Cloud準備の版は `codex/cloud-development-20261011`。既定の `main` とは別なので、セットアップ会話でこのブランチを指定し、`git branch --show-current` と `git rev-parse HEAD` を確認してから実行する。

| 項目 | ClipPipeGen の設定 |
| --- | --- |
| ランタイム | Python 3.11、Node.js 24、uv |
| Install script | このリポジトリで `bash scripts/codex/setup.sh` |
| Start skill | `AGENTS.md` のread orderを読み、`bash scripts/codex/check.sh` を実行。常駐サービスは不要 |
| ネットワーク | 既存GitHub接続とパッケージ取得に必要な範囲 |
| 秘密情報 | 基本開発では不要 |
| 共有 | Only me |

Install scriptは既存テストが使うpytest 8.4.2をisolated venvへ入れ、`package-lock.json` からElectronの依存を復元する。runtime dependencyや既存lockfileは変更しない。準備と検証後に「Publish」で環境を保存する。

`.codex/environments/environment.toml` はDesktopのローカル環境設定。PCのabsolute pathや `npm run cockpit` をCloudのInstall scriptへ流用しない。

## 実装後の検証

```bash
bash scripts/codex/check.sh
.venv/bin/python -B -m pytest -q tests/<対象のテスト>.py
```

checkはCLIの起動、rights manifest、edit pack、transcript、字幕生成、private artifact transferの正常系と拒否系、および既存GUI smokeを確認する。実動画render、素材fetch、OAuth、字幕の実画面採否は実行しない。FFmpeg/FFprobeやフォントを使う変更は、既存integrationの必要ツールとexact入力を追加確認してから該当testを実行する。

Windowsの隔離checkoutで同じ検証を行う場合:

```powershell
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe 'pytest==8.4.2'
$env:CLIPPIPEGEN_PYTHON = '.venv/Scripts/python.exe'
& 'C:\Program Files\Git\bin\bash.exe' scripts/codex/check.sh
```

## 素材とレビュー

`episodes/`、local config、credentials、未保存GUI stateはCloudへ自動転送されない。exact入力がない操作はその操作だけ保留し、同梱fixtureで可能な実装と検証を続ける。欠落を埋めるためのYouTube再取得、cookies/OAuth、既存素材の公開はこのセットアップに含めない。媒体の運搬には既存の `docs/PRIVATE_ARTIFACT_TRANSFER.md` と入力ごとの権限を使う。

修正前にユーザー現象と期待結果、原因根拠または判別できる仮説を示す。原因不明の数値調整を反復しない。Cloudで確認した動作と、Windowsに残る実画面・実動画確認を報告する。rights、production、publication、既存accepted/rejected判断はrepo-local正本を使う。

ローカル個人skillはCloudへ自動同期されない。`AGENTS.md` と正本文書を読み、既存のdirty、untracked、ignored素材を保持する。下流から親チャットへの通知・ACK・callbackは追加せず、結果を担当リポジトリへ保存する。

現在のCloud環境作成・Publish手順: [OpenAI公式ガイド](https://learn.chatgpt.com/docs/environments/cloud-environments)。
