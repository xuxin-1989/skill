---
name: sn-da-image-caption
description: "图片理解与数据提取 skill。当图片文件（.png/.jpg/.jpeg/.gif/.webp/.bmp）是主要输入且用户需要理解、提取数据或分析图片内容时使用。提供预配置的 caption 脚本（scripts/caption.py），通过 SenseNova Vision API 将图片转为文本描述，无需额外配置 API Key。覆盖：(1) 通过 scripts/caption.py 对图表/表格/截图/流程图进行 caption，(2) 将 caption 文本解析为结构化 DataFrame，(3) 基于提取数据重新生成可视化图表，(4) 导出为 Excel/CSV。**遇到以下任一情况就主动使用本 skill，不要自行猜测图片内容**：①用户出现触发词：图片分析、图表提取、表格识别、OCR、图片描述、截图分析、图表数据、提取图片中的数据、图片转表格、识别图片、图像理解、图片识别、caption、图像提取、数据提取、image caption、extract data from image、chart analysis、table OCR、visual recognition、image to text；②用户上传或指定了图片文件（.png / .jpg / .jpeg / .gif / .webp / .bmp）并要求理解、提取数据或分析内容；③任务需要从图表截图、表格截图、UI 截图、流程图中提取结构化信息；④用户要求将图片中的数据转为 Excel/CSV 或重新生成可视化图表。仅不用于：图片编辑（裁剪、滤镜、缩放）、图片生成、不含数据的风景/人物照片描述。"
---

# Image Caption Analysis — 图片描述与数据提取

## ⛔ Anti-Pattern Blacklist — 禁止的做法

以下做法**绝对禁止**，出现任一即为违规：

| # | ⛔ 禁止做法 | ✅ 正确做法 |
|---|-----------|-----------|
| 1 | **直接猜测图片内容**：不调用 caption 就根据文件名/上下文推断图片数据 | 始终先运行 `scripts/caption.py` 获取描述 |
| 2 | **跳过 --prompt 使用默认检测**：对图表/表格/UI/流程图使用 auto-detect | 对已知类型的图片，必须传入 `--prompt` 精确引导提取 |
| 3 | **不验证提取结果**：caption 返回后直接使用，不检查数据完整性 | 检查行列数、数值合理性、百分比之和是否约等于 100% |
| 4 | **一次性提取超大表格**：对 >20 行的表格用单次 caption | 分两次 caption：`"提取前半部分"` + `"提取后半部分"` |
| 5 | **matplotlib 不设中文字体**：生成图表前未设置 WenQuanYi Zen Hei | 必须在 `plt.savefig()` 之前执行中文字体配置代码块 |
| 6 | **混合使用 batch 模式与逐个 caption**：在 batch 目录中同时逐个调用 caption | 二选一：用 `--batch` 一次性处理，或用循环逐个调用 |
| 7 | **忽略 caption.py 返回的错误**：脚本返回 error 字段时仍继续后续解析 | 检查返回的 `error` 字段，非空则停止并报告给用户 |
| 8 | **对不支持格式强行处理**：对 .svg/.pdf/.tiff 等格式调用 caption | 先检查 `SUPPORTED_EXTENSIONS`，不支持则提示用户转换格式 |
| 9 | **在未确认 API Key 可用时开始批处理**：批量处理前不验证单张图片 | 先用单张图片测试 caption 成功，再启动 `--batch` |

## Overview

本 skill 通过 SenseNova Vision API (`scripts/caption.py`) 将图片转为结构化文本描述，然后解析为 DataFrame、可视化或导出为 Excel/CSV。

核心依赖：`scripts/caption.py` — 预配置的 vision model 调用脚本，支持自动类型检测、图片压缩、结果缓存和批量处理。

---

## Numbered Workflow — 标准操作流程

### Step 1: 接收任务并判断触发条件

**输入**：用户消息（可能包含图片路径或触发词）

