---
name: capability-evolver
description: "Skill 能力持续进化引擎。分析 runtime 历史和 skill 使用模式，识别改进机会，生成结构化优化建议。触发词：能力进化、skill 优化分析、分析 skill 使用、evolution analysis、improve capabilities、skill health check。"
---

# Capability Evolver

分析已安装 skills 的使用历史和结构质量，自动识别改进机会，生成可执行的优化建议。

## ⛔ 反例与黑名单

以下操作**禁止**执行：

| 禁止操作 | 原因 |
|----------|------|
| 未经用户确认直接修改任何 SKILL.md | 进化建议需要人工审核 |
| 基于单次使用数据做判断 | 样本不足导致误判 |
| 删除用户手动创建的文件或配置 | 可能破坏用户自定义设置 |
| 在无 git 仓库的目录执行 git 操作 | 无法回滚 |
| 修改 darwin-skill 自身的 SKILL.md | 评估工具不应自我修改 |
| 基于不完整的 skill 列表做全量分析 | 先确认已扫描所有 skills |
| 输出模糊的"建议优化"而不给具体方案 | 进化建议必须可执行 |

---

## 🔴 CHECKPOINT 1: 确认分析范围

**分析前必须确认：**

```
分析模式:
  [1] 单 skill 深度分析 — 指定一个 skill，全面分析其质量
  [2] 全量 skills 扫描   — 扫描所有已安装 skills，排名并标记最需改进的
  [3] 使用历史分析       — 基于 conversation history 分析 skill 使用频率和效果

当前模式: {mode}
目标 skill(s): {targets}
是否继续？[需要用户确认]
```

```
如果用户未指定模式 → 提示选择 [1]/[2]/[3]
如果目标 skill 不存在 → 列出可用 skills 让用户选择
```

---

## 步骤 1: 收集数据

### 1.1 扫描已安装 skills

```bash
find ~/.workbuddy/skills -name "SKILL.md" -maxdepth 2 2>/dev/null | sort
```

### 1.2 提取每个 skill 的关键指标

对每个 SKILL.md 提取：

| 指标 | 提取方法 |
|------|----------|
| 文件大小 | `wc -l` 行数 |
| Frontmatter 完整性 | 检查 name/description 是否存在 |
| 工作流步骤 | `grep -cE '^#{1,3}\s+(步骤|Step|Phase|Stage)'` |
| 检查点数量 | `grep -cE '(CHECKPOINT|🔴|⛔)'` |
| 反例数量 | `grep -cE '(禁止|不要|Don.t|NEVER|MUST NOT)'` |
| 失败分支 | `grep -cE '(如果.*失败|if.*fail|fallback|回退|rollback)'` |

### 1.3 失败分支

```
如果 find 命令失败 → 检查 ~/.workbuddy/skills/ 目录是否存在
如果目录为空     → 标记 NO_SKILLS_FOUND，结束分析
如果 SKILL.md 不可读 → 标记该 skill 为 UNREADABLE，跳过
如果 grep 在 Windows 上编码异常 → 使用 PowerShell: Select-String -Pattern
```

---

## 🔴 CHECKPOINT 2: 数据验证

```
已扫描 {count} 个 skills:
{skill_name}: {lines}行, 工作流{steps}步, 检查点{checkpoints}个, 反例{antipatterns}条

数据完整？[需要用户确认继续分析]
```

---

## 步骤 2: 质量评分

### 2.1 评分维度（简化版，聚焦实用性）

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 结构完整性 | 20 | Frontmatter + 工作流 + 章节层次 |
| 可执行性 | 25 | 有具体命令/参数/示例，无模糊措辞 |
| 健壮性 | 20 | 失败模式编码、回退路径 |
| 安全性 | 15 | 检查点设计、反例黑名单 |
| 可维护性 | 20 | 文件大小合理、无冗余、路径可达 |

### 2.2 评分输出

