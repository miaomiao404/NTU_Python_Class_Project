from image_generator import generate_text_image

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from matcher import match_font
from ai_handler import analyze_font_style, generate_feedback

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
    image_base64 = generate_text_image(data.text)

    return {
        "generated_image_base64": image_base64
    }

@app.post("/score")
def score(data: ScoreRequest):
    mock_score = 85
    feedback = generate_feedback(
        data.user_image,
        data.reference_text,
        mock_score
    )

    return {
        "score": mock_score,
        "feedback": feedback
    }