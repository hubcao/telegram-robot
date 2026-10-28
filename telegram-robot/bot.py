import os
import json
import urllib.request

_BASE = f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}"

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    _post(f"{_BASE}/sendMessage", payload)

def _post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
