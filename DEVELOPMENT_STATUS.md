# 个人记账系统 — 开发进度追踪

> **用途**：当 AI 上下文断开时，新的对话可以读取此文件快速恢复开发状态。
> **更新规则**：每完成一个模块后更新此文件。

## 项目概述

个人记账系统，三大模块：
1. **FastAPI 后端** — AI 识别支付截图 + SQLite 存储 + 统计 API
2. **Vue3 PWA 前端** — ECharts 图表看板，可添加到 iPhone 主屏
3. **iOS 快捷指令** — 截图 → Base64 → POST 到后端

详细计划见项目根目录的 `implementation_plan.md`。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.10+, FastAPI, SQLAlchemy, SQLite, httpx |
| 前端 | Vue 3, Vite, Element Plus, ECharts, Axios |
| AI | 智谱 GLM-4.6V-Flash (视觉语言模型) |
| 部署 | Nginx + Uvicorn + systemd |

## 开发进度

### 后端 (backend/)
- [x] 项目结构与依赖 (requirements.txt)
- [x] 数据库模型 (database.py, models.py)
- [x] Pydantic Schema (schemas.py)
- [x] AI 服务封装 (ai_service.py)
- [x] 上传接口 /api/upload_receipt (main.py)
- [x] 统计接口 /api/get_stats (main.py)
- [x] 年度接口 /api/get_yearly (main.py)
- [x] 明细接口 /api/receipts (main.py)
- [x] CORS 配置

### 前端 (frontend/)
- [x] Vite + Vue3 项目初始化
- [x] Element Plus + ECharts 安装
- [x] API 封装 (src/api/index.js)
- [x] Dashboard 页面 — 本月概况
- [x] Charts 页面 — 图表分析
- [x] YearlyBill 页面 — 年度账单
- [x] PieChart / BarChart / LineChart 组件
- [x] PWA manifest + Apple Web App 配置
- [x] 深色主题设计系统 (style.css)
- [x] 底部导航栏 + 路由

### 文档 (docs/)
- [x] iOS 快捷指令配置指南

## 当前状态

**阶段**：✅ 核心开发完成
**最后更新**：2026-02-21 11:55
**说明**：所有后端 API 已验证通过，前端可构建可运行。用户需要：
1. 在 `.env` 中配置 `ZHIPU_API_KEY` 以启用 AI 识别功能
2. 在浏览器中打开 `http://localhost:5173` 查看前端效果
3. 部署到服务器时参考 `implementation_plan.md` 的部署备注

## 启动命令

```bash
# 后端
cd e:\self_bookkeeping\backend
pip install -r requirements.txt  # 首次运行
python main.py

# 前端 (开发)
cd e:\self_bookkeeping\frontend
npm install  # 首次运行
npm run dev

# 前端 (构建)
npm run build  # 输出到 dist/
```

## 恢复开发指引

如果你是一个新的 AI 对话，请按以下步骤恢复：
1. 读取本文件了解当前进度
2. 读取 `implementation_plan.md` 了解完整技术方案
3. 查看已完成的代码文件确认实现细节
4. 从"开发进度"中第一个未完成的 `[ ]` 项继续开发
5. 每完成一个模块后更新本文件的对应 checkbox 为 `[x]`
