import json
import os
from db.servers import get_user_servers
from auth import verify_telegram_login

BOT_TOKEN = os.environ["BOT_TOKEN"]

def lambda_handler(event, context):
    path   = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    if method == "OPTIONS":
        return cors(200, "OK")

    params = event.get("queryStringParameters") or {}
    user = verify_telegram_login(params, BOT_TOKEN)
    if not user:
        return cors(401, {"error": "Unauthorized"})

    user_id = str(user["id"])

    if path == "/user/servers":
        data = get_user_servers(user_id)
        return cors(200, data)

    return cors(404, {"error": "Not found"})

def cors(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(body, ensure_ascii=False, default=str),
    }
