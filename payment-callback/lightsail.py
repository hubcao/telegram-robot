import os
import time
import secrets
import base64
import boto3
from plans    import PLANS
from userdata import generate as gen_userdata
from ss       import generate_links

_METHOD = "2022-blake3-aes-128-gcm"

def create_instance(plan_key: str, user_id: str, order_id: str) -> dict:
    plan          = PLANS[plan_key]
    ls_region     = plan["region"]
    ls            = boto3.client("lightsail", region_name=ls_region)

    port          = int(os.environ.get("SS_PORT", "8388"))
    raw_password  = secrets.token_bytes(16)
    password      = base64.b64encode(raw_password).decode()
    instance_name = f"ss-{user_id}-{order_id[:8]}"

    # 创建实例
    ls.create_instances(
        instanceNames    = [instance_name],
        availabilityZone = f"{ls_region}a",
        blueprintId      = "debian_12",
        bundleId         = plan["bundle"],
        userData         = gen_userdata(port, password),
    )

    # 开放端口
    time.sleep(5)
    for proto in ("tcp", "udp"):
        ls.open_instance_public_ports(
            instanceName = instance_name,
            portInfo     = {"fromPort": port, "toPort": port, "protocol": proto},
        )

    # 等待实例 running，最多等 3 分钟
    ipv4, ipv6 = None, None
    for _ in range(18):
        time.sleep(10)
        inst = ls.get_instance(instanceName=instance_name)["instance"]
        if inst["state"]["name"] == "running":
            ipv4 = inst.get("publicIpAddress")
            ipv6 = (inst.get("ipv6Addresses") or [None])[0]
            break

    link_v4, link_v6 = generate_links(ipv4, ipv6, port, password, plan["region_name"])

    return {
        "instance_name": instance_name,
        "ipv4":          ipv4,
        "ipv6":          ipv6,
        "ss_link_v4":    link_v4,
        "ss_link_v6":    link_v6,
        "port":          port,
        "password":      password,
    }
