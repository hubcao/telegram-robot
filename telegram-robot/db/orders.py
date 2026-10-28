import os
import time
import boto3

_table = boto3.resource(
    "dynamodb",
    region_name=os.environ.get("DYNAMODB_REGION", "ap-northeast-1")
).Table("orders")

def create_order(order_id, user_id, plan_key):
    _table.put_item(Item={
        "order_id":   order_id,
        "user_id":    user_id,
        "plan_key":   plan_key,
        "status":     "pending",
        "created_at": int(time.time()),
    })

def get_order(order_id):
    return _table.get_item(Key={"order_id": order_id}).get("Item")

def mark_paid(order_id):
    _table.update_item(
        Key={"order_id": order_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "paid"},
    )
