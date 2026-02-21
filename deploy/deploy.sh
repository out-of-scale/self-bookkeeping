#!/bin/bash
# ====== 个人记账系统 一键部署脚本 (CentOS / Alibaba Cloud Linux) ======
# 使用方法: cd /opt/self-bookkeeping && sudo bash deploy/deploy.sh

set -e

APP_DIR="/opt/self-bookkeeping"

echo "===== 1. 安装系统依赖 ====="
yum install -y python3 python3-pip nginx

# 安装 Node.js 18
if ! command -v node &> /dev/null; then
    curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
    yum install -y nodejs
fi

echo "===== 2. 配置后端 ====="
cd $APP_DIR/backend
python3 -m venv venv
source venv/bin/activate
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
# 注释掉默认的 server 块以避免冲突
sed -i '/^\s*server {/,/^\s*}/s/^/#/' /etc/nginx/nginx.conf 2>/dev/null || true
nginx -t && systemctl enable nginx && systemctl restart nginx

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
