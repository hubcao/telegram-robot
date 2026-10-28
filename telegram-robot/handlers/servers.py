from datetime   import datetime, timezone
from bot        import send_message
from db.servers import get_user_servers
from plans      import PLANS

def handle_my_servers(chat_id, user_id):
    items = get_user_servers(user_id)
    if not items:
        send_message(chat_id, "📭 您还没有服务器，发送 /buy 购买！")
        return

    for s in items:
        expire_str = datetime.fromtimestamp(
            int(s["expire_at"]), tz=timezone.utc
        ).strftime("%Y-%m-%d")
        traffic_gb    = round(int(s.get("traffic_bytes", 0)) / 1024**3, 2)
        total_traffic = PLANS.get(s.get("plan_key", ""), {}).get("traffic", "未知")

        ipv6_line = f"🌐 IPv6：`{s['ipv6']}`\n" if s.get("ipv6") else ""
        v6_link   = f"🔗 *SS链接（IPv6）：*\n`{s['ss_link_v6']}`\n\n" if s.get("ss_link_v6") else ""
        ipv6_tip  = (
            f"💡 *进阶用法：*\n"
            f"如果你有自己的域名，可添加以下解析实现 IPv4/IPv6 自动分流：\n"
            f"`你的域名 A {s['ipv4']}`\n"
            f"`你的域名 AAAA {s['ipv6']}`\n"
            f"然后将 SS 链接中的 IPv4 或 IPv6 替换为你的域名即可。"
        ) if s.get("ipv6") else ""

        send_message(chat_id,
            f"🖥 *{s['plan_name']}*\n"
            f"📍 地区：{s['region_name']}\n"
            f"🌐 IPv4：`{s['ipv4']}`\n"
            f"{ipv6_line}"
            f"📊 已用流量：{traffic_gb} GB / {total_traffic}\n"
            f"📅 到期时间：{expire_str}\n\n"
            f"🔗 *SS链接（IPv4）：*\n`{s['ss_link']}`\n\n"
            f"{v6_link}"
            f"{ipv6_tip}"
        )
