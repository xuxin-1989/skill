# WorkBuddy Skills Collection

个人 WorkBuddy AI 助手技能集，涵盖文档处理、数据分析、图片识别、自我优化等场景。

## 技能列表

### 数据处理

| Skill | 说明 |
|-------|------|
| **excel-data-extractor** | Excel 数据提取与图文处理，支持 SenseNova Vision API 图片识别。适用于农业补贴、批量表格分析、字段提取等 |
| **sn-da-image-caption** | 图片理解与数据提取，将图表/表格/截图转为结构化 DataFrame，支持导出 Excel/CSV |

### 文档处理

| Skill | 说明 |
|-------|------|
| **document-format-skills** | 公文格式处理：诊断格式问题、修复中英文标点混用、统一格式规范 |
| **Word / DOCX** | Microsoft Word 文档创建与编辑，处理样式、编号、修订、表格、分节等 |
| **tencent-docs** | 腾讯文档全功能：创建/编辑/管理在线文档、智能表、空间、文件管理 |

### AI 进化与优化

| Skill | 说明 |
|-------|------|
| **darwin-skill** | 自主 Skill 优化器，基于 Microsoft Research SkillLens 9 维评估体系 + SkillOpt 验证门控，自动评分并改进 SKILL.md |
| **capability-evolver** | Skill 能力持续进化引擎，分析使用模式，生成结构化优化建议 |
| **self-reflection** | 结构化自我反思，记录错误和经验教训，追踪改进趋势 |

### 安全与运维

| Skill | 说明 |
|-------|------|
| **skill-vetter** | 安全优先的 Skill 审查工具，安装前检查红旗信号、权限范围、可疑模式 |
| **auto-updater** | 自动更新 WorkBuddy 和所有已安装 skills，每日检查并报告 |
| **proactive-agent** | 将 AI Agent 从被动执行者转变为主动协作伙伴，含 WAL 协议、Working Buffer 等模式 |

### 工具集成

| Skill | 说明 |
|-------|------|
| **agent-memory** | AI Agent 持久化记忆系统，跨会话记忆事实、学习经验、追踪实体 |
| **ima-skills** | IMA 知识库与笔记管理，支持知识搜索、文件上传、笔记编辑 |

## 目录结构

```
skills/
├── agent-memory/          # AI 记忆系统 (Python)
├── auto-updater/          # 自动更新
├── capability-evolver/    # 能力进化引擎 (JS)
├── darwin-skill/          # Skill 优化器 (HTML/JS)
├── document-format-skills/# 公文格式处理 (Python)
├── excel-data-extractor/  # Excel 数据提取 (Python)
├── ima-skills/            # IMA 知识库 (JS)
├── proactive-agent/       # 主动协作代理
├── self-reflection/       # 自我反思
├── skill-vetter/          # Skill 安全审查
├── sn-da-image-caption/   # 图片理解 (Python)
├── tencent-docs/          # 腾讯文档
└── word-docx/             # Word 文档编辑
```

## 使用方式

在 WorkBuddy 中输入对应的触发词即可自动加载对应技能。

## 环境

- **平台**: WorkBuddy Desktop Client
- **Python**: 3.13+
- **Node.js**: 22+
