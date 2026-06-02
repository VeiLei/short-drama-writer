# short-drama-writer

AI短剧/短视频生成 Claude Code 插件。

## 项目结构

- `plugin/` — Claude Code 插件主体
  - `skills/` — 7个技能定义 (drama-init/plan/write/review/generate/query/dashboard)
  - `agents/` — 4个专用代理 (context/reviewer/data/deconstruction)
  - `genres/` — 6种短剧类型知识库
  - `references/` — 共享参考文件
  - `templates/` — 输出模板
  - `scripts/` — Python 数据脚本
- `backend/` — FastAPI 后端 (API代理 + MySQL + 导出 + 仪表盘)

## 开发原则

- 插件内所有创意决策由 Claude 完成，Python 脚本只做数据读写
- 后端不含 Agent 逻辑，只做 API 代理和索引
- 项目目录即项目本身，所有内容本地文件存储，MySQL 仅做索引
