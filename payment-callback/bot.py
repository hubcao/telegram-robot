import os
import json
import urllib.request

_BASE = f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}"

def send_message(chat_id, text, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    data    = json.dumps(payload).encode("utf-8")
    req     = urllib.request.Request(
        f"{_BASE}/sendMessage", data=data,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
