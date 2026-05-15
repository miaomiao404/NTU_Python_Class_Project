import base64
import cv2
import numpy as np


def score_user_writing(
    reference_image_base64: str,
    user_image_base64: str
) -> int:
    """
    評分依據：
    1. IoU 像素重疊程度
    2. bounding box 大小相似度
    3. 位置中心相似度
    4. 筆畫量相似度
    """

    reference_img = decode_base64_to_cv2(reference_image_base64)
    user_img = decode_base64_to_cv2(user_image_base64)

    if reference_img is None or user_img is None:
        return 0

    reference_img = normalize_image(reference_img, size=(512, 512))
    user_img = normalize_image(user_img, size=(512, 512))

    reference_binary = binarize_image(reference_img)
    user_binary = binarize_image(user_img)

    if is_blank(user_binary):
        return 0

    iou_score = calculate_iou_score(reference_binary, user_binary)
    size_score = calculate_bbox_size_similarity(reference_binary, user_binary)
    center_score = calculate_center_similarity(reference_binary, user_binary)
    ink_score = calculate_ink_similarity(reference_binary, user_binary)

    final_score = (
        iou_score * 0.45 +
        size_score * 0.20 +
        center_score * 0.20 +
        ink_score * 0.15
    )

    final_score = int(round(final_score))

    return max(0, min(100, final_score))


def decode_base64_to_cv2(base64_str: str):
    """
    將 data:image/png;base64,... 轉成 OpenCV 圖片。
    """

    if not base64_str:
        return None

    try:
        if "," in base64_str:
            base64_str = base64_str.split(",", 1)[1]

        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

        return img

    except Exception:
        return None


def normalize_image(img, size=(512, 512)):
    """
    統一圖片大小與色彩格式。
    """

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    img = cv2.resize(img, size)

    return img


def binarize_image(img):
    """
    將黑字白底圖轉成二值圖。
    筆畫為 255，背景為 0。
    """

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, binary = cv2.threshold(
        gray,
        200,
        255,
        cv2.THRESH_BINARY_INV
    )

    kernel = np.ones((2, 2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return binary


def is_blank(binary) -> bool:
    """
    判斷使用者是否幾乎沒寫東西。
    """

    ink_pixels = np.sum(binary > 0)
    total_pixels = binary.shape[0] * binary.shape[1]

    ink_ratio = ink_pixels / total_pixels

    return ink_ratio < 0.003


def calculate_iou_score(reference_binary, user_binary) -> float:
    """
    計算 reference 和 user 的像素重疊程度。
    IoU = intersection / union
    """

    reference_mask = reference_binary > 0
    user_mask = user_binary > 0

    intersection = np.logical_and(reference_mask, user_mask).sum()
    union = np.logical_or(reference_mask, user_mask).sum()

    if union == 0:
        return 0

    iou = intersection / union

    return iou * 100


def get_bounding_box(binary):
    """
    取得筆畫外接矩形。
    """

    coords = cv2.findNonZero(binary)

    if coords is None:
        return None

    x, y, w, h = cv2.boundingRect(coords)

    return x, y, w, h


def calculate_bbox_size_similarity(reference_binary, user_binary) -> float:
    """
    比較參考字和手寫字的大小是否接近。
    """

    ref_bbox = get_bounding_box(reference_binary)
    user_bbox = get_bounding_box(user_binary)

    if ref_bbox is None or user_bbox is None:
        return 0

    _, _, ref_w, ref_h = ref_bbox
    _, _, user_w, user_h = user_bbox

    ref_area = ref_w * ref_h
    user_area = user_w * user_h

    if ref_area == 0 or user_area == 0:
        return 0

    ratio = min(ref_area, user_area) / max(ref_area, user_area)

    return ratio * 100


def calculate_center_similarity(reference_binary, user_binary) -> float:
    """
    比較參考字和手寫字的中心位置是否接近。
    """

    ref_bbox = get_bounding_box(reference_binary)
    user_bbox = get_bounding_box(user_binary)

    if ref_bbox is None or user_bbox is None:
        return 0

    ref_x, ref_y, ref_w, ref_h = ref_bbox
    user_x, user_y, user_w, user_h = user_bbox

    ref_center = np.array([
        ref_x + ref_w / 2,
        ref_y + ref_h / 2
    ])

    user_center = np.array([
        user_x + user_w / 2,
        user_y + user_h / 2
    ])

    distance = np.linalg.norm(ref_center - user_center)

    max_distance = np.linalg.norm(np.array([512, 512]))

    distance_ratio = distance / max_distance

    score = 100 * (1 - distance_ratio * 2)

    return max(0, min(100, score))


def calculate_ink_similarity(reference_binary, user_binary) -> float:
    """
    比較參考圖和手寫圖的筆畫量是否接近。
    """

    ref_ink = np.sum(reference_binary > 0)
    user_ink = np.sum(user_binary > 0)

    if ref_ink == 0 or user_ink == 0:
        return 0

    ratio = min(ref_ink, user_ink) / max(ref_ink, user_ink)

    return ratio * 100