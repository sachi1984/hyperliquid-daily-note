# PREFLIGHT — オーナーが事前に用意するもの

## 1. X APIの認証情報(Secrets)
1. https://developer.x.com でDeveloperアカウント登録→Projectとアプリを作成。
2. アプリの **User authentication settings** で App permissions を **Read and write** にする(Type: Web App/Automated App)。
3. **Keys and tokens** で次を発行(権限変更後に必ず再発行):
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

## 4. 実機疎通テスト(コピペ)
```
export X_API_KEY=... X_API_SECRET=... X_ACCESS_TOKEN=... X_ACCESS_SECRET=...
python -c "from bot.common import XClient; print(XClient().me())"   # 自分のユーザーIDが出ればOK
DRY_RUN=true python -m bot.price_alert                               # Hyperliquid公開API疎通
```