```
=== {skill_name} ===
结构完整性: X/20 — {具体问题}
可执行性:   X/25 — {具体问题}
健壮性:     X/20 — {具体问题}
安全性:     X/15 — {具体问题}
可维护性:   X/20 — {具体问题}
总分: XX/100 — {评级}

Top 3 改进点:
  1. [高优先级] {具体建议，包含修改位置和方案}
  2. [中优先级] {具体建议}
  3. [低优先级] {具体建议}
```

### 2.3 失败分支

```
如果 skill 内容为空 → 标记 EMPTY_SKILL，建议删除或重建
如果 frontmatter 完全缺失 → 标记 NO_METADATA，建议补充
如果无法解析 Markdown → 标记 PARSE_ERROR，记录文件路径
```

---

## 步骤 3: 生成进化建议

### 3.1 建议类型

| 类型 | 触发条件 | 输出 |
|------|----------|------|
| **结构修复** | 缺少 frontmatter/工作流步骤 | 具体的 Markdown 补丁 |
| **健壮性增强** | 无失败模式/检查点 | 需要添加的章节模板 |
| **安全加固** | 无反例黑名单 | 建议的禁止操作列表 |
| **去特定化** | 含特定平台/工具引用 | 需替换的文本和替代方案 |
| **精简优化** | 文件 >500 行或有冗余段落 | 建议删除的章节 |

### 3.2 输出格式

每个建议必须包含：

```markdown
## 建议 #{n}: {标题}
**优先级**: 🔴高 / 🟡中 / 🟢低
**目标文件**: {文件路径}
**问题**: {一句话描述}
**修改方案**: {具体的修改内容，可直接执行}
**预期效果**: {改进后的预期得分变化}
```

### 3.3 失败分支

```
如果无改进建议 → 标记 NO_IMPROVEMENTS，报告 "当前 skills 质量良好"
如果建议数量 >20 → 只输出 Top 10，其余放入详细报告文件
如果某 skill 建议会导致破坏性变更 → 标记 DESTRUCTIVE，加 ⚠️ 警告
```

---

## 步骤 4: 生成报告

### 4.1 报告结构

```markdown
# Capability Evolution Report — {date}

## 概览
- 已扫描: {count} skills
- 平均分: {avg_score}/100
- 需立即改进: {urgent_count}
- 建议改进: {suggested_count}
- 质量良好: {good_count}

## 排名

| 排名 | Skill | 得分 | 评级 | 首要问题 |
|------|-------|------|------|----------|
| 1 | {name} | {score} | {grade} | {top_issue} |

## 详细分析

### {skill_name} ({score}/100)
{详细评分和 Top 3 建议}

## 改进路线图

### 第1批（立即执行）
{最高优先级的改进}

### 第2批（本周内）
{中等优先级的改进}

### 第3批（可选）
{低优先级的改进}
```

### 4.2 保存报告

```
保存到 ~/.workbuddy/evolver/reports/{date}-evolution-report.md
同时输出到当前对话
```

---

## 步骤 5: 跟踪改进

### 5.1 记录改进历史

追加到 `~/.workbuddy/evolver/evolution-log.jsonl`:

```json
{"date": "2026-06-02", "skill": "auto-updater", "action": "optimized", "old_score": 25.2, "new_score": 78.0, "changes": ["添加6步工作流", "添加失败模式", "添加检查点", "添加反例黑名单"]}
```

### 5.2 失败分支

```
如果 evolution-log.jsonl 不存在 → 创建新文件
如果写入失败 → 报告写入错误，但继续输出到对话
```

---

## 模式 1: 单 Skill 深度分析

```
触发: "分析 {skill_name}" / "检查 {skill_name} 质量"
执行: 步骤 1→2→3→4（仅针对指定 skill）
```

## 模式 2: 全量 Skills 扫描

```
触发: "扫描所有 skills" / "skills 健康检查" / "哪些 skill 需要改进"
执行: 步骤 1→2→3→4（全部 skills）
```

## 模式 3: 使用历史分析

```
触发: "分析 skill 使用情况" / "哪些 skill 用得最多"
执行: 搜索 conversation history 中的 skill 调用记录
      → 统计频率 → 关联质量评分 → 输出使用效率报告
```

---

## 配置

无需额外配置。所有数据存储在本地 `~/.workbuddy/evolver/` 目录。
