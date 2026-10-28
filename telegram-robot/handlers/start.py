import json
from bot import send_message

def handle_start(chat_id):
    # 常驻键盘
    keyboard = json.dumps({
        "keyboard": [
            [
                {"text": "🛒 购买服务器"},
                {"text": "📊 我的服务器"}
            ]
        ],
        "resize_keyboard": True,
        "persistent": True
    })

    send_message(
        chat_id,
        "<b>⚡ SS2022 双栈亚太独享节点服务概览说明</b>\n\n"
        "<b>🌐 亚太通用节点：</b>\n"
        "└ <b>流量：</b>1TB 起独享流量 / 1Gbps 带宽\n"
        "└ <b>地区：</b>东京 / 首尔 / 新加坡\n"
        "└ <b>特性：</b>支持自定义域名解析\n\n"
        "<b>🌐 香港双栈专区：</b>\n"
        "└ <b>流量：</b>512GB 起独享流量 / 1Gbps 带宽\n"
        "└ <b>特性：</b>支持自定义域名解析\n\n"
        "<b>🖥 服务说明：</b>\n"
        "• 协议支持：<s>https://SS2022.xyz/</s> (开发中)\n"
        "• 协议支持：SS2022，可解析 IPv4 + IPv6 双栈访问\n"
        "• 扣费规则：无任何倍率抵扣，实打实流量统计\n"
        "• 结算方式：支付宝 / <s>微信</s> / <s>USDT</s>，即时到账\n",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

