import base64
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

#缺 fonts/jf-openhuninn.ttf
IMAGE_SIZE = (512, 512)
DEFAULT_FONT_PATH = "fonts/cute.ttf"


def generate_text_image(
    text: str,
    tags: dict,
    font_path: str = DEFAULT_FONT_PATH
) -> str:
    """
    1. 使用 Pillow 載入指定中文字體
    2. 將使用者輸入文字置中渲染成白底黑字圖片
    3. 轉成 OpenCV 格式
    4. 根據 AI tags 套用粗細、圓潤、粗糙、暈染等後處理
    5. 轉成 base64 回傳給前端
    """

    base_img = render_text_to_cv2(
        text=text,
        font_path=font_path,
        image_size=IMAGE_SIZE
    )

    styled_img = apply_style_filters(base_img, tags)

    return cv2_to_base64(styled_img)


def render_text_to_cv2(
    text: str,
    font_path: str,
    image_size=(512, 512)
) -> np.ndarray:
    """
    使用 Pillow 將文字渲染成 OpenCV 圖片。
    """

    img = Image.new("RGB", image_size, color="white")
    draw = ImageDraw.Draw(img)

    font = load_font(font_path, text, image_size)

    bbox = draw.textbbox((0, 0), text, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (image_size[0] - text_width) // 2 - bbox[0]
    y = (image_size[1] - text_height) // 2 - bbox[1]

    draw.text((x, y), text, fill="black", font=font)

    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    return cv_img


def load_font(
    font_path: str,
    text: str,
    image_size=(512, 512)
) -> ImageFont.FreeTypeFont:
    """
    載入中文字體。
    如果指定字體不存在，會嘗試使用預設字體路徑。
    """

    candidate_paths = [
        font_path,
        DEFAULT_FONT_PATH,
        os.path.join(os.path.dirname(__file__), font_path),
        os.path.join(os.path.dirname(__file__), DEFAULT_FONT_PATH),
    ]

    selected_font_path = None

    for path in candidate_paths:
        if path and os.path.exists(path):
            selected_font_path = path
            break

    if selected_font_path is None:
        raise FileNotFoundError(
            f"找不到字體檔：{font_path}，也找不到預設字體 {DEFAULT_FONT_PATH}"
        )

    font_size = choose_font_size(
        text=text,
        font_path=selected_font_path,
        image_size=image_size
    )

    return ImageFont.truetype(selected_font_path, font_size)


def choose_font_size(
    text: str,
    font_path: str,
    image_size=(512, 512)
) -> int:
    """
    根據文字長度自動調整字體大小，避免文字超出圖片邊界。
    """

    max_width = int(image_size[0] * 0.82)
    max_height = int(image_size[1] * 0.65)

    for font_size in range(180, 24, -4):
        font = ImageFont.truetype(font_path, font_size)
        dummy_img = Image.new("RGB", image_size, color="white")
        draw = ImageDraw.Draw(dummy_img)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width <= max_width and text_height <= max_height:
            return font_size

    return 32


def apply_style_filters(img: np.ndarray, tags: dict) -> np.ndarray:
    """
    根據 AI tags 套用 OpenCV 後處理。
    """

    style = tags.get("style", [])
    stroke = tags.get("stroke", [])
    mood = tags.get("mood", [])

    if not isinstance(style, list):
        style = [style]

    if not isinstance(stroke, list):
        stroke = [stroke]

    if not isinstance(mood, list):
        mood = [mood]

    if "bold" in stroke:
        img = apply_thickness(img, level="bold")
    elif "thin" in stroke:
        img = apply_thickness(img, level="thin")
    else:
        img = apply_thickness(img, level="medium")

    if "round" in style or "friendly" in mood or "cute" in mood:
        img = apply_roundness(img)

    if "casual" in style or "handwriting" in style:
        img = apply_edge_roughness(img)

    if "calligraphy" in style:
        img = apply_ink_bleed(img)

    return img


def apply_thickness(img: np.ndarray, level: str = "medium") -> np.ndarray:
    """
    使用 dilation / erosion 控制筆畫粗細。
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(
        gray,
        200,
        255,
        cv2.THRESH_BINARY_INV
    )

    if level == "bold":
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)

    elif level == "thin":
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.erode(binary, kernel, iterations=1)

    result = 255 - binary

    return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)


def apply_roundness(img: np.ndarray) -> np.ndarray:
    """
    模擬圓潤邊緣。
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    _, binary = cv2.threshold(
        blurred,
        210,
        255,
        cv2.THRESH_BINARY
    )

    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def apply_edge_roughness(img: np.ndarray) -> np.ndarray:
    """
    模擬 casual / handwriting 的邊緣不規則感。
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    noise = np.random.normal(0, 10, gray.shape).astype(np.int16)
    noisy = np.clip(
        gray.astype(np.int16) + noise,
        0,
        255
    ).astype(np.uint8)

    _, binary = cv2.threshold(
        noisy,
        200,
        255,
        cv2.THRESH_BINARY
    )

    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def apply_ink_bleed(img: np.ndarray) -> np.ndarray:
    """
    模擬書法或墨水暈染效果。
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, binary = cv2.threshold(
        blurred,
        220,
        255,
        cv2.THRESH_BINARY
    )

    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def cv2_to_base64(img: np.ndarray) -> str:
    """
    OpenCV 圖片轉成前端 img 標籤可直接顯示的 base64。
    """

    success, buffer = cv2.imencode(".png", img)

    if not success:
        raise ValueError("圖片轉換 base64 失敗")

    img_base64 = base64.b64encode(buffer).decode("utf-8")

    return "data:image/png;base64," + img_base64