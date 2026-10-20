import json
import os

# 路由常量
PATH_ALIPAY_NOTIFY = "/alipay/notify"


def lambda_handler(event, context):
    """
    Lambda 主入口
    路由：
      POST /              → Telegram Webhook
      POST /alipay/notify → 支付宝异步回调
      EventBridge         → 每日定时任务
    """
    print(f"[main] event source keys: {list(event.keys())}")

    # ── EventBridge 定时任务 ──────────────────────────────
    if event.get("source") == "aws.events" or event.get("detail-type") == "Scheduled Event":
        from handlers.scheduler import handle_scheduled_event
        handle_scheduled_event()
        return {"statusCode": 200, "body": "ok"}

    # ── HTTP 请求 ─────────────────────────────────────────
    path = event.get("rawPath", event.get("path", "/"))
    method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    body_raw = event.get("body", "{}")

    # base64 解码
    if event.get("isBase64Encoded", False):
        import base64
        body_raw = base64.b64decode(body_raw).decode("utf-8")

    print(f"[main] path={path} method={method}")

    # ── 支付宝回调 ────────────────────────────────────────
    if path == PATH_ALIPAY_NOTIFY:
        from handlers.alipay import handle_alipay_notify
        result = handle_alipay_notify(body_raw)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": result  # "success" or "fail"
        }

    # ── Telegram Webhook ──────────────────────────────────
    try:
        body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
    except Exception:
        body = {}

    from handlers.telegram import handle_telegram_update
    handle_telegram_update(body)

    # ── 原有流量查询逻辑（保留兼容）─────────────────────
    # 如果原 lambda_function.py 有其他逻辑，在此处继续处理
    # _handle_legacy(body)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"ok": True})
    }
