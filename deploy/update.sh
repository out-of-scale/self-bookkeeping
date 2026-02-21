#!/bin/bash
# ====== 更新部署（改了代码后在服务器上执行） ======
# 使用方法: sudo bash /opt/self-bookkeeping/deploy/update.sh

set -e
APP_DIR="/opt/self-bookkeeping"
cd $APP_DIR

echo "===== 拉取最新代码 ====="
git pull

echo "===== 更新后端依赖 ====="
cd $APP_DIR/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo "===== 重新构建前端 ====="
cd $APP_DIR/frontend
npm install
npm run build

echo "===== 重启后端服务 ====="
systemctl restart bookkeeping

echo "✅ 更新完成！"
