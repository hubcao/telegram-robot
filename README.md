# Telegram Bot 自动开通 Lightsail 服务器与 Tuic 节点部署

一个基于 Telegram Bot 的自动化云服务器订购与部署项目。用户在 Telegram 中下单后，系统会自动完成：
- 支付宝扫码支付
- 创建 Amazon Lightsail 实例
- 部署 Tuic V5 节点
- 生成并推送配置
- 查询订单状态、流量和续费提醒

当前支持地区：
- 香港
- 日本
- 韩国
- 新加坡

目前支持的支付方式：
- 支付宝当面付扫码付款

---

## 功能概览

- Telegram 命令交互
  - `/start`
  - `/buy`
  - `/renew`
  - `/status`
  - `/config`
  - `/traffic`
  - `/admintraffic`

- 自动支付流程
  - 生成支付二维码
  - 验签回调
  - 校验金额
  - 更新订单状态

- 自动实例创建
  - 创建 Lightsail 实例
  - 获取实例状态和 IP
  - 打开端口
  - 查询流量数据

- 自动部署 Tuic
  - 生成 Tuic 配置
  - 生成 UUID / password / port
  - 生成 tuic:// 链接
  - 生成 Clash Meta / sing-box 配置

- 定时任务
  - 超时未支付自动取消
  - 创建中实例状态检查
  - 到期提醒与续费提示
  - 用户/管理员流量推送

---

## 技术栈

- Python 3.12
- AWS Lambda
- API Gateway
- DynamoDB
- EventBridge
- CloudWatch
- Telegram Bot API
- 支付宝 OpenAPI
- Amazon Lightsail

---

## 项目架构

```text
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
```

---

## 订单状态流转

```text
pending_pay -> creating -> running -> destroyed
      \
       -> cancelled
```

说明：
- `pending_pay`：待支付
- `creating`：创建实例中
- `running`：运行中
- `destroyed`：已销毁
- `cancelled`：超时未支付或取消

---

## 目录结构

```text
.
├── lambda_function.py
├── handlers/
│   ├── telegram.py
│   ├── alipay.py
│   └── scheduler.py
├── services/
│   ├── dynamodb_service.py
│   ├── lightsail_service.py
│   └── tuic_service.py
├── utils/
│   ├── helpers.py
│   └── alipay_client.py
├── README.md
└── requirements.txt
```

---

## 运行方式

1. 配置 Telegram Bot Token
2. 配置支付宝 OpenAPI 参数
3. 配置 AWS Lambda / API Gateway / DynamoDB
4. 部署项目代码到 Lambda
5. 配置 Telegram Webhook
6. 启用 EventBridge 定时任务

---

## 路线图

- [ ] 支持微信支付
- [ ] 支持 USDT 等支付方式
- [ ] 完善后台管理端
- [ ] 支持更多服务器地区和套餐
- [ ] 增强监控与统计能力

---

## 说明

本项目适合用于：
- Telegram 机器人商店
- 云服务器自动化订购
- Tuic / 代理节点部署
- 简单的低成本无服务器运维场景
