import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class PersonaSimulator:
    def __init__(self):
        # Initialize with LiteLLM endpoint
        self.api_key = os.getenv("LITELLM_API_KEY")
        # Remove the trailing slash from the base URL
        self.base_url = "https://litellm.miqtest.daai.siemens.cloud"
        
        if not self.api_key:
            print("WARNING: LITELLM_API_KEY not found. Using demo mode.")
            self.demo_mode = True
        else:
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            })
            self.demo_mode = False
            print("LiteLLM integration active for persona conversations")
            
        # Store conversation histories for each persona
        self.conversations = {}

    def converse_with_persona(self, user_id, persona_data, user_message):
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append({"role": "user", "content": user_message})

        if self.demo_mode:
            quirk = persona_data.get("quirk", "")
            quirk_note = f" Also, I have this quirk: I {quirk}." if quirk else ""
            response = (
                f"[Demo Mode] As someone who is {self._get_trait_description(persona_data)},"
                f"{quirk_note} I would respond to '{user_message}' in character."
            )
            self.conversations[user_id].append({"role": "assistant", "content": response})
            return response

        system_prompt = self._create_rich_persona_prompt(persona_data)

        try:
            messages = [{"role": "system", "content": system_prompt}]

            example_intro = persona_data.get("example_intro", "")
            example_reply = persona_data.get("example_reply", "")
            if example_intro and example_reply:
                messages.append({"role": "user", "content": example_intro})
                messages.append({"role": "assistant", "content": example_reply})

            messages.extend(self.conversations[user_id][-10:])

            data = {
                "model": "gpt-4o",
                "messages": messages,
                "temperature": 0.9
            }

            response = self.session.post(f"{self.base_url}/chat/completions", json=data)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

            self.conversations[user_id].append({"role": "assistant", "content": content})
            return content

        except Exception as e:
            print(f"Error in persona conversation: {e}")
            fallback = (
                f"As someone who is {self._get_trait_description(persona_data)}, "
                f"I would respond thoughtfully to your message."
            )
            self.conversations[user_id].append({"role": "assistant", "content": fallback})
            return fallback

    def _get_trait_description(self, persona_data):
        traits = persona_data.get('traits', {})
        descriptions = []
        if traits.get('openness', 0) > 0.7: descriptions.append("creative and curious")
        if traits.get('conscientiousness', 0) > 0.7: descriptions.append("organized and responsible")
        if traits.get('extraversion', 0) > 0.7: descriptions.append("outgoing and energetic")
        if traits.get('agreeableness', 0) > 0.7: descriptions.append("cooperative and empathetic")
        if traits.get('neuroticism', 0) > 0.7: descriptions.append("emotionally sensitive")
        if not descriptions:
            descriptions = ["balanced and adaptable"]
        return ", ".join(descriptions)

    def _create_rich_persona_prompt(self, persona_data):
        traits = persona_data.get('traits', {})
        behaviors = persona_data.get('behaviors', {})

        openness = traits.get('openness', 0.5)
        conscientiousness = traits.get('conscientiousness', 0.5)
        extraversion = traits.get('extraversion', 0.5)
        agreeableness = traits.get('agreeableness', 0.5)
        neuroticism = traits.get('neuroticism', 0.5)

        prompt = f"""# Character Profile: {persona_data.get('template_name', 'Unique Individual')}

## Core Personality Summary
{persona_data.get('description', 'A nuanced individual with a distinct personality profile.')}

## Psychological Profile (Big Five)

### Openness to Experience: {openness:.2f}/1.0
{self._get_openness_description(openness)}

### Conscientiousness: {conscientiousness:.2f}/1.0
{self._get_conscientiousness_description(conscientiousness)}

### Extraversion: {extraversion:.2f}/1.0
{self._get_extraversion_description(extraversion)}

### Agreeableness: {agreeableness:.2f}/1.0
{self._get_agreeableness_description(agreeableness)}

### Neuroticism: {neuroticism:.2f}/1.0
{self._get_neuroticism_description(neuroticism)}

## Behavioral Patterns
"""
        for key, value in behaviors.items():
            pattern_name = key.replace('_', ' ').title()
            pattern_desc = ', '.join(value) if isinstance(value, list) else value
            prompt += f"- **{pattern_name}**: {pattern_desc}\n"

        quirk = persona_data.get("quirk", "")
        if quirk:
            prompt += f"\n## Unique Quirk\n- This person {quirk}.\n"

        prompt += f"""
## Communication Style
- This person {"speaks directly and assertively" if extraversion > 0.6 else "communicates thoughtfully and deliberately"}.
- They {"use rich, expressive language with varied vocabulary" if openness > 0.6 else "prefer clear, straightforward communication"}.
- Their tone is typically {"warm and empathetic" if agreeableness > 0.7 else "objective and matter-of-fact"}.
- They {"often share personal examples and stories" if extraversion > 0.6 else "tend to keep personal details private unless relevant"}.
- {"Their emotional state comes through clearly in their words" if neuroticism > 0.6 else "They maintain emotional consistency in their communication"}.

## Roleplaying Instructions (Strict)
You are now acting as this individual. You must respond exactly as this person would:
- Use **their voice**, **vocabulary**, and **emotional tone**
- Respond **in the first person**, like you’re chatting with a friend or peer.
- Share your personal perspective, values, and reactions honestly.
- Avoid generalizations or robotic phrasing — express opinions naturally.
- Never describe yourself in third person or explain that you're acting.

Never say you're an AI or simulation. Stay fully in character at all times.
"""
        return prompt

    def _get_openness_description(self, score):
        if score > 0.8:
            return "Extremely curious and imaginative. Loves abstract ideas, artistic expression, and intellectual exploration."
        elif score > 0.6:
            return "Quite open-minded and appreciative of new ideas and experiences."
        elif score > 0.4:
            return "Moderately open to new ideas with a balanced approach to change."
        elif score > 0.2:
            return "Generally prefers familiar routines and practical thinking."
        else:
            return "Strongly conventional and focused on established methods."

    def _get_conscientiousness_description(self, score):
        if score > 0.8:
            return "Extremely organized and responsible. Strong work ethic and attention to detail."
        elif score > 0.6:
            return "Quite diligent and goal-oriented. Reliable and methodical."
        elif score > 0.4:
            return "Moderately structured with occasional flexibility."
        elif score > 0.2:
            return "Somewhat relaxed about organization and deadlines."
        else:
            return "Highly spontaneous and unstructured. Dislikes routine and planning."

    def _get_extraversion_description(self, score):
        if score > 0.8:
            return "Extremely sociable and energized by social interaction. Loves attention and group activities."
        elif score > 0.6:
            return "Quite outgoing and talkative. Enjoys being around people."
        elif score > 0.4:
            return "Balanced between social and solitary preferences."
        elif score > 0.2:
            return "Somewhat reserved and introspective."
        else:
            return "Deeply introverted. Prefers solitude and reflection over interaction."

    def _get_agreeableness_description(self, score):
        if score > 0.8:
            return "Highly empathetic, cooperative, and kind. Values harmony."
        elif score > 0.6:
            return "Generally friendly and considerate."
        elif score > 0.4:
            return "Balanced between self-interest and cooperation."
        elif score > 0.2:
            return "Sometimes skeptical and prefers blunt honesty over tact."
        else:
            return "Very blunt and logical. Focused on facts over feelings."

    def _get_neuroticism_description(self, score):
        if score > 0.8:
            return "Emotionally intense and deeply reactive. Prone to stress and worry."
        elif score > 0.6:
            return "Responsive to emotional ups and downs. Self-aware and sensitive."
        elif score > 0.4:
            return "Emotionally balanced with a typical range of reactions."
        elif score > 0.2:
            return "Generally calm and even-tempered."
        else:
            return "Highly emotionally stable and resilient. Unfazed by stress."
