# src/integrations/persona_simulator.py
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
        self.base_url = "https://litellm.miqtest.daai.siemens.cloud/"
        
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
        """Have a conversation with the persona"""
        # Initialize conversation history if needed
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            
        # Add user message to history
        self.conversations[user_id].append({"role": "user", "content": user_message})
        
        if self.demo_mode:
            # Use a basic response in demo mode
            response = f"[Demo Mode] As someone who is {self._get_trait_description(persona_data)}, I would respond to '{user_message}' in character."
            self.conversations[user_id].append({"role": "assistant", "content": response})
            return response
            
        # Create a detailed system prompt that captures the persona
        system_prompt = self._create_rich_persona_prompt(persona_data)
        
        try:
            # Prepare messages including system prompt and conversation history
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.conversations[user_id][-10:])  # Last 10 messages
            
            # Call LiteLLM API
            data = {
                "model": "gpt-4o",
                "messages": messages,
                "temperature": 0.8  # Higher temp for more personality
            }
            
            response = self.session.post(f"{self.base_url}/chat/completions", json=data)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the content from the response
            content = response_data["choices"][0]["message"]["content"]
            
            # Add response to conversation history
            self.conversations[user_id].append({"role": "assistant", "content": content})
            
            return content
                
        except Exception as e:
            print(f"Error in persona conversation: {e}")
            # Simple fallback
            response = f"As someone who is {self._get_trait_description(persona_data)}, I would respond thoughtfully to your message."
            self.conversations[user_id].append({"role": "assistant", "content": response})
            return response
            
    def _get_trait_description(self, persona_data):
        """Get a simple description of the main personality traits"""
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
        """Create a detailed prompt that fully captures the persona"""
        traits = persona_data.get('traits', {})
        behaviors = persona_data.get('behaviors', {})
        
        # Calculate trait levels for more nuanced descriptions
        openness = traits.get('openness', 0.5)
        conscientiousness = traits.get('conscientiousness', 0.5)
        extraversion = traits.get('extraversion', 0.5)
        agreeableness = traits.get('agreeableness', 0.5)
        neuroticism = traits.get('neuroticism', 0.5)
        
        # Build a rich description based on the Big Five trait model
        prompt = f"""# Character Profile: {persona_data.get('template_name', 'Unique Individual')}

## Core Personality Summary
{persona_data.get('description', 'A nuanced individual with a distinct personality profile.')}

## Psychological Profile (Based on Big Five Personality Model)

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

        # Add all behavior patterns
        for key, value in behaviors.items():
            pattern_name = key.replace('_', ' ').title()
            if isinstance(value, list):
                pattern_desc = ', '.join(value)
            else:
                pattern_desc = value
            prompt += f"- **{pattern_name}**: {pattern_desc}\n"

        # Add communication guidance based on traits
        prompt += f"""
## Communication Style
This person {"speaks directly and assertively" if extraversion > 0.6 else "communicates thoughtfully and deliberately"}.
They {"use rich, expressive language with varied vocabulary" if openness > 0.6 else "prefer clear, straightforward communication"}.
Their tone is typically {"warm and empathetic" if agreeableness > 0.7 else "objective and matter-of-fact"}.
They {"often share personal examples and stories" if extraversion > 0.6 else "tend to keep personal details private unless relevant"}.
{"Their emotional state comes through clearly in their words" if neuroticism > 0.6 else "They maintain emotional consistency in their communication"}.

## Acting Instructions
You are now embodying this character completely. Respond to messages exactly as this person would, with their unique:
1. Vocabulary, speech patterns, and communication quirks
2. Attitudes, values, and worldview
3. Emotional reactions and thought processes
4. Decision-making style and priorities
5. Level of self-disclosure and interpersonal warmth

