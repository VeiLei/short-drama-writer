# short-drama-writer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Claude Code plugin (short-drama-writer) with a lightweight FastAPI backend for AI short drama/video generation.

**Architecture:** Claude Code plugin handles all creative work (skills + agents + knowledge base). Lightweight Python backend handles API proxying (image/video generation), MySQL indexing, export, and dashboard. Plugin and backend in a monorepo.

**Tech Stack:** Claude Code Plugin (Markdown skills/agents), Python 3.12+ (FastAPI, SQLAlchemy 2.0, httpx), MySQL 8.0

**New project path:** `d:\PersonalFiles\Project_Space\short-drama-writer\`

---

## Phase 0: Project Initialization

### Task 0.1: Create project directory & git init

**Files:**
- Create: `d:\PersonalFiles\Project_Space\short-drama-writer\README.md`
- Create: `d:\PersonalFiles\Project_Space\short-drama-writer\.gitignore`

- [ ] **Step 1: Create directory and init git**

```bash
mkdir -p "d:\PersonalFiles\Project_Space\short-drama-writer"
cd "d:\PersonalFiles\Project_Space\short-drama-writer"
git init
```

- [ ] **Step 2: Write .gitignore**

```
__pycache__/
*.pyc
.env
.venv/
node_modules/
dist/
*.egg-info/
.drama/
素材/
导出/
```

- [ ] **Step 3: Write README.md**

```markdown
# short-drama-writer

AI短剧/短视频生成 Claude Code 插件

## 项目结构

- `plugin/` — Claude Code 插件 (skills + agents + 知识库 + 模板 + 脚本)
- `backend/` — 轻量 FastAPI 后端 (API代理 + MySQL + 导出 + 仪表盘)
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore README.md
git commit -m "chore: init short-drama-writer project"
```

---

### Task 0.2: Create plugin directory skeleton

**Files:**
- Create: `d:\PersonalFiles\Project_Space\short-drama-writer\plugin\.claude-plugin\plugin.json`

- [ ] **Step 1: Create plugin directories**

```bash
cd "d:\PersonalFiles\Project_Space\short-drama-writer\plugin"
mkdir -p .claude-plugin
mkdir -p skills/drama-init
mkdir -p skills/drama-plan
mkdir -p skills/drama-write
mkdir -p skills/drama-review
mkdir -p skills/drama-generate
mkdir -p skills/drama-query
mkdir -p skills/drama-dashboard
mkdir -p agents
mkdir -p genres/urban-cool
mkdir -p genres/period-drama
mkdir -p genres/sweet-romance
mkdir -p genres/family-drama
mkdir -p genres/revenge-makeover
mkdir -p genres/suspense-mystery
mkdir -p references
mkdir -p templates
mkdir -p scripts
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "short-drama-writer",
  "version": "0.1.0",
  "description": "AI短剧/短视频生成系统 (skills + agents + knowledge base + data chain)",
  "author": { "name": "jwge" },
  "keywords": ["short-drama", "ai-video", "claude-code", "skills", "agents"],
  "license": "MIT"
}
```

- [ ] **Step 3: Commit**

```bash
git add plugin/
git commit -m "chore: scaffold plugin directory structure"
```

---

## Phase 1: Knowledge Base & Templates

### Task 1.1: Create genre knowledge files — urban-cool

**Files:**
- Create: `plugin/genres/urban-cool/character-archetypes.md`
- Create: `plugin/genres/urban-cool/plot-templates.md`
- Create: `plugin/genres/urban-cool/pacing.md`
- Create: `plugin/genres/urban-cool/face-slapping-patterns.md`

- [ ] **Step 1: Write character-archetypes.md**

```markdown
# 都市爽文 — 角色原型

## 男主原型

### 归来战神型
- 身份：退役兵王/隐世高手/回归都市的传奇
- 核心欲望：过平静生活（但麻烦主动找上门）
- 能力锚点：格斗/医术/商业洞察/人脉网络
- 性格锚点：低调隐忍→被迫展露实力
- 口头禅倾向：简洁、不解释、行动先于言语
- 禁忌行为：主动欺凌弱者、炫耀武力

### 商界巨擘型
- 身份：隐藏身份的富豪/商业天才/幕后大佬
- 核心欲望：保护家人/复仇/重建商业帝国
- 能力锚点：资本运作/识人用人/信息差优势
- 性格锚点：表面温和实则深不可测
- 禁忌行为：情绪失控、低级失误

## 女主原型

### 冷艳总裁型
- 身份：家族企业掌舵人/白手起家的女强人
- 核心欲望：证明自己/守护事业
- 性格锚点：外冷内热、理性决策
- 禁忌行为：恋爱脑、无端示弱

### 逆境逆袭型
- 身份：被轻视的普通人/隐藏天赋者
- 核心欲望：打破偏见/复仇/自我实现
- 性格锚点：坚韧、聪明、步步为营
- 禁忌行为：无理由的圣母行为

## 反派层次

1. 跳脸小丑（5集内打脸）→ 2. 地方势力（20集）→ 3. 商业对手（50集）→ 4. 幕后黑手（100集）
```

- [ ] **Step 2: Write plot-templates.md**

```markdown
# 都市爽文 — 情节模板

## 核心爽点循环

```
挑衅 → 轻视 → 步步紧逼 → 底牌初现 → 震惊全场 → 余波（新威胁暗示）
```

每轮循环3-5集，每集结尾留悬念钩子。

## 经典开局（前10集）

1. 第1集：反差登场（主角隐藏身份出现在平常场合，被轻视）
2. 第2集：首次打脸（展示冰山一角的能力）
3. 第3集：余波+新冲突（引起注意，引来更强的对手）
4. 第4-5集：建立关系网络（盟友/红颜/小弟）
5. 第6-8集：第一次重大危机（商业/武力双线）
6. 第9-10集：阶段性胜利+伏笔（更大威胁浮现）

## 打脸节奏控制

- 轻度打脸：每1-2集1次（语言压制、小场面反转）
- 中度打脸：每3-5集1次（公开场合身份揭示、实力碾压）
- 重度打脸：每10-15集1次（终极反转、幕后身份曝光）
```

- [ ] **Step 3: Write pacing.md**

```markdown
# 都市爽文 — 节奏控制

## 单集节奏（1-5分钟短剧）

```
00:00-00:30  钩子（冲突/悬念/反差）→ 抓住注意力
00:30-02:00  发展（情节推进+角色互动）
02:00-04:00  高潮（打脸/反转/情感爆点）
04:00-04:30  余波+下集钩子
```

## 悬念密度

- 每集至少1个即时悬念（本集内解决）
- 每3集至少1个中期悬念（3-5集跨度）
- 每10集至少1个长期悬念（跨卷追踪）

## 情绪曲线约束

单个场景内情绪需要有起伏，不允许连续3分钟以上同一情绪基调。
连续两集不能在同一情绪高点结束（防止观众疲劳）。
```

- [ ] **Step 4: Write face-slapping-patterns.md**

```markdown
# 都市爽文 — 打脸模式库

## 身份反转式
场景：主角被当众羞辱 → 大人物/权威突然出现并对主角毕恭毕敬 → 全场震惊
适用：商场/餐厅/公司等公共场合
注意：反转身份需要有前期伏笔支撑

## 实力碾压式
场景：对手展示武力/财力 → 主角轻描淡写化解 → 对手意识到差距
适用：武力冲突/商业谈判
注意：不能让主角显得嗜血，碾压要有"不得已"的理由

## 专业降维式
场景：专家/权威在主角面前卖弄 → 主角指出致命错误 → 专家哑口无言
适用：医学/法律/技术等专业领域
注意：需要提前铺垫主角的专业背景
```

- [ ] **Step 5: Commit**

```bash
git add plugin/genres/urban-cool/
git commit -m "feat: add urban-cool genre knowledge base"
```

---

### Task 1.2: Create genre knowledge files — period-drama

**Files:**
- Create: `plugin/genres/period-drama/character-design.md`
- Create: `plugin/genres/period-drama/plot-patterns.md`
- Create: `plugin/genres/period-drama/dialogue-style.md`

- [ ] **Step 1: Write character-design.md**

```markdown
# 古装剧 — 角色设计

## 核心角色原型

### 帝王/君主型
- 外貌锚点：龙袍/常服区分，发冠制式，配饰等级
- 性格锚点：威仪不外露，喜怒不形于色
- 禁忌行为：当众失态、不遵礼制、无故偏宠

### 将门之后型
- 外貌锚点：劲装/铠甲，身上有旧伤，站姿端正
- 性格锚点：直来直往但粗中有细
- 禁忌行为：欺压百姓、临阵退缩

### 商户/民间型
- 外貌锚点：布衣/绸缎区分身份，配饰暗示财富等级
- 性格锚点：精明圆滑，善于察言观色
- 禁忌行为：与官府正面冲突

## 女性角色

### 后宫妃嫔型
- 外貌锚点：品级对应的服饰规制（颜色/绣纹/头饰）
- 性格锚点：表面温婉，言外有意
- 禁忌行为：直接表达敌意、越级行为

### 江湖侠女型
- 外貌锚点：束发/披发区分场合，武器随身
- 性格锚点：快意恩仇，江湖义气
- 禁忌行为：扭捏作态、软弱依赖
```

- [ ] **Step 2: Write plot-patterns.md**

```markdown
# 古装剧 — 情节模式

## 宫斗模板

### 经典节奏
1. 示弱潜伏（3-5集）：新人入宫/入府，被轻视
2. 首次反击（第6-8集）：借力打力，不露痕迹的第一次反击
3. 建立同盟（第9-15集）：拉拢中间派，培养心腹
4. 正面对决（第16-25集）：与主要对手正面交锋
5. 阶段性胜利 + 更大威胁出现

### 宫斗手段库
- 信息战：截获消息/散布谣言/安插眼线
- 借势：借更高级别的势力压制对手
- 示弱陷阱：主动示弱引诱对手犯错
- 礼制武器：利用规矩/礼仪限制对手

## 权谋模板

### 朝堂博弈
- 利益交换（不得不见的对手）
- 站队博弈（选择阵营的逻辑）
- 连环计（一石三鸟的谋划）
```

- [ ] **Step 3: Write dialogue-style.md**

```markdown
# 古装剧 — 对白规范

## 基本规则

1. 身份决定措辞：帝王/臣子/平民/商户各有适宜的表达方式
2. 场合决定语气：朝堂正式 vs 私下交谈 vs 书信往来
3. 时代感但不晦涩：避免现代词汇（OK、搞定、nice），但也不刻意用文言文

## 层级称呼体系

| 关系 | 自称 | 称对方 |
|------|------|--------|
| 臣→君 | 臣/微臣 | 陛下/皇上 |
| 下级→上级 | 下官/属下 | 大人/将军 |
| 平级 | 在下/某 | 兄/阁下 |
| 长辈↔晚辈 | 老夫/老身 ↔ 晚辈 | 依辈分而定 |

## 不同场景的语气

### 朝堂之上
- 含蓄委婉，借古喻今
- "臣以为此事……" 而非 "我不同意"
- 用"似有不妥"代替"不对"

### 宫闱私语
- 表面客套，暗藏锋芒
- 一句话两个意思：说给外人听的 + 说给明白人听的

### 市井巷陌
- 直接、通俗、有烟火气
- 可使用当时的市井俚语
```

- [ ] **Step 4: Commit**

```bash
git add plugin/genres/period-drama/
git commit -m "feat: add period-drama genre knowledge base"
```

---

### Task 1.3: Create genre knowledge files — sweet-romance + suspense-mystery

**Files:**
- Create: `plugin/genres/sweet-romance/romance-patterns.md`
- Create: `plugin/genres/sweet-romance/character-archetypes.md`
- Create: `plugin/genres/suspense-mystery/clue-design.md`
- Create: `plugin/genres/suspense-mystery/reversal-patterns.md`

- [ ] **Step 1: Write sweet-romance files**

For `plugin/genres/sweet-romance/romance-patterns.md`:

```markdown
# 甜宠剧 — 情感模式

