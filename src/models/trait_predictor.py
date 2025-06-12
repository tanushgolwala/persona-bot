# src/models/trait_predictor.py
import pandas as pd
import numpy as np
import os
import json
from src.integrations.openai_client import LLMClient

class PersonalityTraitPredictor:
    def __init__(self):
        # For a prototype, we'll use a simplified approach with OpenAI integration
        self.openai_client = LLMClient()
        
    def predict(self, features_df):
        """Predict personality traits from features"""
        # The TextAnalyzer now does the heavy lifting by calling OpenAI,
        # so we'll use those values directly with some refinement
        
        predictions = pd.DataFrame()
        
        # Extract the OpenAI predictions which are now in our features
        predictions['openness'] = features_df['openness']
        predictions['conscientiousness'] = features_df['conscientiousness']
        predictions['extraversion'] = features_df['extraversion'] 
        predictions['agreeableness'] = features_df['agreeableness']
        predictions['neuroticism'] = features_df['neuroticism']
        
        # Add a small amount of jitter to create some variation in results
        # This makes the demo more interesting by showing changes over time
        for column in predictions.columns:
            noise = np.random.normal(0, 0.05, size=len(predictions))  # Small Gaussian noise
            predictions[column] = predictions[column] + noise
        
        # Normalize to 0-1 range
        for column in predictions.columns:
            predictions[column] = predictions[column].clip(0, 1)
        
        return predictions