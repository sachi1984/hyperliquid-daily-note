# 環境変数一覧(値は書かない)

| 名前 | 種別 | 用途 |
|---|---|---|
| `X_API_KEY` / `X_API_SECRET` | Secret | X開発者アプリのConsumer Keys |
| `X_ACCESS_TOKEN` / `X_ACCESS_SECRET` | Secret | 投稿アカウントのAccess Token(Read and write権限) |
| `ANTHROPIC_API_KEY` | Secret | 記事生成ワークフロー用 |
| `DRY_RUN` | Variable | 既定 true。`false` にした時だけ実際に投稿/リポスト/フォロー |
| `KILL_SWITCH` | Variable | `true` で全ボットジョブが何もせず終了(緊急停止) |
| `STATE_DIR` | 任意 | 状態ファイルの保存先(既定 `state/`) |
