import os
import boto3

_ls_regions = [
    "ap-east-1",       # 香港
    "ap-northeast-1",  # 东京
    "ap-northeast-2",  # 首尔
    "ap-southeast-1",  # 新加坡
]

def get_instance_traffic(instance_name: str, region: str) -> int:
    """
    从 Lightsail 拉取实例当月入站+出站流量，返回字节数
    """
    client = boto3.client("lightsail", region_name=region)
    try:
        resp = client.get_instance_metric_data(
            instanceName   = instance_name,
            metricName     = "NetworkOut",
            period         = 2592000,   # 30天
            startTime      = _month_start(),
            endTime        = _now(),
            unit           = "Bytes",
            statistics     = ["Sum"],
        )
        out = sum(p.get("sum", 0) for p in resp.get("metricData", []))

        resp = client.get_instance_metric_data(
            instanceName   = instance_name,
            metricName     = "NetworkIn",
            period         = 2592000,
            startTime      = _month_start(),
            endTime        = _now(),
            unit           = "Bytes",
            statistics     = ["Sum"],
        )
        in_ = sum(p.get("sum", 0) for p in resp.get("metricData", []))

        return int(out + in_)
    except Exception as e:
        print(f"[traffic] {instance_name} @ {region} error: {e}")
        return 0

def _now():
    from datetime import datetime, timezone
    return datetime.now(tz=timezone.utc)

def _month_start():
    from datetime import datetime, timezone
    t = datetime.now(tz=timezone.utc)
    return t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
