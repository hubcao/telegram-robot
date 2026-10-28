import time
from datetime   import datetime, timezone
from yipay      import verify_sign
from bot        import send_message
from db.orders  import get_order, mark_paid
from db.servers import save_server
from lightsail  import create_instance
from plans      import PLANS

def lambda_handler(event, context):
    params = event.get("queryStringParameters") or {}

    if not verify_sign(params):
        return {"statusCode": 400, "body": "sign error"}

    if params.get("trade_status") != "TRADE_SUCCESS":
        return {"statusCode": 200, "body": "success"}

    order_id = params.get("out_trade_no", "")
    extra    = params.get("param", "")
    user_id, plan_key = extra.split("|") if "|" in extra else ("", "")

    order = get_order(order_id)
    if not order or order.get("status") == "paid":
        return {"statusCode": 200, "body": "success"}

    mark_paid(order_id)

    send_message(user_id,
        "✅ *支付成功！*\n\n"
        "🔧 正在为您自动开通服务器，预计需要 2-3 分钟，请稍候...")

    plan   = PLANS[plan_key]
    result = create_instance(plan_key, user_id, order_id)

    expire_at  = int(time.time()) + 30 * 24 * 3600
    expire_str = datetime.fromtimestamp(expire_at, tz=timezone.utc).strftime("%Y-%m-%d")

    save_server({
        "user_id":       user_id,
        "instance_name": result["instance_name"],
        "plan_key":      plan_key,
        "plan_name":     plan["name"],
        "region_name":   plan["region_name"],
        "ls_region":     plan["region"],
        "ipv4":          result["ipv4"] or "",
        "ipv6":          result["ipv6"] or "",
        "ss_link":       result["ss_link_v4"],
        "ss_link_v6":    result["ss_link_v6"] or "",
        "port":          result["port"],
        "password":      result["password"],
        "traffic_bytes": 0,
        "traffic":       plan["traffic"],   # ← 新增
        "expire_at":     expire_at,
        "created_at":    int(time.time()),
    })

    ipv6_line = f"🌐 IPv6：`{result['ipv6']}`\n" if result.get("ipv6") else ""
    v6_link   = f"🔗 *SS链接（IPv6）：*\n`{result['ss_link_v6']}`\n\n" if result.get("ss_link_v6") else ""
    ipv6_tip  = (
        f"💡 *进阶用法：* \n"
        f"如果你有自己的域名，可添加以下解析实现 IPv4/IPv6 自动分流：\n"
        f"`你的域名 A {result['ipv4']}`\n"
        f"`你的域名 AAAA {result['ipv6']}`\n"
        f"然后将 SS 链接中的 IPv4 或 IPv6 替换为你的域名即可。"
    ) if result.get("ipv6") else ""

    msg = (
        f"🎉 *服务器已开通！*\n\n"
        f"📍 地区：{plan['region_name']}\n"
        f"🌐 IPv4：`{result['ipv4']}`\n"
        f"{ipv6_line}"
        f"📅 到期时间：{expire_str}\n\n"
        f"🔗 *SS链接（IPv4）：*\n`{result['ss_link_v4']}`\n\n"
        f"{v6_link}"
        f"📱 复制链接到 Shadowsocks 客户端即可使用！\n\n"
        f"{ipv6_tip}"
    )

    send_message(user_id, msg)

    return {"statusCode": 200, "body": "success"}
