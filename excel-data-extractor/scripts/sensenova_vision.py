"""
SenseNova Vision API 调用脚本
用法：python sensenova_vision.py <图片路径> [--prompt "提示词"] [--text]

功能：
- 自动压缩大图片（避免token超限）
- 输出JSON供脚本二次处理
- API密钥自动从环境变量读取
"""

import base64
import io
import json
import os
import sys
import requests
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ─── API 配置 ──────────────────────────────────────────────────────
API_KEY = (
    os.environ.get("SN_VISION_API_KEY")
    or os.environ.get("SN_API_KEY")
    or ""
)
API_BASE = os.environ.get("SN_VISION_BASE_URL") or "https://token.sensenova.cn/v1"
MODEL = os.environ.get("SN_VISION_MODEL") or "sensenova-6.7-flash-lite"

SUPPORTED = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
MAX_PIXELS = 1024  # 最长边最大像素（控制token量）


def compress_image(file_path: str) -> tuple:
    """
    压缩图片，返回 (base64字符串, mime类型)
    图片过大时自动缩小至最长边≤MAX_PIXELS，确保token不超限
    """
    ext = Path(file_path).suffix.lower()
    mime_map = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp',
    }
    mime = mime_map.get(ext, 'image/png')

    if not HAS_PIL:
        # 无Pillow，直接读取（可能因大图失败）
        with open(file_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        return b64, mime

    img = Image.open(file_path)
    w, h = img.size

    # 压缩：最长边不超过MAX_PIXELS
    if max(w, h) > MAX_PIXELS:
        ratio = MAX_PIXELS / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 转为RGB（JPEG不支持RGBA）
    if img.mode in ('RGBA', 'P', 'LA'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        bg.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
        img = bg

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return b64, 'image/jpeg'


def call_vision_api(
    image_path: str,
    prompt: str = "请详细描述这张图片的内容",
    system_prompt: str = "你是一个说话客观公正的小助手",
    max_tokens: int = 1000,
) -> dict:
    """调用 SenseNova Vision API"""

    if not Path(image_path).exists():
        return {"error": f"文件不存在: {image_path}"}
    ext = Path(image_path).suffix.lower()
    if ext not in SUPPORTED:
        return {"error": f"不支持的格式: {ext}"}
    if not API_KEY:
        return {"error": "未配置API密钥"}

    # 图片压缩 → Base64
    b64, mime = compress_image(image_path)
    data_url = f"data:{mime};base64,{b64}"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        "n": 1,
        "stream": False,
        "max_tokens": max_tokens,
        "reasoning_effort": "none",
    }

    try:
        resp = requests.post(
            f"{API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=120,
        )
        if resp.status_code != 200:
            detail = ""
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text[:500]
            return {"error": f"请求失败 ({resp.status_code})", "detail": detail}
        result = resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"请求失败: {e}"}

    try:
        text = result["choices"][0]["message"]["content"]
        usage = {
            "prompt_tokens": result.get("usage", {}).get("prompt_tokens", 0),
            "completion_tokens": result.get("usage", {}).get("completion_tokens", 0),
        }
    except (KeyError, IndexError) as e:
        return {"error": f"解析响应失败: {e}", "raw": result}

    return {
        "description": text,
        "usage": usage,
        "image": Path(image_path).name,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="SenseNova Vision API 调用")
    parser.add_argument("image_path", help="图片文件路径")
    parser.add_argument("--prompt", "-p", default="请详细描述这张图片的内容",
                        help="自定义提示词")
    parser.add_argument("--system", "-s", default="你是一个说话客观公正的小助手",
                        help="System提示词")
    parser.add_argument("--max-tokens", type=int, default=1000,
                        help="最大token数")
    parser.add_argument("--json", action="store_true",
                        help="输出JSON格式（默认）")
    parser.add_argument("--text", action="store_true",
                        help="只输出描述文本")
    args = parser.parse_args()

    result = call_vision_api(
        args.image_path,
        prompt=args.prompt,
        system_prompt=args.system,
        max_tokens=args.max_tokens,
    )

    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    if args.text:
        print(result["description"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
