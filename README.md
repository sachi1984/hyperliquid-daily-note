# Hyperliquid Daily Note (自動化)

毎朝、HYPEの価格＋直近ニュースをキュレーションしたnote記事を**下書き**として
自動生成するGitHub Actionsワークフローです。実行はGitHub Actions上のClaude Code
（`anthropic_api_key`によるAPI課金。Claude ProプランのClaude Codeとは別会計）が
行います。

## 含まれるファイル

- `.github/workflows/daily-hyperliquid-note.yml` … 毎日07:30(JST)に自動実行されるワークフロー本体
- `.mcp.json` … note.comへの下書き投稿に使う`note-com-mcp`サーバーの接続設定

## セットアップ手順(最初の1回だけ)

### 1. このファイル一式を新しいGitHubリポジトリにpush

### 2. GitHubリポジトリにSecretsを登録

対象リポジトリの **Settings → Secrets and variables → Actions → New repository secret**
で以下の3つを登録してください。

| Secret名 | 内容 |
|---|---|
| `ANTHROPIC_API_KEY` | Claude APIキー(console.anthropic.comで発行。Claude Proとは別料金) |
| `NOTE_EMAIL` | noteのログインに使っているメールアドレス |
| `NOTE_PASSWORD` | noteのログインパスワード |

ログイン処理自体はワークフローの中でnote-com-mcpが自動で行うので、
手元での事前準備は不要です。

### 3. 手動実行でテスト

GitHubの **Actions** タブ → `Daily Hyperliquid Note` → **Run workflow** で
手動実行し、noteに下書きが1件できているか確認してください。

## 運用上の注意

- **記事は必ず下書き(非公開)止まりです。** 公開は毎日あなたが内容を確認してから
  手動で行ってください。
- GitHub Actionsの実行環境は毎回IPアドレスが変わるため、note側が
  「いつもと違う環境からのログイン」と判断してメール認証コードを要求してくる
  ことがあります。その場合はワークフローが一度失敗するので、届いたメールの
  認証コードをnote.comのサイト上で手動入力して一度ログインを通してあげれば、
  以降は安定することが多いです。何度も頻発するようなら、Cookie直接指定方式
  (`NOTE_SESSION_V5`等)への切り替えを検討してください(その際はまた相談してください)。
- コストの目安: 1日あたり数円〜十数円程度(Claude API従量課金)。Claude Proの
  利用枠(Claude Code/claude.aiの対話)とは別会計なので、他の作業を圧迫しません。
- ビルドエントリ確認: `.mcp.json`は`node mcp/note-com-mcp/dist/index.js`を
  起動する前提です。note-com-mcpの`package.json`の`"main"`フィールドが違う
  場合は、`.mcp.json`の`args`を合わせて書き換えてください。
- note.com側の内部API仕様が変わると、予告なくワークフローが失敗することが
  あります(非公式API利用に伴う既知のリスクです)。
