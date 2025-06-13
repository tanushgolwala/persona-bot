# src/models/persona_evolve.py
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from src.integrations.persona_creator import PersonaCreator
 
class DynamicPersonaGenerator:
    def __init__(self):
        # Add this line to your existing init
        self.persona_creator = PersonaCreator()
        # ... rest of your init
    def generate_user_persona(self, user_id, trait_dict, text_samples=None):
        """Generate or update a user's dynamic persona"""
        # If this is a new user, create a new persona
        if user_id not in self.user_personas:
            # Generate rich persona details using LLM
            llm_persona = self.persona_creator.generate_complete_persona(trait_dict, text_samples)
            template_id = self._assign_persona_template(trait_dict)
            template = self.persona_templates.get(template_id, {})
            self.user_personas[user_id] = {
                'user_id': user_id,
                'template_id': template_id,
                'template_name': template.get('name', 'Custom Persona'),
                'description': template.get('description', 'A unique individual'),
                'traits': trait_dict,
                'llm_persona': llm_persona,  # Store the LLM-generated persona details
                'behaviors': self._derive_behavior_patterns(trait_dict),
                'trait_history': [{
                    'timestamp': datetime.now().isoformat(),
                    'traits': trait_dict
                }],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        else:
            # Update existing persona
            persona = self.user_personas[user_id]
            # Add to trait history
            persona['trait_history'].append({
                'timestamp': datetime.now().isoformat(),
                'traits': trait_dict
            })
            # Update traits with moving average
            alpha = 0.7  # Weight for new data vs old data
            for trait in trait_dict:
                persona['traits'][trait] = alpha * trait_dict[trait] + (1 - alpha) * persona['traits'][trait]
            # Only regenerate the LLM persona if traits change significantly
            trait_diff = sum(abs(persona['traits'][t] - trait_dict[t]) for t in trait_dict)
            if trait_diff > 0.5:  # Threshold for regeneration
                persona['llm_persona'] = self.persona_creator.generate_complete_persona(
                    persona['traits'], text_samples
                )
            # Check if template should change
            new_template_id = self._assign_persona_template(persona['traits'])
            if new_template_id != persona['template_id']:
                persona['template_id'] = new_template_id
                template = self.persona_templates.get(new_template_id, {})
                persona['template_name'] = template.get('name', 'Custom Persona')
                persona['description'] = template.get('description', 'A unique individual')
            # Update behaviors
            persona['behaviors'] = self._derive_behavior_patterns(persona['traits'])
            persona['updated_at'] = datetime.now().isoformat()
            self.user_personas[user_id] = persona
        # Save personas to file
        self.save_personas()
        return self.user_personas[user_id]
    
    
class DynamicPersonaGenerator:
    def __init__(self):
        self.persona_templates = {
            0: {
                'id': 0,
                'name': 'The Enthusiastic Explorer',
                'description': 'Curious, open to new experiences, and socially engaged. Seeks novelty and enjoys sharing discoveries with others.'
            },
            1: {
                'id': 1,
                'name': 'The Dependable Supporter',
                'description': 'Reliable, organized, and caring. Values stability and helping others, with strong attention to detail.'
            },
            2: {
                'id': 2,
                'name': 'The Innovative Achiever',
                'description': 'Creative, ambitious, and goal-oriented. Combines originality with discipline to create novel solutions.'
            },
            3: {
                'id': 3,
                'name': 'The Sensitive Reactor',
                'description': 'Emotionally aware, responsive to environment, and deeply feeling. Processes experiences with intensity.'
            },
            4: {
                'id': 4,
                'name': 'The Balanced Individual',
                'description': 'Adaptable, moderate, and well-rounded. Shows flexibility across different situations and contexts.'
            }
        }
        
        self.user_personas = {}
        
        # Create data directory for personas
        os.makedirs("data/personas", exist_ok=True)
        
        # Try to load any existing personas
        if os.path.exists("data/personas/user_personas.json"):
            try:
                with open("data/personas/user_personas.json", 'r') as f:
                    self.user_personas = json.load(f)
            except:
                pass
        
    def _assign_persona_template(self, traits):
        """Assign a persona template based on traits"""
        # Convert traits dict to array for easier processing
        trait_array = np.array([
            traits['openness'],
            traits['conscientiousness'],
            traits['extraversion'],
            traits['agreeableness'],
            traits['neuroticism']
        ])
        
        # Template characteristic arrays (simplified)
        template_traits = {
            0: np.array([0.8, 0.5, 0.8, 0.6, 0.4]),  # Explorer
            1: np.array([0.4, 0.8, 0.5, 0.8, 0.3]),  # Supporter
            2: np.array([0.8, 0.8, 0.6, 0.4, 0.4]),  # Achiever
            3: np.array([0.6, 0.5, 0.5, 0.6, 0.8]),  # Reactor
            4: np.array([0.5, 0.5, 0.5, 0.5, 0.5])   # Balanced
        }
        
        # Find closest template
        min_distance = float('inf')
        best_template = 0
        
        for template_id, template_array in template_traits.items():
            distance = np.linalg.norm(trait_array - template_array)
            if distance < min_distance:
                min_distance = distance
                best_template = template_id
                
        return best_template
    
    def _derive_behavior_patterns(self, traits):
        """Derive behavioral patterns from trait values"""
        patterns = {}
        
        # Content preferences
        patterns['content_preferences'] = []
        if traits['openness'] > 0.7:
            patterns['content_preferences'].extend(['Creative', 'Novel', 'Thought-provoking'])
        elif traits['openness'] < 0.3:
            patterns['content_preferences'].extend(['Practical', 'Familiar', 'Concrete'])
        else:
            patterns['content_preferences'].extend(['Balanced', 'Varied'])
            
        if traits['conscientiousness'] > 0.7:
            patterns['content_preferences'].append('Organized')
        
        # Communication style
        if traits['extraversion'] > 0.7:
            patterns['communication_style'] = 'Outgoing and expressive'
        elif traits['extraversion'] < 0.3:
            patterns['communication_style'] = 'Reserved and thoughtful'
        else:
            patterns['communication_style'] = 'Adaptable communication style'
            
        # Decision making
        if traits['conscientiousness'] > 0.7 and traits['neuroticism'] < 0.3:
            patterns['decision_making'] = 'Methodical and confident'
        elif traits['openness'] > 0.7 and traits['neuroticism'] < 0.4:
            patterns['decision_making'] = 'Creative and bold'
        elif traits['agreeableness'] > 0.7:
            patterns['decision_making'] = 'Collaborative and considerate'
        elif traits['neuroticism'] > 0.7:
            patterns['decision_making'] = 'Careful and thorough'
        else:
            patterns['decision_making'] = 'Balanced approach to decisions'
            
        # Learning style
        if traits['openness'] > 0.7 and traits['conscientiousness'] > 0.7:
            patterns['learning_style'] = 'Self-directed and exploratory'
        elif traits['extraversion'] > 0.7 and traits['openness'] > 0.5:
            patterns['learning_style'] = 'Social and discussion-based'
        elif traits['conscientiousness'] > 0.7 and traits['openness'] < 0.4:
            patterns['learning_style'] = 'Structured and practical'
        else:
            patterns['learning_style'] = 'Flexible learning approach'
            
        return patterns
    
    def generate_user_persona(self, user_id, trait_dict, text_samples=None):
        """Generate or update a user's dynamic persona"""
        # Get template
        template_id = self._assign_persona_template(trait_dict)
        template = self.persona_templates[template_id]
        
        # Derive behaviors
        behaviors = self._derive_behavior_patterns(trait_dict)
        
        # If this is a new user, create a new persona
        if user_id not in self.user_personas:
            self.user_personas[user_id] = {
                'user_id': user_id,
                'template_id': template_id,
                'template_name': template['name'],
                'description': template['description'],
                'traits': trait_dict,
                'behaviors': behaviors,
                'trait_history': [{
                    'timestamp': datetime.now().isoformat(),
                    'traits': trait_dict
                }],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
        else:
            # Update existing persona
            persona = self.user_personas[user_id]
            
            # Add to trait history
            persona['trait_history'].append({
                'timestamp': datetime.now().isoformat(),
                'traits': trait_dict
            })
            
            # Update traits with moving average
            alpha = 0.7  # Weight for new data vs old data
            for trait in trait_dict:
                persona['traits'][trait] = alpha * trait_dict[trait] + (1 - alpha) * persona['traits'][trait]
            
            # Check if template should change
            new_template_id = self._assign_persona_template(persona['traits'])
            if new_template_id != persona['template_id']:
                persona['template_id'] = new_template_id
                persona['template_name'] = self.persona_templates[new_template_id]['name']
                persona['description'] = self.persona_templates[new_template_id]['description']
            
            # Update behaviors
            persona['behaviors'] = self._derive_behavior_patterns(persona['traits'])
            persona['updated_at'] = datetime.now().isoformat()
            
            self.user_personas[user_id] = persona
            
        # Save personas to file
        self.save_personas()
            
        return self.user_personas[user_id]
    
    def save_personas(self):
        """Save persona data"""
        with open("data/personas/user_personas.json", 'w') as f:
            json.dump(self.user_personas, f, indent=2, default=str)
    
    def load_personas(self):
        """Load persona data"""
        try:
            with open("data/personas/user_personas.json", 'r') as f:
                self.user_personas = json.load(f)
        except:
            self.user_personas = {}