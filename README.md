# short-drama-writer

AI 短剧/短视频生成工具，基于 Claude Code 插件 + FastAPI 后端。从项目初始化、大纲规划、剧本写作、审查润色到视觉素材生成，覆盖短剧创作全流程。

## 功能概览

| 阶段 | 命令 | 说明 |
|------|------|------|
| 项目初始化 | `/drama-init` | 交互式收集创作信息，生成世界观、角色档案、视觉风格 |
| 大纲规划 | `/drama-plan` | 基于总纲生成卷纲、时间线、分集大纲 |
| 剧本写作 | `/drama-write` | 生成单集剧本，含分镜流图、ASCII 空间布局 |
| 审查润色 | `/drama-review` | 设定一致性、叙事连贯性、角色一致性、AI 味检测 |
| 素材生成 | `/drama-generate` | 角色四视图、变装、场景全景图、取景框、视频 |
| 项目查询 | `/drama-query` | 查询设定、角色、剧情状态、伏笔追踪 |
| 可视化面板 | `/drama-dashboard` | 只读 Web 仪表盘，查看项目进度与素材 |

## 项目结构

```
short-drama-writer/
├── plugin/                  # Claude Code 插件
│   ├── skills/              # 7 个技能定义 (init/plan/write/review/generate/query/dashboard)
│   ├── agents/              # 4 个专用代理 (context/reviewer/data/deconstruction)
│   ├── genres/              # 6 种短剧类型知识库 (霸总/甜宠/逆袭/悬疑/古装/都市)
│   ├── templates/           # 输出模板 (角色卡/场景卡/分集大纲/剧本/视频提示词)
│   ├── references/          # 影视创作规则参考
│   └── scripts/             # Python 数据脚本 (只做读写，不做决策)
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/             # REST API 路由 (projects, generate)
│   │   ├── image_providers/ # 图片生成适配器 (即梦 4.6)
│   │   ├── models/          # SQLAlchemy 数据库模型
│   │   ├── utils/           # 工具 (TOS 上传, AssetIndex)
│   │   └── cli.py           # 命令行素材生成工具
│   └── dashboard/           # Vite + React 仪表盘前端
├── CLAUDE.md                # 项目开发原则
└── .gitignore
```

## 安装插件

```bash
# 克隆仓库
git clone https://gitee.com/vei_ge/short-drama-writer.git

# 将插件目录链接到 Claude Code 插件目录
# Windows
mklink /D %USERPROFILE%\.claude\plugins\short-drama-writer ^
  插件仓库路径\plugin

# macOS / Linux
ln -s /path/to/short-drama-writer/plugin ~/.claude/plugins/short-drama-writer
```

安装后重启 Claude Code，输入 `/drama-init` 即可使用。

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- 火山引擎即梦 4.6 API Key（图片生成）

### 2. 安装后端依赖

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
# 或 .venv/bin/pip install -r requirements.txt  # macOS/Linux
```

### 3. 配置 API Key

在 `backend/.env` 中填写：

```env
# 即梦 4.6 — 图片生成
JIMENG_API_KEY=你的AK
JIMENG_API_SECRET=你的SK

# 火山引擎 TOS — 图片存储
TOS_ACCESS_KEY=你的AK
TOS_SECRET_KEY=你的SK
TOS_BUCKET=你的Bucket名
TOS_ENDPOINT=tos-cn-beijing.volces.com
```

### 4. 启动仪表盘（可选）

```bash
cd backend/dashboard
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`。

## 素材生成 CLI

不需要启动后端服务，一行命令生成素材：

```bash
cd backend

# 角色基础四视图
.venv\Scripts\python -m app.cli four-views --project <项目目录> --name 林若雪 --prompt "CG游戏角色..."

# 角色变装
.venv\Scripts\python -m app.cli variant --project <项目目录> --name 林若雪 --outfit 晚礼服 --prompt "..."

# 场景全景图
.venv\Scripts\python -m app.cli scene-master --project <项目目录> --name 咖啡厅 --prompt "..."

# 场景取景框
.venv\Scripts\python -m app.cli shot-frame --project <项目目录> --scene 咖啡厅 --frame-id bar --frame-type two_shot --prompt "..."

# 查看已有素材
.venv\Scripts\python -m app.cli assets --project <项目目录>
```

prompt 过长时用文件传入：`--prompt @C:\temp\prompt.txt`

## 后端 API

如需启动完整后端服务：

```bash
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/projects/overview` | GET | 扫描项目目录，聚合概览数据 |
| `/api/generate/character/four-views` | POST | 生成角色基础四视图 |
| `/api/generate/character/variant` | POST | 生成角色变装四视图 |
| `/api/generate/scene/master` | POST | 生成场景全景图 |
| `/api/generate/scene/shot-frame` | POST | 生成场景取景框 |
| `/api/generate/assets` | GET | 查询已生成素材索引 |

## 开发原则

- 插件内所有创意决策由 Claude 完成，Python 脚本只做数据读写
- 后端不含 Agent 逻辑，只做 API 代理和索引
- 项目数据本地文件存储（Markdown + JSON），MySQL 仅做索引
- 素材生成前自动检查已有资产，避免重复
