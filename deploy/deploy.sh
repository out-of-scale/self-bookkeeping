#!/bin/bash
# ====== 个人记账系统 一键部署脚本 (CentOS / Alibaba Cloud Linux) ======
# 使用方法: cd /opt/self-bookkeeping && sudo bash deploy/deploy.sh

set -e

APP_DIR="/opt/self-bookkeeping"

echo "===== 1. 安装系统依赖 ====="
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx curl

# 安装 Node.js 20 (Vite 7 需要)
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

echo "===== 2. 配置后端 ====="
cd $APP_DIR/backend

# Ubuntu 自带比较新的 Python3 且通常被链接为 python3
PY="python3"

echo "使用 $PY"
$PY -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo "请输入你的智谱 API Key（可留空按回车跳过）："
    read -r api_key
    echo "ZHIPU_API_KEY=$api_key" > .env
    echo "PORT=8000" >> .env
    echo ".env 文件已创建"
fi

deactivate

echo "===== 3. 构建前端 ====="
cd $APP_DIR/frontend
npm install
npm run build

echo "===== 4. 配置 Nginx ====="
cp $APP_DIR/deploy/nginx.conf /etc/nginx/conf.d/bookkeeping.conf
# 原来的 CentOS SELinux 步骤在纯净 Ubuntu 中不需要
# Ubuntu 下直接替换 Nginx 配置即可
cat > /etc/nginx/nginx.conf << 'EOF'
user root;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;
include /usr/share/nginx/modules/*.conf;
events {
    worker_connections 1024;
}
http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    access_log  /var/log/nginx/access.log  main;
    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;
    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    client_max_body_size 50M; # 增加请求体大小限制

    # 后端 API 反向代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
        client_max_body_size 50M; # 增加请求体大小限制
    }
    
    # 仅引入我们的自定义配置模块，不包含默认的 server
    include /etc/nginx/conf.d/*.conf;
}
EOF
systemctl daemon-reload
nginx -t && systemctl enable --now nginx || systemctl restart nginx

echo "===== 5. 配置后端 systemd 服务 ====="
cp $APP_DIR/deploy/bookkeeping.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable bookkeeping
systemctl restart bookkeeping

echo ""
echo "===== ✅ 部署完成！ ====="
echo "访问地址: http://你的服务器公网IP"
echo ""
echo "常用命令："
echo "  查看状态: systemctl status bookkeeping"
echo "  查看日志: journalctl -u bookkeeping -f"
echo "  重启服务: systemctl restart bookkeeping"
echo "  更新部署: cd $APP_DIR && sudo bash deploy/update.sh"
