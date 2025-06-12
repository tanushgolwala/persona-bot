# src/api/endpoints.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import os

from src.collectors.social_media import SocialMediaCollector
from src.processors.text_analysis import TextAnalyzer
from src.models.trait_predictor import PersonalityTraitPredictor
from src.models.persona_evolve import DynamicPersonaGenerator

# Initialize FastAPI app
app = FastAPI(title="Dynamic Persona API")

# Initialize components
social_collector = SocialMediaCollector()
text_analyzer = TextAnalyzer()
trait_predictor = PersonalityTraitPredictor()
persona_generator = DynamicPersonaGenerator()

# Load any existing persona data
persona_generator.load_personas()

# Data models for API
class TextAnalysisRequest(BaseModel):
    texts: List[str]
    user_id: str

class SocialMediaRequest(BaseModel):
    username: str
    platform: str
    user_id: str

class PersonaResponse(BaseModel):
    user_id: str
    persona: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Welcome to Dynamic Persona API"}

@app.post("/analyze-text", response_model=PersonaResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text and update user persona"""
    try:
        # Extract features from texts
        features = text_analyzer.extract_linguistic_features(request.texts)
        features_df = pd.DataFrame({k: features[k] for k in features})
        
        # Predict personality traits
        traits_df = trait_predictor.predict(features_df)
        
        # Get average of predictions
        avg_traits = traits_df.mean().to_dict()
        
        # Generate or update persona
        persona = persona_generator.generate_user_persona(request.user_id, avg_traits)
        
        return {"user_id": request.user_id, "persona": persona}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-social", response_model=PersonaResponse)
async def analyze_social_media(request: SocialMediaRequest):
    """Analyze social media data and update user persona"""
    try:
        # Collect posts
        posts = social_collector.collect_user_data(request.username, request.platform)
        
        if posts:
            # Extract text from posts
            texts = [post.get('text', '') for post in posts]
            
            # Extract features
            features = text_analyzer.extract_linguistic_features(texts)
            features_df = pd.DataFrame({k: features[k] for k in features})
            
            # Predict traits
            traits_df = trait_predictor.predict(features_df)
            
            # Get average of predictions
            avg_traits = traits_df.mean().to_dict()
            
            # Generate or update persona
            persona = persona_generator.generate_user_persona(request.user_id, avg_traits)
            
            return {"user_id": request.user_id, "persona": persona}
        else:
            raise HTTPException(status_code=404, detail=f"No posts found for {request.username} on {request.platform}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/persona/{user_id}", response_model=PersonaResponse)
async def get_persona(user_id: str):
    """Get a user's persona"""
    if user_id in persona_generator.user_personas:
        return {"user_id": user_id, "persona": persona_generator.user_personas[user_id]}
    else:
        raise HTTPException(status_code=404, detail=f"No persona found for user {user_id}")

@app.get("/personas", response_model=Dict[str, Any])
async def get_all_personas(limit: int = Query(10, ge=1, le=100), skip: int = Query(0, ge=0)):
    """Get all personas with pagination"""
    user_ids = list(persona_generator.user_personas.keys())
    
    if not user_ids:
        return {"total": 0, "personas": {}}
    
    user_ids = user_ids[skip:skip+limit]
    
    result = {
        "total": len(persona_generator.user_personas),
        "personas": {uid: persona_generator.user_personas[uid] for uid in user_ids}
    }
    
    return result