## 核心情感循环

```
磨合冲突 → 一方主动 → 另一方动心 → 甜宠互动 → 外部危机 → 共同面对 → 感情升温
```

每轮循环后关系进一阶：陌生人→认识→心动→暧昧→确认→公开→考验→稳固。

## 甜宠互动频次

- 每集至少1次"心动时刻"（眼神/触碰/话语直击内心的瞬间）
- 每3集至少1次"撒糖名场面"（告白/保护/公开示爱等高甜事件）
- 每隔5-8集一次"虐→甜"反转（小误会后的大和解）

## 冲突类型与比例

- 内部误会：40%（可1-3集内解决）
- 外部干预：35%（第三者/家庭/事业冲突）
- 自我怀疑：25%（觉得自己配不上对方）
```

For `plugin/genres/sweet-romance/character-archetypes.md`:

```markdown
# 甜宠剧 — 角色原型

## 男主原型

### 霸道总裁型
- 外貌锚点：西装/名表/冷峻面容
- 性格锚点：对外冷酷、对内独宠，占有欲强但尊重女主
- 核心反差：商场杀伐果断 ↔ 面对女主时笨拙真诚
- 禁忌行为：真正伤害女主、不尊重女主选择

### 暖男守护型
- 外貌锚点：干净柔和，细节处显示品位
- 性格锚点：默默守护，行动多于言语
- 核心反差：表面普通 ↔ 关键时刻展现惊人能力
- 禁忌行为：过度干涉、擅自替女主做决定

## 女主原型

### 独立自强型
- 外貌锚点：干练清爽，不浓妆艳抹
- 性格锚点：有自己事业/追求，不依附
- 核心魅力：在男主面前保持独立人格
- 禁忌行为：恋爱后放弃自我、过度依赖

### 灰姑娘成长型
- 外貌锚点：初期朴素→逐渐精致（自然变化）
- 性格锚点：从自卑到自信的成长曲线
- 禁忌行为：一步登天式转变（需要合理成长节奏）
```

- [ ] **Step 2: Write suspense-mystery files**

For `plugin/genres/suspense-mystery/clue-design.md`:

```markdown
# 悬疑剧 — 线索设计

## 线索投喂节奏

| 集数 | 线索类型 | 密度 |
|------|---------|------|
| 第1集 | 核心谜面 + 1条表面线索 + 1条隐藏线索 | 高 |
| 第2-5集 | 每集1-2条线索 + 1条误导线索 | 中 |
| 第6-9集 | 线索开始交汇，出现矛盾信息 | 高 |
| 第10集 | 关键线索 + 反转 + 新谜面 | 最高 |

## 线索埋设规则

1. **公平原则**：所有关键线索必须在揭晓前出现过（不凭空出现）
2. **误导原则**：每2条真线索配1条可解释为多义的误导线索
3. **层次原则**：线索分三层——表面层（观众能看到）、隐藏层（回看才能发现）、暗线层（跨集追踪才能拼凑）

## 线索类型

- 物品线索：出现在场景中的物体，需要特写镜头强调
- 对话线索：角色无意间说出的话，事后验证是关键信息
- 行为线索：角色的反常举动，暗示隐藏动机
- 时间线索：时间线上的矛盾，暴露出谎言
```

For `plugin/genres/suspense-mystery/reversal-patterns.md`:

```markdown
# 悬疑剧 — 反转模式

## 反转节奏

- 小型反转（每3-5集）：配角身份/单条线索的真相
- 中型反转（每10-15集）：主要角色的隐藏面/核心线索的重新解释
- 大型反转（每30集/卷末）：推翻之前的基本假设，重新定义整个故事

## 反转模板

### 身份反转
- 你以为的盟友其实是对手
- 看似无关的配角是关键人物
- "死者"其实没死 / "凶手"其实是被嫁祸

### 动机反转
- 表面的恶意行为背后是保护
- 看似无私的帮助其实有阴暗目的

### 时间线反转
- 你以为的"现在"其实是"过去"
- 多条时间线在关键点交汇

## 反转质量检查

1. 反转后回头检查前文：是否有足够伏笔支撑？
2. 观众是否会觉得被欺骗？（需要足够的fair-play线索）
3. 反转后故事是否更有趣？（而非只是让人意外）
```

- [ ] **Step 3: Commit**

```bash
git add plugin/genres/sweet-romance/ plugin/genres/suspense-mystery/
git commit -m "feat: add sweet-romance and suspense-mystery genre knowledge"
```

---

### Task 1.4: Create genre knowledge files — family-drama + revenge-makeover

**Files:**
- Create: `plugin/genres/family-drama/conflict-templates.md`
- Create: `plugin/genres/family-drama/character-archetypes.md`
- Create: `plugin/genres/revenge-makeover/rhythm.md`
- Create: `plugin/genres/revenge-makeover/makeover-patterns.md`

- [ ] **Step 1: Write family-drama/conflict-templates.md**

```markdown
# 家庭伦理剧 — 冲突模板

## 核心冲突类型

### 代际冲突
- 传统 vs 现代价值观（婚姻观/职业选择/育儿方式）
- 父母偏心引发的兄弟姐妹矛盾
- 养老责任分配

### 婚姻冲突
- 婆媳矛盾（核心高频冲突）
- 出轨/信任危机
- 经济权力不平衡
- 子女教育分歧

### 家族利益冲突
- 财产分配/继承权争夺
- 家族企业控制权
- 亲情与利益的撕扯

## 冲突节奏

```
每集：1个即时冲突（可在本集或下集解决）
每5集：1个积累爆发（长期压抑后的集中释放）
每10集：1个关系转折（某些关系彻底改变）
```

## 情感爆点触发条件

1. 秘密被发现（藏了10集以上的秘密突然曝光）
2. 立场反转（一直站在一方的人突然倒戈）
3. 牺牲揭示（某人的默默付出被偶然发现）
4. 亲情考验（在利益和亲情之间的终极选择）
```

For `plugin/genres/family-drama/character-archetypes.md`:

```markdown
# 家庭伦理剧 — 角色原型

## 核心角色

### 强势婆婆型
- 外貌锚点：精致得体，细节显示掌控欲
- 性格锚点：爱子心切但方式错误，有自己的人生创伤
- 角色弧：从控制→理解→放手
- 禁忌行为：纯粹的恶毒（需要有合理的心理动机）

### 夹缝丈夫型
- 外貌锚点：得体但不张扬，可能有些疲惫
- 性格锚点：爱妻子也孝顺母亲，逃避冲突
- 角色弧：从逃避→站出来的成长
- 禁忌行为：完全偏袒一方（需要体现两难）

### 成长媳妇型
- 外貌锚点：初期单纯/温顺→逐渐坚定自信
- 性格锚点：有底线有智慧，不卑不亢
- 角色弧：从忍让→智慧应对→赢得尊重
- 禁忌行为：黑化报复（家庭剧不是宫斗剧）
```

- [ ] **Step 2: Write revenge-makeover files**

For `plugin/genres/revenge-makeover/rhythm.md`:

```markdown
# 复仇逆袭剧 — 节奏控制

## 核心情绪曲线

```
压抑 → 触发 → 决心 → 准备 → 第一步 → 受阻 → 突破 → 阶段性复仇 → 代价 → 更大的复仇
```

## 阶段划分

### 第一阶段：压抑累积（第1-5集）
- 第1集：终极打击（被陷害/背叛/失去一切）
- 第2-3集：低谷挣扎（展现主角的痛苦和求生欲）
- 第4-5集：转折契机（获得力量/盟友/关键信息）

### 第二阶段：准备蓄力（第6-15集）
- 每2-3集完成一项准备工作
- 穿插小型复仇（给观众的即时满足）
- 建立新的身份/能力/关系网络

### 第三阶段：逐步复仇（第16-30集）
- 从外围到核心，逐个击破对手势力
- 每完成一个阶段的复仇，揭示更大的幕后黑手
- 复仇手段递进升级

### 第四阶段：终极对决（第31-40集）
- 对手拼死反扑
- 最大的代价（可能失去重要的人）
- 复仇完成后的空虚/反思/新目标
```

For `plugin/genres/revenge-makeover/makeover-patterns.md`:

```markdown
# 复仇逆袭剧 — 变身模式

## 变身关键帧（必有特写镜头）

### 外貌变身
1. 发现伤痕/缺陷 → 下定决心
2. 开始训练/准备 → 过程蒙太奇
3. 第一次亮相 → 特写旁人震惊反应
4. 需要维持的代价 → 展现坚持

### 身份变身
1. 舍弃旧名/旧身份（仪式感）
2. 建立新身份（证件/形象/社交圈）
3. 新旧身份冲突（差点暴露）
4. 新身份被认可/被识破

### 能力变身
1. 发现天赋/获得能力（偶然/命中注定）
2. 首次尝试失败（展示学习曲线）
3. 第一次成功运用（给观众满足感）
4. 能力的极限/代价（防止无敌感）

## 变身频率约束
- 同一角色在同一集内只能有1次显著的"变身展示"
- 每10集内至少安排1次"变身回报"（观众期待兑现）
- 不能连续两集都在"变身"（需要缓冲集来展示新状态下的日常）
```

- [ ] **Step 3: Commit**

```bash
git add plugin/genres/family-drama/ plugin/genres/revenge-makeover/
git commit -m "feat: add family-drama and revenge-makeover genre knowledge"
```

---

### Task 1.5: Create shared reference files

**Files:**
- Create: `plugin/references/cinematic-rules.md`
- Create: `plugin/references/shot-composition.md`
- Create: `plugin/references/ai-flavor-checklist.md`
- Create: `plugin/references/style-inference.md`
- Create: `plugin/references/platform-standards.md`

- [ ] **Step 1: Write cinematic-rules.md**

```markdown
# 摄影规则参考

## 取景框类型

| 取景 | 英文 | 画面范围 | 典型用途 |
|------|------|---------|---------|
| 远景 | ELS | 环境全貌+人物渺小 | 建立场景、展示空间关系 |
| 全景 | LS | 人物全身+部分环境 | 人物入场、动作展示 |
| 中景 | MS | 人物膝盖以上 | 对话、多人互动 |
| 近景 | MCU | 人物胸部以上 | 情感反应、关键对话 |
| 特写 | CU | 面部/物体 | 情绪放大、细节强调 |
| 大特写 | ECU | 眼睛/手部/物品局部 | 极致情绪/关键线索 |

## 每个场景的取景框配比要求

- 至少1个广角（远景/全景）：建立空间感
- 至少1个中景：人物互动主体
- 至少1个特写：情绪/细节
- 推荐3-5个取景框

## 180度法则

两个对话角色之间有一条隐形轴线。所有镜头必须在轴线同一侧拍摄。
违反=跳轴，角色视线方向突然反转，观众迷失空间关系。

## 运镜手法

| 手法 | 效果 | 适用场景 |
|------|------|---------|
| 推 | 从全景→特写，引导注意力集中 | 揭示关键信息、情绪升温 |
| 拉 | 从特写→全景，展示环境/孤立感 | 建立场景、情绪降温 |
| 摇 | 水平旋转，展示空间关系 | 环境建立、追逐 |
| 跟 | 跟随移动物体/人物 | 运动场景、长镜头 |
| 升/降 | 垂直移动 | 展示高度/地位变化 |

## 不允许的运镜

- 同一场景内连续3次同一方向摇镜（单调）
- 对话场景中无故快速变焦（观众眩晕）
```

- [ ] **Step 2: Write shot-composition.md**

```markdown
# 短视频分镜构图指南

## 画面比例

- 竖屏 9:16（抖音/快手/微短剧标准）
- 横屏 16:9（传统影视/B站）

## 竖屏构图规则

1. **安全区**：主体放在画面中上1/3处（不被标题遮挡）
2. **视线空间**：人物看向的方向留更多空间（看向右侧→左侧留白少）
3. **黄金分割**：主体不建议正中，偏左或偏右1/3处更自然

