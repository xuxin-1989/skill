---
name: brainstorming
description: "在任何创造性工作之前必须使用。在实施之前探索用户意图、需求和设计。触发词：头脑风暴、brainstorming、设计方案、design thinking、架构设计、方案讨论、需求分析、先想想再写、先设计再实现、技术方案。"
---

# Brainstorming Skill

在任何创造性工作（创建功能、构建组件、添加功能或修改行为）**之前**必须使用。在实施之前探索用户意图、需求和设计。

## Core Checklist (9 Steps)

1. **探索项目上下文** — 检查文件、文档、最近的提交记录
2. **提供可视化伴侣**（如果涉及视觉问题）— 独立消息，不与澄清问题合并
3. **提出澄清问题** — 一次一个，理解目的/约束/成功标准
4. **提出 2-3 种方案** — 包含权衡分析和你的推荐
5. **呈现设计方案** — 按复杂度分节呈现，每节获得用户批准
6. **编写设计文档** — 保存到 `docs/designs/YYYY-MM-DD-<topic>-design.md` 并提交
7. **规格自查** — 快速内联检查占位符、矛盾、歧义、范围
8. **用户审核书面规格** — 在继续之前请用户审核规格文件
9. **过渡到实施** — 设计确认后进入实施阶段

## Key Rules

### HARD-GATE
> 在呈现设计方案并获得用户批准之前，不要编写任何代码、搭建任何项目或采取任何实施行动。这适用于每个项目，无论看起来多简单。

### Anti-pattern: "It's too simple to need design"
每个项目都要经过这个流程。待办列表、单功能工具、配置更改——所有项目无一例外。

## Design Principles

### Understand the Idea
- 首先检查当前项目状态（文件、文档、最近的提交）
- 在提出详细问题之前评估范围
- 一次只问一个问题来完善想法
- 优先使用选择题，但开放式问题也可以
- 重点理解：目的、约束、成功标准

### Explore Approaches
- 提出 2-3 种不同的方案，附带权衡分析
- 以对话方式呈现选项，附上你的推荐和理由
- 首先介绍你推荐的选项并解释原因

### Present Design
- 按复杂度缩放每节内容
- 每节之后询问是否正确
- 涵盖：架构、组件、数据流、错误处理、测试

### Isolation & Clarity
- 将系统分解为更小的单元，每个单元有明确的目的
- 通过良好定义的接口通信，可以独立理解和测试

### Working in Existing Codebases
- 在提出更改之前探索当前结构，遵循现有模式
- 如果现有代码存在问题影响工作，将有针对性的改进纳入设计
- 不要提出无关的重构

## After Design

### Documentation
- 将验证过的设计写入 `docs/designs/YYYY-MM-DD-<topic>-design.md`
- 将设计文档提交到 git

### Spec Self-Check
1. **占位符扫描**: 是否有 "TBD"、"TODO"、不完整的部分？修复它们
2. **内部一致性**: 各部分之间是否有矛盾？
3. **范围检查**: 是否足够聚焦？
4. **歧义检查**: 是否有需求可以被两种方式解释？

### User Review Gate
> "设计规格已写入 `<path>`。请审核，在开始实施之前是否需要任何更改？"

等待用户回应。仅在用户批准后才继续。

## Visual Companion

基于浏览器的可视化工具，用于展示模型、图表和选项。

### When to Propose
当预计讨论涉及视觉内容（模型、布局、图表）时，单独提出：
> "我们可以通过浏览器展示模型、图表和对比效果。需要开启本地可视化伴侣吗？"

### Usage
启动服务器后，在 `screen_dir` 中写入 HTML 内容片断，用户在浏览器中查看并点击交互。

## WorkBuddy Adaptation Notes

- 设计文档目录: `docs/designs/` (WorkBuddy 项目内)
- 可视化伴侣脚本位于 `scripts/` 目录
- 此 Skill 来自 [obra/superpowers](https://github.com/obra/superpowers) 项目，已适配 WorkBuddy
