import cv2
import numpy as np
import base64
from PIL import Image, ImageDraw, ImageFont


def render_text_to_image(text: str, font_path: str) -> np.ndarray:
    """
    用 Pillow 把文字畫成基礎圖片。
    回傳 OpenCV 格式圖片。
    """

    image_size = (512, 512)
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)

    font_size = 120
    font = ImageFont.truetype(font_path, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (image_size[0] - text_width) // 2
    y = (image_size[1] - text_height) // 2

    draw.text((x, y), text, font=font, fill="black")

    img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return img_cv2


def apply_style_filters(img: np.ndarray, tags: dict) -> np.ndarray:
    """
    根據 AI tags 套用 OpenCV 後處理。
    """

    style = tags.get("style", [])
    stroke = tags.get("stroke", [])
    mood = tags.get("mood", [])

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
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    if level == "bold":
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=1)

    elif level == "thin":
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.erode(binary, kernel, iterations=1)

    result = 255 - binary
    return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)


def apply_roundness(img: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(img, (3, 3), 0)

    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY)

    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def apply_edge_roughness(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    noise = np.random.normal(0, 12, gray.shape).astype(np.int16)
    noisy = np.clip(gray.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    _, binary = cv2.threshold(noisy, 200, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def apply_ink_bleed(img: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    return blurred


def cv2_to_base64(img: np.ndarray) -> str:
    """
    OpenCV 圖片轉成前端 <img> 可直接顯示的 base64。
    """

    success, buffer = cv2.imencode(".png", img)

    if not success:
        raise ValueError("圖片轉換 base64 失敗")

    img_base64 = base64.b64encode(buffer).decode("utf-8")
    return "data:image/png;base64," + img_base64


def generate_styled_text_base64(text: str, tags: dict, font_path: str) -> str:
    base_img = render_text_to_image(text, font_path)
    styled_img = apply_style_filters(base_img, tags)
    return cv2_to_base64(styled_img)