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
Telegram Webhook
       ↓
  API Gateway
       ↓
   lambda_function.py
       ├── handlers/telegram.py
       ├── handlers/alipay.py
       ├── handlers/scheduler.py
       │
       ├── services/dynamodb_service.py
       ├── services/lightsail_service.py
       ├── services/tuic_service.py
       │
       └── utils/helpers.py
           └── utils/alipay_client.py
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

如果你有需要，我也可以继续整理成：
- 更完整的 GitHub README 版本
- 英文版 README
- 带部署步骤的完整版 README
- 更偏产品展示风格的 README
