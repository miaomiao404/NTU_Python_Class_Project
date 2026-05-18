import json


def load_registry():
    with open("registry.json", "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_score(ai_tags, font_tags):
    score = 0

    for category in ai_tags:
        ai_values = set(ai_tags.get(category, []))
        font_values = set(font_tags.get(category, []))

        matched_tags = ai_values & font_values
        score += len(matched_tags)

    return score


def match_font(ai_tags):
    registry = load_registry()

    best_font = None
    best_score = -1

    for font in registry:
        score = calculate_score(ai_tags, font["tags"])

        if score > best_score:
            best_score = score
            best_font = font

    return {
        "font_name": best_font["font_name"],
        "file_path": best_font["file_path"],
        "score": best_score
    }

# --- 測試啟動區塊 ---
if __name__ == "__main__":
    # 模擬 Gemini AI 看完圖片後，產生的標籤 (可以隨意修改測試)
    mock_ai_input = {
        "style": ["cute", "round"],
        "stroke": ["medium"],
        "spacing": ["loose"],
        "mood": ["warm", "friendly"]
    }
    
    print("🔍 正在接收 AI 標籤，開始匹配字體...")
    
    # 呼叫妳寫好的函數，並把結果存起來
    result = match_font(mock_ai_input)
    
    # 印出結果
    print("\n🎉 匹配完成！")
    print(f"👉 推薦字體：{result['font_name']}")
    print(f"📁 檔案位置：{result['file_path']}")
    print(f"⭐ 吻合分數：{result['score']} 分")