## 分镜衔接规则

| 前镜头 | 可接后镜头 | 不可接 |
|--------|-----------|--------|
| 全景 | 中景、近景 | 另一全景（除非新场景） |
| 中景 | 近景、特写 | 另一中景（跳切感） |
| 近景 | 特写、中景 | 另一近景相同角度 |
| 特写 | 近景、全景 | 另一特写同一主体 |
```

- [ ] **Step 3: Write ai-flavor-checklist.md**

```markdown
# AI味检测清单

## 词汇维度

### 高频AI词汇（避免）
- 缓缓、微微、渐渐、轻轻、淡淡、悄然
- 深邃、璀璨、纯真、纯粹、无比、无限
- 似乎、仿佛、犹如、宛若、宛如

### 面部表情模板（避免）
- "嘴角微微上扬/勾起一抹笑容"
- "眼中闪过一丝XX"
- "眸色一暗/眸光一沉"
- "眉头微微蹙起"

## 句式维度

### 四段式闭环（警惕）
- 原因→过程→结果→感悟（完整闭环，不留给读者空间）
- 每一段结尾都来一句总结升华

### 同构句重复（警惕）
- 连续3句以上相同句式结构
- 排比句滥用

### 段落结尾总结句（必须删除）
- 所有以感悟/道理收尾的段落尾句

## 叙事维度

### 匀速节奏（警惕）
- 全篇没有节奏变化，匀速推进
- 对话/动作/描写/内心独白的比例过于均匀

### 天机式预示（必须删除）
- "殊不知，更大的危机正在等待着他"
- "他不知道的是，这只是开始"
- "命运的齿轮已经开始转动"

### "安全着陆"章节结尾（警惕）
- 每集都解决冲突才结束
- 不留悬念或情绪钩子

### Show-Then-Tell（警惕）
- 角色做了某事→叙述者立刻解释他为什么这样做
- 读者能从行为自己判断的，不需要再解释

## 情感维度

### 标签化情感（避免）
- "他感到愤怒" → 改为：他攥紧了拳头，指节发白
- "她十分悲伤" → 改为：她盯着手机屏幕，直到眼眶酸涩才意识到自己在等什么

### 瞬间情绪切换（警惕）
- 上一秒还在愤怒，下一秒就温柔微笑（没有过渡）

### 千人一面（警惕）
- 所有角色用同样的方式表达情绪
- 反派生气和主角生气没有区别

## 对白维度

### 信息传教（警惕）
- 角色说出观众需要知道的信息，但这些信息角色之间根本不需要说出来
- "你也知道，我们已经三年没见了"（双方都知道，纯为观众解说）

### 缺乏口语特征（警惕）
- 所有角色对白书面化、无口头禅、无语癖
- 对话中角色说话方式完全一致

### 对话后解释（警惕）
- 角色说完→叙述者解释"他的意思是..."
- 好的对白自带潜台词，不需要旁白翻译
```

- [ ] **Step 4: Write style-inference.md**

```markdown
# 类型 → 视觉风格映射

## 都市爽剧

| 属性 | 值 |
|------|-----|
| 色调 | 冷峻蓝灰调为主，关键场景暖色对冲 |
| 灯光 | 高对比度、硬光为主、阴影锐利 |
| 景深 | 浅景深（主角与背景分离） |
| 镜头语言 | 快速切换（1.5-2.5s/镜头），强调节奏感 |
| 参考 | 《疾速追杀》现代都市段落 |

## 古装剧

| 属性 | 值 |
|------|-----|
| 色调 | 低饱和暖色（宫廷）/ 低饱和冷色（江湖） |
| 灯光 | 柔光为主，烛光/自然光质感 |
| 景深 | 深景深（展示空间层级） |
| 镜头语言 | 中慢节奏（2-3s/镜头），静态构图为主 |
| 参考 | 《琅琊榜》《长安十二时辰》 |

## 甜宠剧

| 属性 | 值 |
|------|-----|
| 色调 | 高调暖色，粉色/杏色基底 |
| 灯光 | 柔光、逆光（发丝光）、眼神光必补 |
| 景深 | 浅景深（两人同框时加深） |
| 镜头语言 | 中速切换（2-2.5s/镜头），多用大特写 |
| 参考 | 《你是我的荣耀》甜宠段落 |

## 悬疑剧

| 属性 | 值 |
|------|-----|
| 色调 | 低饱和、偏绿/偏蓝暗调 |
| 灯光 | 局部照明、大量阴影、实用光源（台灯/窗光） |
| 景深 | 变化景深（揭示关键信息时变浅） |
| 镜头语言 | 慢速推镜、静态长镜头、突然变速 |
| 参考 | 《隐秘的角落》 |

## 家庭伦理

| 属性 | 值 |
|------|-----|
| 色调 | 自然真实色调，不做过度风格化 |
| 灯光 | 自然光+室内实用光源 |
| 景深 | 中景深 |
| 镜头语言 | 中慢节奏，手持感增加真实感 |
| 参考 | 《都挺好》 |

## 复仇逆袭

| 属性 | 值 |
|------|-----|
| 色调 | 前期阴冷→后期渐变暖/亮（随复仇进度变化） |
| 灯光 | 高低反差交替，气场变化时用光质切换 |
| 景深 | 浅景深（特写主角）vs 深景深（展示复仇现场） |
| 镜头语言 | 节奏随复仇进度加速，前期慢→后期快 |
| 参考 | 《黑暗荣耀》 |
```

- [ ] **Step 5: Write platform-standards.md**

```markdown
# 平台标准

## 抖音短剧

| 属性 | 约束 |
|------|------|
| 单集时长 | 1-3分钟 |
| 画面比例 | 9:16 竖屏 |
| 分辨率 | 1080x1920 |
| 前3秒 | 必须有钩子（冲突/悬念/反差） |
| 结尾 | 强悬念钩子（引导下一集） |
| 字幕 | 必须大字幕（屏幕中下1/3） |

## 快手短剧

| 属性 | 约束 |
|------|------|
| 单集时长 | 1-5分钟 |
| 画面比例 | 9:16 竖屏 |
| 分辨率 | 1080x1920 |
| 风格 | 更接地气，强冲突优先 |

## 微短剧平台（小程序短剧）

| 属性 | 约束 |
|------|------|
| 单集时长 | 1-2分钟 |
| 画面比例 | 9:16 |
| 集数 | 100集+ |
| 节奏 | 极快，每30秒一个爽点 |
| 前10集 | 免费试看，需要极高转化率 |
```

- [ ] **Step 6: Commit**

```bash
git add plugin/references/
git commit -m "feat: add shared reference files (cinematic, shot, ai-flavor, style, platform)"
```

---

### Task 1.6: Create templates

**Files:**
- Create: `plugin/templates/project-init.json`
- Create: `plugin/templates/world-setting.md`
- Create: `plugin/templates/character-card.md`
- Create: `plugin/templates/scene-card.md`
- Create: `plugin/templates/master-outline.md`
- Create: `plugin/templates/episode-outline.md`
- Create: `plugin/templates/episode-script.md`
- Create: `plugin/templates/shot-prompt.json`

- [ ] **Step 1: Write project-init.json**

```json
{
  "project": {
    "title": "",
    "genre": "",
    "sub_genre": "",
    "target_platform": "",
    "total_episodes": 100,
    "episode_duration_min": 1,
    "episode_duration_max": 3,
    "aspect_ratio": "9:16"
  },
  "creative_constraints": {
    "one_liner": "",
    "core_conflict": "",
    "target_audience": "",
    "anti_trope_rules": [],
    "hard_constraints": []
  },
  "created_at": "",
  "version": "1.0"
}
```

- [ ] **Step 2: Write world-setting.md**

```markdown
# 世界观设定

## 基本设定

| 属性 | 值 |
|------|-----|
| 世界类型 | （现代都市/古代架空/近代/未来/异世界） |
| 时代背景 | |
| 地理范围 | （单城市/多城市/跨大陆/多世界） |
| 社会结构 | （阶层/权力分布/主要矛盾） |

## 特殊规则

（如果世界有与现实不同的基础规则，在此定义。例如：存在超能力/灵气复苏/科技超前等）

| 规则 | 说明 | 影响 |
|------|------|------|
| | | |

## 势力分布

### [势力名1]
- 性质：（商业帝国/江湖门派/政治派系/地下组织）
- 核心人物：
- 势力范围：
- 与其他势力的关系：

## 重要地点

### [地点名]
- 类型：（城市/建筑/区域）
- 空间特征：（关键地标/布局特点）
- 氛围：
- 关联角色/势力：
```

- [ ] **Step 3: Write character-card.md**

```markdown
# 角色档案：[角色名]

## 外貌锚点（这些不可随意变更 → 影响图像一致性）

| 属性 | 值 |
|------|-----|
| 性别 | |
| 年龄段 | |
| 身高体型 | |
| 面部特征 | （眉型/眼型/鼻梁/唇形/脸型） |
| 发型发色 | |
| 标志性特征 | （伤疤/痣/纹身/特殊配饰） |
| 穿衣风格 | （颜色偏好/款式偏好/标志性单品） |

## 性格锚点

| 属性 | 值 |
|------|-----|
| 核心欲望 | （最想要的东西，驱动一切行为的根源） |
| 核心恐惧 | （最害怕发生的事，性格弱点的根源） |
| 口头禅/语癖 | |
| 情绪反应模式 | （愤怒时/悲伤时/开心时的典型反应） |
| 在压力下的行为 | |

## 禁忌行为（绝对不能做的事/说的话）

1.
2.
3.

## 角色弧（全剧变化方向）

| 阶段 | 集数 | 角色状态 |
|------|------|---------|
| 起点 | 第1集 | |
| 变化触发 | 第X集 | |
| 转折点 | 第X集 | |
| 终点 | 第100集 | |

## 与其他角色的关系

| 角色 | 关系 | 关系动态 |
|------|------|---------|
| | | |
```

- [ ] **Step 4: Write scene-card.md**

```markdown
# 场景档案：[场景名]

## 空间锚点（不可随意变更 → 影响场景图像一致性）

| 属性 | 值 |
|------|-----|
| 场景类型 | （室内/室外/半开放） |
| 关键地标 | （场景中最有辨识度的物体或结构） |
| 色调/光照方向 | （主光源方向/色温/亮度） |
| 典型取景角度 | （这个场景最适合从哪个角度拍摄） |
| 空间尺寸 | （大致面积和比例） |

## 氛围约束

| 属性 | 值 |
|------|-----|
| 氛围基调 | （温馨/紧张/阴暗/明亮/浪漫/压抑） |
| 可允许的情绪范围 | （这个场景里可以发生哪种情绪，不可以发生哪种） |
| 时间特征 | （这个场景通常出现在什么时间段） |

## 道具清单

| 道具 | 位置 | 备注 |
|------|------|------|
| | | |

## 场景中的典型活动

（在这个场景里通常发生什么类型的事件）
```

- [ ] **Step 5: Write master-outline.md**

```markdown
# 总纲

## 故事概要

| 属性 | 值 |
|------|-----|
| 系列标题 | |
| 一句话简介 | |
| 类型 | |
| 目标平台 | |
| 总集数 | |
| 单集时长 | |

## 主题与核心冲突

| 属性 | 值 |
|------|-----|
| 核心主题 | |
| 主要冲突 | （主角想要什么 vs 什么在阻碍） |
| 深层冲突 | （价值观/信仰层面的冲突） |

## 主角弧线

（主角从第1集到最后一集的变化轨迹）

## 反派层次

| 层级 | 角色 | 登场集数 | 解决集数 | 威胁级别 |
|------|------|---------|---------|---------|
| 1 | | | | 跳脸小丑 |
| 2 | | | | 地方势力 |
| 3 | | | | 主要对手 |
| 4 | | | | 幕后黑手 |

## 分期规划

| 卷 | 集数范围 | 核心剧情 | 主线/支线 |
|----|---------|---------|----------|
| 1 | 1-10 | | |
| 2 | 11-20 | | |
| ... | | | |
```

- [ ] **Step 6: Write episode-outline.md**

```markdown
# 分集大纲

