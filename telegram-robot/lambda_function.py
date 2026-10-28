import json
from handlers.start   import handle_start
from handlers.buy     import handle_buy, handle_buy_callback
from handlers.servers import handle_my_servers

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    if "callback_query" in body:
        cq      = body["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        user_id = str(cq["from"]["id"])
        data    = cq["data"]

        if data == "show_plans":
            handle_buy(chat_id)
        elif data.startswith("buy_"):
            handle_buy_callback(chat_id, user_id, data[4:])
        elif data == "my_servers":
            handle_my_servers(chat_id, user_id)

        return {"statusCode": 200, "body": "OK"}

    msg     = body.get("message", {})
    chat_id = msg.get("chat", {}).get("id")
    user_id = str(msg.get("from", {}).get("id", ""))
    text    = msg.get("text", "")

    if not chat_id:
        return {"statusCode": 200, "body": "OK"}

    routes = {
        "/start":        lambda: handle_start(chat_id),
        "/buy":          lambda: handle_buy(chat_id),
        "/myservers":    lambda: handle_my_servers(chat_id, user_id),
        "/traffic":      lambda: handle_my_servers(chat_id, user_id),
        "🛒 购买服务器":  lambda: handle_buy(chat_id),        # 新增
        "📊 我的服务器":  lambda: handle_my_servers(chat_id, user_id),  # 新增
    }
    routes.get(text, lambda: handle_start(chat_id))()

    return {"statusCode": 200, "body": "OK"}
