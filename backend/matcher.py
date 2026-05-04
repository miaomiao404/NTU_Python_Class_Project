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