**操作**：
- 检查用户消息是否包含图片文件路径（.png/.jpg/.jpeg/.gif/.webp/.bmp）
- 检查是否出现触发词：图片分析/图表提取/表格识别/OCR/图片描述/截图分析/图表数据/提取图片中的数据/图片转表格/识别图片/图像理解/图片识别/caption/图像提取/数据提取
- 判断任务类型：单张图片分析 / 批量图片处理 / 图表数据提取 / 表格 OCR / UI 分析 / 流程图解析

**输出**：确认的任务类型 + 图片路径列表

> **If** 用户未提供图片路径且消息中无图片 → **Then** 提示用户提供图片文件路径
>
> **If** 用户要求的是图片编辑（裁剪/滤镜/缩放）或图片生成 → **Then** 告知用户本 skill 不支持，建议使用其他工具
>
> **If** 图片格式不在 SUPPORTED_EXTENSIONS 中 → **Then** 提示用户转换为 .png/.jpg 等支持格式

### Step 2: 🔴 CHECKPOINT — 确认 API 配置与单张测试

**输入**：图片路径

**操作**：
1. 确认 `SN_API_KEY` 环境变量已设置（或 `SN_VISION_API_KEY`）
2. 对**单张图片**执行 `scripts/caption.py <image> --json` 验证 API 可用
3. 检查返回结果中无 `error` 字段

```bash
python3 scripts/caption.py /path/to/image.png --json
```

**输出**：API 可用性确认（True/False）

> **If** 返回 `error` 或 API 调用失败 → **Then** 检查 `SN_API_KEY` 环境变量，提示用户配置 API Key
>
> **If** 返回正常 JSON 含 `description` → **Then** 继续下一步

### Step 3: 根据图片类型选择 Prompt 并执行 Caption

**输入**：图片路径 + 图片类型判断结果

**操作**：
- 根据图片类型选择对应 prompt（参考下方 Prompt Strategy 表）
- 执行 caption 命令：

```bash
# 单张图片 — 结构化输出
python3 scripts/caption.py <image> --json --prompt "<类型专用 prompt>"

# 批量处理
python3 scripts/caption.py <dir> --batch --output /mnt/data/captions.json
```

**输出**：JSON 对象 `{file, type, description, usage, cached}`

> **If** `type` 检测错误（如表格被识别为 chart） → **Then** 重新调用并手动指定 `--prompt`
>
> **If** `cached: true` → **Then** 直接使用缓存结果，无需等待 API
>
> **If** description 以 `Error:` 开头 → **Then** 检查网络/API Key，重试最多 3 次（脚本内置重试）

### Step 4: 🔴 CHECKPOINT — 验证 Caption 结果质量

**输入**：caption 返回的 description 文本

**操作**：
- 检查 description 是否包含 Markdown 表格（含 `|` 分隔符）
- 检查关键数据是否完整（表头存在、行数合理）
- 对于图表：检查数值数量是否与可见柱/线/扇区匹配
- 对于表格：检查行列数与原始截图是否一致

**输出**：质量评估结果（Pass / 需重新 Caption）

> **If** 数据明显不完整或格式错误 → **Then** 调整 `--prompt`（更具体）后重新 caption
>
> **If** 表格截断（行数不足） → **Then** 分两次 caption 分别提取前后半部分
>
> **If** 质量 Pass → **Then** 继续下一步

### Step 5: 解析 Caption 结果为结构化数据

**输入**：caption description 文本（Markdown 表格格式）

**操作**：
- 使用 `parse_markdown_table()` 函数将 Markdown 表格解析为 pandas DataFrame
- 自动数值转换（去除逗号、百分号处理）
- 可选：合并多个 caption 结果（多图片批处理场景）

```python
import pandas as pd

def parse_markdown_table(text):
    lines = text.strip().split('\n')
    table_lines = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if '|' in stripped:
            in_table = True
            table_lines.append(stripped)
        elif in_table:
            break

    data_lines = []
    for l in table_lines:
        cells = [c.strip() for c in l.split('|') if c.strip()]
        if cells and not all(set(c) <= set('-: ') for c in cells):
            data_lines.append(cells)

    if len(data_lines) < 2:
        return None

    header = data_lines[0]
    rows = [r for r in data_lines[1:] if len(r) == len(header)]
    df = pd.DataFrame(rows, columns=header)

    # Auto numeric conversion
    for col in df.columns:
        try:
            cleaned = df[col].str.replace(',', '').str.strip()
            if cleaned.str.endswith('%').any():
                df[col] = pd.to_numeric(cleaned.str.rstrip('%'), errors='coerce')
            else:
                converted = pd.to_numeric(cleaned, errors='coerce')
                if converted.notna().sum() > len(df) * 0.5:
                    df[col] = converted
        except Exception:
            pass
    return df
```

