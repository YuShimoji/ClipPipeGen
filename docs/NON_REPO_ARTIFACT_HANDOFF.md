# Non-Repo Artifact Handoff

ClipPipeGen の local episode には、diagnostic render video や source media のように、サイズや権利境界の理由で Git に入れない artifact がある。これらは存在そのものを隠すのではなく、Git 外の実体と Git 管理できる手順・境界情報を分けて引き継ぐ。

`rendered_video.mp4` は Git に含めない。Git に含める対象は、仕組みを再現するコード、schema、docs であり、local handoff manifest には artifact identity、source identity、local path、size、hash、generation command、dependency artifact、rights boundary、production boundary、missing 時の復旧手順を記録する。episode 配下の実体や R3 固有の `non_repo_artifact_handoff.json` / `.html` は `.gitignore` の対象なので、fresh checkout には含まれない。別端末で必要な場合は CLI で再生成し、動画本体が必要な場合だけ Git ではなく許可された local storage / artifact transfer 経路を使う。

## CLI

`build-non-repo-handoff` は local artifact handoff manifest/report を作る command であり、`render-tiny-proof` の代替ではない。動画本体を再生成する場合は、manifest の `missing_behavior.regeneration_command` に記録された render command などを別途実行する。

```powershell
python -m src.cli.main build-non-repo-handoff `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --render-manifest episodes/jp_pilot01_hololive_bancho_20260525/renders/jp_pilot01r3_subtitle_import_diagnostic_render/render_manifest.json `
  --nle-manifest episodes/jp_pilot01_hololive_bancho_20260525/exports/jp_pilot01r3_subtitle_import/nle_export_manifest.json `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review `
  --format json
```

出力は `non_repo_artifact_handoff.json` と `non_repo_artifact_handoff.html`。動画本体をコピー、埋め込み、Base64 化、HTML の `video` tag 参照にはしない。

## 別端末での扱い

「別端末」は三つに分けて読む。

| 状態 | 何があるか | 扱い |
|---|---|---|
| Same machine / same workspace | ignored `episodes/` が残っていれば、local manifest/report、`rendered_video.mp4`、source media、subtitle track を照合できる | hash / size / source identity を確認し、diagnostic local review evidence としてだけ扱う |
| Different machine with transferred local episode artifacts | Git 外の許可された transfer 経路で episode artifacts を移した場合のみ、R3 固有 manifest/report や動画を照合できる | 移送後も Git 管理対象にはしない。hash / size / source identity と rights / production boundary を確認する |
| Fresh checkout only | generator / schema / docs / tests はあるが、R3 固有 manifest/report、`rendered_video.mp4`、source media、subtitle track、render manifest は無い | 必要な upstream artifacts が揃うまで missing として扱い、production / creative / publish acceptance へ進めない |

1. まず handoff manifest を開き、`artifact.exists`、`artifact.local_path`、`artifact.sha256`、`source_identity`、`boundary` を確認する。
2. `rendered_video.mp4` が存在する場合は hash と size を確認し、diagnostic local review evidence としてだけ扱う。
3. 存在しない場合は `missing_behavior.regeneration_command` を使い、`dependency_artifacts` にある upstream artifacts と local source media が揃っているか確認してから再生成する。
4. 再生成できない場合は artifact を missing のまま扱い、production / creative / publish acceptance には進めない。
5. exact verification は source media、upstream JSON、render command、tool versions、profile が同じ場合の sha256 比較。環境差で hash が揺れる場合は duration / resolution / codec / timeline / subtitle source refs / boundary flags を approximate verification として比較する。再 render の byte-exact hash と metadata approximate の採否基準は、今後の Verify slice で決める。

## 境界

diagnostic render は local review only であり、production render、creative acceptance、publish acceptance ではない。`rights_manifest.compliance_check.status=pending` の artifact は production / public 利用しない。rights approval、production subtitle/render acceptance、publishing/OAuth は別 slice で扱う。

特定クラウドや公開共有はこの docs では前提にしない。動画本体が必要な場合は、権限のある local storage または許可された artifact transfer 経路で移す。
