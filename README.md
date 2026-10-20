# 项目介绍
在 Telegram Bot 上 39.99 下单自动开通 Amazon Lightsail $5 美金服务器并搭建 Tuic V5 节点的云函数程序。
支持开通 香港、日本、韩国、新加坡，主要是亚太地区。
目前仅支持 支付宝当面付 扫码付款，未来会支持 微信支付 USDT 等支付方式
网站控制端也已进行开发中

# 运行环境
采用云函数无服务器模式
Lambda Python 3.12
API Gateway
DynamoDB
EventBridge
CloudWatch
Telegram Bot API
Alpay OpenAPI

# 实现方式

├── 触发入口
│   ├── Telegram Webhook (HTTP POST)
│   │   └── API Gateway → lambda_function.py
│   └── EventBridge (每分钟)
│       └── lambda_function.py
│
├── handlers/
│   ├── telegram.py          # Webhook 消息处理
│   │   ├── 命令路由 CMD_MAP
│   │   │   ├── /start        → 欢迎信息
│   │   │   ├── /buy · 购买服务    → 选区域 → 生成二维码
│   │   │   ├── /renew · 续费服务  → 生成续费二维码
│   │   │   ├── /status · 当前订单状态 → 查最近3条订单
│   │   │   ├── /config · 重新获取配置 → 推送 TUIC 配置
│   │   │   ├── /traffic · 流量查询   → 查本月流量（用户）
│   │   │   └── /admintraffic         → 推送全部流量（管理员）
│   │   └── inline keyboard
│   │       └── region:tokyo/seoul/hongkong/singapore
│   │
│   ├── alipay.py            # 支付宝回调处理
│   │   ├── verify_notify()  → RSA2 验签
│   │   ├── 校验金额 ≥ 39.99
│   │   ├── update_order_paid()
│   │   ├── send_message()   → 通知用户支付成功
│   │   └── create_instance() → 触发 Lightsail 建机
│   │
│   └── scheduler.py         # 定时任务
│       ├── 每分钟
│       │   ├── _check_pending_orders()
│       │   │   └── 超过 600s 未支付 → cancelled + 通知用户
│       │   └── _check_creating_instances()
│       │       └── 实例 running → update_order_running
│       │                        → open_instance_ports
│       │                        → 推送 TUIC 配置
│       ├── 每天 UTC 01:00
│       │   └── _check_running_instances()
│       │       ├── days_left < 0  → 销毁实例 + 通知用户
│       │       └── days_left ≤ 2  → 续费提醒（去重）
│       └── 按需（命令触发）
│           ├── _push_traffic_usage()       → 推送所有用户流量
│           └── _push_admin_traffic_report() → 推送管理员实例流量
│
├── services/
│   ├── dynamodb_service.py
│   │   ├── 订单状态机
│   │   │   ├── pending_pay → creating → running → destroyed
│   │   │   └── pending_pay → cancelled
│   │   └── 操作
│   │       ├── create_order / get_order / get_orders_by_chat_id
│   │       ├── get_active_order_by_chat_id
│   │       ├── update_order_paid / running / renewed / destroyed / cancelled
│   │       └── increment_reminded_days
│   │
│   ├── lightsail_service.py
│   │   ├── 4 区域 client 缓存
│   │   │   ├── tokyo     ap-northeast-1a  1TB
│   │   │   ├── seoul     ap-northeast-2a  1TB
│   │   │   ├── singapore ap-southeast-1a  1TB
│   │   │   └── hongkong  ap-east-1a       512GB
│   │   └── 操作
│   │       ├── create_instance / delete_instance
│   │       ├── get_instance / get_instance_state / get_instance_ips
│   │       ├── open_instance_ports
│   │       ├── get_instance_traffic (NetworkOut / NetworkIn)
│   │       ├── get_instance_az
│   │       └── get_bundle_info
│   │
│   └── tuic_service.py
│       ├── generate_tuic_config()  → port / uuid / password
│       ├── build_user_data()       → cloud-init 安装脚本
│       ├── build_tuic_url()        → tuic:// 链接
│       ├── build_clash_config()    → Clash Meta JSON
│       ├── build_singbox_config()  → sing-box JSON
│       └── build_config_message()  → 完整配置消息
│
└── utils/
    ├── helpers.py
    │   ├── generate_uuid / generate_password / generate_port
    │   ├── generate_order_id
    │   ├── now_iso / expire_iso / format_datetime_jst
    │   ├── days_until_expire / is_expired
    │   └── fmt_gb / fmt_total
    └── alipay_client.py
        ├── create_qr_code()  → 支付宝预创建订单
        ├── query_order()     → 查询订单状态
        └── verify_notify()   → RSA2 验签
