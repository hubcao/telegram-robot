import time
import boto3
from datetime   import datetime, timezone
from bot        import send_message
from db.servers import scan_expiring, delete_server

def lambda_handler(event, context):
    now  = int(time.time())
    day3 = now + 3 * 24 * 3600

    for s in scan_expiring(day3):
        user_id       = s["user_id"]
        expire_at     = int(s["expire_at"])
        instance_name = s["instance_name"]
        ls_region     = s["ls_region"]
        expire_str    = datetime.fromtimestamp(
            expire_at, tz=timezone.utc
        ).strftime("%Y-%m-%d")
        days_left     = (expire_at - now) // 86400

        if expire_at <= now:
            # 销毁
            try:
                boto3.client("lightsail", region_name=ls_region)\
                     .delete_instance(instanceName=instance_name)
            except Exception as e:
                print(f"delete error: {e}")

            delete_server(user_id, instance_name)
            send_message(user_id,
                f"⚠️ *服务器已到期销毁*\n\n"
                f"`{instance_name}` 已于 {expire_str} 到期并自动销毁。\n"
                f"如需继续使用请发送 /buy 重新购买。"
            )

        elif days_left <= 1:
            send_message(user_id,
                f"🚨 *服务器最后1天！*\n\n"
                f"`{instance_name}` 将于 {expire_str} 到期。\n"
                f"明天将自动销毁，请尽快续费！\n/buy"
            )

        else:
            send_message(user_id,
                f"⏰ *服务器即将到期*\n\n"
                f"`{instance_name}` 还有 *{days_left} 天* 到期（{expire_str}）。\n"
                f"如需续费请发送 /buy"
            )
