import os
import json
import uuid
from bot        import send_message
from plans      import PLANS
from yipay      import create_order as pay_create_order
from db.orders  import create_order as db_create_order

_NOTIFY_URL = os.environ["NOTIFY_URL"]
_RETURN_URL = f"https://t.me/{os.environ['BOT_USERNAME']}"

def handle_buy(chat_id):
    def btn(plan_key):
        p = PLANS[plan_key]
        return {"text": f"{p['flag']} {p['region_name']} ¥{p['price_cny']}/月",
                "callback_data": f"buy_{plan_key}"}

    # 动态生成按钮，每个地区一行，只显示 PLANS 里存在的套餐
    regions = {}
    for key in PLANS:
        prefix = key.split("_")[0]  # hk / kr / sg / jp
        if prefix not in regions:
            regions[prefix] = []
        regions[prefix].append(btn(key))

    inline_keyboard = [btns for btns in regions.values()]

    keyboard = json.dumps({"inline_keyboard": inline_keyboard})

    send_message(
        chat_id,
        "<b>请选择要部署的独享节点区域：</b>\n\n"
        "🇯🇵 <b>日本 · 东京</b> - 起步 1TB\n"
        "└ <b>说明</b>：北方联通 / 移动首选 ｜ 低延迟\n\n"
        "🇭🇰 <b>中国 · 香港</b> -  起步 512G\n"
        "└ <b>说明</b>：三网通用 ｜ 全国平均延迟最低\n\n"
        "🇰🇷 <b>韩国 · 首尔</b> -  起步 1TB\n"
        "└ <b>说明</b>：北方联通 / 电信优选 ｜ 东北首选\n\n"
        "🇸🇬 <b>新加坡</b> -  起步 1TB\n"
        "└ <b>说明</b>：东南亚节点 ｜ 南方电信表现好\n\n"
        "<i>若不确定本地网络，优先推荐选择【香港】节点。</i>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

def handle_buy_callback(chat_id, user_id, plan_key):
    plan     = PLANS[plan_key]
    order_id = uuid.uuid4().hex[:20]

    db_create_order(order_id, user_id, plan_key)

    result = pay_create_order(
        order_id   = order_id,
        plan_name  = plan["name"],
        money      = plan["price_cny"],
        notify_url = _NOTIFY_URL,
        return_url = _RETURN_URL,
        user_id    = user_id,
        plan_key   = plan_key,
    )

    if result.get("code") != 1:
        send_message(chat_id,
            f"❌ 创建订单失败：{result.get('msg', '未知错误')}\n请稍后重试")
        return

    qrcode = result.get("qrcode", "")
    payurl = result.get("payurl", "")

    msg = (
        f"📦 *订单已创建*\n\n"
        f"套餐：{plan['name']}\n"
        f"金额：¥{plan['price_cny']} 元\n"
        f"订单号：`{order_id}`\n\n"
    )
    if payurl:
        msg += f"👇 点击链接支付：\n[点击支付]({payurl})\n\n"
    if qrcode:
        msg += f"📱 二维码内容：\n`{qrcode}`\n\n"
    msg += "支付成功后将自动开通服务器，请稍候..."

    send_message(chat_id, msg)
