import base64
import cv2
import numpy as np


def decode_base64_to_cv2(base64_str: str):
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]

    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

    return img_cv2


def score_user_writing(user_image_base64: str) -> int:
    """
    Demo 版：
    目前只有 user image，沒有 reference image。
    所以先用簡單的黑色像素完整度估計。
    真正完整版本應該要傳 reference image 進來比對。
    """

    img = decode_base64_to_cv2(user_image_base64)

    if img is None:
        return 0

    img = cv2.resize(img, (512, 512))

    if img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    black_pixels = np.sum(binary > 0)
    total_pixels = binary.shape[0] * binary.shape[1]

    ratio = black_pixels / total_pixels

    if ratio < 0.01:
        return 10

    if ratio > 0.45:
        return 60

    score = int(min(100, max(40, ratio * 400)))

    return score