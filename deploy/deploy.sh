#!/bin/bash
# ====== 个人记账系统 一键部署脚本 (CentOS / Alibaba Cloud Linux) ======
# 使用方法: cd /opt/self-bookkeeping && sudo bash deploy/deploy.sh

set -e

APP_DIR="/opt/self-bookkeeping"

echo "===== 1. 安装系统依赖 ====="
yum install -y python3 python3-pip nginx

# 安装 Node.js 20 (Vite 7 需要)
if ! command -v node &> /dev/null; then
    curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
    yum install -y nodejs
fi

echo "===== 2. 配置后端 ====="
cd $APP_DIR/backend

# 查找可用的 Python 3.8+ 版本
if command -v python3.11 &> /dev/null; then
    PY=python3.11
elif command -v python3.9 &> /dev/null; then
    PY=python3.9
else
    echo "安装 Python 3.11..."
    yum install -y python3.11 python3.11-pip
    PY=python3.11
fi

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
# 临时关闭SELinux（如果因为SELinux导致Nginx无法读取前端文件）
setenforce 0 || true
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config || true

# 彻底修复 CentOS 下被破坏的 nginx.conf 或者默认配置的 80 端口冲突
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
