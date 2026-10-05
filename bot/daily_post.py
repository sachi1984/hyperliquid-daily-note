"""最新のdrafts記事から要点を短くまとめたX投稿を作る。"""
import re, sys
from bot import common as c


def latest_draft():
    files = sorted((c.ROOT / "drafts").glob("*-hyperliquid.md"))
    return files[-1] if files else None


def summarize(md, max_len=270):
    lines = [l.strip() for l in md.splitlines() if l.strip()]
    title = next((re.sub(r"^#+\s*", "", l) for l in lines if l.startswith("#")), "今日のHyperliquid")
    price = next((l for l in lines if "前日比" in l and "$" in l), "")
    price = ("HYPE " + price) if price else ""
    bullets = [re.sub(r"^[-*・]\s*", "", l) for l in lines if re.match(r"^[-*・]\s", l)]
    bullets = [re.sub(r"[*_`]|\[([^\]]+)\]\([^)]*\)", r"\1", b) for b in bullets]
    price = re.sub(r"[*_`#]", "", price)
    parts = [title, price[:100]]
    for b in bullets[:3]:
        parts.append("・" + b.split("。")[0][:60])
    parts.append("#Hyperliquid #HYPE")
    text = "\n".join(p for p in parts if p)
    return text if len(text) <= max_len else text[:max_len - 1] + "…"


def main():
    if c.guard("post"):
        return 0
    d = latest_draft()
    if not d:
        c.log("post", "draftsがありません")
        return 0
    text = summarize(d.read_text(encoding="utf-8"), c.load_config()["post"]["max_len"])
    st = c.load_state("posted.json", {"files": []})
    if d.name in st["files"]:
        c.log("post", f"{d.name} は投稿済み")
        return 0
    if c.dry_run():
        c.log("post", f"[DRY_RUN] 投稿内容({d.name}):\n{text}")
    else:
        c.get_client(True).post(text)
        c.log("post", "投稿しました")
        st["files"].append(d.name)
        c.save_state("posted.json", st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
