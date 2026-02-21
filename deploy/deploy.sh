#!/bin/bash
# ====== 个人记账系统 一键部署脚本 (Ubuntu 22.04) ======
# 使用方法: sudo bash deploy.sh

set -e

APP_DIR="/opt/self-bookkeeping"
REPO_URL="git@github.com:out-of-scale/self-bookkeeping.git"

echo "===== 1. 安装系统依赖 ====="
apt update
apt install -y python3 python3-pip python3-venv nodejs npm nginx git

echo "===== 2. 克隆项目 ====="
if [ -d "$APP_DIR" ]; then
    echo "项目目录已存在，拉取最新代码..."
    cd $APP_DIR && git pull
else
    git clone $REPO_URL $APP_DIR
fi
cd $APP_DIR

echo "===== 3. 配置后端 ====="
cd $APP_DIR/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    echo "请输入你的智谱 API Key（用于AI识别功能，可留空跳过）："
    read -r api_key
    echo "ZHIPU_API_KEY=$api_key" > .env
    echo "PORT=8000" >> .env
    echo ".env 文件已创建"
fi

deactivate

echo "===== 4. 构建前端 ====="
cd $APP_DIR/frontend
npm install
npm run build

echo "===== 5. 配置 Nginx ====="
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/bookkeeping
ln -sf /etc/nginx/sites-available/bookkeeping /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "===== 6. 配置后端 systemd 服务 ====="
cp $APP_DIR/deploy/bookkeeping.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable bookkeeping
systemctl restart bookkeeping

echo ""
echo "===== ✅ 部署完成！ ====="
echo "前端地址: http://你的服务器IP"
echo "后端API:  http://你的服务器IP/api"
echo ""
echo "常用命令："
echo "  查看状态: systemctl status bookkeeping"
echo "  查看日志: journalctl -u bookkeeping -f"
echo "  重启服务: systemctl restart bookkeeping"
