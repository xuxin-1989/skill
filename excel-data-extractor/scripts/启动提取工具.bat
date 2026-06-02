@echo off
chcp 65001 >nul
title Excel数据提取工具
cd /d "%~dp0"
python extract_data.py
pause
