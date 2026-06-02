---
name: Word / DOCX
slug: word-docx
version: 1.0.3
description: "Microsoft Word 文档创建、检查和编辑。处理 .docx 文件的样式、编号、修订、表格、分节和兼容性。触发词：Word、docx、文档编辑、修订、tracked changes、公文排版、表格调整、页码、页眉页脚。"
---

## ⛔ 反例与黑名单

以下操作**禁止**执行：

| 禁止操作 | 原因 |
|----------|------|
| 将 .docx 当纯文本处理（直接字符串替换） | 破坏 OOXML 结构，导致文件损坏 |
| 在修订模式下整段重写 | 产生噪音审阅，破坏原始格式上下文 |
| 用空格/空段落做间距 | 模板脆弱，用段落设置中的间距属性 |
| 复制粘贴内容时不检查样式导入 | 静默引入外部样式、主题和编号定义 |
| 靠肉眼重启列表编号 | 编号状态在 XML 中，视觉对齐不等于正确 |
| 编辑 .docm 宏文件时不警告用户 | 宏文件有安全风险 |
| 处理 .doc 旧格式时不先转换 | 旧格式与现代 .docx 行为不一致 |
| 交付前不验证跨编辑器兼容性 | Word/LibreOffice/Google Docs 渲染可能不同 |

---

## 步骤 1: 确定任务类型

### 🔴 CHECKPOINT: 任务分类

阅读用户请求，确定操作类型：

| 类型 | 特征 | 策略 |
|------|------|------|
| **读取/提取** | "查看""提取""读取""分析" | 结构保留读取，不修改文件 |
| **新建文档** | "创建""生成""新建" | 样式驱动生成 |
| **轻量编辑** | "修改一句话""改个词" | 最小替换，保护修订和书签 |
| **深度编辑** | "重构""重排版""调整格式" | OOXML 感知编辑，检查包结构 |
| **兼容性检查** | "检查兼容""验证" | 跨编辑器验证 |

```
如果用户意图不明确 → 询问任务类型再开始
如果文件是 .doc → 先转换为 .docx（用 Word 或 LibreOffice）
如果文件是 .docm → 警告宏安全风险，确认后继续
```

---

## 步骤 2: 读取文档（结构保留模式）

### 2.1 检查文件包结构

```bash
python3 -c "
import zipfile, os
with zipfile.ZipFile('{file_path}') as z:
    for name in sorted(z.namelist()):
        print(name)
"
```

### 2.2 提取关键信息

```bash
python3 -c "
from docx import Document
doc = Document('{file_path}')
print(f'段落数: {len(doc.paragraphs)}')
print(f'表格数: {len(doc.tables)}')
print(f'分节数: {len(doc.sections)}')
# 检查修订和批注
import zipfile
with zipfile.ZipFile('{file_path}') as z:
    has_revisions = 'word/revisions.xml' in z.namelist()
    has_comments = 'word/comments.xml' in z.namelist()
    print(f'含修订: {has_revisions}')
    print(f'含批注: {has_comments}')
"
```

### 2.3 失败分支

```
如果文件不存在 → 报告 FILE_NOT_FOUND
如果文件不是有效 ZIP → 报告 NOT_VALID_DOCX
如果读取失败     → 报告 READ_ERROR，建议用 Word 修复
如果含修订/批注  → 标记 HAS_REVIEW_CONTENT，后续操作需特别注意
```

---

## 步骤 3: 执行操作

### 3.1 读取/提取 → 仅读取，不写

```bash
python3 -c "
from docx import Document
doc = Document('{file_path}')
for i, p in enumerate(doc.paragraphs):
    style = p.style.name if p.style else 'None'
    text = p.text[:100]
    print(f'[{i}] ({style}) {text}')
"
```

### 3.2 新建文档 → 样式驱动

```bash
python3 -c "
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# 设置默认样式
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)

# 页面设置
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)

# 添加内容...
doc.save('{output_path}')
"
```

### 3.3 编辑 → 最小替换

