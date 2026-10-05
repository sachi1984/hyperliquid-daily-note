"""キーワード検索でHyperliquid関連の重要ポストをリポスト(1日上限あり)。"""
import datetime, sys
from bot import common as c


def pick(tweets, done, min_likes, limit):
    ok = [t for t in tweets if t["id"] not in done and
          t.get("public_metrics", {}).get("like_count", 0) >= min_likes]
    ok.sort(key=lambda t: t["public_metrics"]["like_count"], reverse=True)
    return ok[:limit]


def main(client=None):
    if c.guard("repost"):
        return 0
    cfg = c.load_config()["repost"]
    today = datetime.date.today().isoformat()
    st = c.load_state("reposted.json", {"ids": [], "day": today, "count": 0})
    if st["day"] != today:
        st["day"], st["count"] = today, 0
    remain = cfg["daily_limit"] - st["count"]
    if remain <= 0:
        c.log("repost", "本日の上限に達しています")
        return 0
    real = not c.dry_run()
    client = client or (c.get_client(True) if real else None)
    tweets = []
    if client:
        for q in cfg["queries"]:
            tweets += client.search(q).get("data", [])
    else:
        c.log("repost", "[DRY_RUN] 検索はスキップ(読み取りも実行したい場合は DRY_RUN=false)。候補ダミーで動作確認")
        tweets = [{"id": "DUMMY1", "text": "(ダミー)Hyperliquid関連の重要ポスト", "public_metrics": {"like_count": 99}}]
    chosen = pick(tweets, set(st["ids"]), cfg["min_likes"], remain)
    me = client.me() if client else "ME"
    for t in chosen:
        if real:
            client.retweet(me, t["id"])
            st["ids"].append(t["id"]); st["count"] += 1
            c.log("repost", f"リポスト: {t['id']}")
        else:
            c.log("repost", f"[DRY_RUN] リポスト対象: {t['id']} {t['text'][:60]}")
    c.save_state("reposted.json", st) if real else None
    return 0


if __name__ == "__main__":
    sys.exit(main())
