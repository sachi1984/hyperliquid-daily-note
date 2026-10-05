import os, unittest
from bot import price_alert as pa, common as c, daily_post, follow, repost

CFG = {"coin": "HYPE", "threshold_pct": 1.0, "window_minutes": 60, "cooldown_minutes": 120}
NOW = 100000
HIST = [{"t": NOW - 3600, "p": 100.0}, {"t": NOW - 1800, "p": 100.0}]


class Alert(unittest.TestCase):
    def test_surge(self):
        a, _ = pa.evaluate(HIST, NOW, 102.0, CFG, None)
        self.assertEqual(a["direction"], "up"); self.assertIn("急騰", a["text"])

    def test_drop(self):
        a, _ = pa.evaluate(HIST, NOW, 98.0, CFG, None)
        self.assertEqual(a["direction"], "down"); self.assertIn("急落", a["text"])

    def test_no_change(self):
        a, h = pa.evaluate(HIST, NOW, 100.5, CFG, None)
        self.assertIsNone(a); self.assertEqual(len(h), 3)

    def test_cooldown_same_direction(self):
        a, _ = pa.evaluate(HIST, NOW, 102.0, CFG, {"t": NOW - 600, "direction": "up"})
        self.assertIsNone(a)

    def test_cooldown_opposite_direction_allowed(self):
        a, _ = pa.evaluate(HIST, NOW, 98.0, CFG, {"t": NOW - 600, "direction": "up"})
        self.assertEqual(a["direction"], "down")

    def test_cooldown_expired(self):
        a, _ = pa.evaluate(HIST, NOW, 102.0, CFG, {"t": NOW - 8000, "direction": "up"})
        self.assertIsNotNone(a)

    def test_insufficient_history(self):
        a, _ = pa.evaluate([{"t": NOW - 60, "p": 100.0}], NOW, 110.0, CFG, None)
        self.assertIsNone(a)


class Misc(unittest.TestCase):
    def test_follow_pick_dedupe_limit(self):
        u = [{"id": str(i)} for i in range(20)]
        self.assertEqual([x["id"] for x in follow.pick(u, ["0", "1"], 3)], ["2", "3", "4"])

    def test_repost_pick(self):
        t = [{"id": "a", "public_metrics": {"like_count": 1}}, {"id": "b", "public_metrics": {"like_count": 9}},
             {"id": "c", "public_metrics": {"like_count": 20}}]
        self.assertEqual([x["id"] for x in repost.pick(t, {"c"}, 5, 3)], ["b"])

    def test_summarize_len(self):
        s = daily_post.summarize("# 今日のHyperliquid 2026年10月5日\nHYPE $40 (+2.1%)\n- あ。い\n- う\n", 270)
        self.assertLessEqual(len(s), 270); self.assertIn("#Hyperliquid", s)

    def test_oauth_header_shape(self):
        h = c.oauth1_header("POST", "https://api.twitter.com/2/tweets", {},
                            {"api_key": "k", "api_secret": "s", "access_token": "t", "access_secret": "u"},
                            nonce="n", ts=1)
        self.assertTrue(h.startswith("OAuth ")); self.assertIn("oauth_signature=", h)

    def test_kill_switch(self):
        os.environ["KILL_SWITCH"] = "true"
        try:
            self.assertTrue(c.guard("t"))
        finally:
            del os.environ["KILL_SWITCH"]

    def test_dry_run_without_creds_succeeds(self):
        import subprocess, sys
        env = {k: v for k, v in os.environ.items() if not k.startswith("X_")}
        env.update(DRY_RUN="true", STATE_DIR="/tmp/_st")
        for m in ("daily_post", "repost", "follow"):
            r = subprocess.run([sys.executable, "-m", "bot." + m], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("認証情報なし", r.stdout)

    def test_dry_run_default(self):
        os.environ.pop("DRY_RUN", None)
        self.assertTrue(c.dry_run())


if __name__ == "__main__":
    unittest.main()
