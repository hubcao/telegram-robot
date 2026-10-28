import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

_table = boto3.resource(
    "dynamodb",
    region_name=os.environ.get("DYNAMODB_REGION", "ap-northeast-1")
).Table("servers")

def save_server(item: dict):
    _table.put_item(Item=item)

def delete_server(user_id, instance_name):
    _table.delete_item(Key={
        "user_id":       user_id,
        "instance_name": instance_name,
    })

def scan_expiring(before_ts: int):
    return _table.scan(
        FilterExpression=Attr("expire_at").lte(before_ts)
    ).get("Items", [])

def scan_all_servers():
    """扫描所有服务器记录"""
    items = []
    resp  = _table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = _table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items

def update_traffic(user_id, instance_name, traffic_bytes: int):
    """更新服务器已用流量"""
    _table.update_item(
        Key={
            "user_id":       user_id,
            "instance_name": instance_name,
        },
        UpdateExpression="SET traffic_bytes = :t",
        ExpressionAttributeValues={":t": traffic_bytes},
    )
