---
description: 恢复个人记账系统的开发进度，当上下文断开时使用此工作流
---

# 恢复开发工作流

当 AI 上下文断开后，用户可以发送 `/resume` 来触发此工作流，AI 将自动恢复开发。

## 步骤

1. 读取项目进度文件 `e:\self_bookkeeping\DEVELOPMENT_STATUS.md`，了解当前开发到哪一步。

2. 读取实施计划 `e:\self_bookkeeping\implementation_plan.md`，了解完整的技术方案和 API 设计。

3. 检查已完成代码的当前状态：
   - 后端：检查 `e:\self_bookkeeping\backend\` 目录下的文件
   - 前端：检查 `e:\self_bookkeeping\frontend\` 目录下的文件

4. 根据 `DEVELOPMENT_STATUS.md` 中的 checkbox 状态，找到第一个未完成的 `[ ]` 项，从该项继续开发。

5. 每完成一个模块后，更新 `DEVELOPMENT_STATUS.md` 对应的 checkbox 为 `[x]`，并更新"当前状态"和"最后更新"字段。

## 注意事项

- 所有代码写在 `e:\self_bookkeeping\` 目录下
- 后端使用 FastAPI + SQLAlchemy + SQLite
- 前端使用 Vue3 + Vite + Element Plus + ECharts
- AI 模型使用智谱 GLM-4.6V-Flash
- 保持与 `implementation_plan.md` 中的 API 规格一致
