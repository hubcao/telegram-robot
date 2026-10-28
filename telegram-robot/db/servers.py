import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

_table = boto3.resource(
    "dynamodb",
    region_name=os.environ.get("DYNAMODB_REGION", "ap-northeast-1")
).Table("servers")

def get_user_servers(user_id):
    return _table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    ).get("Items", [])

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
