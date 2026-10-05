"""疎通確認(読み取りのみ・書き込みなし)。結果を GITHUB_STEP_SUMMARY に出力。"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from bot import common as c, price_alert

rows = []


def rec(name, ok, detail):
    rows.append((name, ok, detail))
    c.log("check", f"{'OK' if ok else 'NG'} {name}: {detail}")


def x_get(path, params=None):
    url = "https://api.twitter.com/2" + path
    params = params or {}
    full = url + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(full, method="GET")  # GET固定: 書き込みは一切しない
    req.add_header("Authorization", c.oauth1_header("GET", url, params, c.creds_from_env()))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}"), r.headers
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:300]}, e.headers


def check_hyperliquid():
    try:
        p = price_alert.fetch_price("HYPE")
        rec("Hyperliquid 価格取得", True, f"HYPE markPx={p}")
    except Exception as e:
        rec("Hyperliquid 価格取得", False, repr(e)[:200]); return
    try:
        pts = price_alert.fetch_recent_points("HYPE")
        cfg = c.load_config()["alert"]
        a, _ = price_alert.evaluate(pts, int(time.time()), p, cfg, None)
        first = pts[0]["p"] if pts else None
        rec("Hyperliquid ローソク足", len(pts) > 0, f"{len(pts)}点, 最古={first}, 現在アラート判定={'あり' if a else 'なし'}")
    except Exception as e:
        rec("Hyperliquid ローソク足", False, repr(e)[:200])


def check_x():
    try:
        c.creds_from_env()
    except RuntimeError as e:
        rec("X 認証", False, str(e)); return
    st, body, h = x_get("/users/me")
    if st == 200:
        rec("X 認証(GET /users/me)", True, f"@{body['data'].get('username')} (id={body['data']['id']})")
    else:
        hint = {401: "キー/トークン不一致。4つのSecretsを再確認", 403: "プラン/権限不足の可能性",
                429: "レート制限"}.get(st, "")
        rec("X 認証(GET /users/me)", False, f"HTTP {st} {hint} {body.get('error','')}")
        return
    st, body, h = x_get("/tweets/search/recent", {"query": "Hyperliquid", "max_results": "10"})
    rem = h.get("x-rate-limit-remaining") if h else None
    rec("X 検索API(読み取り)", st == 200,
        f"HTTP {st}" + (f" 残り{rem}" if rem else "") + ("" if st == 200 else f" {body.get('error','')}"))


def main():
    check_hyperliquid()
    check_x()
    lines = ["## 疎通確認結果(読み取りのみ・投稿/フォロー/リポストは未実行)", "",
             "| 項目 | 結果 | 詳細 |", "|---|---|---|"]
    for n, ok, d in rows:
        lines.append(f"| {n} | {'✅ OK' if ok else '❌ NG'} | {d.replace('|', '/')} |")
    lines += ["", "※ 書き込み権限(Read and write)とフォロー/リポストの可否は、書き込み無しでは検証できません。"
              "最初の本番実行(DRY_RUN=false)の結果で確認してください。"]
    out = "\n".join(lines)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(out + "\n")
    print(out)
    return 0 if all(ok for _, ok, _ in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