```
原则:
- 只修改需要改的 run/段落，不重写整个段落
- 保留修订标记、书签锚点、批注范围
- 编辑后检查编号连续性和交叉引用完整性
```

### 3.4 失败分支

```
如果样式不存在 → 创建样式后再应用
如果字体缺失 → 报告 MISSING_FONT，用默认字体替代
如果编号断裂 → 修复 numbering.xml 中的 abstractNum 定义
如果编辑后文件损坏 → 从备份恢复，报告 CORRUPTED_AFTER_EDIT
```

---

## 步骤 4: OOXML 专项处理

### 4.1 样式操作

```
层次: 段落样式 > 字符样式 > 直接格式
原则: 优先使用命名样式，移除多余的直接格式
警告: 文档间复制会静默导入外部样式定义
```

### 4.2 列表和编号

```
关键文件: word/numbering.xml
关键元素: abstractNum, num, numPr
陷阱: 视觉对齐不等于编号正确，重启行为由 XML 状态决定
```

### 4.3 页面布局

```
关键: 分节符 (sectPr)
作用域: 页边距/方向/页眉页脚/页码 均按节独立
注意: A4 vs US Letter 默认值不同，显式设置页面尺寸
```

### 4.4 修订和批注

```
修订: word/revisions.xml（含插入/删除标记和元数据）
批注: word/comments.xml（独立于正文的部件）
原则: 编辑时做最小替换，不要整段重写
```

### 4.5 域代码

```
常见域: 目录/页码/日期/交叉引用/邮件合并
操作: 编辑域源代码，缓存显示值在刷新前可能滞后
风险: 锚点断裂导致引用失效
```

---

## 步骤 5: 兼容性验证

### 🔴 CHECKPOINT: 交付前验证

```
验证项目:
  [ ] 表格宽度在 A4/US Letter 下是否正常
  [ ] 页眉页脚图片链接是否有效
  [ ] 编号在重启后是否连续
  [ ] 修订是否已全部接受/拒绝（如需要）
  [ ] 域代码是否已更新（非缓存值）
  [ ] 嵌入字体是否已子集化（如需要）
```

### 5.1 执行验证

```bash
python3 -c "
from docx import Document
doc = Document('{output_path}')
issues = []

# 检查表格宽度
for i, table in enumerate(doc.tables):
    for j, cell in enumerate(table.rows[0].cells):
        if cell.width and cell.width > 5000000:  # ~14cm
            issues.append(f'表格{i}列{j}宽度异常')

# 检查空段落间距
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == '' and p.paragraph_format.space_before is None:
        issues.append(f'段落{i}使用空段落做间距')

for issue in issues:
    print(f'⚠️ {issue}')
print(f'共 {len(issues)} 个问题')
"
```

---

## 步骤 6: 输出报告

```
📘 DOCX 操作完成

📄 文件: {output_path}
📋 操作: {task_type}
⚠️ 注意事项:
  - 需安装字体: {required_fonts}
  - 建议在 Word 中打开验证: 表格/页眉/编号
  - 跨编辑器兼容: {compatibility_notes}
```

---

## 常见陷阱速查

| 陷阱 | 根因 | 预防 |
|------|------|------|
| 复制粘贴破坏样式 | 静默导入外部样式和编号 | 粘贴后用"保留目标格式" |
| 编号肉眼对齐但实际断裂 | 编号状态在 XML 中 | 检查 numbering.xml |
| 空段落做间距 | 未用段落间距属性 | 设置 space_before/space_after |
| 表格跨编辑器漂移 | 自动宽度在不同编辑器解释不同 | 用显式固定宽度 |
| 页眉图片断裂 | 部件特定关系 ID 失效 | 复制后重建关系 |
| 修订残留 | 表面接受但元数据仍在 | 检查 revisions.xml |
| 域代码缓存过期 | 显示值未刷新 | 打开后 Ctrl+A → F9 刷新 |
| 兼容模式限制 | .doc 模式静默禁用新特性 | 转换为 .docx 原生格式 |
