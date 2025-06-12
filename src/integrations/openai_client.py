# src/integrations/openai_client.py
import os
import json
from dotenv import load_dotenv
 
load_dotenv()
 
class LLMClient:
    def __init__(self):
        # Initialize with direct API access to LiteLLM 
        self.litellm_api_key = os.getenv("LITELLM_API_KEY")
        self.base_url = "https://litellm.miqtest.daai.siemens.cloud/"
        if not self.litellm_api_key:
            print("WARNING: LITELLM_API_KEY not found in environment variables.")
            print("Using demo mode with synthetic responses.")
            self.demo_mode = True
            
        else:
            # Use requests for API calls instead of LangChain
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.litellm_api_key}"
            })
            self.demo_mode = False
    def analyze_sentiment(self, text):
        """Analyze the sentiment of a text"""
        if self.demo_mode:
            # Return synthetic sentiment in demo mode
            import random
            return {
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "sentiment_score": random.uniform(-1, 1),
                "confidence": random.uniform(0.7, 0.95)
            }
        try:
            import requests
            # Direct API call to LiteLLM without LangChain
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a sentiment analysis system that evaluates the emotional tone of text."},
                    {"role": "user", "content": f"Analyze the sentiment of this text and respond with a JSON object containing 'sentiment' (positive, neutral, or negative), 'sentiment_score' (from -1 to 1), and 'confidence' (0.0 to 1.0): '{text}'"}
                ],
                "temperature": 0.2
            }
            response = self.session.post(f"{self.base_url}/chat/completions", json=data)
            response.raise_for_status()
            response_data = response.json()
            # Extract the content from the response
            content = response_data["choices"][0]["message"]["content"]
            # Parse the JSON from the content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON-like content
                import re
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not extract JSON from response")
            return result
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            # Fallback to synthetic sentiment
            import random
            return {
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "sentiment_score": random.uniform(-1, 1),
                "confidence": random.uniform(0.7, 0.95)
            }
    def analyze_personality_traits(self, texts):
        """Analyze texts to extract Big Five personality traits"""
        combined_text = " ".join(texts[:5])  # Limit to first 5 texts to avoid token limits
        if self.demo_mode:
            # Return synthetic trait analysis in demo mode
            import random
            return {
                "openness": random.uniform(0.3, 0.9),
                "conscientiousness": random.uniform(0.3, 0.9),
                "extraversion": random.uniform(0.3, 0.9),
                "agreeableness": random.uniform(0.3, 0.9),
                "neuroticism": random.uniform(0.3, 0.9),
                "confidence": random.uniform(0.7, 0.9)
            }
        try:
            import requests
            # Direct API call to LiteLLM
            data = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a psychology researcher specialized in evaluating personality traits from text. Analyze text samples to estimate Big Five personality traits."},
                    {"role": "user", "content": f"Based on these writing samples, estimate the Big Five personality traits (openness, conscientiousness, extraversion, agreeableness, neuroticism) on a scale of 0.0 to 1.0. Respond with a JSON object containing these five traits and a confidence score: '{combined_text}'"}
                ],
                "temperature": 0.2
            }
            response = self.session.post(f"{self.base_url}/chat/completions", json=data)
            response.raise_for_status()
            response_data = response.json()
            # Extract the content from the response
            content = response_data["choices"][0]["message"]["content"]
            # Parse the JSON from the content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON-like content
                import re
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    raise ValueError("Could not extract JSON from response")
            return result
        except Exception as e:
            print(f"Error in personality analysis: {e}")
            # Fallback to synthetic analysis
            import random
            return {
                "openness": random.uniform(0.3, 0.9),
                "conscientiousness": random.uniform(0.3, 0.9),
                "extraversion": random.uniform(0.3, 0.9),
                "agreeableness": random.uniform(0.3, 0.9),
                "neuroticism": random.uniform(0.3, 0.9),
                "confidence": random.uniform(0.7, 0.9)
            }
