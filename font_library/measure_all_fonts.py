"""
量測所有字體的五項原始數值
執行前請先跑 download_fonts.py

執行方式: python measure_all_fonts.py
"""

import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
TEST_CHARS = ["永", "國", "中", "字", "美"]


def render_char(font_path, char, size=256, font_size=200):
    img = Image.new("L", (size, size), 255)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        return None
    bbox = draw.textbbox((0, 0), char, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - w) // 2 - bbox[0]
    y = (size - h) // 2 - bbox[1]
    draw.text((x, y), char, fill=0, font=font)
    return np.array(img)


def ink_bbox(arr):
    rows = np.any(arr < 128, axis=1)
    cols = np.any(arr < 128, axis=0)
    if not rows.any() or not cols.any():
        return None
    y1, y2 = np.where(rows)[0][[0, -1]]
    x1, x2 = np.where(cols)[0][[0, -1]]
    return int(x1), int(y1), int(x2), int(y2)


def measure_weight(arr):
    bbox = ink_bbox(arr)
    if bbox is None:
        return 0.0
    x1, y1, x2, y2 = bbox
    region = arr[y1:y2, x1:x2]
    black = np.sum(region < 128)
    return black / region.size


def measure_spacing(arr):
    bbox = ink_bbox(arr)
    if bbox is None:
        return 1.0
    x1, y1, x2, y2 = bbox
    region = arr[y1:y2, x1:x2]
    white = np.sum(region >= 128)
    return white / region.size


def measure_aspect(arr):
    bbox = ink_bbox(arr)
    if bbox is None:
        return 1.0
    x1, y1, x2, y2 = bbox
    w, h = x2 - x1, y2 - y1
    return w / h if h > 0 else 1.0


def measure_slant(arr):
    binary = (arr < 128).astype(np.uint8) * 255
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 20:
        return 0.0
    mean = coords.mean(axis=0)
    centered = (coords - mean).astype(np.float32)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    principal = vt[0]
    angle = np.degrees(np.arctan2(principal[1], principal[0]))
    slant = abs(90 - abs(angle))
    return round(slant, 2)


def measure_roundness(arr):
    binary = (arr < 128).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0.0
    scores = []
    for c in contours:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter > 0 and area > 50:
            scores.append(4 * np.pi * area / (perimeter ** 2))
    return round(np.mean(scores), 4) if scores else 0.0


def measure_font(font_path):
    results = {"weight": [], "spacing": [], "aspect": [], "slant": [], "roundness": []}
    for char in TEST_CHARS:
        arr = render_char(font_path, char)
        if arr is None:
            continue
        results["weight"].append(measure_weight(arr))
        results["spacing"].append(measure_spacing(arr))
        results["aspect"].append(measure_aspect(arr))
        results["slant"].append(measure_slant(arr))
        results["roundness"].append(measure_roundness(arr))
    return {k: round(float(np.mean(v)), 4) for k, v in results.items() if v}


def main():
    fonts = sorted([
        f for f in os.listdir(FONTS_DIR)
        if f.lower().endswith((".ttf", ".otf"))
    ])

    if not fonts:
        print("fonts/ 資料夾是空的，請先執行 download_fonts.py")
        return

    print(f"{'字體檔名':<45} {'粗細':>8} {'間距':>8} {'寬高比':>8} {'斜體':>8} {'圓潤度':>8}")
    print("-" * 90)

    for filename in fonts:
        path = os.path.join(FONTS_DIR, filename)
        m = measure_font(path)
        print(
            f"{filename:<45} "
            f"{m.get('weight', 0):>8.4f} "
            f"{m.get('spacing', 0):>8.4f} "
            f"{m.get('aspect', 0):>8.4f} "
            f"{m.get('slant', 0):>8.2f} "
            f"{m.get('roundness', 0):>8.4f}"
        )


if __name__ == "__main__":
    main()
