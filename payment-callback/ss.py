import base64

def generate_links(ipv4: str, ipv6: str, port: int,
                   password: str, region_name: str) -> tuple[str, str]:
    method   = "2022-blake3-aes-128-gcm"
    userinfo = base64.b64encode(f"{method}:{password}".encode()).decode()
    tag      = f"SS2022-{region_name}"

    link_v4 = f"ss://{userinfo}@{ipv4}:{port}#{tag}"
    link_v6 = f"ss://{userinfo}@[{ipv6}]:{port}#{tag}-IPv6" if ipv6 else ""
    return link_v4, link_v6
