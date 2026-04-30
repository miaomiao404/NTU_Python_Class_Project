"""
字體庫管理模組
提供字體列表查詢、渲染參照字圖片等功能
"""

import os
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")

# 字體風格標籤（方便前端顯示）
FONT_STYLES = {
    "MaShanZheng-Regular.ttf":           "楷書",
    "ZhiMangXing-Regular.ttf":           "行書",
    "LongCang-Regular.ttf":              "毛草書",
    "ZCOOLQingKeHuangYou-Regular.ttf":   "毛筆行楷",
    "ZCOOLKuaiLe-Regular.ttf":           "圓潤黑體",
    "LiuJianMaoCao-Regular.ttf":         "草書",
    "NotoSansTC-Regular.otf":            "黑體",
    "NotoSerifTC-Regular.otf":           "宋體",
    "LXGWWenKai-Regular.ttf":            "半手寫楷書",
    "LXGWWenKaiTC-Regular.ttf":          "半手寫楷書（繁）",
    "jf-openhuninn-2.1.ttf":             "圓體",
    "cwTeXMing-Medium.ttf":              "明體",
    "cwTeXKai-Medium.ttf":               "楷書",
    "cwTeXFangSong-Medium.ttf":          "仿宋體",
    "cwTeXYen-Medium.ttf":               "圓體",
    "SourceHanSansTC-Regular.otf":       "黑體（思源）",
    "SourceHanSerifTC-Regular.otf":      "宋體（思源）",
    "qiji.ttf":                          "明朝（木刻古典）",
    "Iansui-Regular.ttf":                "手寫楷書",
    "StudyMing-Regular.ttf":             "明體（教育）",
    "zpix.ttf":                          "像素體",
    "TW-Sung-98_1.ttf":                  "宋體（全字庫）",
    "TW-Kai-98_1.ttf":                   "楷書（全字庫）",
}


def list_fonts() -> list[dict]:
    """
    回傳所有可用字體的清單
    每項包含 {"filename": ..., "style": ..., "path": ...}
    """
    results = []
    if not os.path.isdir(FONTS_DIR):
        return results
    for filename in sorted(os.listdir(FONTS_DIR)):
        if filename.lower().endswith((".ttf", ".otf")):
            results.append({
                "filename": filename,
                "style": FONT_STYLES.get(filename, "未分類"),
                "path": os.path.join(FONTS_DIR, filename),
            })
    return results


def get_font_path(filename: str) -> str | None:
    """根據字體檔名取得完整路徑，找不到回傳 None"""
    path = os.path.join(FONTS_DIR, filename)
    return path if os.path.isfile(path) else None


def render_reference(
    char: str,
    font_filename: str,
    img_size: int = 256,
    font_size: int = 200,
    bg_color: int = 255,
    text_color: int = 0,
) -> Image.Image:
    """
    用指定字體渲染單一文字，回傳灰階 PIL Image。

    Args:
        char: 要渲染的單一文字
        font_filename: fonts/ 資料夾內的字體檔名
        img_size: 輸出圖片尺寸（正方形）
        font_size: 字體大小（像素）
    """
    font_path = get_font_path(font_filename)
    if font_path is None:
        raise FileNotFoundError(f"找不到字體: {font_filename}，請先執行 download_fonts.py")

    img = Image.new("L", (img_size, img_size), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        raise RuntimeError(f"載入字體失敗 ({font_filename}): {e}")

    # 置中排版
    bbox = draw.textbbox((0, 0), char, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (img_size - w) // 2 - bbox[0]
    y = (img_size - h) // 2 - bbox[1]
    draw.text((x, y), char, fill=text_color, font=font)
    return img


def render_reference_bytes(char: str, font_filename: str, img_size: int = 256) -> bytes:
    """渲染文字並回傳 PNG bytes（方便 Flask 直接回傳）"""
    import io
    img = render_reference(char, font_filename, img_size)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


if __name__ == "__main__":
    # 快速測試：印出所有可用字體
    fonts = list_fonts()
    if not fonts:
        print("fonts/ 資料夾是空的，請先執行 download_fonts.py")
    else:
        print(f"找到 {len(fonts)} 套字體:")
        for f in fonts:
            print(f"  [{f['style']}] {f['filename']}")
