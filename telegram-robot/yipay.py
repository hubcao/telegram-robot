import os
import hashlib
import urllib.parse
import urllib.request
import json

_PID  = os.environ["YIPAY_PID"]
_KEY  = os.environ["YIPAY_KEY"]
_API  = "https://juea.cn/mapi.php"

def _sign(params: dict) -> str:
    filtered = {k: v for k, v in params.items()
                if k not in ("sign", "sign_type") and str(v) != ""}
    sign_str = "&".join(
        f"{k}={filtered[k]}" for k in sorted(filtered)
    ) + _KEY
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()

def verify_sign(params: dict) -> bool:
    return params.get("sign") == _sign(params)

def create_order(order_id: str, plan_name: str, money: str,
                 notify_url: str, user_id: str, plan_key: str,
                 return_url: str = "") -> dict:          # ← 加了 return_url
    params = {
        "pid":          _PID,
        "type":         "alipay",
        "out_trade_no": order_id,
        "notify_url":   notify_url,
        "name":         plan_name,
        "money":        money,
        "clientip":     "127.0.0.1",
        "device":       "pc",
        "param":        f"{user_id}|{plan_key}",
        "sign_type":    "MD5",
    }
    if return_url:
        params["return_url"] = return_url               # ← 有值才加入签名
    params["sign"] = _sign(params)
    data = urllib.parse.urlencode(params).encode("utf-8")
    req  = urllib.request.Request(
        _API, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read().decode("utf-8"))
