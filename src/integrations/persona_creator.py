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
 
# src/integrations/persona_creator.py

import os

import json

import requests

from dotenv import load_dotenv
 
load_dotenv()
 
class PersonaCreator:

    def __init__(self):

        # Initialize with LiteLLM endpoint

        self.api_key = os.getenv("LITELLM_API_KEY")

        self.base_url = "https://litellm.miqtest.daai.siemens.cloud/"

        if not self.api_key:

            print("WARNING: LITELLM_API_KEY not found. Using synthetic personas.")

            self.demo_mode = True

        else:

            self.session = requests.Session()

            self.session.headers.update({

                "Content-Type": "application/json",

                "Authorization": f"Bearer {self.api_key}"

            })

            self.demo_mode = False

    def generate_complete_persona(self, traits, text_samples=None):

        """Generate a complete persona profile using LLM"""

        if self.demo_mode:

            return self._generate_fallback_persona(traits)

        # Prepare traits information

        traits_description = "\n".join([f"- {trait}: {score:.2f}/1.0" for trait, score in traits.items()])

        # Prepare text samples if available

        text_context = ""

        if text_samples and len(text_samples) > 0:

            samples = "\n".join([f"- \"{sample}\"" for sample in text_samples[:3]])

            text_context = f"\nText samples from this person:\n{samples}\n"

        system_prompt = """You are an expert psychological profiler who creates detailed, realistic persona descriptions. 

        Based on the Big Five personality trait scores (0-1 scale) and any text samples provided, create a comprehensive persona.
 
        Focus on creating a realistic, nuanced individual rather than a stereotype. Include:
 
        1. Core personality traits with specific behavioral examples

        2. Communication style with specific phrases and language patterns they would use

        3. Decision-making process and what factors influence them

        4. Values and motivations that drive them

        5. Typical emotional responses to different situations

        6. Social interaction style and relationship preferences

        7. Interests, hobbies, and content preferences

        8. Life philosophy and guiding principles

        9. Linguistic quirks, favorite phrases or expressions

        10. How they might respond in different scenarios
 
        Respond in JSON format with fields for each aspect of the persona."""
 
        try:

            # Call LiteLLM API

            data = {

                "model": "gpt-4o",

                "messages": [

                    {"role": "system", "content": system_prompt},

                    {"role": "user", "content": f"Create a detailed persona based on these Big Five personality traits:\n{traits_description}{text_context}"}

                ],

                "temperature": 0.7,

                "response_format": {"type": "json_object"}

            }

            response = self.session.post(f"{self.base_url}/chat/completions", json=data)

            response.raise_for_status()

            response_data = response.json()

            # Extract the content from the response

            content = response_data["choices"][0]["message"]["content"]

            # Parse the JSON from the content

            try:

                persona = json.loads(content)

                return persona

            except json.JSONDecodeError:

                print("Error parsing JSON from LLM response")

                return self._generate_fallback_persona(traits)

        except Exception as e:

            print(f"Error generating persona: {e}")

            return self._generate_fallback_persona(traits)

    def _generate_fallback_persona(self, traits):

        """Generate a basic fallback persona when LLM is unavailable"""

        # Simple template-based persona

        openness = traits.get('openness', 0.5)

        conscientiousness = traits.get('conscientiousness', 0.5)

        extraversion = traits.get('extraversion', 0.5)

        agreeableness = traits.get('agreeableness', 0.5)

        neuroticism = traits.get('neuroticism', 0.5)

        if openness > 0.7 and extraversion > 0.6:

            persona_type = "The Creative Explorer"

            communication = "Enthusiastic and expressive, uses colorful language and asks lots of questions"

        elif conscientiousness > 0.7 and agreeableness > 0.6:

            persona_type = "The Reliable Supporter"

            communication = "Clear, organized, and supportive, focuses on facts and others' needs"

        elif neuroticism > 0.7:

            persona_type = "The Sensitive Analyzer"

            communication = "Thoughtful and cautious, expresses concerns and considers details carefully"

        else:

            persona_type = "The Balanced Pragmatist"

            communication = "Straightforward and practical, adapts style based on context"

        return {

            "core_personality": f"This person is a {persona_type.lower()}, showing traits of {', '.join([k for k, v in traits.items() if v > 0.6])}",

            "communication_style": communication,

            "decision_making": "Considers options carefully before deciding" if conscientiousness > 0.6 else "Makes decisions quickly based on intuition",

            "values_and_motivations": "Values creativity and new experiences" if openness > 0.6 else "Values stability and tradition",

            "emotional_responses": "Reacts strongly to setbacks" if neuroticism > 0.6 else "Maintains emotional stability in difficult situations",

            "social_style": "Seeks out social interaction" if extraversion > 0.6 else "Prefers meaningful one-on-one connections",

            "interests": "Enjoys creative and intellectual pursuits" if openness > 0.6 else "Enjoys practical and familiar activities",

            "life_philosophy": "Life is about exploration and growth" if openness > 0.7 else "Life is about building stability and security",

            "linguistic_patterns": "Uses expressive language" if extraversion > 0.6 else "Uses precise, measured language",

            "scenario_responses": {

                "stress": "Seeks support from others" if extraversion > 0.6 and agreeableness > 0.6 else "Processes challenges internally",

                "success": "Celebrates openly" if extraversion > 0.6 else "Reflects quietly on achievements",

                "conflict": "Seeks compromise" if agreeableness > 0.6 else "Stands firm on principles"

            }

        }
 