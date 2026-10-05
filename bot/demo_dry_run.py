"""ネットワーク不要のDRY_RUNデモ(価格APIをモック)。実行: python -m bot.demo_dry_run"""
import os, tempfile, time
os.environ["DRY_RUN"] = "true"
os.environ["STATE_DIR"] = tempfile.mkdtemp()
from bot import common as c, price_alert, daily_post, repost, follow  # noqa: E402

now = int(time.time())
c.save_state("price_history.json", {"history": [{"t": now - 3600, "p": 40.0}], "last_alert": None})
price_alert.fetch_price = lambda coin="HYPE", opener=None: 41.0  # +2.5%
print("== price_alert =="); price_alert.main()
print("== daily_post =="); daily_post.main()
print("== repost =="); repost.main()
print("== follow =="); follow.main()