## 第0001集：[标题]

| 属性 | 值 |
|------|-----|
| 情绪基调 | |
| 时长分配 | 钩子(:30) / 发展(1:30) / 高潮(1:30) / 钩子(:30) |
| 本集目标 | （这一集要完成什么叙事任务） |

### 情绪曲线

```
情绪强度
  │     ╱‾‾‾‾‾╲
  │    ╱        ╲
  │   ╱          ╲___
  │  ╱               ╲
  │ ╱                 ╲
  └─────────────────────→ 时间
   00:00            04:00
```

### 节拍序列

| # | 节拍 | 时长 | 场景 | 内容 | 情绪 |
|---|------|------|------|------|------|
| 1 | 钩子 | :30 | | | 好奇/紧张 |
| 2 | 发展 | :45 | | | |
| 3 | 发展 | :45 | | | |
| 4 | 高潮 | 1:30 | | | |
| 5 | 钩子 | :30 | | | 悬念 |

### 场景梗概

| 场景 | 地点 | 出场角色 | 核心事件 | 取景框数 |
|------|------|---------|---------|---------|
| S1 | | | | 3-5 |
| S2 | | | | 3-5 |

### 出场角色状态

| 角色 | 本集开始时状态 | 本集结束时状态 | 变化 |
|------|--------------|--------------|------|
| | | | |

### 伏笔操作

| 操作 | 伏笔内容 | 关联集数 |
|------|---------|---------|
| 埋设 | | → 第X集回收 |
| 推进 | | ← 第X集埋设 |
| 回收 | | ← 第X集埋设 |
```

- [ ] **Step 7: Write episode-script.md**

```markdown
# 第0001集：[标题]

> 情绪基调： | 场景数： | 总取景框数：

---

## 场景1：[场景名]

**场景设定**：[地点] | [时间] | [出场角色]

**取景框序列**：WIDE → MS → CU → MS → WIDE

### ASCII 空间布局

```
┌──────────────────────┐
│                      │
│                      │
│                      │
│                      │
│                      │
└──────────────────────┘
图例：
```

### 分镜流图

---

#### 镜头 S1_F01 [WIDE 远景]

**画面描述**：

**人物位置**：
| 角色 | 位置 | 朝向 | 服装 |
|------|------|------|------|
| | | | |

**动作**：

**对白**：

**衔接**：← 开场镜头

---

#### 镜头 S1_F02 [MS 中景]

**画面描述**：

**人物位置**：
| 角色 | 位置变化 | 当前位置 | 朝向 | 服装 |
|------|---------|---------|------|------|
| | | | | |

**动作**：

**对白**：

**衔接**：← 接 S1_F01，[衔接方式]

---

（每个场景重复此结构，3-5个镜头）

---
```

- [ ] **Step 8: Write shot-prompt.json**

```json
{
  "episode_id": "0001",
  "episode_title": "",
  "platform": "jimeng",
  "shots": [
    {
      "shot_id": "S01_F01",
      "frame_type": "WIDE",
      "prompt": {
        "positive": "",
        "negative": "",
        "spatial_anchors": "",
        "lighting_mood": "",
        "character_references": [],
        "scene_reference": ""
      },
      "video_params": {
        "duration_sec": 4,
        "aspect_ratio": "9:16",
        "fps": 24
      }
    }
  ]
}
```

- [ ] **Step 9: Commit**

```bash
git add plugin/templates/
git commit -m "feat: add output templates (project, world, character, scene, outline, script, prompt)"
```

---

## Phase 2: Python Data Scripts

### Task 2.1: Create CLI entry & state manager

**Files:**
- Create: `plugin/scripts/drama.py`
- Create: `plugin/scripts/state_manager.py`

- [ ] **Step 1: Write drama.py**

```python
#!/usr/bin/env python3
"""short-drama-writer CLI entry point."""

import sys
import os


