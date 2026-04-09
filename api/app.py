"""
AgroCure - FastAPI Backend
Main API server — all routes for FE integration
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from model.predict import predict, load_model
from utils.preprocessing import preprocess_image, validate_image
from utils.weather_api import get_weather
from engine.disease_mapper import get_disease_info
from engine.severity import calculate_severity, calculate_health_score, assess_outbreak_risk
from engine.recommendation import recommend_crops
from chatbot.bot import chat

# ─────────────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AgroCure API",
    description="AI-powered crop disease detection and farming intelligence",
    version="1.0.0",
)

# CORS — allow all origins for hackathon; tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Load ML model on server start."""
    print("[AgroCure] 🌱 Starting AgroCure API...")
    load_model()
    print("[AgroCure] ✅ Ready!")


# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "project": "AgroCure", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 1: DISEASE DETECTION (core feature)
# POST /api/scan
#
# Accepts: image file upload
# Returns: disease label, confidence, severity, treatment, prevention
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/scan")
async def scan_crop(
    image: UploadFile = File(...),
    lat: Optional[float] = Query(None, description="Latitude for weather context"),
    lon: Optional[float] = Query(None, description="Longitude for weather context"),
):
    """
    Main disease detection endpoint.
    Upload a leaf image → get disease diagnosis + treatment recommendations.
    """
    # Read image
    image_bytes = await image.read()

    # Validate
    is_valid, error_msg = validate_image(image_bytes)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # Preprocess
    img_array = preprocess_image(image_bytes)
    if img_array is None:
        raise HTTPException(status_code=422, detail="Failed to process image. Please try again.")

    # ── ML Prediction ─────────────────────────────────────────────────────────
    prediction = predict(img_array)
    label = prediction["label"]
    confidence = prediction["confidence"]

    # ── Disease Info ──────────────────────────────────────────────────────────
    disease_info = get_disease_info(label)

    # ── Severity ──────────────────────────────────────────────────────────────
    severity = calculate_severity(confidence, disease_info.get("urgency"))

    # ── Weather Context (optional) ────────────────────────────────────────────
    weather = None
    if lat is not None and lon is not None:
        weather = await get_weather(lat, lon)

    # ── Build response ────────────────────────────────────────────────────────
    response = {
        "scan_result": {
            "label": label,
            "confidence": confidence,
            "demo_mode": prediction.get("demo_mode", False),
            "top3": prediction.get("top3", []),
        },
        "diagnosis": {
            "crop": disease_info["crop"],
            "disease": disease_info["disease"],
            "display_name": disease_info["display_name"],
            "pathogen": disease_info["pathogen"],
            "is_healthy": disease_info["disease"] is None,
        },
        "severity": severity,
        "recommendations": {
            "treatment": disease_info["treatment"],
            "prevention": disease_info["prevention"],
            "organic_option": disease_info["organic_option"],
        },
        "weather_context": weather,
    }

    return JSONResponse(content=response)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 2: FARM HEALTH ANALYTICS
# POST /api/analytics
#
# Accepts: list of scan results
# Returns: farm health score, outbreak risk, disease breakdown
# ─────────────────────────────────────────────────────────────────────────────

class ScanResult(BaseModel):
    disease: Optional[str] = None
    confidence: float = 0.0


class AnalyticsRequest(BaseModel):
    scan_results: list[ScanResult]


@app.post("/api/analytics")
async def get_analytics(body: AnalyticsRequest):
    """
    Farm-level health analytics from multiple scan results.
    """
    results = [r.dict() for r in body.scan_results]

    health = calculate_health_score(results)
    outbreak = assess_outbreak_risk(results)

    return {
        "health": health,
        "outbreak_risk": outbreak,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 3: CHATBOT
# POST /api/chat
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None    # Optional disease context from last scan
    use_llm: bool = True              # Set False to force rule-based


@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest):
    """
    Farming assistant chatbot.
    Supports rule-based and LLM-powered responses.
    """
    response = chat(body.message, context=body.context, use_llm=body.use_llm)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 4: CROP RECOMMENDATION
# GET /api/recommend
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/recommend")
async def crop_recommend(
    season: Optional[str] = Query(None, description="kharif | rabi | zaid"),
    soil_type: Optional[str] = Query(None, description="loamy | sandy | clay | red | black"),
    water_availability: Optional[str] = Query(None, description="low | medium | high"),
    drought_region: bool = Query(False, description="Is region drought-prone?"),
    top_n: int = Query(4, ge=1, le=10),
):
    """
    Returns ranked crop recommendations based on farmer's conditions.
    """
    recommendations = recommend_crops(
        season=season,
        soil_type=soil_type,
        water_availability=water_availability,
        drought_region=drought_region,
        top_n=top_n,
    )
    return {"recommendations": recommendations}


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE 5: WEATHER
# GET /api/weather?lat=...&lon=...
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/weather")
async def weather_endpoint(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Fetch weather context for a location."""
    weather = await get_weather(lat, lon)
    if weather is None:
        raise HTTPException(status_code=503, detail="Weather service unavailable")
    return weather


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
