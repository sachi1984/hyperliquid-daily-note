"""HYPE価格アラート。15分間隔で価格を保存し、約1時間前との比較で±閾値超えを判定。"""
import json, sys, time, urllib.request
from bot import common as c

API = "https://api.hyperliquid.xyz/info"


def fetch_price(coin="HYPE", opener=urllib.request.urlopen):
    req = urllib.request.Request(API, data=json.dumps({"type": "metaAndAssetCtxs"}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with opener(req, timeout=20) as r:
        meta, ctxs = json.loads(r.read().decode())
    for i, u in enumerate(meta["universe"]):
        if u["name"] == coin:
            return float(ctxs[i]["markPx"])
    raise RuntimeError(f"{coin}が見つかりません")


def evaluate(history, now, price, cfg, last_alert):
    """history: [{t,p}]。戻り値: (alert|None, history_new)。alert={direction,change_pct,text}"""
    win = cfg["window_minutes"] * 60
    hist = [h for h in history if now - h["t"] <= win * 3] + [{"t": now, "p": price}]
    # window前後で最も近い過去点(窓の0.5〜1.5倍の範囲内)を基準にする
    cands = [h for h in hist[:-1] if win * 0.5 <= now - h["t"] <= win * 1.5]
    if not cands:
        return None, hist
    base = min(cands, key=lambda h: abs((now - h["t"]) - win))
    chg = (price / base["p"] - 1) * 100
    if abs(chg) < cfg["threshold_pct"]:
        return None, hist
    direction = "up" if chg > 0 else "down"
    if last_alert and last_alert.get("direction") == direction and \
            now - last_alert["t"] < cfg["cooldown_minutes"] * 60:
        return None, hist
    arrow = "📈 急騰" if chg > 0 else "📉 急落"
    text = (f"{arrow} ${cfg['coin']} が1時間で{chg:+.2f}%\n"
            f"${base['p']:.3f} → ${price:.3f}\n#Hyperliquid #HYPE")
    return {"direction": direction, "change_pct": chg, "text": text}, hist


def main():
    if c.guard("alert"):
        return 0
    cfg = c.load_config()["alert"]
    now = int(time.time())
    price = fetch_price(cfg["coin"])
    st = c.load_state("price_history.json", {"history": [], "last_alert": None})
    alert, hist = evaluate(st["history"], now, price, cfg, st["last_alert"])
    st["history"] = hist
    c.log("alert", f"{cfg['coin']}={price} 履歴{len(hist)}件")
    if alert:
        c.log("alert", f"検知: {alert['direction']} {alert['change_pct']:+.2f}%")
        if c.dry_run():
            c.log("alert", f"[DRY_RUN] 投稿内容:\n{alert['text']}")
        else:
            c.get_client(True).post(alert["text"])
            c.log("alert", "投稿しました")
        st["last_alert"] = {"t": now, "direction": alert["direction"]}
    else:
        c.log("alert", "アラート条件なし")
    c.save_state("price_history.json", st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
