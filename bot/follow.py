"""Hyperliquid関連の日本語アカウントを保守的にフォロー(上限・揺らぎ・重複回避・KILL_SWITCH)。"""
import datetime, random, sys, time
from bot import common as c


def pick(users, followed, limit):
    seen, out = set(followed), []
    for u in users:
        if u["id"] in seen:
            continue
        seen.add(u["id"]); out.append(u)
        if len(out) >= limit:
            break
    return out


def main(client=None, sleep=time.sleep):
    if c.guard("follow"):
        return 0
    cfg = c.load_config()["follow"]
    today = datetime.date.today().isoformat()
    st = c.load_state("followed.json", {"ids": [], "day": today, "count": 0})
    if st["day"] != today:
        st["day"], st["count"] = today, 0
    remain = cfg["daily_limit"] - st["count"]
    if remain <= 0:
        c.log("follow", "本日の上限に達しています")
        return 0
    real = not c.dry_run()
    client = client or (c.get_client(True) if real else None)
    users = []
    if client:
        for q in cfg["queries"]:
            r = client.search(q)
            users += r.get("includes", {}).get("users", [])
    else:
        c.log("follow", "[DRY_RUN] 検索はスキップ。ダミー候補で動作確認")
        users = [{"id": f"DUMMY{i}", "username": f"dummy_user{i}"} for i in range(1, 4)]
    chosen = pick(users, st["ids"], remain)
    me = client.me() if client else "ME"
    for i, u in enumerate(chosen):
        if real:
            client.follow(me, u["id"])
            st["ids"].append(u["id"]); st["count"] += 1
            c.log("follow", f"フォロー: @{u.get('username')}")
            if i < len(chosen) - 1:
                sleep(random.uniform(cfg["min_sleep_sec"], cfg["max_sleep_sec"]))
        else:
            c.log("follow", f"[DRY_RUN] フォロー対象: @{u.get('username')} (上限{cfg['daily_limit']}/日)")
    if real:
        c.save_state("followed.json", st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
