---
name: skill-vetter
version: 1.0.1
description: "安全优先的 Skill 审查工具。安装任何 Skill 前必须执行审查。检查红旗信号、权限范围、可疑模式。触发词：审查skill、安全检查、skill审查、vet skill、安全审计、安装前检查。"
---

# Skill Vetter 🔒

安全优先的 Skill 审查协议。**安装任何 Skill 前必须执行审查。**

## ⛔ 反例与黑名单

以下行为**禁止**执行：

| 禁止操作 | 原因 |
|----------|------|
| 跳过审查直接安装任何 skill | 安全风险不可接受 |
| 仅凭作者声誉跳过代码审查 | 账号可能被盗，供应链攻击常见 |
| 审查后不输出正式报告 | 需要审计追溯 |
| 对高风险 skill 自作主张批准安装 | 高风险必须用户确认 |
| 审查时只看 SKILL.md 不检查 scripts/ | 恶意代码常藏在脚本中 |
| 使用未经审查的 skill 操作敏感文件 | 可能泄露或破坏数据 |
| 审查结果用模糊语言（"看起来安全"） | 必须给出明确的风险等级和判定 |

---

## 步骤 1: 来源检查

### 1.1 确定来源

```
来源类型:
  [1] GitHub 仓库 — 检查 stars/forks/更新时间/作者
  [2] 本地文件   — 检查文件来源和创建时间
  [3] URL 下载   — 检查域名可信度
  [4] 其他 agent 分享 — 最高审查级别
```

### 1.2 获取仓库信息（GitHub 来源）

```bash
curl -s "https://api.github.com/repos/{owner}/{repo}" | jq '{stars: .stargazers_count, forks: .forks_count, updated: .updated_at, license: .license.spdx_id}'
```

### 1.3 失败分支

```
如果 GitHub API 不可达 → 标记 SOURCE_UNVERIFIED，升级到 🔴 HIGH 审查级别
如果仓库 < 10 stars  → 标记 LOW_TRUST_SOURCE
如果仓库 > 1年未更新 → 标记 STALE_REPO，检查依赖兼容性
如果来源完全未知   → 标记 UNKNOWN_SOURCE，升级到 ⛔ EXTREME 审查级别
```

---

## 步骤 2: 代码审查（强制）

### 🔴 CHECKPOINT: 代码审查

**必须逐文件读取并检查：**

```
已读取文件:
  [ ] SKILL.md
  [ ] scripts/ (全部 .py/.js/.sh/.mjs 文件)
  [ ] templates/ (检查是否含外部脚本引用)
  [ ] references/ (检查是否含可疑链接)
  [ ] assets/ (检查文件大小和类型)
```

### 2.1 红旗信号清单

```
🚨 发现以下任一信号 → 立即标记为 REJECT:

• curl/wget 到未知 URL
• 向外发送数据
• 请求凭证/token/API key
• 读取 ~/.ssh, ~/.aws, ~/.config 无明确理由
• 访问 MEMORY.md, USER.md, SOUL.md, IDENTITY.md
• 对任何内容使用 base64 解码
• 使用 eval() 或 exec() 处理外部输入
• 修改 workspace 外的系统文件
• 安装未列出的包
• 向 IP 地址发起网络请求（非域名）
• 混淆代码（压缩/编码/最小化）
• 请求提权/sudo 权限
• 访问浏览器 cookie/session
• 触碰凭证文件
```

### 2.2 失败分支

```
如果发现任一红旗信号 → 标记为 ⛔ EXTREME，拒绝安装
如果文件无法读取     → 标记 UNREADABLE，升级风险等级
如果脚本文件过多(>10) → 标记 LARGE_SURFACE，建议分批审查
如果含二进制文件     → 标记 BINARY_PRESENT，检查文件类型和大小
```

---

## 步骤 3: 权限范围评估

### 3.1 权限清单

```
文件读取: {列出所有读取路径}
文件写入: {列出所有写入路径}
命令执行: {列出所有 shell 命令}
网络访问: {列出所有网络端点}
环境变量: {列出所需的环境变量}
```

### 3.2 最小权限原则

```
如果权限范围超出声明功能 → 标记 OVER_PERMISSIONED
如果读取用户个人文件无理由 → 标记 PRIVACY_CONCERN
如果写入系统目录 → 标记 SYSTEM_WRITE
```

---

## 步骤 4: 风险分级

| 风险等级 | 条件 | 操作 |
|----------|------|------|
| 🟢 LOW | 无网络/文件写入/命令执行，纯文本处理 | 基础审查，可安装 |
| 🟡 MEDIUM | 有文件操作但仅在 workspace 内 | 完整代码审查后安装 |
| 🔴 HIGH | 有网络请求、凭证操作、跨目录文件访问 | **需要用户确认** |
| ⛔ EXTREME | 含红旗信号、系统级操作、提权请求 | **禁止安装** |

### 🔴 CHECKPOINT: 风险确认

```
风险等级: {🟢/🟡/🔴/⛔}
判定依据: {具体原因}

如果 🔴 HIGH 或 ⛔ EXTREME:
  → 必须向用户展示完整报告
  → 等待用户明确确认或拒绝
  → 不可自动决定
```

---

## 步骤 5: 输出审查报告

```
SKILL VETTING REPORT
═══════════════════════════════════════
Skill: {name}
来源: {source}
作者: {author}
版本: {version}
───────────────────────────────────────
指标:
• Stars/Downloads: {count}
• 最后更新: {date}
• 已审查文件: {count}/{total}
───────────────────────────────────────
红旗信号: {None / 列出具体信号}

权限需求:
• 文件: {list 或 "无"}
• 网络: {list 或 "无"}
• 命令: {list 或 "无"}
───────────────────────────────────────
风险等级: {🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ EXTREME}

判定: {✅ 可安全安装 / ⚠️ 谨慎安装 / ❌ 禁止安装}

注意事项: {具体观察和建议}
═══════════════════════════════════════
```

---

## 步骤 6: 记录审查结果

### 6.1 保存审查记录

追加到 `~/.workbuddy/skill-vetter/vetting-log.jsonl`:

```json
{"date": "2026-06-02", "skill": "{name}", "source": "{source}", "risk": "LOW", "verdict": "SAFE", "red_flags": 0}
```

### 6.2 失败分支

```
如果无法写入审查记录 → 输出到对话中，提示用户手动记录
```

---

## 快速审查命令（GitHub 来源）

```bash
# 检查仓库统计
curl -s "https://api.github.com/repos/{owner}/{repo}" | jq '{stars: .stargazers_count, forks: .forks_count, updated: .updated_at}'

# 列出 skill 文件
curl -s "https://api.github.com/repos/{owner}/{repo}/contents/" | jq '.[].name'

# 获取 SKILL.md 原始内容
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/main/SKILL.md"
```

## 信任层级

| 级别 | 来源 | 审查力度 |
|------|------|----------|
| 1 | 官方 WorkBuddy skills | 基础审查（仍须审查） |
| 2 | 高星仓库 (1000+) | 中等审查 |
| 3 | 已知作者 | 中等审查 |
| 4 | 新/未知来源 | 最高审查 |
| 5 | 涉及凭证的 skill | **始终需要用户确认** |