**输出**：pandas DataFrame 或 None（解析失败）

> **If** `parse_markdown_table()` 返回 None → **Then** description 不含有效表格，尝试重新 caption 或直接展示原始文本描述
>
> **If** 数值列转换后大部分为 NaN → **Then** 检查 caption description 格式，可能需调整 prompt 要求更规范的表格输出

### Step 6: 🔴 CHECKPOINT — 确认后续操作方向

**输入**：解析后的 DataFrame + 用户原始需求

**操作**：根据用户需求选择后续操作路径

**输出**：选定的操作方向

> **If** 用户只需提取数据 → **Then** 直接展示 DataFrame 或导出 Excel/CSV（跳至 Step 7 导出部分）
>
> **If** 用户需要重新生成可视化 → **Then** 执行 Visualization 代码块（先设中文字体）
>
> **If** 用户需要多图片合并分析 → **Then** 重复 Step 3-5 处理所有图片，合并 DataFrame

### Step 7: 导出结果（Excel / CSV / 可视化图表）

**输入**：DataFrame

**操作**：

**导出 Excel**：
```python
from openpyxl.styles import Font, PatternFill, Alignment

output_path = "/mnt/data/result.xlsx"
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='提取数据')
    ws = writer.sheets['提取数据']
    fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = fill
        cell.alignment = Alignment(horizontal='center')
    for i, col in enumerate(df.columns, 1):
        w = max(df[col].astype(str).str.len().max(), len(str(col))) + 2
        ws.column_dimensions[chr(64 + i)].width = min(w * 1.2, 40)

print(f"[下载](sandbox:{output_path})")
```

**生成可视化图表**（必须先设中文字体）：
```python
import matplotlib.pyplot as plt
import matplotlib
import os

# ⚠️ MANDATORY — 中文显示配置
font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
if os.path.exists(font_path):
    matplotlib.rcParams['font.family'] = 'WenQuanYi Zen Hei'
matplotlib.rcParams['axes.unicode_minus'] = False

COLORS = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD']

# ... plotting code ...

plt.savefig('/mnt/data/chart.png', dpi=150, bbox_inches='tight')
plt.show()
print("![图表](sandbox:/mnt/data/chart.png)")
```

**输出**：Excel/CSV 文件路径 或 可视化图表

> **If** matplotlib 图表中文乱码 → **Then** 检查中文字体路径是否存在，确认 `font.family` 设置正确
>
> **If** Excel 列宽异常 → **Then** 检查 DataFrame 列名是否含特殊字符，调整列宽计算逻辑

---

## scripts/caption.py — Image Caption

脚本通过 SenseNova Vision API 将图片转为文本描述。配置方式：设置 `SN_API_KEY`（最低要求），或使用 `SN_VISION_API_KEY` / `SN_VISION_BASE_URL` / `SN_VISION_MODEL` 进行精细控制。完整 fallback 链见环境变量规范。

### Usage

```bash
# Basic — get text description
python3 scripts/caption.py /mnt/data/image.png

# Custom prompt — guide what to extract
python3 scripts/caption.py /mnt/data/chart.png --prompt "提取所有数值，Markdown 表格格式"

# JSON output — includes detected type, usage stats, cache info
python3 scripts/caption.py /mnt/data/image.png --json

# Batch — process all images in a directory
python3 scripts/caption.py /mnt/data/images/ --batch --output /mnt/data/captions.json

# Override model (optional)
python3 scripts/caption.py /mnt/data/image.png --model gemini-3.1-flash-lite-preview
```

### Options

