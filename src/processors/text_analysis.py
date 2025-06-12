# src/processors/text_analysis.py
import pandas as pd
import numpy as np
import re
import random

class TextAnalyzer:
    def __init__(self):
        # Word lists for different traits
        self.trait_word_lists = {
            'openness': ['creative', 'curious', 'artistic', 'imaginative', 'insightful', 'original', 'wide', 'deep', 'complex', 'inventive', 'new', 'unusual'],
            'conscientiousness': ['organized', 'efficient', 'systematic', 'thorough', 'precise', 'disciplined', 'careful', 'diligent', 'responsible', 'reliable', 'plan', 'detail'],
            'extraversion': ['outgoing', 'energetic', 'talkative', 'active', 'social', 'enthusiastic', 'assertive', 'people', 'group', 'party', 'talk', 'share'],
            'agreeableness': ['kind', 'sympathetic', 'warm', 'helpful', 'generous', 'friendly', 'cooperative', 'considerate', 'caring', 'compassionate', 'supportive', 'nice'],
            'neuroticism': ['worried', 'anxious', 'nervous', 'tense', 'stressed', 'emotional', 'moody', 'feel', 'concerned', 'upset', 'overwhelmed', 'doubt']
        }
        
    def extract_linguistic_features(self, texts):
        """Extract simple linguistic features from texts"""
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
        
        for text in texts:
            # Basic features
            words = re.findall(r'\w+', text.lower())
            features['word_count'].append(len(words))
            
            if words:
                features['avg_word_length'].append(sum(len(w) for w in words) / len(words))
            else:
                features['avg_word_length'].append(0)
            
            # Simple sentiment (positive - negative words)
            features['sentiment'].append(random.uniform(-1, 1))
            
            # Check for trait-related words
            for trait, trait_words in self.trait_word_lists.items():
                word_count = sum(1 for word in words if word in trait_words)
                normalized_score = min(1.0, word_count / 5)  # Normalize to 0-1
                features[trait].append(normalized_score)
                
        return features