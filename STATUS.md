# STATUS — hyperliquid-daily-note

最終更新: 2026-10-05(状態保存・実行時間・疎通確認を改善)

## あなたがやること(これだけ見ればOK)
- [ ] 作業ブランチ `claude/new-session-wiotz0` のPRを確認してマージ
- [ ] `docs/PREFLIGHT.md` の手順でX APIキーを発行し、GitHub Secrets(`X_API_KEY` `X_API_SECRET` `X_ACCESS_TOKEN` `X_ACCESS_SECRET`)に登録。Xの料金プランで投稿/検索/フォロー/リポストが使えるかも確認
- [ ] Actionsタブ → `X Automation` を `job=alert` などで手動実行し、DRY_RUNログを確認
- [ ] 自動フォローを本番ONにするかの判断(既定はdry-run。ONは Variables に `DRY_RUN=false`、緊急停止は `KILL_SWITCH=true`)

## 現状(要件の実装状況)
| # | 要件 | 状況 | 備考 |
|---|---|---|---|
| 1 | note日次記事の生成 | 完了 | `daily-hyperliquid-note.yml`、drafts/へコミット。note投稿は手動貼り付け運用 |
| 2 | X投稿・リポスト | 実装済み(未実機) | `bot/daily_post.py` `bot/repost.py`。リポストは1日3件上限。DRY_RUNで確認済、X API実機は未確認 |
| 3 | 日本語アカウント自動フォロー | 実装済み(未実機) | `bot/follow.py`。上限既定10/日、ランダム間隔、重複回避、KILL_SWITCH |
| 4 | HYPE急騰急落アラート | 実装済み(未実機) | `bot/price_alert.py`。15分間隔、1時間±1%、クールダウン2時間。判定テスト通過 |

実行基盤: `.github/workflows/x-automation.yml`(状態は専用ブランチ `bot-state` に変更時のみコミット。アラートは30分間隔)。疎通確認: `connectivity-check.yml`。設定: `config/bot.json`。環境変数: `docs/ENV.md`。

## 決定事項
- 課金はある程度許容する。
- noteは手動貼り付け運用で確定。
- 外部依存を避けるためボットはPython標準ライブラリのみ・OAuth1.0aをtweepy無しで実装。
- 同方向アラートのみクールダウン対象(逆方向は即通知)。
- X API仕様(エンドポイント/プラン制限)はこの環境から公式ドキュメントを参照できず、既知のv2仕様で実装。変更があれば実機テストで判明する前提。

- 状態は main に置かず `bot-state` ブランチへ(履歴汚染防止)。価格履歴は保存せずローソク足APIで毎回1時間前と比較。
- アラート間隔を15分→30分に変更(月約1,700分で無料枠2,000分内。根拠は docs/PREFLIGHT.md §5)。

## 未了タスク
- X API実機での疎通(上記「あなたがやること」)

## ブロック/リスク
- 自動フォローはXの自動化ルールに抵触してアカウント凍結のリスクがある。保守的な上限とdry-run既定で実装。
- X APIの無料枠では書き込み/検索が使えない可能性。
