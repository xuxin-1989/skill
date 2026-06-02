---
name: auto-updater
description: "自动更新 WorkBuddy 和所有已安装 skills。每日检查更新、应用更新、向用户报告变更摘要。触发词：自动更新、daily update、更新检查、update skills、upgrade skills、check for updates。"
---

# Auto-Updater Skill

每日自动检查并应用 WorkBuddy 及 skills 更新，确保始终运行最新版本。

## ⛔ 反例与黑名单

以下操作**禁止**执行：

| 禁止操作 | 原因 |
|----------|------|
| 跳过 `doctor`/`health-check` 直接更新 | 可能因环境不兼容导致更新后无法启动 |
| 在用户活跃会话期间执行更新 | 更新可能重启进程，中断用户工作 |
| 静默更新（不报告结果） | 用户需要知道更新了什么 |
| 更新失败后自动重试超过 2 次 | 避免死循环消耗资源 |
| 修改用户手动锁定的 skill 版本 | 用户锁定版本表示有特定原因 |
| 删除旧版本备份（保留最近 3 次） | 需要回滚能力 |
| 在无网络环境下尝试更新 | 浪费资源，直接跳过并记录 |

---

## 🔴 CHECKPOINT 1: 环境准备

**在执行任何更新前，必须确认：**

1. 当前无用户活跃会话（idle 状态）
2. 网络连通性正常
3. 磁盘空间 > 500MB

```
如果任一条件不满足 → 跳过本轮更新，记录原因，等待下次 cron 触发
```

---

## 步骤 1: 检查 WorkBuddy 更新

### 1.1 获取当前版本

```bash
workbuddy --version
```

### 1.2 检查最新版本

```bash
# npm 安装方式
npm view @workbuddy/cli version 2>/dev/null || echo "NPM_CHECK_FAILED"

# 或通过内置更新命令
workbuddy update --check 2>/dev/null || echo "CHECK_FAILED"
```

### 1.3 失败分支

```
如果 npm view 超时（>30s） → 标记 NETWORK_TIMEOUT，跳到步骤 2
如果 workbuddy update --check 返回非零 → 标记 CHECK_FAILED，跳到步骤 2
如果当前版本 == 最新版本 → 标记 NO_UPDATE，跳到步骤 2
如果最新版本 < 当前版本 → 标记 DOWNGRADE_WARN，跳到步骤 2（不执行降级）
```

---

## 🔴 CHECKPOINT 2: 更新确认

**仅在步骤 1 检测到新版本时触发：**

```
发现新版本: {old} → {new}
变更日志: {changelog 摘要}
是否继续更新？[自动确认：cron 模式直接继续]
```

```
如果 changelog 包含 BREAKING CHANGE → 标记 WARNING，但仍执行更新
如果新版本为 prerelease（含 -alpha/-beta/-rc） → 跳过，标记 SKIP_PRERELEASE
```

---

## 步骤 2: 应用 WorkBuddy 更新

### 2.1 执行更新

```bash
# npm 安装方式
npm update -g @workbuddy/cli@latest 2>&1 | tee /tmp/workbuddy_update.log
```

### 2.2 执行健康检查

```bash
workbuddy doctor 2>&1 || workbuddy health-check 2>&1
```

### 2.3 失败分支

```
如果 npm update 失败（exit code ≠ 0）:
  → 读取 /tmp/workbuddy_update.log 获取错误信息
  → 如果是权限错误 → 标记 PERMISSION_DENIED，记录到报告
  → 如果是网络错误 → 标记 NETWORK_FAILED，记录到报告
  → 如果是包冲突   → 标记 CONFLICT，记录冲突包名，跳到步骤 3
  → 其他错误       → 标记 UNKNOWN_ERROR，记录完整错误日志

如果 doctor/health-check 失败:
  → 执行回滚: npm install -g @workbuddy/cli@{old_version}
  → 标记 ROLLBACK_EXECUTED，记录到报告
  → 跳过步骤 3（skills 更新在稳定版本上执行风险高）
```

---

## 步骤 3: 检查 Skills 更新

### 3.1 获取已安装 skills 列表

```bash
npx skills list 2>/dev/null || echo "SKILL_LIST_FAILED"
```

### 3.2 检查每个 skill 的更新

