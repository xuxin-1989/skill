---
name: self-reflection
description: "结构化自我反思与持续改进。记录错误和经验教训，定期回顾，追踪改进趋势。触发词：反思、自我反思、记录教训、lesson learned、self reflection、总结经验、复盘、回顾改进。"
---

# Self-Reflection

通过结构化反思记录和定期回顾，持续追踪和改进工作质量。

## ⛔ 反例与黑名单

以下操作**禁止**执行：

| 禁止操作 | 原因 |
|----------|------|
| 在反思中记录敏感信息（密码/token/密钥） | 反思文件可能被同步或共享 |
| 跳过反思周期（连续 3 次） | 失去持续改进的意义 |
| 反思时只写"做得不错"不写具体问题 | 无实质改进价值 |
| 修改历史反思记录（只追加不修改） | 保持审计追溯 |
| 在反思中使用模糊语言（"有些问题""需要改进"） | 不可执行，无法跟踪 |
| 基于单次失败做过度泛化的规则 | 需要 3 次以上同类问题才提炼规则 |
| 删除超过 30 天的反思记录 | 长期趋势分析需要历史数据 |

---

## 步骤 1: 检查是否需要反思

### 1.1 读取状态文件

```bash
cat ~/.workbuddy/self-reflection/state.json 2>/dev/null || echo '{"last_reflection": null, "total_reflections": 0, "streak": 0}'
```

### 1.2 判断是否到期

```
如果 last_reflection 为空 → 标记 FIRST_RUN，这是首次反思
如果距今 < 24小时        → 标记 NOT_DUE，跳过，输出上次反思摘要
如果距今 >= 24小时       → 标记 DUE，继续步骤 2
如果 streak >= 7         → 标记 WEEKLY_DEEP_REFLECTION，触发深度反思模式
```

### 1.3 失败分支

```
如果 state.json 不存在 → 创建默认状态文件
如果 state.json 损坏   → 从反思日志重建状态
如果无法写入状态文件   → 报告错误，但继续反思流程（不阻塞）
```

---

## 步骤 2: 收集反思素材

### 2.1 读取近期记忆

```bash
# 读取最近 3 天的 workspace memory
find ~/WorkBuddy/*/memory -name "*.md" -mtime -3 2>/dev/null | sort -r | head -5
```

### 2.2 读取上次反思

```bash
tail -30 ~/.workbuddy/self-reflection/reflections.jsonl 2>/dev/null || echo "NO_PAST_REFLECTIONS"
```

### 2.3 检查未完成事项

从近期对话和工作日志中提取：
- 未解决的错误
- 被用户指出的问题
- 重复出现的困难

### 2.4 失败分支

```
如果无 memory 文件     → 标记 NO_MEMORY_DATA，仅基于当前会话反思
如果 reflections.jsonl 为空 → 标记 FIRST_REFLECTION，跳过对比分析
```

---

## 🔴 CHECKPOINT: 反思前确认

```
准备开始第 {total_reflections + 1} 次反思
上次反思: {last_reflection}（{hours_ago} 小时前）
连续反思: {streak} 天
模式: {regular / deep}

反思将记录到 ~/.workbuddy/self-reflection/reflections.jsonl
是否继续？[cron 模式下自动继续]
```

---

## 步骤 3: 执行反思

### 3.1 反思模板

对以下 4 个维度逐一回答：

```markdown
## 反思 #{n} — {date}

### 1. 错误与教训
- 错误: {具体描述，包含上下文}
- 根因: {为什么发生}
- 教训: {学到了什么，如何避免}

### 2. 成功经验
- 做法: {做了什么效果好}
- 效果: {具体数据或反馈}
- 可复用: {是否可以标准化为规则/skill}

### 3. 待改进
- 领域: {哪个方面需要提升}
- 当前状态: {现在做得如何}
- 目标状态: {希望达到什么水平}
- 行动计划: {具体做什么}

### 4. 用户反馈
- 正面反馈: {用户满意的点}
- 改进建议: {用户提出的要求}
- 已采纳: {是否已调整}
```

### 3.2 深度反思模式（每周一次）

额外回答：

```markdown
### 5. 趋势分析
- 本周高频错误类型: {top 3}
- 对比上周: {改善/恶化/持平}
- 新出现的问题: {之前没见过的}

### 6. 规则提炼
- 是否出现 ≥3 次同类问题？ → 应提炼为规则
- 提炼的规则: {具体可执行的约束}
- 写入位置: ~/.workbuddy/MEMORY.md 或 skill
```

### 3.3 失败分支

```
如果反思过程中断 → 保存草稿到 ~/.workbuddy/self-reflection/draft.md
如果无法写入 reflections.jsonl → 保存为独立文件 reflections-{date}.md
```

---

## 步骤 4: 写入记录

### 4.1 追加到反思日志

```bash
echo '{"date":"2026-06-02T14:55:00","type":"regular","errors":["..."],"lessons":["..."],"actions":["..."]}' >> ~/.workbuddy/self-reflection/reflections.jsonl
```

### 4.2 更新状态

```json
{
  "last_reflection": "2026-06-02T14:55:00",
  "total_reflections": {n},
  "streak": {streak},
  "last_deep_reflection": "2026-05-26T14:00:00"
}
```

### 4.3 提取可执行改进

```
如果提炼出新规则 → 提示用户确认后写入 ~/.workbuddy/MEMORY.md
如果发现 skill 改进点 → 建议运行 capability-evolver 分析
如果发现重复错误 ≥3 次 → 标记为 PATTERN，建议创建自动化检查
```

### 4.4 失败分支

```
如果 reflections.jsonl 写入失败 → 保存到 fallback 路径
如果状态更新失败 → 下次反思时自动修复
```

---

## 步骤 5: 输出反思摘要

```
🪞 反思 #{n} 完成 — {date}

📊 统计:
  总反思次数: {total}
  连续天数: {streak}
  累计记录错误: {total_errors}
  累计提炼规则: {total_rules}

🔑 本次关键发现:
  {top 3 insights}

📋 行动计划:
  {action items}
```

---

## 手动触发

```
用户说 "反思" / "总结教训" / "复盘" 等触发词时
→ 执行步骤 1→2→3→4→5（无论是否到期）
→ CHECKPOINT 需要用户确认（非 cron 模式）
```

## 查看历史

```
用户说 "查看反思记录" / "reflection history"
→ 读取 ~/.workbuddy/self-reflection/reflections.jsonl
→ 输出最近 10 条反思摘要
→ 可选：生成趋势图表（错误类型分布、改进速度）
```

## 配置

配置文件: `~/.workbuddy/self-reflection/config.json`

```json
{
  "interval_hours": 24,
  "deep_reflection_day": "sunday",
  "max_entries_per_reflection": 5,
  "auto_extract_rules": true,
  "rule_extract_threshold": 3
}
```

默认值适用于大多数场景，无需修改。
