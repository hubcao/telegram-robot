import hashlib
import hmac
import time

def verify_telegram_login(params: dict, bot_token: str) -> dict | None:
    received_hash = params.get("hash", "")
    auth_date     = int(params.get("auth_date", 0))

    if time.time() - auth_date > 86400:
        return None

    fields = {k: v for k, v in params.items() if k != "hash"}
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(fields.items())
    )

    secret_key     = hashlib.sha256(bot_token.encode()).digest()
    expected_hash  = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        return None

    return {
        "id":         params.get("id"),
        "first_name": params.get("first_name", ""),
        "username":   params.get("username", ""),
    }
