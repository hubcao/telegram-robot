import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
table    = dynamodb.Table("servers")

def get_user_servers(user_id: str) -> list:
    resp = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )
    servers = []
    for item in resp.get("Items", []):
        servers.append({
            "instance_name": item.get("instance_name"),
            "plan_name":     item.get("plan_name"),
            "region_name":   item.get("region_name"),
            "ipv4":          item.get("ipv4"),
            "ipv6":          item.get("ipv6", ""),
            "port":          item.get("port"),
            "password":      item.get("password"),
            "ss_link":       item.get("ss_link"),
            "ss_link_v6":    item.get("ss_link_v6"),
            "expire_at":     item.get("expire_at"),
            "traffic_bytes": item.get("traffic_bytes", 0),
            "created_at":    item.get("created_at"),
        })
    return servers