```bash
npx skills outdated 2>/dev/null || echo "SKILL_CHECK_FAILED"
```

### 3.3 失败分支

```
如果 npx skills list 失败 → 标记 SKILL_LIST_FAILED，跳到步骤 5（报告）
如果 npx skills outdated 失败 → 标记 SKILL_CHECK_FAILED，跳到步骤 5
如果没有可更新 skills → 标记 SKILLS_CURRENT，跳到步骤 5
```

---

## 🔴 CHECKPOINT 3: Skills 更新确认

```
以下 skills 有可用更新:
{skill_name}: {old_version} → {new_version}
...
共 {count} 个 skills 待更新。

排除锁定版本的 skills: {locked_skills}
是否更新？[自动确认：cron 模式直接继续]
```

---

## 步骤 4: 应用 Skills 更新

### 4.1 逐个更新（每批 ≤ 5 个）

```bash
# 单个更新
npx skills update {skill_name} 2>&1

# 或批量更新
npx skills update --all 2>&1
```

### 4.2 失败分支（每个 skill 独立处理）

```
对于每个 skill 更新:
  如果成功 → 记录 {skill}: {old} → {new}
  如果失败:
    → 记录错误原因到报告
    → 尝试单独更新（非批量模式下可能更稳定）
    → 如果单独更新仍失败 → 标记 {skill}_UPDATE_FAILED
    → 继续下一个 skill（不中断整体流程）

如果全部 skills 更新失败 → 标记 ALL_SKILLS_FAILED
如果部分 skills 更新失败 → 标记 PARTIAL_SKILLS_FAILED
```

---

## 步骤 5: 生成并发送报告

### 5.1 报告格式

```
🔄 每日自动更新报告 — {date}

**WorkBuddy**:
  {status_emoji} {old_version} → {new_version}
  或
  {status_emoji} 已是最新 ({current_version})
  或
  {status_emoji} 更新失败: {error_summary}

**Skills**:
  ✅ 已更新 ({count}):
    - {skill}: {old} → {new}
  
  ⚠️ 更新失败 ({count}):
    - {skill}: {error_summary}
  
  ⏭️ 已跳过 ({count}):
    - {skill}: {skip_reason}
  
  ✓ 已是最新 ({count}):
    {skill_list}

**状态**: {overall_status}
**耗时**: {duration}
```

### 5.2 状态图标

| 状态 | 图标 | 含义 |
|------|------|------|
| 成功更新 | ✅ | 更新已应用 |
| 无需更新 | ✓ | 已是最新版本 |
| 更新失败 | ⚠️ | 出错但已记录 |
| 已跳过 | ⏭️ | 有原因跳过 |
| 已回滚 | 🔄 | 更新后回滚 |
| 全部失败 | ❌ | 本轮无任何更新成功 |

### 5.3 发送报告

通过当前会话消息系统发送给用户。

```
如果报告发送失败 → 保存到 ~/.workbuddy/auto-updater/reports/{date}.md
如果发送成功   → 同时保存副本到 reports/ 目录
```

---

## 步骤 6: 记录日志

### 6.1 写入更新日志

追加到 `~/.workbuddy/auto-updater/update-log.jsonl`:

```json
{"date": "2026-06-02", "workbuddy": {"old": "x.x.x", "new": "y.y.y", "status": "success"}, "skills_updated": 3, "skills_failed": 0, "duration_sec": 45}
```

### 6.2 保留备份

```
保留最近 3 次更新前的旧版本备份
删除超过 3 次的旧备份
备份路径: ~/.workbuddy/auto-updater/backups/
```

---

## Cron 配置

### 推荐配置

```
时间: 每天凌晨 4:00（用户不活跃时段）
时区: 用户本地时区
命令: 触发此 skill 执行完整 6 步流程
```

### 手动触发

```
用户说 "检查更新" / "update skills" 等触发词时
→ 执行完整流程，但 CHECKPOINT 2/3 需要用户确认（非 cron 模式）
```

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 权限不足 | 检查安装目录写入权限 |
| 网络超时 | 跳过本轮，下次 cron 自动重试 |
| 包冲突 | 记录冲突详情，跳过该包 |
| 更新后无法启动 | 自动回滚到旧版本 |
| Skills 列表获取失败 | 跳过 skills 更新，仅更新 WorkBuddy |