| Option | Description |
|--------|------------|
| `--prompt, -p` | Custom prompt (overrides auto-detection) |
| `--model, -m` | Vision model (default: sensenova-6.7-flash-lite) |
| `--json` | Output structured JSON instead of plain text |
| `--batch` | Process all images in a directory |
| `--output, -o` | Output file for batch results |
| `--no-cache` | Skip MD5 cache |

### What it does automatically

- **Type detection**: Detects image type from filename (chart/table/UI/diagram/general) and picks the best prompt
- **Compression**: Images >5MB or >2048px are compressed before sending
- **Caching**: Same image + same prompt → instant cached result, no API cost
- **Error handling**: Retries on failure, returns error message on permanent failure

### JSON output format

```json
{
  "file": "/mnt/data/image.png",
  "type": "chart",
  "description": "这是一张柱状图...",
  "usage": {"prompt_tokens": 1100, "completion_tokens": 400},
  "cached": false
}
```

## Calling from Python

```python
import subprocess, json

CAPTION = "/path/to/skills/sn-da-image-caption/scripts/caption.py"

# Single image
result = subprocess.run(
    ["python3", CAPTION, "/mnt/data/chart.png", "--json",
     "--prompt", "提取图表数据，Markdown 表格输出"],
    capture_output=True, text=True, timeout=60
)
data = json.loads(result.stdout)
description = data["description"]

# Batch
result = subprocess.run(
    ["python3", CAPTION, "/mnt/data/images/", "--batch",
     "--output", "/mnt/data/captions.json"],
    capture_output=True, text=True, timeout=300
)
with open("/mnt/data/captions.json") as f:
    all_captions = json.load(f)
```

## Prompt Strategy

不同图片类型需要不同的 prompt。脚本自动检测类型，但显式指定 `--prompt` 可获得更好结果。

| Image Type | When | Recommended --prompt |
|-----------|------|---------------------|
| Data chart | 柱状图/折线图/饼图 | `"提取图表标题、坐标轴、每个数据点数值、图例。Markdown 表格输出。"` |
| Table screenshot | 表格截图 | `"提取表格所有内容，Markdown 表格格式，保持行列结构，数值不四舍五入。"` |
| UI screenshot | 界面截图 | `"以前端开发者视角描述：布局、组件、文字、颜色。"` |
| Diagram | 流程图/架构图 | `"描述所有节点、连接关系（A→B）、分支条件。"` |
| General | 照片、其他 | 不传 --prompt，用默认 |

## Multi-Image Processing

```python
import glob

image_files = sorted(glob.glob("/mnt/data/*.png"))
all_dfs = []

for img in image_files:
    r = subprocess.run(
        ["python3", CAPTION, img, "--json", "--prompt", "提取数据，Markdown 表格"],
        capture_output=True, text=True, timeout=60
    )
    desc = json.loads(r.stdout)["description"]
    df = parse_markdown_table(desc)
    if df is not None:
        all_dfs.append(df)

combined = pd.concat(all_dfs, ignore_index=True) if all_dfs else None
```

Or batch mode:

```bash
python3 scripts/caption.py /mnt/data/images/ --batch --output /mnt/data/captions.json
```

## Failure Mode Reference — 常见问题速查

| 症状 | 原因 | 解决 |
|------|------|------|
| Caption 返回 `Error:` | API Key 未设置或网络不通 | 检查 `SN_API_KEY`，确认网络可访问 `token.sensenova.cn` |
| 解析后 DataFrame 为空 | Caption 未返回 Markdown 表格 | 调整 `--prompt` 明确要求 "Markdown 表格格式" |
| 中文图表显示方框 | 未设置中文字体 | 在 `plt.savefig()` 前执行中文配置代码块 |
| 大表格数据截断 | 单次 caption token 限制 | 分两次 caption：`"提取前半部分"` + `"提取后半部分"` |
| 数值精度丢失 | Caption prompt 未要求保留精度 | 在 prompt 中加 "数值保持原样，不四舍五入" |
| Batch 模式部分图片失败 | 某张图片格式/大小问题 | 检查失败图片的 `error` 字段，单独处理 |
| Cached 结果与实际不符 | 图片已更新但缓存未失效 | 使用 `--no-cache` 强制重新调用 API |