def resolve_project_root() -> str:
    """Walk up from cwd to find .drama/state.json."""
    cwd = os.getcwd()
    for _ in range(20):
        if os.path.isfile(os.path.join(cwd, ".drama", "state.json")):
            return cwd
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    raise FileNotFoundError(
        "No .drama/state.json found. Run from a drama project directory."
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: drama.py <command> [args]")
        print("Commands: init, state, character, memory, commit, outline, review")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        from project_init import init_project
        init_project(sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == "state":
        from state_manager import StateManager
        root = resolve_project_root()
        sm = StateManager(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "get"
        if sub == "get":
            print(sm.get_state_json())
        elif sub == "update":
            key = sys.argv[3]
            value = sys.argv[4]
            sm.update(key, value)
    elif command == "character":
        from character_manager import CharacterManager
        root = resolve_project_root()
        cm = CharacterManager(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "list"
        if sub == "list":
            for name in cm.list_characters():
                print(name)
        elif sub == "get":
            print(cm.get_character(sys.argv[3]))
        elif sub == "set":
            cm.save_character(sys.argv[3], sys.argv[4])
    elif command == "memory":
        from memory_manager import MemoryManager
        root = resolve_project_root()
        mm = MemoryManager(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "summary"
        if sub == "summary":
            print(mm.get_summary())
        elif sub == "character_state":
            print(mm.get_character_states_json())
        elif sub == "foreshadowing":
            print(mm.get_foreshadowing_json())
    elif command == "commit":
        from chapter_commit import commit_episode
        root = resolve_project_root()
        commit_episode(root, sys.argv[2])
    elif command == "outline":
        from outline_loader import OutlineLoader
        root = resolve_project_root()
        ol = OutlineLoader(root)
        ep_num = sys.argv[2] if len(sys.argv) > 2 else None
        if ep_num:
            print(ol.get_episode_outline(ep_num))
        else:
            print(ol.get_all_outlines_json())
    elif command == "review":
        from review_saver import ReviewSaver
        root = resolve_project_root()
        rs = ReviewSaver(root)
        sub = sys.argv[2] if len(sys.argv) > 2 else "save"
        if sub == "save":
            rs.save_review(sys.argv[3], sys.argv[4])
        elif sub == "get":
            print(rs.get_review(sys.argv[3]))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write state_manager.py**

```python
"""Read/write .drama/state.json projection."""

import json
import os
from datetime import datetime


class StateManager:
    def __init__(self, project_root: str):
        self.root = project_root
        self.state_dir = os.path.join(project_root, ".drama")
        self.state_path = os.path.join(self.state_dir, "state.json")
        os.makedirs(self.state_dir, exist_ok=True)
        if not os.path.exists(self.state_path):
            self._write_default()

    def _write_default(self):
        default = {
            "project_title": "",
            "current_episode": 0,
            "total_episodes": 100,
            "phase": "init",  # init | plan | writing | generate | done
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "episodes_written": 0,
                "episodes_reviewed": 0,
                "shots_generated": 0
            }
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

    def get_state(self) -> dict:
        with open(self.state_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_state_json(self) -> str:
        return json.dumps(self.get_state(), ensure_ascii=False, indent=2)

    def update(self, key: str, value):
        state = self.get_state()
        # support dot notation: "stats.episodes_written"
        keys = key.split(".")
        target = state
        for k in keys[:-1]:
            target = target.setdefault(k, {})
        target[keys[-1]] = self._parse_value(value)
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _parse_value(self, value: str):
        if value.isdigit():
            return int(value)
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        return value

    def advance_phase(self, new_phase: str):
        self.update("phase", new_phase)
```

- [ ] **Step 3: Commit**

```bash
git add plugin/scripts/drama.py plugin/scripts/state_manager.py
git commit -m "feat: add CLI entry point and state manager"
```

---

### Task 2.2: Create project init script

**Files:**
- Create: `plugin/scripts/project_init.py`

- [ ] **Step 1: Write project_init.py**

```python
"""Initialize a new drama project directory."""

import json
import os
from datetime import datetime


DIRS = [
    ".drama",
    "设定集/角色档案",
    "设定集/场景档案",
    "大纲",
    "剧本",
    "分镜",
    "提示词",
    "素材/角色",
    "素材/场景",
    "素材/视频",
    "审查报告",
    "记忆",
    "导出",
]


def sanitize_dirname(title: str) -> str:
    """Remove chars unsafe for directory names."""
    unsafe = '<>:"/\\|?*'
    for ch in unsafe:
        title = title.replace(ch, "")
    return title.strip()[:80]


def init_project(title: str = None):
    cwd = os.getcwd()
    if title:
        project_dir = os.path.join(cwd, sanitize_dirname(title))
        os.makedirs(project_dir, exist_ok=True)
    else:
        project_dir = cwd

    for d in DIRS:
        os.makedirs(os.path.join(project_dir, d), exist_ok=True)

    # Write initial state.json
    state = {
        "project_title": title or os.path.basename(project_dir),
        "current_episode": 0,
        "total_episodes": 100,
        "phase": "init",
        "last_updated": datetime.now().isoformat(),
        "stats": {
            "episodes_written": 0,
            "episodes_reviewed": 0,
            "shots_generated": 0
        }
    }
    state_path = os.path.join(project_dir, ".drama", "state.json")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    # Write empty memory files
    memory_files = {
        "角色状态变迁.json": [],
        "场景状态.json": [],
        "伏笔追踪.json": [],
        "道具-服装追踪.json": {}
    }
    for fname, default in memory_files.items():
        fpath = os.path.join(project_dir, "记忆", fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

    print(f"Project initialized at: {project_dir}")
    return project_dir


if __name__ == "__main__":
    import sys
    title = sys.argv[1] if len(sys.argv) > 1 else None
    init_project(title)
```

- [ ] **Step 2: Commit**

```bash
git add plugin/scripts/project_init.py
git commit -m "feat: add project init script"
```

---

### Task 2.3: Create character & memory managers

**Files:**
- Create: `plugin/scripts/character_manager.py`
- Create: `plugin/scripts/memory_manager.py`
- Create: `plugin/scripts/outline_loader.py`

- [ ] **Step 1: Write character_manager.py**

```python
"""Read/write character card files in 设定集/角色档案/."""

import os
import re


class CharacterManager:
    def __init__(self, project_root: str):
        self.char_dir = os.path.join(project_root, "设定集", "角色档案")
        os.makedirs(self.char_dir, exist_ok=True)

    def list_characters(self) -> list[str]:
        """List all character names (from filenames)."""
        chars = []
        for fname in os.listdir(self.char_dir):
            if fname.endswith(".md"):
                # Strip prefix like "主角-" or "反派-"
                name = re.sub(r"^(主角|反派|配角|女主|男主)-", "", fname)
                name = name.replace(".md", "")
                chars.append(name)
        return sorted(chars)

    def get_character(self, name: str) -> str | None:
        """Read a character card by name. Returns markdown content."""
        for fname in os.listdir(self.char_dir):
            if name in fname and fname.endswith(".md"):
                fpath = os.path.join(self.char_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    return f.read()
        return None

    def save_character(self, name: str, content: str, role: str = "角色"):
        """Save or update a character card."""
        safe_name = name.replace("/", "_")
        fname = f"{role}-{safe_name}.md"
        fpath = os.path.join(self.char_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        return fpath

    def get_character_summary(self, name: str) -> dict | None:
        """Extract key fields from character card as dict."""
        content = self.get_character(name)
        if not content:
            return None

        summary = {"name": name}
        current_section = None
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                current_section = line[3:]
            elif current_section == "外貌锚点" and "|" in line and "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0] != "属性":
                    summary[parts[0]] = parts[1]
            elif current_section == "禁忌行为" and line.startswith("- "):
                summary.setdefault("forbidden_behaviors", []).append(line[2:])
        return summary
```

- [ ] **Step 2: Write memory_manager.py**

```python
"""Read/write memory files for cross-episode consistency."""

import json
import os


class MemoryManager:
    def __init__(self, project_root: str):
        self.mem_dir = os.path.join(project_root, "记忆")
        os.makedirs(self.mem_dir, exist_ok=True)

    def _read_json(self, filename: str) -> dict | list:
        fpath = os.path.join(self.mem_dir, filename)
        if not os.path.exists(fpath):
            return {}
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, filename: str, data):
        fpath = os.path.join(self.mem_dir, filename)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_character_states(self) -> list:
        return self._read_json("角色状态变迁.json")

    def get_character_states_json(self) -> str:
        return json.dumps(self.get_character_states(), ensure_ascii=False, indent=2)

    def update_character_state(self, episode_id: str, character_name: str,
                                state: dict, changes: list[str]):
        """Append a new state snapshot for a character after an episode."""
        states = self.get_character_states()
        entry = {
            "episode": episode_id,
            "character": character_name,
            "state": state,
            "changes": changes
        }
        states.append(entry)
        self._write_json("角色状态变迁.json", states)

    def get_foreshadowing(self) -> list:
        return self._read_json("伏笔追踪.json")

    def get_foreshadowing_json(self) -> str:
        return json.dumps(self.get_foreshadowing(), ensure_ascii=False, indent=2)

    def update_foreshadowing(self, foreshadowing_list: list):
        """Replace foreshadowing list entirely after data-agent extraction."""
        self._write_json("伏笔追踪.json", foreshadowing_list)

    def get_scene_states(self) -> list:
        return self._read_json("场景状态.json")

    def update_scene_state(self, scene_name: str, episode_id: str, changes: dict):
        states = self.get_scene_states()
        states.append({
            "scene": scene_name,
            "episode": episode_id,
            "changes": changes
        })
        self._write_json("场景状态.json", states)

    def get_costume_tracking(self) -> dict:
        return self._read_json("道具-服装追踪.json")

    def update_costume(self, character: str, outfit: str, episode_id: str):
        tracking = self.get_costume_tracking()
        tracking[character] = {
            "current_outfit": outfit,
            "last_updated_episode": episode_id
        }
        self._write_json("道具-服装追踪.json", tracking)

    def get_summary(self) -> str:
        """Return a compact summary of all memory for context-agent."""
        parts = []

        char_states = self.get_character_states()
        if char_states:
            # Get latest state per character
            latest = {}
            for entry in char_states:
                latest[entry["character"]] = entry
            parts.append("## 角色当前状态")
            for char, entry in latest.items():
                parts.append(f"- {char} (第{entry['episode']}集后): {json.dumps(entry['state'], ensure_ascii=False)}")

        foreshadowing = self.get_foreshadowing()
        if foreshadowing:
            active = [f for f in foreshadowing if f.get("status") != "resolved"]
            if active:
                parts.append("## 未闭合伏笔")
                for fb in active:
                    parts.append(f"- [{fb.get('id')}] {fb.get('content')} (埋设于第{fb.get('planted_in')}集)")

        costumes = self.get_costume_tracking()
        if costumes:
            parts.append("## 当前服装状态")
            for char, info in costumes.items():
                parts.append(f"- {char}: {info['current_outfit']} (第{info['last_updated_episode']}集)")

        return "\n\n".join(parts) if parts else "(无记忆数据)"
```

- [ ] **Step 3: Write outline_loader.py**

```python
"""Load episode outline data."""

import json
import os
import re


class OutlineLoader:
    def __init__(self, project_root: str):
        self.outline_dir = os.path.join(project_root, "大纲")
        self.outline_path = os.path.join(self.outline_dir, "分集大纲.md")

    def get_all_outlines_json(self) -> str:
        """Return the full outline file content."""
        if not os.path.exists(self.outline_path):
            return "{}"
        with open(self.outline_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Parse markdown into structured dict
        episodes = {}
        current_ep = None
        current_section = None
        for line in content.split("\n"):
            ep_match = re.match(r"^## 第(\d{4})集", line)
            if ep_match:
                current_ep = ep_match.group(1)
                episodes[current_ep] = {}
                current_section = None
            elif current_ep and line.startswith("### "):
                current_section = line[4:]
                episodes[current_ep][current_section] = ""
            elif current_ep and current_section:
                episodes[current_ep][current_section] += line + "\n"
        return json.dumps(episodes, ensure_ascii=False, indent=2)

    def get_episode_outline(self, ep_num: str) -> str:
        """Get outline for a specific episode as markdown."""
        if not os.path.exists(self.outline_path):
            return ""
        with open(self.outline_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Extract the section for this episode
        pattern = rf"(## 第{ep_num}集.*?)(?=\n## 第|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1) if match else ""
```

- [ ] **Step 4: Commit**

```bash
git add plugin/scripts/character_manager.py plugin/scripts/memory_manager.py plugin/scripts/outline_loader.py
git commit -m "feat: add character, memory managers and outline loader"
```

---

### Task 2.4: Create chapter commit & review saver

**Files:**
- Create: `plugin/scripts/chapter_commit.py`
- Create: `plugin/scripts/review_saver.py`

- [ ] **Step 1: Write chapter_commit.py**

```python
"""Commit an episode after write+review+polish: update state, write memory deltas."""

import json
import os
from datetime import datetime
from state_manager import StateManager


def commit_episode(project_root: str, episode_id: str,
                   memory_deltas: dict | None = None):
    """Update state.json and write memory deltas after episode is finalized.

    memory_deltas should be the JSON output from data-agent, with keys:
    - character_states: list of {character, state, changes}
    - scene_changes: list of {scene, changes}
    - foreshadowing: list (replaces current)
    - costume_updates: dict of {character: {outfit, episode}}
    """
    sm = StateManager(project_root)
    sm.update("current_episode", episode_id)
    sm.update("stats.episodes_written",
              sm.get_state()["stats"]["episodes_written"] + 1)
    sm.update("phase", "writing")
    sm.update("last_updated", datetime.now().isoformat())

    if memory_deltas:
        from memory_manager import MemoryManager
        mm = MemoryManager(project_root)

        for cs in memory_deltas.get("character_states", []):
            mm.update_character_state(
                episode_id, cs["character"], cs["state"], cs.get("changes", [])
            )

        for sc in memory_deltas.get("scene_changes", []):
            mm.update_scene_state(sc["scene"], episode_id, sc.get("changes", {}))

        if "foreshadowing" in memory_deltas:
            mm.update_foreshadowing(memory_deltas["foreshadowing"])

        for char, info in memory_deltas.get("costume_updates", {}).items():
            mm.update_costume(char, info["outfit"], episode_id)

    print(f"Episode {episode_id} committed.")


if __name__ == "__main__":
    import sys
    commit_episode(sys.argv[1], sys.argv[2])
```

- [ ] **Step 2: Write review_saver.py**

```python
"""Save review reports and write back review metrics."""

import json
import os
from datetime import datetime


class ReviewSaver:
    def __init__(self, project_root: str):
        self.review_dir = os.path.join(project_root, "审查报告")
        os.makedirs(self.review_dir, exist_ok=True)

    def save_review(self, episode_id: str, review_json: str):
        """Save review JSON and generate a markdown report."""
        review = json.loads(review_json)
        ep_num = episode_id.zfill(4) if episode_id.isdigit() else episode_id
        fname = f"第{ep_num}集审查报告.md"

        # Build markdown report
        lines = [
            f"# 第{ep_num}集审查报告",
            f"审查时间：{datetime.now().isoformat()}",
            "",
            f"## 摘要",
            f"问题总数：{len(review.get('issues', []))}",
        ]

        blocking = [i for i in review.get("issues", []) if i.get("blocking")]
        lines.append(f"阻塞问题：{len(blocking)}")

        for severity in ["critical", "high", "medium", "low"]:
            issues = [i for i in review.get("issues", [])
                      if i.get("severity") == severity]
            if issues:
                lines.append(f"\n## {severity.upper()} ({len(issues)}个)")
                for idx, issue in enumerate(issues, 1):
                    lines.append(f"\n### {idx}. [{issue.get('category')}] {issue.get('description')}")
                    lines.append(f"- **位置**: {issue.get('location')}")
                    lines.append(f"- **证据**: {issue.get('evidence')}")
                    lines.append(f"- **修复方向**: {issue.get('fix_hint')}")
                    lines.append(f"- **阻塞**: {'是' if issue.get('blocking') else '否'}")

        report = "\n".join(lines)
        fpath = os.path.join(self.review_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(report)

        # Also save raw JSON
        json_path = fpath.replace(".md", ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(review, f, ensure_ascii=False, indent=2)

        print(f"Review saved to {fpath}")
        return fpath

    def get_review(self, episode_id: str) -> str | None:
        ep_num = episode_id.zfill(4) if episode_id.isdigit() else episode_id
        json_path = os.path.join(self.review_dir, f"第{ep_num}集审查报告.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
```

- [ ] **Step 3: Commit**

```bash
git add plugin/scripts/chapter_commit.py plugin/scripts/review_saver.py
git commit -m "feat: add chapter commit and review saver scripts"
```

---

## Phase 3: Agent Definitions

### Task 3.1: Create context-agent

**Files:**
- Create: `plugin/agents/context-agent.md`

- [ ] **Step 1: Write context-agent.md**

```markdown
---
name: context-agent
description: Pre-writing research for drama episodes, outputs a writing task book for drama-write draft stage.
tools: Read, Bash
model: inherit
---

You are a pre-writing assembler for short drama episodes. Research first, then output a **writing task book** to the draft stage.

## Input

You receive from the calling skill:
1. The episode number to write
2. The project root directory path

## Execution

### Phase A: Load Base Package

Run these Bash commands to load context:

```bash
cd {project_root}
python {plugin_scripts}/outline_loader.py {episode_number}  # Get this episode's outline
python {plugin_scripts}/memory_manager.py summary           # Get all memory (character states, foreshadowing, costumes)
```

Then Read these files:
- `{project_root}/大纲/总纲.md`
- `{project_root}/设定集/世界观.md`
- `{project_root}/设定集/角色档案/` (all character cards for characters appearing in this episode)
- `{project_root}/设定集/场景档案/` (all scene cards for scenes in this episode)
- `{project_root}/设定集/视觉风格.md`
- `{project_root}/剧本/` (previous 3 episode scripts, if they exist)

### Phase B: On-Demand Deep Research

If the episode outline references side characters or specific rules, query them:
```bash
python {plugin_scripts}/character_manager.py get {character_name}
```

### Phase C: Cross-Episode Analysis

From the memory summary, identify:
1. **Open loops**: Which foreshadowing entries are still unresolved? This episode MUST either advance or resolve them.
2. **Character state continuity**: What was each character's emotional state and position at the end of the last episode?
3. **Costume continuity**: What is each character wearing? Only change outfits if there is a scene/time break or explicit reason.

### Phase D: Assemble Task Book

Output the following 5-section task book. Use Chinese. Do NOT include file paths, JSON, or meta-commentary.

---

**1. 前情回顾** (2-3 sentences)
What happened last episode that directly flows into this episode.

**2. 本集叙事任务**
- 本集目标: One sentence on what this episode must accomplish
- 节拍序列: List the beats from the outline, with any adjustments needed
- 必须覆盖的节点: From the outline's must-cover list
- 禁止区域: What must NOT happen (from character forbidden behaviors + creative constraints)

**3. 出场角色状态**
For each character appearing:
- Name, current emotional state entering this episode
- Their goal in this episode
- Speech tendencies (verbal tics, tone)
- Current outfit (from memory)
- Forbidden behaviors/words for THIS episode specifically

**4. 拍摄指导**
- 场景取景框策略: Per scene, what frame types are needed (must include at least 1 wide, 1 medium, 1 close-up per scene)
- 视觉风格要点: Color tone, lighting mood per scene
- ASCII空间布局要求: Each scene needs a spatial layout diagram
- 分镜流图要求: Each shot must track character position, facing direction, outfit continuity

**5. 结尾钩子**
What unresolved feeling or question should the audience be left with at the end of this episode.

---

## Rules

1. **Outline is law**: Do not contradict the episode outline. If something in the outline seems wrong, flag it but follow it.
2. **Setting is physics**: Characters cannot do things the world rules forbid.
3. **Memory is continuity**: Character states from memory MUST be respected as starting conditions.
4. **No AI clichés**: In your task book itself, avoid: 缓缓/微微/渐渐/悄然, reflective sentence endings, "little did he know" constructions.
5. **Chapter numbers always 4 digits**: 0001, 0002, ... 0099, 0100.
```

- [ ] **Step 2: Commit**

```bash
git add plugin/agents/context-agent.md
git commit -m "feat: add context-agent definition"
```

---

### Task 3.2: Create reviewer agent

**Files:**
- Create: `plugin/agents/reviewer.md`

- [ ] **Step 1: Write reviewer.md**

```markdown
---
name: reviewer
description: Unified review agent for drama episodes. Checks setting consistency, narrative coherence, character consistency, timeline, AI flavor, and shot continuity. Outputs structured issue list only.
tools: Read, Bash
model: inherit
---

You are a drama episode reviewer. You do NOT score, do NOT give overall evaluations, do NOT suggest plot changes. You ONLY find verifiable issues, provide evidence, and give fix direction.

## Input

You receive:
1. The episode script file path
2. The project root directory path

## Check Dimensions (in order)

For each dimension, Read the relevant source files, then Compare the episode content against them, then Judge if there's a contradiction.

### 1. Setting Consistency (category: setting)

Read: `设定集/世界观.md`, `设定集/视觉风格.md`

Check:
- Does any character action violate world rules?
- Does any scene description contradict the established world?
- Are visual style notes consistent with the genre's style inference?

### 2. Timeline (category: timeline)

Read: Previous episode script (if exists), `分集大纲.md`

Check:
- Does time connect logically to the previous episode?
- Is any character in two places at once?
- Are time-of-day markers consistent within the episode?

### 3. Narrative Coherence (category: continuity)

Read: Previous episode's ending, this episode's beginning

Check:
- Was the previous episode's hook/cliffhanger addressed?
- Do scene transitions make spatial sense?
- Is the emotional arc continuous (no jarring mood jumps)?

### 4. Character Consistency (category: character)

Read: All character cards in `设定集/角色档案/`

Check:
- Does each character's dialogue match their speech tendencies?
- Does behavior match motivation and personality?
- Are knowledge boundaries respected (character doesn't know things they shouldn't)?
- Are forbidden behaviors violated?

### 5. Logic (category: logic)

Check:
- Are causal chains valid (A causes B, not B happens because the plot needs it)?
- Are character decisions adequately motivated?
- Do any actions contradict established capabilities?

### 6. AI Flavor (category: ai_flavor)

Check FIVE sub-dimensions:

**Vocabulary**: High-frequency AI words:
- 缓缓, 微微, 渐渐, 轻轻, 淡淡, 悄然, 深邃, 璀璨, 无比
- "嘴角微微上扬/勾起一抹笑容"
- "眼中闪过一丝XX"
- "眸色一暗"

**Sentence Patterns**:
- 4-segment closed loops (cause → process → result → reflection)
- Same-structure sentences repeated 3+ times in sequence
- Paragraph-ending summary/reflection sentences (MUST flag as blocking)

**Narrative**:
- Uniform pacing with no rhythm variation
- "Little did he know..." type dramatic irony hints (MUST flag as blocking)
- "Safe landing" endings where all tension is resolved (MUST flag as blocking)
- Show-then-explain patterns

**Emotion**:
- Labeled emotions ("他感到愤怒") instead of behavioral implication
- Instant emotion switching with no transition
- All characters express emotions the same way

**Dialogue**:
- Information-preaching (characters say things they both already know)
- No colloquial features (everyone speaks in written language)
- Post-dialogue explanatory narration ("他的意思是...")

### 7. Shot Continuity (category: shot_continuity)

Read: The shot flow map JSON in `分镜/`

Check:
- Is character position physically reasonable across consecutive shots?
- Does any character's outfit change without explanation?
- Do facing directions match between reverse shots?
- Is the 180-degree rule violated?
- Do props remain consistent across shots?

## Output Format

Output ONLY a JSON object (no markdown, no explanation outside the JSON):

```json
{
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "setting|timeline|continuity|character|logic|ai_flavor|shot_continuity",
      "location": "场景X, 镜头SXX_FXX, paragraph N",
      "description": "specific issue description in Chinese",
      "evidence": "原文: '<quote>' vs 设定: '<reference>'",
      "fix_hint": "specific fix direction in Chinese",
      "blocking": true
    }
  ],
  "summary": "N issues: X blocking, Y high priority"
}
```

## Boundaries

- NO overall score or pass/fail judgment
- NO literary quality evaluation
- NO plot change suggestions
- Only report VERIFIABLE issues with specific evidence
- `blocking: true` means MUST fix before proceeding
```

- [ ] **Step 2: Commit**

```bash
git add plugin/agents/reviewer.md
git commit -m "feat: add reviewer agent definition"
```

---

### Task 3.3: Create data-agent & deconstruction-agent

**Files:**
- Create: `plugin/agents/data-agent.md`
- Create: `plugin/agents/deconstruction-agent.md`

- [ ] **Step 1: Write data-agent.md**

```markdown
---
name: data-agent
description: Extracts structured facts from finalized episode scripts. Generates memory deltas for cross-episode consistency.
tools: Read, Bash
model: inherit
---

You extract structured information from finalized drama episode scripts. You do NOT write files directly — you output JSON that the calling skill's scripts will write.

## Input

You receive:
1. The finalized episode script file path
2. The project root directory path

## Execution

### Phase A: Load Context

Read the episode script and run:
```bash
python {plugin_scripts}/memory_manager.py summary
```

This gives you the BEFORE state for comparison.

### Phase B: Extract

Read the episode and extract:

1. **Character state deltas**: For each character appearing, what changed?
   - Emotional state (before → after)
   - Physical position (start → end of episode)
   - Relationship changes
   - New abilities or knowledge gained

2. **Scene changes**: For each scene used:
   - Props added/removed/moved
   - Any permanent changes to the scene (damage, renovation, etc.)

3. **Foreshadowing operations**:
   - New foreshadowing planted in this episode
   - Existing foreshadowing advanced (but not resolved)
   - Existing foreshadowing resolved (with resolution details)

4. **Costume tracking**:
   - What is each character wearing at the END of the episode?
   - Did any costume change occur? If so, what triggered it?

5. **Appeared entities**: All characters, locations, and significant props mentioned

### Phase C: Output

Output ONLY this JSON (no markdown, no explanation):

```json
{
  "character_states": [
    {
      "character": "角色名",
      "state": {
        "emotional": "当前情绪",
        "position": "当前所在位置",
        "goal": "当前目标",
        "relationships": {}
      },
      "changes": ["变化描述1", "变化描述2"]
    }
  ],
  "scene_changes": [
    {
      "scene": "场景名",
      "changes": {
        "props_added": [],
        "props_removed": [],
        "permanent_changes": []
      }
    }
  ],
  "foreshadowing": [
    {
      "id": "FSH_0001_003",
      "content": "伏笔内容",
      "planted_in": "0001",
      "status": "active|advanced|resolved",
      "resolved_in": null,
      "resolution": null
    }
  ],
  "costume_updates": {
    "角色名": {
      "outfit": "当前服装描述",
      "episode": "0001"
    }
  },
  "entities_appeared": {
    "characters": [],
    "locations": [],
    "props": []
  },
  "episode_summary": "100-150 word summary in Chinese, including hook type used at the end"
}
```

## Rules

1. Only report VERIFIABLE changes that appear in the text
2. Emotional state descriptions should be behavioral, not label-based ("紧握的拳头微微发抖" not "愤怒")
3. Costume changes must have a trigger (scene change, time jump, explicit action)
4. Foreshadowing IDs follow format: FSH_{first_appearance_episode}_{sequence}
5. If a character does not appear in this episode, do NOT include them in character_states
```

- [ ] **Step 2: Write deconstruction-agent.md**

```markdown
---
name: deconstruction-agent
description: Reference drama/film deconstruction agent. Extracts transferable craft patterns from reference works without contaminating the project's story canon.
tools: Read, Bash
model: inherit
---

You analyze reference short dramas or film clips to extract transferable craft patterns. You NEVER write to project files. You output ONLY abstract patterns — no specific character names, locations, or plot events from the source material.

## Input

You receive:
1. Reference material text (provided directly in the prompt by the calling skill)
2. Optional: specific aspects to focus on (shot composition, pacing, character dynamics, etc.)

## Output

Output ONLY this JSON:

```json
{
  "source_type": "short_drama|film|novel|other",
  "analysis_mode": "quick|deep",
  "patterns": {
    "shot_composition": [
      {
        "pattern_name": "pattern label",
        "description": "abstract description (no specific names/places)",
        "when_to_use": "narrative situations where this pattern works",
        "example_abstraction": "genericized example"
      }
    ],
    "pacing": [
      {
        "rhythm_name": "rhythm label",
        "structure": "abstract structure description",
        "emotion_curve": "how emotion rises and falls",
        "applicable_genres": []
      }
    ],
    "character_dynamics": [
      {
        "dynamic_type": "type of interaction",
        "pattern": "abstract interaction pattern",
        "why_it_works": "psychological/叙事 reason"
      }
    ],
    "cool_point_loops": [
      {
        "loop_name": "loop label",
        "setup_phase": "abstract setup",
        "payoff_phase": "abstract payoff",
        "cycle_length_episodes": 0
      }
    ],
    "borrowable_structures": [
      "Abstract structural idea 1",
      "Abstract structural idea 2"
    ]
  },
  "do_not_copy": [
    "Specific element that should NOT be copied (character type, plot twist, etc.)"
  ],
  "quality": {
    "confidence": 0.85,
    "coverage": 0.85
  }
}
```

## Hard Rules

1. NEVER include original character names, place names, organization names, or specific ability names
2. Abstract ALL specific events into pattern descriptions
3. If the source material is insufficient for confident extraction, set confidence < 0.7
4. Do NOT create any files — you are a pure analysis agent
```

- [ ] **Step 3: Commit**

```bash
git add plugin/agents/data-agent.md plugin/agents/deconstruction-agent.md
git commit -m "feat: add data-agent and deconstruction-agent definitions"
```

---

## Phase 4: Skill Definitions

### Task 4.1: Create drama-init SKILL.md

**Files:**
- Create: `plugin/skills/drama-init/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: drama-init
description: Deep initialization of short drama projects. Collects creative info through interactive dialogue, generates project skeleton with worldbuilding, character profiles, and visual style ready for planning.
allowed-tools: Read Write Edit Bash AskUserQuestion Agent
---

Initialize a new short drama project. Gather creative direction through structured questioning, then generate the complete project skeleton.

## Project Root

Ask the user for the project directory or use current working directory. Run:
```bash
python {PLUGIN_SCRIPTS}/project_init.py "<Project Title>"
```
where `{PLUGIN_SCRIPTS}` is the `scripts/` directory of this plugin.

## Workflow

### Step 1: Story Core & Commercial Positioning

Ask the user (use AskUserQuestion, one at a time):

1. **选题方向**: What type of story? Offer the 6 genre options + "Other"
   - 都市爽文 / 古装剧 / 甜宠 / 家庭伦理 / 复仇逆袭 / 悬疑

2. **一句话梗概**: Ask user to describe the story in one sentence.

3. **目标平台**: 抖音 / 快手 / 微短剧小程序 / 其他

4. **目标量级**: How many episodes total? (Default: 100)

### Step 2: Character Skeleton

Ask about:
1. **主角**: Name, core desire, core flaw. What makes them compelling?
2. **反派结构**: Single antagonist or layered (跳脸小丑 → 地方势力 → 主要对手 → 幕后黑手)?
3. **关键配角**: Key supporting characters and their relationship to the protagonist.

### Step 3: Worldbuilding

Ask about:
1. **世界观类型**: Modern urban? Ancient架空? Near future?
2. **特殊规则**: Any special rules or power systems?
3. **核心冲突**: What drives the central conflict?

### Step 4: Creative Constraints

Ask about:
1. **卖点**: What's the unique hook? (one sentence)
2. **反套路**: Any tropes to deliberately AVOID?
3. **硬约束**: Any hard constraints (e.g., no romantic subplot, no character deaths before episode 50)?

### Step 5: Visual Style Reference

Ask:
1. **视觉参考**: Any reference dramas/films for visual style?
2. **色调偏好**: Cold tones? Warm tones? High contrast? Natural?

### Step 6: Generate Project Files

Based on all collected information, generate these files using the Write tool:

1. `{project_root}/设定集/世界观.md` — from `templates/world-setting.md`
2. `{project_root}/设定集/视觉风格.md` — from style inference + user preferences
3. `{project_root}/设定集/角色档案/主角-{name}.md` — from `templates/character-card.md`
4. `{project_root}/设定集/角色档案/反派-{name}.md`
5. Character cards for key supporting characters
6. `{project_root}/大纲/总纲.md` — from `templates/master-outline.md`

### Step 7: Review & Confirm

Present a summary of everything generated. Ask user to confirm before proceeding.

## Sufficiency Gate (6 conditions — ALL must pass before generation)

1. [ ] 选题方向明确
2. [ ] 主角核心欲望+缺陷清晰
3. [ ] 反派结构有层次
4. [ ] 世界观有至少1条特殊规则
5. [ ] 一句话卖点存在
6. [ ] 视觉风格有明确参考

## Reference Deconstruction (Optional)

If the user wants to analyze reference works, delegate to `short-drama-writer:deconstruction-agent` via the Agent tool:

```
Agent(
  subagent_type: "short-drama-writer:deconstruction-agent",
  prompt: "Analyze this reference: <text>"
)
```

Apply extracted patterns to the creative constraints, NOT as direct copies.
```

- [ ] **Step 2: Commit**

```bash
git add plugin/skills/drama-init/SKILL.md
git commit -m "feat: add drama-init skill definition"
```

---

### Task 4.2: Create drama-plan SKILL.md

**Files:**
- Create: `plugin/skills/drama-plan/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: drama-plan
description: Generates episode outlines based on the master outline. Breaks the series into episodes with emotion curves, beats, and scene briefs. Writes new settings incrementally back to existing setting files.
allowed-tools: Read Write Edit Bash Agent
---

Generate the episode-by-episode outline based on the master outline and creative constraints.

## Prerequisites

- Master outline exists at `大纲/总纲.md`
- World setting exists at `设定集/世界观.md`
- Character profiles exist in `设定集/角色档案/`

Run preflight:
```bash
python {PLUGIN_SCRIPTS}/state_manager.py get
```

## Workflow

### Step 1: Load Context

Read:
- `大纲/总纲.md`
- `设定集/世界观.md`
- All files in `设定集/角色档案/`
- `设定集/视觉风格.md`

### Step 2: Fill Setting Baseline (Incremental)

If any character cards or world settings are incomplete, fill them NOW before generating outlines. This ensures outlines reference complete information.

### Step 3: Volume Planning

Divide the series into volumes (~10 episodes each). For each volume:
- Core conflict for this volume
- Which antagonist tier is active
- Protagonist's stage in their character arc

Write to `大纲/卷规划.md`.

### Step 4: Generate Episode Outline

For each episode, write to `大纲/分集大纲.md` following `templates/episode-outline.md`. Each episode must have:

- 情绪基调 (emotional tone)
- 时长分配 (timing breakdown)
- 情绪曲线 (emotion curve)
- 节拍序列 (beat sequence: hook → development → climax → new hook)
- 场景梗概 (scene briefs with location, characters, core event, frame count)
- 出场角色状态 (character states entering and leaving)
- 伏笔操作 (foreshadowing operations)

### Constraints

1. **Emotion curve variety**: No two consecutive episodes should end on the same emotional peak type
2. **Scene variety**: Each episode should have 2-4 scenes; avoid single-scene episodes
3. **Frame requirement**: Each scene needs 3-5 shot frames (at least 1 wide + 1 medium + 1 close-up)
4. **Hook requirement**: Every episode must end with a hook (immediate suspense, medium mystery, or emotional cliffhanger)
5. **Genre-specific pacing**: Follow the rhythm template from the relevant genre knowledge base

### Step 5: Validate & Save

Validate:
- [ ] All episodes have beat sequences
- [ ] All episodes have time fields  
- [ ] All episodes have character state entries
- [ ] Hooks exist for every episode
- [ ] No BLOCKER-level contradictions with settings

Update state:
```bash
python {PLUGIN_SCRIPTS}/state_manager.py update phase plan
python {PLUGIN_SCRIPTS}/state_manager.py update total_episodes <N>
```
```

- [ ] **Step 2: Commit**

```bash
git add plugin/skills/drama-plan/SKILL.md
git commit -m "feat: add drama-plan skill definition"
```

---

### Task 4.3: Create drama-write SKILL.md

**Files:**
- Create: `plugin/skills/drama-write/SKILL.md`

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: drama-write
description: Produces a single episode script. Full execution: context research → draft → review → polish → submit. Includes shot flow map and ASCII spatial layout generation.
allowed-tools: Read Write Edit Bash Agent
---

Produce one episode script with full shot flow map and spatial layout. This is the core creative pipeline.

## Modes

| Mode | Flow |
|------|------|
| Default | Steps 1-2-3-4-5 |
| `--fast` | Steps 1-2-3(light check only)-4-5 |
| `--minimal` | Steps 1-2-4(format fix only)-5 |

## Workflow

### Preflight

Determine episode number (ask user or read current state):
```bash
python {PLUGIN_SCRIPTS}/state_manager.py get
```

### Step 1: Context Research (context-agent)

**MUST delegate to `short-drama-writer:context-agent` via Agent tool.**

```
Agent(
  subagent_type: "short-drama-writer:context-agent",
  prompt: "Episode {episode_number}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

The context-agent outputs a 5-section writing task book. This becomes the creative brief for Step 2.

### Step 2: Draft

Write the episode script following `templates/episode-script.md`. The draft must include:

**For each scene:**
1. Scene header (location, time, characters)
2. ASCII spatial layout diagram
3. Shot flow map (3-5 shots with position/facing/outfit tracking)

**For each shot:**
1. Frame type (WIDE/MS/CU/ECU)
2. Visual description
3. Character position table (position, position_change, facing, outfit)
4. Action description
5. Dialogue (if any)
6. Continuity note (how it connects to the previous shot)

**Writing rules:**
- Show emotion through behavior, not labels
- No AI cliché words (缓缓, 微微, 渐渐, 悄然, 深邃, 璀璨)
- No paragraph-ending reflective/总结 sentences
- No "殊不知/little did he know" constructions
- End each scene with a mini-hook that pushes to the next scene
- End the episode with the hook specified in the task book

Save the draft to `剧本/第{episode_number}集-{title}.md`.

Save the shot flow map to `分镜/第{episode_number}集-分镜.json`.

### Step 3: Review (reviewer agent)

**MUST delegate to `short-drama-writer:reviewer` via Agent tool.**

```
Agent(
  subagent_type: "short-drama-writer:reviewer",
  prompt: "Review episode script: {script_path}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

The reviewer outputs a JSON issue list. Save raw review:
```bash
python {PLUGIN_SCRIPTS}/review_saver.py save {episode_number} '<review_json>'
```

**Blocking gate:** If any issue has `blocking: true`, the draft MUST return to Step 2 for fixes. Non-blocking issues can be handled in Step 4.

### Step 4: Polish

Address all non-blocking issues from review:
1. Fix AI-flavor issues (apply `references/ai-flavor-checklist.md`)
2. Verify shot continuity (apply `references/cinematic-rules.md`)
3. Check dialogue authenticity (apply genre-specific dialogue guide)
4. Format consistency (ensure template structure is clean)

### Step 5: Submit

**5.1 Data Extraction** — delegate to `short-drama-writer:data-agent`:
```
Agent(
  subagent_type: "short-drama-writer:data-agent",
  prompt: "Extract data from: {script_path}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

**5.2 Commit** — run the commit script with the data-agent output:
```bash
python {PLUGIN_SCRIPTS}/chapter_commit.py {episode_number}
```

Then manually update memory files using the data-agent JSON output via Python scripts.

**5.3 Sufficiency Gate:**
- [ ] Episode script file exists at `剧本/第{episode_number}集-*.md`
- [ ] Shot flow map JSON exists at `分镜/第{episode_number}集-分镜.json`
- [ ] Review report exists at `审查报告/第{episode_number}集审查报告.md`
- [ ] ALL blocking issues resolved
- [ ] Memory files updated
```

- [ ] **Step 2: Commit**

```bash
git add plugin/skills/drama-write/SKILL.md
git commit -m "feat: add drama-write skill definition"
```

---

### Task 4.4: Create drama-review, drama-generate, drama-query, drama-dashboard SKILL.md

**Files:**
- Create: `plugin/skills/drama-review/SKILL.md`
- Create: `plugin/skills/drama-generate/SKILL.md`
- Create: `plugin/skills/drama-query/SKILL.md`
- Create: `plugin/skills/drama-dashboard/SKILL.md`

- [ ] **Step 1: Write drama-review/SKILL.md**

```markdown
---
name: drama-review
description: Uses the reviewer agent to evaluate episode quality. Generates structured review reports.
allowed-tools: Read Bash Agent AskUserQuestion
---

Review a specific episode's quality using the reviewer agent.

## Workflow

### Step 1: Determine Target Episode

Ask user which episode to review, or read current state:
```bash
python {PLUGIN_SCRIPTS}/state_manager.py get
```

### Step 2: Load References

Read:
- `references/cinematic-rules.md`
- `references/ai-flavor-checklist.md`
- `references/shot-composition.md`
- The relevant genre knowledge files from `genres/`

### Step 3: Call Reviewer Agent

```
Agent(
  subagent_type: "short-drama-writer:reviewer",
  prompt: "Review: {script_path}, project root: {project_root}, plugin scripts: {PLUGIN_SCRIPTS}"
)
```

### Step 4: Generate Report

Save the review:
```bash
python {PLUGIN_SCRIPTS}/review_saver.py save {episode_number} '<review_json>'
```

### Step 5: Handle Blocking Issues

If blocking issues exist, ask user via AskUserQuestion:
- Fix now (return to drama-write)
- Save for later (continue to next episode)

### Step 6: Update State

```bash
python {PLUGIN_SCRIPTS}/state_manager.py update stats.episodes_reviewed <N>
```
```

- [ ] **Step 2: Write drama-generate/SKILL.md**

```markdown
---
name: drama-generate
description: Reads prompt JSON files and calls backend API to generate character reference images, scene images, and shot videos.
allowed-tools: Read Bash
---

Generate visual assets by calling the backend API with prepared prompt JSON files.

## Workflow

### Step 1: Determine Scope

Ask user what to generate:
- Character reference images only
- Scene reference images only
- Shot videos only
- Full pipeline (characters → scenes → videos)

### Step 2: Load Prompts

Read the relevant prompt JSON files from `提示词/`.

### Step 3: Generate Character Images

For each character prompt file:
```bash
curl -X POST {BACKEND_URL}/api/generate/image \
  -H "Content-Type: application/json" \
  -d @提示词/{episode}-角色图提示词.json
```

Save returned asset references to `素材/角色/`.

### Step 4: Generate Scene Images

For each scene prompt file:
```bash
curl -X POST {BACKEND_URL}/api/generate/image \
  -H "Content-Type: application/json" \
  -d @提示词/{episode}-场景图提示词.json
```

### Step 5: Generate Shot Videos

For each shot in the video prompt file:
```bash
curl -X POST {BACKEND_URL}/api/generate/video \
  -H "Content-Type: application/json" \
  -d '<shot_prompt_json>'
```

Poll status:
```bash
curl {BACKEND_URL}/api/generate/status/{task_id}
```

Save completed video references to `素材/视频/`.

### Step 6: Update State

```bash
python {PLUGIN_SCRIPTS}/state_manager.py update stats.shots_generated <N>
```
```

- [ ] **Step 3: Write drama-query/SKILL.md**

```markdown
---
name: drama-query
description: Queries project settings, characters, scene profiles, episode states, and foreshadowing status.
allowed-tools: Read Bash
---

Query any aspect of the current drama project.

## Query Types

### Character Query
```bash
python {PLUGIN_SCRIPTS}/character_manager.py list
python {PLUGIN_SCRIPTS}/character_manager.py get <name>
```

### Episode Query
```bash
python {PLUGIN_SCRIPTS}/outline_loader.py <episode_number>
```

### Memory Query
```bash
python {PLUGIN_SCRIPTS}/memory_manager.py summary
python {PLUGIN_SCRIPTS}/memory_manager.py character_state
python {PLUGIN_SCRIPTS}/memory_manager.py foreshadowing
```

### State Query
```bash
python {PLUGIN_SCRIPTS}/state_manager.py get
```

### Review Query
```bash
python {PLUGIN_SCRIPTS}/review_saver.py get <episode_number>
```

## Output

Present results in structured markdown. For foreshadowing, highlight:
- URGENT: Active foreshadowing with approaching deadline
- OVERDUE: Foreshadowing past its expected resolution episode
```

- [ ] **Step 4: Write drama-dashboard/SKILL.md**

```markdown
---
name: drama-dashboard
description: Starts a read-only web dashboard to view project status, episode content, asset gallery, and character relationship graphs.
allowed-tools: Bash
---

Launch the read-only drama project dashboard.

## Workflow

### Step 1: Verify Backend

Check backend is running:
```bash
curl {BACKEND_URL}/api/health
```

If not running, start it:
```bash
cd {BACKEND_DIR} && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
```

### Step 2: Launch Dashboard

```bash
cd {BACKEND_DIR}/dashboard && npm run dev
```

The dashboard is a read-only React app that:
- Shows project overview (episodes written, assets generated)
- Displays character relationship graph
- Shows episode list with scene and shot breakdowns
- Previews generated images and videos
- Allows marking assets for regeneration (returns to Claude for execution)

### Step 3: Open Browser

Tell user to open `http://localhost:5173` (or the port shown in terminal output).
```

- [ ] **Step 5: Commit**

```bash
git add plugin/skills/drama-review/ plugin/skills/drama-generate/ plugin/skills/drama-query/ plugin/skills/drama-dashboard/
git commit -m "feat: add drama-review, drama-generate, drama-query, drama-dashboard skill definitions"
```

---

## Phase 5: Lightweight Backend

### Task 5.1: Create backend scaffold

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/requirements.txt`

- [ ] **Step 1: Write config.py**

```python
"""Backend configuration."""

import os


class Config:
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "short_drama")
    DATABASE_URL: str = (
        f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

    JIMENG_API_KEY: str = os.getenv("JIMENG_API_KEY", "")
    JIMENG_API_SECRET: str = os.getenv("JIMENG_API_SECRET", "")
    MINIMAX_API_KEY: str = os.getenv("MINIMAX_API_KEY", "")
    DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "")

    TOS_ACCESS_KEY: str = os.getenv("TOS_ACCESS_KEY", "")
    TOS_SECRET_KEY: str = os.getenv("TOS_SECRET_KEY", "")
    TOS_BUCKET: str = os.getenv("TOS_BUCKET", "")
    TOS_ENDPOINT: str = os.getenv("TOS_ENDPOINT", "")

    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "./storage")


config = Config()
```

- [ ] **Step 2: Write main.py**

```python
"""FastAPI application entry."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="short-drama-writer Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

- [ ] **Step 3: Write requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
aiomysql==0.2.0
httpx==0.27.0
pydantic==2.9.0
python-multipart==0.0.9
volcengine-python-sdk==1.0.0
```

- [ ] **Step 4: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend with FastAPI app"
```

---

### Task 5.2: Create MySQL models

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/base.py`

- [ ] **Step 1: Write base.py**

```python
"""SQLAlchemy models for MySQL."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON, ForeignKey, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship

from ..config import config

engine = create_engine(
    config.DATABASE_URL.replace("+aiomysql", "+pymysql"),
    echo=False,
    pool_pre_ping=True,
)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    genre = Column(String(50), nullable=False)
    sub_genre = Column(String(50), default="")
    platform = Column(String(50), default="")
    total_episodes = Column(Integer, default=100)
    episode_duration_min = Column(Integer, default=1)
    episode_duration_max = Column(Integer, default=3)
    local_path = Column(String(500), nullable=False, comment="Path to project directory")
    phase = Column(String(20), default="init")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    episodes = relationship("Episode", back_populates="project")
    assets = relationship("Asset", back_populates="project")


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    episode_number = Column(Integer, nullable=False)
    title = Column(String(200), default="")
    emotion_tone = Column(String(100), default="")
    scenes_count = Column(Integer, default=0)
    shots_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft | reviewed | final
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="episodes")
    assets = relationship("Asset", back_populates="episode")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=True, index=True)
    asset_type = Column(String(20), nullable=False)  # character_image | scene_image | video
    name = Column(String(200), nullable=False)
    file_path = Column(String(500), default="")
    external_url = Column(String(1000), default="")
    provider = Column(String(50), default="")
    prompt_json = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="assets")
    episode = relationship("Episode", back_populates="assets")


def init_db():
    Base.metadata.create_all(engine)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add MySQL models (Project, Episode, Asset)"
```

---

### Task 5.3: Create API proxy layer

**Files:**
- Create: `backend/app/providers/__init__.py`
- Create: `backend/app/providers/base.py`
- Create: `backend/app/providers/jimeng.py`

- [ ] **Step 1: Write base.py**

```python
"""Base provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class GenerateResult:
    task_id: str
    status: str  # pending | processing | done | failed
    file_url: str | None = None
    file_path: str | None = None
    error: str | None = None


class ImageProvider(ABC):
    @abstractmethod
    async def generate_image(self, prompt: dict) -> GenerateResult:
        ...

    @abstractmethod
    async def get_status(self, task_id: str) -> GenerateResult:
        ...


class VideoProvider(ABC):
    @abstractmethod
    async def generate_video(self, prompt: dict) -> GenerateResult:
        ...

    @abstractmethod
    async def get_status(self, task_id: str) -> GenerateResult:
        ...
```

- [ ] **Step 2: Write jimeng.py (stub with real API structure)**

```python
"""Jimeng 4.6 image generation provider."""

import httpx
from .base import ImageProvider, GenerateResult


class JimengProvider(ImageProvider):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://visual.volcengineapi.com"

    async def generate_image(self, prompt: dict) -> GenerateResult:
        positive = prompt.get("positive", "")
        negative = prompt.get("negative", "")
        width = prompt.get("width", 1080)
        height = prompt.get("height", 1920)

        payload = {
            "req_key": "jimeng_highres_v46",
            "prompt": positive,
            "negative_prompt": negative,
            "width": width,
            "height": height,
            "return_url": True,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/submit",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            data = resp.json()
            if data.get("code") != 10000:
                return GenerateResult(
                    task_id="", status="failed", error=data.get("message", "Unknown error")
                )
            return GenerateResult(
                task_id=data.get("data", {}).get("task_id", ""),
                status="pending",
            )

    async def get_status(self, task_id: str) -> GenerateResult:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/query",
                json={"req_key": "jimeng_highres_v46", "task_id": task_id},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            data = resp.json()
            if data.get("code") != 10000:
                return GenerateResult(task_id=task_id, status="failed", error=data.get("message"))
            status = data.get("data", {}).get("status", "unknown")
            file_url = data.get("data", {}).get("image_urls", [None])[0]
            return GenerateResult(
                task_id=task_id,
                status=status,
                file_url=file_url,
            )
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/providers/
git commit -m "feat: add API proxy layer (base + Jimeng provider)"
```

---

### Task 5.4: Create API routes

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/generate.py`
- Create: `backend/app/api/projects.py`

- [ ] **Step 1: Write generate.py**

```python
"""Asset generation API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/generate", tags=["generate"])


class ImageGenerateRequest(BaseModel):
    provider: str = "jimeng"
    prompt: dict


class VideoGenerateRequest(BaseModel):
    provider: str = "seedance"
    prompt: dict


@router.post("/image")
async def generate_image(req: ImageGenerateRequest):
    """Submit an image generation task."""
    if req.provider == "jimeng":
        from ..providers.jimeng import JimengProvider
        from ..config import config
        provider = JimengProvider(config.JIMENG_API_KEY, config.JIMENG_API_SECRET)
        result = await provider.generate_image(req.prompt)
        return {"task_id": result.task_id, "status": result.status}
    raise HTTPException(400, f"Unknown provider: {req.provider}")


@router.post("/video")
async def generate_video(req: VideoGenerateRequest):
    """Submit a video generation task."""
    # Stub — real implementation follows same pattern as image
    return {"task_id": "stub", "status": "pending"}


@router.get("/status/{task_id}")
async def get_status(task_id: str, provider: str = "jimeng"):
    """Query generation task status."""
    if provider == "jimeng":
        from ..providers.jimeng import JimengProvider
        from ..config import config
        p = JimengProvider(config.JIMENG_API_KEY, config.JIMENG_API_SECRET)
        result = await p.get_status(task_id)
        return {
            "task_id": result.task_id,
            "status": result.status,
            "file_url": result.file_url,
            "error": result.error,
        }
    return {"task_id": task_id, "status": "unknown"}
```

- [ ] **Step 2: Write projects.py**

```python
"""Project management API routes (stub — full CRUD to be fleshed out)."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/")
async def list_projects():
    return {"projects": []}


@router.get("/{project_id}")
async def get_project(project_id: int):
    return {"id": project_id, "title": "stub"}
```

- [ ] **Step 3: Register routes in main.py**

In `backend/app/main.py`, add after creating app:

```python
from .api import generate, projects

app.include_router(generate.router)
app.include_router(projects.router)
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/ backend/app/main.py
git commit -m "feat: add API routes (generate, projects)"
```

---

## Phase 6: Wire Everything Together

### Task 6.1: Create CLAUDE.md for the plugin project

**Files:**
- Create: `d:\PersonalFiles\Project_Space\short-drama-writer\CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add project CLAUDE.md"
```

---

### Task 6.2: Create global plugin registry entry

- [ ] **Step 1: Register plugin**

Create the symlink or registry entry so Claude Code discovers the plugin:

```bash
mkdir -p "$HOME/.claude/plugins/cache/short-drama-writer-marketplace/short-drama-writer/0.1.0"
# Copy or symlink plugin directory to registry
```

(Exact registration mechanism depends on Claude Code plugin loading — document as needed.)

---

## Execution Notes

### Plugin Script Path

All SKILL.md files use `{PLUGIN_SCRIPTS}` as a placeholder. At runtime, resolve to the plugin's `scripts/` directory via the plugin's installation path.

### Project Root Resolution

All Python scripts resolve the project root by walking up from `cwd` to find `.drama/state.json`.

### Genre Knowledge Loading

Skills should load genre knowledge on-demand (not all at once) to avoid context overflow. The `drama-init` skill loads the selected genre's files. The `drama-write` skill loads the relevant genre + shared references.

### Backend URL

The backend URL is configured via environment variable `DRAMA_BACKEND_URL` (default: `http://localhost:8001`).

---

## Remaining Work (Future Phases)

The following items in the design spec are deferred to subsequent iterations:

- **P4.1**: drama-generate full implementation (video generation flow with Seedance)
- **P4.2**: Dashboard frontend (React app for asset preview, character graphs)
- **P5.1**: ASCII layout → 2D wireframe renderer (backend)
- **P5.2**: Multi-modal prompt embedding (wireframe + text → video API)
- **Backend completion**: Full CRUD for all API endpoints, export module, asset management with TOS
- **Tests**: Unit tests for Python scripts, integration tests for API proxy
