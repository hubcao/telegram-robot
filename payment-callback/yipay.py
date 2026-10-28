import os
import hashlib

_KEY = os.environ["YIPAY_KEY"]

def _sign(params: dict) -> str:
    filtered = {k: v for k, v in params.items()
                if k not in ("sign", "sign_type") and str(v) != ""}
    sign_str = "&".join(
        f"{k}={filtered[k]}" for k in sorted(filtered)
    ) + _KEY
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()

def verify_sign(params: dict) -> bool:
    return params.get("sign") == _sign(params)
