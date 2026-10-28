import os
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Attr

# ── DynamoDB ──────────────────────────────────────────
_table = boto3.resource(
    "dynamodb",
    region_name=os.environ.get("DYNAMODB_REGION", "ap-northeast-1")
).Table("servers")

def scan_all_servers():
    items = []
    resp  = _table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = _table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items

def update_traffic(user_id, instance_name, traffic_bytes: int):
    _table.update_item(
        Key={
            "user_id":       user_id,
            "instance_name": instance_name,
        },
        UpdateExpression="SET traffic_bytes = :t",
        ExpressionAttributeValues={":t": traffic_bytes},
    )

# ── Lightsail 流量拉取 ────────────────────────────────
def _now():
    return datetime.now(tz=timezone.utc)

def _month_start():
    t = datetime.now(tz=timezone.utc)
    return t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def get_instance_traffic(instance_name: str, region: str) -> int:
    client = boto3.client("lightsail", region_name=region)
    try:
        resp = client.get_instance_metric_data(
            instanceName = instance_name,
            metricName   = "NetworkOut",
            period       = 2592000,
            startTime    = _month_start(),
            endTime      = _now(),
            unit         = "Bytes",
            statistics   = ["Sum"],
        )
        out = sum(p.get("sum", 0) for p in resp.get("metricData", []))

        resp = client.get_instance_metric_data(
            instanceName = instance_name,
            metricName   = "NetworkIn",
            period       = 2592000,
            startTime    = _month_start(),
            endTime      = _now(),
            unit         = "Bytes",
            statistics   = ["Sum"],
        )
        in_ = sum(p.get("sum", 0) for p in resp.get("metricData", []))

        return int(out + in_)
    except Exception as e:
        print(f"[traffic] {instance_name} @ {region} error: {e}")
        return 0

# ── Lambda 入口 ───────────────────────────────────────
def lambda_handler(event, context):
    servers = scan_all_servers()
    print(f"[traffic-updater] 共 {len(servers)} 台服务器")

    for s in servers:
        instance_name = s["instance_name"]
        region        = s["ls_region"]
        user_id       = s["user_id"]

        traffic_bytes = get_instance_traffic(instance_name, region)
        update_traffic(user_id, instance_name, traffic_bytes)

        gb = round(traffic_bytes / 1024**3, 2)
        print(f"[traffic-updater] {instance_name} → {gb} GB")

    return {"statusCode": 200, "body": "done"}
