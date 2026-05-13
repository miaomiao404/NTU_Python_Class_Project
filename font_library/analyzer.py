"""
字體分析與匹配模組

流程：
  1. analyze_image(img) → 分析圖片，回傳五項 1-5 分數
  2. match_font(scores)  → 比對 font_scores.json，找出最像的字體
"""

import json
import os
import io
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
_DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY")

SCORES_PATH = os.path.join(os.path.dirname(__file__), "font_scores.json")


# ── 內部工具 ─────────────────────────────────────────────────────────

def _to_gray_array(img: Image.Image, size=(256, 256)) -> np.ndarray:
    return np.array(img.convert("L").resize(size))


def _ink_bbox(arr: np.ndarray) -> tuple:
    """取實際墨水範圍的 bounding box，回傳 (x1, y1, x2, y2)"""
    rows = np.any(arr < 128, axis=1)
    cols = np.any(arr < 128, axis=0)
    if not rows.any() or not cols.any():
        return 0, 0, arr.shape[1], arr.shape[0]
    y1, y2 = np.where(rows)[0][[0, -1]]
    x1, x2 = np.where(cols)[0][[0, -1]]
    return int(x1), int(y1), int(x2), int(y2)


def _score_weight(black_ratio: float) -> int:
    """筆畫黑色像素比例 → 粗細分數"""
    if black_ratio < 0.10: return 1
    if black_ratio < 0.20: return 2
    if black_ratio < 0.35: return 3
    if black_ratio < 0.50: return 4
    return 5


def _score_spacing(white_ratio: float) -> int:
    """空白像素比例 → 間距分數（標楷體基準 0.847 = 3）"""
    if white_ratio < 0.70: return 1
    if white_ratio < 0.80: return 2
    if white_ratio < 0.90: return 3
    if white_ratio < 0.95: return 4
    return 5


def _score_aspect(ratio: float) -> int:
    """墨水範圍寬高比 → 字寬高比分數（標楷體基準 0.938 = 3）"""
    if ratio < 0.65: return 1
    if ratio < 0.85: return 2
    if ratio < 1.06: return 3
    if ratio < 1.25: return 4
    return 5


# ── Gemini 評估圓潤度與斜體 ──────────────────────────────────────────

def _gemini_scores(img: Image.Image, api_key: str) -> dict:
    """呼叫 Gemini，回傳圓潤度和斜體的 1-5 分數"""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return {"roundness": 3, "slant": 1}

    client = genai.Client(api_key=api_key)

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")

    prompt = (
        "這是一張中文字體的圖片。請針對以下兩個維度，各給出 1 到 5 的整數分數。\n\n"
        "【圓潤度】筆畫轉角與端點的圓弧程度：\n"
        "  1 = 極銳利（尖角、切直端點，如宋體勾角）\n"
        "  2 = 略有稜角\n"
        "  3 = 中等（部分圓弧部分稜角）\n"
        "  4 = 圓潤（轉角明顯帶弧度）\n"
        "  5 = 極圓潤（像泡泡字）\n\n"
        "【斜體】字體整體向右傾斜程度：\n"
        "  1 = 完全垂直\n"
        "  2 = 微微傾斜\n"
        "  3 = 明顯傾斜（約 10-15 度）\n"
        "  4 = 大幅傾斜（約 15-25 度）\n"
        "  5 = 極度傾斜\n\n"
        "請只回傳 JSON，不要有其他文字：\n"
        "{\"roundness\": <1-5>, \"slant\": <1-5>}"
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"),
        ],
    )

    try:
        text = response.text.strip()
        if "```" in text:
            text = text.split("```")[1].lstrip("json").strip()
        result = json.loads(text)
        return {
            "roundness": max(1, min(5, int(result.get("roundness", 3)))),
            "slant":     max(1, min(5, int(result.get("slant", 1)))),
        }
    except Exception:
        return {"roundness": 3, "slant": 1}


# ── 主要函式 1：分析圖片 ──────────────────────────────────────────────

def analyze_image(img: Image.Image, api_key: str = None) -> dict:
    """
    分析上傳的字體圖片，回傳五項 1-5 分數。

    Args:
        img:     使用者上傳的字體圖片（PIL Image）
        api_key: Gemini API Key（用於圓潤度和斜體；不填則這兩項給預設值）

    回傳:
        {
            "weight":    int,  # 粗細    1=極細  5=極粗
            "roundness": int,  # 圓潤度  1=極銳利 5=極圓潤
            "slant":     int,  # 斜體    1=垂直  5=極斜
            "spacing":   int,  # 間距    1=極密  5=極疏
            "aspect":    int,  # 字寬高比 1=極窄  5=極寬
        }
    """
    api_key = api_key or _DEFAULT_API_KEY
    arr = _to_gray_array(img)

    x1, y1, x2, y2 = _ink_bbox(arr)
    region = arr[y1:y2, x1:x2]
    w, h = x2 - x1, y2 - y1

    if region.size == 0 or h == 0:
        return {"weight": 3, "roundness": 3, "slant": 1, "spacing": 3, "aspect": 3}

    black = int(np.sum(region < 128))
    total = region.size

    scores = {
        "weight":  _score_weight(black / total),
        "spacing": _score_spacing((total - black) / total),
        "aspect":  _score_aspect(w / h),
    }

    if api_key:
        ai = _gemini_scores(img, api_key)
        scores["roundness"] = ai["roundness"]
        scores["slant"]     = ai["slant"]
    else:
        scores["roundness"] = 3
        scores["slant"]     = 1

    return scores


# ── 主要函式 2：比對字體 ──────────────────────────────────────────────

def match_font(scores: dict) -> dict:
    """
    根據五項分數，從 font_scores.json 找出最接近的字體。
    比對方式：各項分數差距絕對值加總，最小者為最佳配對。

    Args:
        scores: analyze_image() 的回傳值

    回傳:
        {
            "font_name": str,   # 字體名稱
            "filename":  str,   # 檔名（給秈穎用）
            "scores":    dict,  # 該字體的五項分數
            "distance":  int,   # 與輸入的總差距（越小越像）
        }
    """
    with open(SCORES_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    keys = ["weight", "roundness", "slant", "spacing", "aspect"]

    best = None
    best_dist = float("inf")

    for font in registry:
        dist = sum(abs(scores.get(k, 3) - font["scores"].get(k, 3)) for k in keys)
        if dist < best_dist:
            best_dist = dist
            best = font

    return {
        "font_name": best["font_name"],
        "filename":  best["filename"],
        "scores":    best["scores"],
        "distance":  best_dist,
    }


# ── 快速測試 ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    from font_library import render_reference, list_fonts

    fonts = list_fonts()
    if not fonts:
        print("請先執行 download_fonts.py")
    else:
        # 用第一套字體渲染「永」當作測試圖
        test_font = fonts[0]["filename"]
        img = render_reference("永", test_font)

        print(f"測試字體：{test_font}")
        scores = analyze_image(img)
        print(f"分析結果：{scores}")

        result = match_font(scores)
        print(f"\n最像的字體：{result['font_name']}")
        print(f"檔名：{result['filename']}")
        print(f"總差距：{result['distance']}")
