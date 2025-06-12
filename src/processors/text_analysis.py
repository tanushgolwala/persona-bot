# src/processors/text_analysis.py
import pandas as pd
import numpy as np
import re
import random
from src.integrations.openai_client import LLMClient
class TextAnalyzer:
    def __init__(self):
        # Word lists for different traits (fallback for when OpenAI is unavailable)
        self.trait_word_lists = {
            'openness': ['creative', 'curious', 'artistic', 'imaginative', 'insightful', 'original', 'wide', 'deep', 'complex', 'inventive', 'new', 'unusual'],
            'conscientiousness': ['organized', 'efficient', 'systematic', 'thorough', 'precise', 'disciplined', 'careful', 'diligent', 'responsible', 'reliable', 'plan', 'detail'],
            'extraversion': ['outgoing', 'energetic', 'talkative', 'active', 'social', 'enthusiastic', 'assertive', 'people', 'group', 'party', 'talk', 'share'],
            'agreeableness': ['kind', 'sympathetic', 'warm', 'helpful', 'generous', 'friendly', 'cooperative', 'considerate', 'caring', 'compassionate', 'supportive', 'nice'],
            'neuroticism': ['worried', 'anxious', 'nervous', 'tense', 'stressed', 'emotional', 'moody', 'feel', 'concerned', 'upset', 'overwhelmed', 'doubt']
        }
        
        # Initialize OpenAI client
        self.llm_client = LLMClient()
        
    def extract_linguistic_features(self, texts):
        """Extract linguistic features from texts using OpenAI for sentiment and personality traits"""
        features = {
            'word_count': [],
            'avg_word_length': [],
            'sentiment': [],
            'openness': [],
            'conscientiousness': [],
            'extraversion': [],
            'agreeableness': [],
            'neuroticism': []
        }
        
        # Get personality trait analysis for all texts combined
        # Note: This is more meaningful when analyzing multiple texts from the same person
        if len(texts) > 0:
            trait_analysis = self.openai_client.analyze_personality_traits(texts)
            
            # Extract values or use defaults if any key is missing
            openness = trait_analysis.get('openness', 0.5)
            conscientiousness = trait_analysis.get('conscientiousness', 0.5)
            extraversion = trait_analysis.get('extraversion', 0.5)
            agreeableness = trait_analysis.get('agreeableness', 0.5)
            neuroticism = trait_analysis.get('neuroticism', 0.5)
        else:
            openness = 0.5
            conscientiousness = 0.5
            extraversion = 0.5
            agreeableness = 0.5
            neuroticism = 0.5
        
        for text in texts:
            # Basic features
            words = re.findall(r'\w+', text.lower())
            features['word_count'].append(len(words))
            
            if words:
                features['avg_word_length'].append(sum(len(w) for w in words) / len(words))
            else:
                features['avg_word_length'].append(0)
            
            # Get sentiment with OpenAI
            sentiment_result = self.openai_client.analyze_sentiment(text)
            sentiment_score = sentiment_result.get('sentiment_score', random.uniform(-1, 1))
            features['sentiment'].append(sentiment_score)
            
            # Use the trait analysis from all texts for each individual text
            # This gives a more coherent profile based on all available data
            features['openness'].append(openness)
            features['conscientiousness'].append(conscientiousness)
            features['extraversion'].append(extraversion)
            features['agreeableness'].append(agreeableness)
            features['neuroticism'].append(neuroticism)
                
        return features