def generate(port: int, password: str) -> str:
    return f"""#!/bin/bash
apt-get update -y
apt-get install -y wget tar

# 自动判断架构
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    ARCH_NAME="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH_NAME="arm64"
else
    ARCH_NAME="amd64"
fi

# 下载并解压 sing-box
VERSION="1.9.7"
cd /tmp
wget -q "https://github.com/SagerNet/sing-box/releases/download/v${{VERSION}}/sing-box-${{VERSION}}-linux-${{ARCH_NAME}}.tar.gz"
tar -xzf "sing-box-${{VERSION}}-linux-${{ARCH_NAME}}.tar.gz"
cp "sing-box-${{VERSION}}-linux-${{ARCH_NAME}}/sing-box" /usr/local/bin/sing-box
chmod +x /usr/local/bin/sing-box

# 写入配置
cat > /etc/sing-box.json << 'EOF'
{{
  "inbounds": [
    {{
      "type": "shadowsocks",
      "listen": "::",
      "listen_port": {port},
      "method": "{password and "2022-blake3-aes-128-gcm"}",
      "password": "{password}",
      "multiplex": {{"enabled": true}}
    }}
  ],
  "outbounds": [{{"type": "direct"}}]
}}
EOF

# systemd 服务
cat > /etc/systemd/system/sing-box.service << 'EOF2'
[Unit]
Description=sing-box
After=network.target
[Service]
ExecStart=/usr/local/bin/sing-box run -c /etc/sing-box.json
Restart=always
[Install]
WantedBy=multi-user.target
EOF2

systemctl daemon-reload
systemctl enable sing-box
systemctl start sing-box
"""
