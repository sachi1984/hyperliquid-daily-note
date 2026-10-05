# PREFLIGHT — オーナーが事前に用意するもの

## 1. X APIの認証情報(Secrets)
1. https://developer.x.com でDeveloperアカウント登録→Projectとアプリを作成。
2. アプリの **User authentication settings** で App permissions を **Read and write** にして保存する(Type: Web App/Automated App)。
3. **必ず手順2の後に** **Keys and tokens** でアクセストークンを発行する。
   ⚠ 権限を変更する前に発行したAccess Token/Secretは**読み取り専用のまま**で、権限を変えても自動では書き込み可能にならない(投稿時に403になる)。権限変更後は **Regenerate** で再発行し、Secretsも新しい値に更新すること。発行するもの:
   - API Key / API Key Secret
   - Access Token / Access Token Secret(自分の運用アカウントで)
4. GitHub → Settings → Secrets and variables → Actions → **Secrets** に登録:

| Secret名 | 値 |
|---|---|
| `X_API_KEY` | API Key |
| `X_API_SECRET` | API Key Secret |
| `X_ACCESS_TOKEN` | Access Token |
| `X_ACCESS_SECRET` | Access Token Secret |

## 2. APIの利用プラン(課金)
投稿・検索・フォロー・リポストの各エンドポイントは、無料枠では使えない/上限が極小の場合がある。X Developer Portalで現在のプランと従量課金を確認し、必要なら有料プランを有効化する。
(課金は許容済み。ただし料金体系は変動するため実機で確認すること。)

## 3. 段階的な本番化(Variables)
- 既定は `DRY_RUN=true`(ログ出力のみ)。Actionsタブで各ジョブを手動実行し、ログの内容を確認。
- 問題なければ Variables に `DRY_RUN=false` を追加。まず価格アラート/投稿→リポスト→最後にフォローの順を推奨。
- 緊急停止: Variables に `KILL_SWITCH=true`。
- フォローは Xの自動化ルール抵触リスクあり。上限は `config/bot.json` の `follow.daily_limit`(既定10)。

## 4. 疎通確認(ブラウザだけで完結。Python不要)
GitHub → Actions → **Connectivity Check** → **Run workflow**。
実行後、そのRunのページ下部の **Summary** に結果表が出る(Hyperliquid価格/ローソク足、X認証、X検索の読み取り)。
読み取り(GET)のみで、投稿・フォロー・リポストは一切しない。
書き込み権限とフォロー/リポストの可否は書き込み無しでは確認できないため、`DRY_RUN=false` にした最初の実行で確認する。

## 5. 状態の保存先と実行時間
- 状態(クールダウン、フォロー済み、リポスト済み、投稿済み)は main ではなく専用ブランチ `bot-state` に、変更があった時だけコミットされる(GITHUB_TOKENのpushは他のワークフローを起動しない)。価格履歴は保存せず、毎回ローソク足APIから取得する。
- 月間使用時間の見積もり(1ジョブ最低1分課金): アラート 30分間隔=約1,440分 + 日次投稿/リポスト/フォロー 約120分 + 記事生成 約90〜150分 = **約1,650〜1,710分**(無料枠2,000分/月に収まる。パブリックなら無制限)。15分間隔だと約2,880分+αで超過するため30分間隔にしている。
- 余裕がなければ `.github/workflows/x-automation.yml` の `7,37 * * * *` を `7 * * * *`(毎時、約720分)に変える。
