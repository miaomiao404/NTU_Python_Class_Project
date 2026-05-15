"""
字體分析與匹配模組（全 OpenCV，無 AI API 依賴）

流程：
  1. analyze_image(img) → 分析圖片，回傳五項 1-5 分數
  2. match_font(scores)  → 比對 font_scores.json，找出最像的字體

閾值依據：對 20 套已下載字體實際量測後定出。
"""

import json
import os
import numpy as np
import cv2
from PIL import Image

SCORES_PATH = os.path.join(os.path.dirname(__file__), "font_scores.json")


# ── 內部工具 ─────────────────────────────────────────────────────────

def _to_gray_binary(img: Image.Image, size=(256, 256)) -> np.ndarray:
    """轉灰階後二值化，筆畫為白(255)、背景為黑(0)"""
    arr = np.array(img.convert("L").resize(size))
    _, binary = cv2.threshold(arr, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary


def _ink_bbox(binary: np.ndarray):
    rows = np.any(binary > 0, axis=1)
    cols = np.any(binary > 0, axis=0)
    if not rows.any() or not cols.any():
        return None
    y1, y2 = np.where(rows)[0][[0, -1]]
    x1, x2 = np.where(cols)[0][[0, -1]]
    return int(x1), int(y1), int(x2), int(y2)


# ── 五項測量函式 ──────────────────────────────────────────────────────

def _measure_weight(binary: np.ndarray) -> float:
    """黑色像素（筆畫）佔 bounding box 的比例"""
    bbox = _ink_bbox(binary)
    if bbox is None:
        return 0.2
    x1, y1, x2, y2 = bbox
    region = binary[y1:y2, x1:x2]
    return float(np.sum(region > 0)) / region.size


def _measure_spacing(binary: np.ndarray) -> float:
    """bounding box 內空白像素比例（越高越疏）"""
    bbox = _ink_bbox(binary)
    if bbox is None:
        return 0.75
    x1, y1, x2, y2 = bbox
    region = binary[y1:y2, x1:x2]
    return float(np.sum(region == 0)) / region.size


def _measure_aspect(binary: np.ndarray) -> float:
    """實際墨水範圍寬 ÷ 高"""
    bbox = _ink_bbox(binary)
    if bbox is None:
        return 0.93
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    return w / h if h > 0 else 1.0


def _measure_slant(binary: np.ndarray) -> float:
    """
    PCA 主軸角度（度）：值越高代表結構越直立，值越低代表字形越傾斜或橫向延展。
    量測範圍約 44–88 度。
    """
    coords = np.column_stack(np.where(binary > 0)).astype(np.float32)
    if len(coords) < 20:
        return 70.0
    mean = coords.mean(axis=0)
    centered = coords - mean
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    principal = vt[0]
    angle = np.degrees(np.arctan2(principal[1], principal[0]))
    return float(abs(90 - abs(angle)))


def _measure_roundness(binary: np.ndarray) -> float:
    """輪廓圓形度（4π×面積 ÷ 周長²），越高越圓潤"""
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0.25
    scores = []
    for c in contours:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter > 0 and area > 50:
            scores.append(4 * np.pi * area / (perimeter ** 2))
    return float(np.mean(scores)) if scores else 0.25


# ── 原始值 → 1-5 分 ──────────────────────────────────────────────────
# 閾值依據：20 套字體實際量測後定出

def _score_weight(v: float) -> int:
    if v < 0.18: return 1
    if v < 0.25: return 2
    if v < 0.32: return 3
    if v < 0.43: return 4
    return 5

def _score_spacing(v: float) -> int:
    if v < 0.62:  return 1
    if v < 0.70:  return 2
    if v < 0.755: return 3
    if v < 0.82:  return 4
    return 5

def _score_aspect(v: float) -> int:
    if v < 0.80:  return 1
    if v < 0.93:  return 2
    if v < 0.950: return 3
    if v < 0.968: return 4
    return 5

def _score_slant(v: float) -> int:
    """值越高=越直立=分數越低；值越低=越傾斜/橫向=分數越高"""
    if v > 75: return 1
    if v > 65: return 2
    if v > 57: return 3
    if v > 50: return 4
    return 5

def _score_roundness(v: float) -> int:
    if v < 0.23: return 1
    if v < 0.27: return 2
    if v < 0.32: return 3
    if v < 0.37: return 4
    return 5


# ── 主要函式 1：分析圖片 ──────────────────────────────────────────────

def analyze_image(img: Image.Image) -> dict:
    """
    分析上傳的字體圖片，回傳五項 1-5 分數。

    Args:
        img: 使用者上傳的字體圖片（PIL Image）

    回傳:
        {
            "weight":    int,  # 粗細    1=極細  5=極粗
            "spacing":   int,  # 間距    1=極密  5=極疏
            "aspect":    int,  # 字寬高比 1=極窄  5=極寬
            "slant":     int,  # 斜體    1=直立  5=傾斜
            "roundness": int,  # 圓潤度  1=銳利  5=圓潤
        }
    """
    binary = _to_gray_binary(img)
    return {
        "weight":    _score_weight(_measure_weight(binary)),
        "spacing":   _score_spacing(_measure_spacing(binary)),
        "aspect":    _score_aspect(_measure_aspect(binary)),
        "slant":     _score_slant(_measure_slant(binary)),
        "roundness": _score_roundness(_measure_roundness(binary)),
    }


# ── 主要函式 2：比對字體 ──────────────────────────────────────────────

def match_font(scores: dict) -> dict:
    """
    根據五項分數，從 font_scores.json 找出最接近的字體。
    比對方式：各項分數差距絕對值加總，最小者為最佳配對。

    Args:
        scores: analyze_image() 的回傳值

    回傳:
        {
            "font_name": str,
            "filename":  str,
            "scores":    dict,
            "distance":  int,
        }
    """
    with open(SCORES_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    keys = ["weight", "spacing", "aspect", "slant", "roundness"]
    best, best_dist = None, float("inf")

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
        test_font = fonts[0]["filename"]
        img = render_reference("永", test_font)
        print(f"測試字體：{test_font}")
        scores = analyze_image(img)
        print(f"分析結果：{scores}")
        result = match_font(scores)
        print(f"最像的字體：{result['font_name']}（距離={result['distance']}）")
