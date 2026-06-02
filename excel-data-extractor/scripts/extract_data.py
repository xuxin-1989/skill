"""
Excel 数据提取脚本 - 完整交互版
功能：
  1. 交互式选择文件
  2. 序号/字段名双模式选择列
  3. 多格式导出（Excel + JSON + CSV，方便二次处理）

用法：python extract_data.py [文件路径]
"""

import pandas as pd
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 常用目录
DEFAULT_DIRS = [
    "D:/编程",
    "D:/",
    "C:/Users/Administrator/Desktop",
    "C:/Users/Administrator/Downloads",
]

def find_excel_files(directory):
    """查找目录下所有Excel文件"""
    excel_files = []
    for ext in ['*.xlsx', '*.xls', '*.xlsm']:
        excel_files.extend(Path(directory).glob(ext))
    return sorted(set(excel_files))

def select_file_interactive():
    """交互式选择文件"""
    print("\n" + "="*60)
    print("📁 选择文件目录：")
    print("="*60)
    
    all_files = {}
    for directory in DEFAULT_DIRS:
        files = find_excel_files(directory)
        if files:
            print(f"\n📂 {directory}")
            for j, f in enumerate(files[:10], 1):
                idx = len(all_files) + 1
                all_files[idx] = f
                print(f"   [{idx}] {f.name}")
            if len(files) > 10:
                print(f"   ... 还有 {len(files)-10} 个文件")
    
    if not all_files:
        print("\n❌ 未找到任何Excel文件！")
        return None
    
    print("\n" + "-"*60)
    print("请输入文件序号（1-{}），或直接输入完整路径：".format(len(all_files)))
    print("输入 q 退出")
    print("-"*60)
    
    while True:
        choice = input("\n> ").strip()
        
        if choice.lower() == 'q':
            return None
        
        if not choice:
            continue
        
        try:
            idx = int(choice)
            if idx in all_files:
                return str(all_files[idx])
        except ValueError:
            pass
        
        if Path(choice).exists() and Path(choice).is_file():
            return choice
        
        print("⚠️ 无效选择，请重新输入")

def fuzzy_match(user_input, available_columns):
    """模糊匹配字段名"""
    user_fields = [f.strip() for f in user_input.split(',') if f.strip()]
    found, missing = [], []
    
    for field in user_fields:
        if field in available_columns:
            found.append(field)
        else:
            matches = [c for c in available_columns if field in c or c in field]
            if matches:
                found.append(min(matches, key=len))
            else:
                missing.append(field)
    
    return found, missing

def parse_numbers(user_input, max_num):
    """解析序号选择"""
    selected = set()
    parts = [p.strip() for p in user_input.split(',') if p.strip()]
    
    for part in parts:
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                selected.update(range(start, end + 1))
            except:
                pass
        else:
            try:
                selected.add(int(part))
            except:
                pass
    
    return sorted([n for n in selected if 1 <= n <= max_num])

def display_columns(columns):
    """分列显示字段及序号"""
    print(f"\n{'='*60}")
    print(f"📋 可用字段（共 {len(columns)} 个）：")
    print('='*60)
    
    for i in range(0, len(columns), 2):
        left = f"{i+1}. {columns[i]}"
        right = f"{i+2}. {columns[i+1]}" if i+1 < len(columns) else ''
        print(f"  {left:<28}{right}")

def to_json_serializable(obj):
    """转换为JSON可序列化类型"""
    if pd.isna(obj):
        return None
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    if isinstance(obj, pd.Series):
        return obj.tolist()
    return obj

def extract_and_save(df, selected_cols, file_path):
    """提取并保存数据（多格式）"""
    result = df[selected_cols].copy()
    original = Path(file_path)
    base_name = original.stem
    out_dir = original.parent
    
    # 1. 保存Excel（人类查看）
    excel_path = out_dir / f"{base_name}_提取结果.xlsx"
    result.to_excel(excel_path, index=False)
    print(f"💾 Excel: {excel_path}")
    
    # 2. 保存JSON（脚本处理）- 标准化结构
    json_path = out_dir / f"{base_name}_提取结果.json"
    json_data = {
        "meta": {
            "source": str(original.name),
            "extract_time": datetime.now().isoformat(),
            "total_rows": len(result),
            "columns": selected_cols
        },
        "data": []
    }
    
    for _, row in result.iterrows():
        record = {col: to_json_serializable(row[col]) for col in selected_cols}
        json_data["data"].append(record)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON:  {json_path}")
    
    # 3. 保存CSV（通用格式）
    csv_path = out_dir / f"{base_name}_提取结果.csv"
    result.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"💾 CSV:   {csv_path}")
    
    # 4. 保存字段定义（方便脚本解析）
    schema_path = out_dir / f"{base_name}_提取结果_字段.json"
    schema = {
        "columns": [
            {
                "name": col,
                "dtype": str(result[col].dtype),
                "sample": to_json_serializable(result[col].iloc[0]) if len(result) > 0 else None
            }
            for col in selected_cols
        ]
    }
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    print(f"💾 字段定义: {schema_path}")
    
    # 显示预览
    print(f"\n{'='*60}")
    print(f"✅ 提取完成（共 {len(result)} 行，{len(selected_cols)} 列）")
    print('='*60)
    print(result.to_string(index=False))
    
    return result

def main():
    # 文件选择
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            file_path = None
    else:
        file_path = None
    
    while file_path is None:
        file_path = select_file_interactive()
        if file_path is None:
            print("已退出")
            return
    
    # 读取
    print(f"\n📖 正在读取: {file_path}")
    try:
        df = pd.read_excel(file_path, header=0)
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    
    columns = list(df.columns)
    print(f"✅ 读取成功！共 {len(df)} 行数据")
    
    display_columns(columns)
    
    print("\n" + "="*60)
    print("【选择方式】")
    print("  序号模式: 输入数字，如 1,3,5 或 1-5")
    print("  名称模式: 输入字段名，如 姓名,身份证,银行卡")
    print("  退出: 输入 q")
    print("="*60)
    
    while True:
        print("\n请输入序号或字段名: ", end='')
        user_input = input().strip()
        
        if user_input.lower() == 'q':
            print("已退出")
            break
        
        if not user_input:
            continue
        
        selected_cols = []
        
        nums = parse_numbers(user_input, len(columns))
        if nums:
            selected_cols = [columns[n-1] for n in nums]
            print(f"已选择: {', '.join(selected_cols)}")
        else:
            found, missing = fuzzy_match(user_input, columns)
            if missing:
                print(f"⚠️ 未找到: {', '.join(missing)}")
            if found:
                selected_cols = found
                print(f"已匹配: {', '.join(found)}")
            else:
                print("❌ 无法识别的输入")
                continue
        
        if selected_cols:
            extract_and_save(df, selected_cols, file_path)
            break

if __name__ == '__main__':
    main()
