"""共通: 設定・状態・DRY_RUN/KILL_SWITCH・OAuth1付きXクライアント(標準ライブラリのみ)。"""
import base64, hashlib, hmac, json, os, secrets, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = Path(os.environ.get("STATE_DIR", ROOT / "state"))


def load_config():
    return json.loads((ROOT / "config" / "bot.json").read_text(encoding="utf-8"))


def dry_run():
    return os.environ.get("DRY_RUN", "true").strip().lower() != "false"


def kill_switch():
    return os.environ.get("KILL_SWITCH", "").strip().lower() in ("1", "true", "yes", "on")


def load_state(name, default):
    p = STATE_DIR / name
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return default


def save_state(name, data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def log(tag, msg):
    print(f"[{tag}] {msg}", flush=True)


def _pct(s):
    return urllib.parse.quote(str(s), safe="~")


def oauth1_header(method, url, params, creds, nonce=None, ts=None):
    """OAuth1.0a HMAC-SHA1。JSONボディは署名対象外、クエリは対象。"""
    oauth = {
        "oauth_consumer_key": creds["api_key"],
        "oauth_nonce": nonce or secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(ts or int(time.time())),
        "oauth_token": creds["access_token"],
        "oauth_version": "1.0",
    }
    allp = {**params, **oauth}
    pstr = "&".join(f"{_pct(k)}={_pct(v)}" for k, v in sorted(allp.items()))
    base = "&".join([method.upper(), _pct(url), _pct(pstr)])
    key = f"{_pct(creds['api_secret'])}&{_pct(creds['access_secret'])}"
    sig = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    oauth["oauth_signature"] = sig
    return "OAuth " + ", ".join(f'{_pct(k)}="{_pct(v)}"' for k, v in sorted(oauth.items()))


def creds_from_env():
    m = {"api_key": "X_API_KEY", "api_secret": "X_API_SECRET",
         "access_token": "X_ACCESS_TOKEN", "access_secret": "X_ACCESS_SECRET"}
    c = {k: os.environ.get(v, "") for k, v in m.items()}
    missing = [m[k] for k, v in c.items() if not v]
    if missing:
        raise RuntimeError("X認証情報が未設定: " + ", ".join(missing))
    return c


class XClient:
    BASE = "https://api.twitter.com/2"

    def __init__(self, creds=None, opener=None):
        self.creds = creds or creds_from_env()
        self.opener = opener or urllib.request.urlopen

    def request(self, method, path, params=None, body=None):
        url = self.BASE + path
        params = params or {}
        full = url + ("?" + urllib.parse.urlencode(params) if params else "")
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(full, data=data, method=method)
        req.add_header("Authorization", oauth1_header(method, url, params, self.creds))
        if data:
            req.add_header("Content-Type", "application/json")
        with self.opener(req, timeout=30) as r:
            return json.loads(r.read().decode() or "{}")

    def me(self):
        return self.request("GET", "/users/me")["data"]["id"]

    def post(self, text):
        return self.request("POST", "/tweets", body={"text": text})

    def retweet(self, my_id, tweet_id):
        return self.request("POST", f"/users/{my_id}/retweets", body={"tweet_id": tweet_id})

    def follow(self, my_id, target_id):
        return self.request("POST", f"/users/{my_id}/following", body={"target_user_id": target_id})

    def search(self, query, max_results=50):
        return self.request("GET", "/tweets/search/recent", params={
            "query": query, "max_results": str(max_results),
            "tweet.fields": "public_metrics,author_id", "expansions": "author_id",
            "user.fields": "username,public_metrics"})


def get_client(real):
    return XClient() if real else None


def guard(tag):
    """KILL_SWITCH時はTrue(処理を中止すべき)。"""
    if kill_switch():
        log(tag, "KILL_SWITCH有効のため何もせず終了")
        return True
    return False
