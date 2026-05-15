from image_generator import generate_text_image

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from matcher import match_font
from ai_handler import analyze_font_style, generate_feedback
from scoring import score_user_writing

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    image_base64: str

class GenerateRequest(BaseModel):
    text: str
    tags: dict

class ScoreRequest(BaseModel):
    user_image: str
    reference_image: str
    reference_text: str

@app.get("/")
def home():
    return {"message": "Font Mimic Backend is running"}

@app.post("/analyze")
def analyze(data: AnalyzeRequest):
    ai_result = analyze_font_style(data.image_base64)
    matched_font = match_font(ai_result)

    return {
        "ai_tags": ai_result,
        "matched_font": matched_font
    }

@app.post("/generate")
def generate(data: GenerateRequest):
    matched_font = match_font(data.tags)

    image_base64 = generate_text_image(
        text=data.text,
        tags=data.tags,
        font_path=matched_font["file_path"]
    )

    return {
        "generated_image_base64": image_base64,
        "matched_font": matched_font
    }

@app.post("/score")
def score(data: ScoreRequest):
    #新增 reference image
    score_value = score_user_writing(
        reference_image_base64=data.reference_image,
        user_image_base64=data.user_image
    )

    feedback = generate_feedback(
        user_image=data.user_image,
        reference_text=data.reference_text,
        score=score_value
    )

    return {
        "score": score_value,
        "feedback": feedback
    }