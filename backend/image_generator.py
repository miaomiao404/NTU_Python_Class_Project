from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO


def generate_text_image(text: str):
    # 建立白底圖片
    img = Image.new("RGB", (500, 250), color="white")
    draw = ImageDraw.Draw(img)

    # 先用系統預設字體
    font = ImageFont.load_default()

    # 畫文字
    draw.text((200, 100), text, fill="black", font=font)

    # 轉成 base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return "data:image/png;base64," + img_base64