Stay completely in character at all times. Never break the fourth wall or mention that you're roleplaying or an AI.
"""

        return prompt
        
    def _get_openness_description(self, score):
        if score > 0.8:
            return "Extremely curious and imaginative. Loves abstract ideas, artistic expression, and intellectual exploration. Constantly seeking new experiences and thinking outside conventional boundaries. Values creativity highly and is likely to have unusual interests or hobbies."
        elif score > 0.6:
            return "Quite open-minded and appreciative of art, new ideas, and unconventional concepts. Enjoys exploring theoretical possibilities and has diverse interests. Values innovation and typically prefers variety over routine."
        elif score > 0.4:
            return "Moderately receptive to new experiences, balancing traditional approaches with occasional interest in novel ideas. Can appreciate art and creativity while maintaining practical perspectives. Neither strongly conventional nor unconventional."
        elif score > 0.2:
            return "Generally prefers familiar routines and conventional approaches. Values practicality over abstract thinking and may be skeptical of radical ideas. Tends to focus on concrete rather than theoretical matters."
        else:
            return "Strongly conventional and traditional. Prefers established methods and familiar routines. Practical-minded and focused on immediate realities rather than abstract possibilities. May find artistic or theoretical pursuits impractical."
    
    def _get_conscientiousness_description(self, score):
        if score > 0.8:
            return "Extremely organized, responsible, and detail-oriented. Plans meticulously and follows through reliably. Strong work ethic and high personal standards. Self-disciplined and careful in decisions. Values structure and completion of tasks to high standards."
        elif score > 0.6:
            return "Quite diligent and organized. Sets clear goals and works systematically toward them. Generally reliable and prepared. Values efficiency and tends to think before acting. Takes obligations seriously."
        elif score > 0.4:
            return "Moderately organized and responsible. Can create and follow plans but also adapt when needed. Balances work and leisure reasonably well. Neither extremely disciplined nor particularly spontaneous."
        elif score > 0.2:
            return "Somewhat flexible with schedules and planning. May prefer spontaneity over rigid organization. Takes a relaxed approach to goals and deadlines. Can be occasionally disorganized or procrastinate on less interesting tasks."
        else:
            return "Highly spontaneous and present-focused. Dislikes rigid schedules and detailed planning. Prefers to keep options open and may change direction frequently. May struggle with organization and meeting deadlines but can be adaptable and in-the-moment."
    
    def _get_extraversion_description(self, score):
        if score > 0.8:
            return "Extremely sociable, outgoing, and energetic. Thrives in social situations and actively seeks interaction. Speaks enthusiastically with animated expression. Prefers group activities to solitude and draws energy from being around others. Often takes leadership roles in social settings."
        elif score > 0.6:
            return "Quite social and talkative. Enjoys group activities and usually feels comfortable meeting new people. Expresses opinions readily and tends to be cheerful and optimistic in social settings. Balances talking and listening but generally prefers company over solitude."
        elif score > 0.4:
            return "Moderately comfortable in social situations. Can enjoy both socializing and alone time in balanced measure. Neither strongly reserved nor particularly attention-seeking. Adapts to both quiet and lively environments."
        elif score > 0.2:
            return "Somewhat reserved and private. Prefers deeper one-on-one conversations to large social gatherings. Values quiet time for reflection and may find extensive socializing draining. Thinks before speaking and listens more than talks."
        else:
            return "Strongly introverted and internally focused. Requires significant alone time to recharge. Prefers deep thinking and observation to social interaction. Carefully considers words before speaking and may find large gatherings overwhelming. Values privacy and depth over breadth in relationships."
            
    def _get_agreeableness_description(self, score):
        if score > 0.8:
            return "Extremely cooperative, compassionate, and focused on harmony. Always considering others' needs and feelings. Trusting and eager to help. Avoids conflict whenever possible and readily forgives. Values kindness above winning arguments or being right."
        elif score > 0.6:
            return "Quite caring and considerate. Generally trusting of others and willing to compromise. Values getting along with people and maintaining positive relationships. Shows empathy readily and tries to be helpful when possible."
        elif score > 0.4:
            return "Moderately concerned with others' needs while also standing up for personal interests. Can be cooperative or competitive depending on the situation. Neither particularly suspicious nor naive about others' intentions."
        elif score > 0.2:
            return "Somewhat skeptical and questioning. Values honesty over tact and may prioritize truth over feelings. Can be competitive and willing to challenge others. Prefers direct communication even if it creates some tension."
        else:
            return "Highly analytical and challenging of others. Skeptical of people's motives and quick to question assumptions. Values logic over emotional considerations. Comfortable with conflict and disagreement, possibly enjoying debate. Direct and straightforward in expressing opinions."
    
    def _get_neuroticism_description(self, score):
        if score > 0.8:
            return "Highly sensitive to stress and emotional stimuli. Experiences emotions intensely and may worry frequently. Prone to self-doubt and can be easily overwhelmed by challenging situations. Notices subtle threats or problems others might miss. Inner emotional life is complex and reactive."
        elif score > 0.6:
            return "Quite responsive to emotional situations. Experiences clear ups and downs in mood. May worry about important matters and feel stress more readily than average. Tends toward self-reflection and awareness of potential problems."
        elif score > 0.4:
            return "Moderately stable emotionally with normal responses to stress. Experiences typical range of emotions without excessive intensity or blunting. Neither particularly prone to worry nor especially carefree. Recovers from negative emotions in reasonable time."
        elif score > 0.2:
            return "Generally calm and even-tempered. Not easily stressed by typical life challenges. Tends toward optimism and emotional stability. Recovers quickly from setbacks and rarely dwells on negative feelings."
        else:
            return "Extremely resilient and emotionally stable. Rarely worried or anxious even under pressure. Maintains calm perspective in crisis situations. May appear almost unflappable and consistently confident. Minimal self-doubt and strong stress tolerance."