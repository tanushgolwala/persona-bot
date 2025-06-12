# src/data_generator.py
import random
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SyntheticDataGenerator:
    def __init__(self):
        self.user_ids = [f"user{i}" for i in range(1, 21)]
        self.persona_types = [
            "The Enthusiastic Explorer",
            "The Dependable Supporter",
            "The Innovative Achiever", 
            "The Sensitive Reactor",
            "The Balanced Individual"
        ]
        
        # Sample social media posts by persona type
        self.sample_posts = {
            "The Enthusiastic Explorer": [
                "Just discovered this amazing new coffee place! Can't wait to try more of their drinks!",
                "Planning my next adventure to Southeast Asia! Any recommendations?",
                "Tried rock climbing for the first time today - what a rush! #NewExperiences",
                "Reading three books at once right now because I can't decide which one I'm most excited about!",
                "Just signed up for a pottery class. Always wanted to learn how to make my own ceramics!"
            ],
            "The Dependable Supporter": [
                "Helped my neighbor move in today. It's important to build community.",
                "Made dinner for my friend who's going through a tough time. Small acts of kindness matter.",
                "Reminder to everyone: the charity drive ends this Friday! Please donate if you can.",
                "Always double-check your calendar for the day. Being prepared saves everyone time.",
                "Successfully completed our team project ahead of schedule! Good planning pays off."
            ],
            "The Innovative Achiever": [
                "Just filed my third patent this year. Innovation never sleeps!",
                "My 5am productivity routine has changed my life. Here's how you can optimize your mornings...",
                "Fascinating research on quantum computing today. The possibilities are endless.",
                "Just finished coding my own productivity app. Beta testers wanted!",
                "Efficiency hack: I've automated 80% of my repetitive tasks this month."
            ],
            "The Sensitive Reactor": [
                "Feeling overwhelmed by the news today. Taking a social media break for self-care.",
                "Why do people have to be so rude in traffic? It really affects my whole day.",
                "The soundtrack to this movie has me in tears. Music can be so powerful.",
                "Really need some positive vibes today. Share your good news with me?",
                "Overthinking a conversation I had yesterday. Does anyone else do this?"
            ],
            "The Balanced Individual": [
                "Enjoyed a productive morning and a relaxing afternoon. Balance is key!",
                "Sometimes you need to work hard, sometimes you need rest. Listening to what I need today.",
                "Tried that new restaurant but also saved some money this week. All about moderation.",
                "I see both sides of that debate. There's usually truth in the middle ground.",
                "Mixing up my routine with both familiar activities and new experiences this weekend."
            ]
        }
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
    
    def generate_user_traits(self):
        """Generate synthetic user personality traits"""
        traits_data = []
        
        for user_id in self.user_ids:
            # Randomly assign a persona type
            persona_type = random.choice(self.persona_types)
            
            # Base traits for each persona type
            if persona_type == "The Enthusiastic Explorer":
                base_traits = {
                    "openness": random.uniform(0.7, 1.0),
                    "conscientiousness": random.uniform(0.3, 0.7),
                    "extraversion": random.uniform(0.7, 1.0),
                    "agreeableness": random.uniform(0.4, 0.8),
                    "neuroticism": random.uniform(0.3, 0.6)
                }
            elif persona_type == "The Dependable Supporter":
                base_traits = {
                    "openness": random.uniform(0.3, 0.6),
                    "conscientiousness": random.uniform(0.7, 1.0),
                    "extraversion": random.uniform(0.4, 0.7),
                    "agreeableness": random.uniform(0.7, 1.0),
                    "neuroticism": random.uniform(0.2, 0.5)
                }
            elif persona_type == "The Innovative Achiever":
                base_traits = {
                    "openness": random.uniform(0.7, 1.0),
                    "conscientiousness": random.uniform(0.7, 1.0),
                    "extraversion": random.uniform(0.5, 0.8),
                    "agreeableness": random.uniform(0.3, 0.6),
                    "neuroticism": random.uniform(0.3, 0.6)
                }
            elif persona_type == "The Sensitive Reactor":
                base_traits = {
                    "openness": random.uniform(0.5, 0.8),
                    "conscientiousness": random.uniform(0.3, 0.7),
                    "extraversion": random.uniform(0.3, 0.7),
                    "agreeableness": random.uniform(0.4, 0.8),
                    "neuroticism": random.uniform(0.7, 1.0)
                }
            else:  # The Balanced Individual
                base_traits = {
                    "openness": random.uniform(0.4, 0.7),
                    "conscientiousness": random.uniform(0.4, 0.7),
                    "extraversion": random.uniform(0.4, 0.7),
                    "agreeableness": random.uniform(0.4, 0.7),
                    "neuroticism": random.uniform(0.3, 0.6)
                }
            
            # Add random variation
            traits = {k: min(1.0, max(0.0, v + random.uniform(-0.1, 0.1))) for k, v in base_traits.items()}
            
            traits_data.append({
                "user_id": user_id,
                "persona_type": persona_type,
                **traits
            })
        
        # Save to CSV
        traits_df = pd.DataFrame(traits_data)
        traits_df.to_csv("data/processed/user_traits.csv", index=False)
        
        return traits_df
    
    def generate_social_posts(self):
        """Generate synthetic social media posts for users"""
        all_posts = []
        
        for user_id in self.user_ids:
            # Find user's persona type
            traits_df = pd.read_csv("data/processed/user_traits.csv")
            user_row = traits_df[traits_df['user_id'] == user_id].iloc[0]
            persona_type = user_row['persona_type']
            
            # Generate 5-10 posts for each user
            num_posts = random.randint(5, 10)
            
            # Generate posts with timestamps over the last 30 days
            for _ in range(num_posts):
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                post_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
                
                # Get posts relevant to persona type
                possible_posts = self.sample_posts[persona_type]
                post_text = random.choice(possible_posts)
                
                # Add some random hashtags
                hashtags = ["#life", "#thoughts", "#experience", "#journey", "#growth", 
                           "#motivation", "#inspiration", "#learning", "#sharing"]
                if random.random() < 0.7:  # 70% of posts have hashtags
                    num_hashtags = random.randint(1, 3)
                    selected_hashtags = " ".join(random.sample(hashtags, num_hashtags))
                    post_text += " " + selected_hashtags
                    
                all_posts.append({
                    "user_id": user_id,
                    "timestamp": post_time.isoformat(),
                    "text": post_text,
                    "platform": random.choice(["twitter", "facebook", "instagram"])
                })
                
        # Save to JSON
        with open("data/raw/social_posts.json", "w") as f:
            json.dump(all_posts, f, indent=2)
        
        return all_posts
    
    def generate_survey_responses(self):
        """Generate synthetic survey responses for users"""
        survey_questions = [
            "I enjoy trying new things",
            "I complete tasks thoroughly",
            "I enjoy being the center of attention",
            "I sympathize with others' feelings",
            "I get stressed easily",
            "I have a vivid imagination",
            "I like order and organization",
            "I start conversations with new people easily",
            "I take time out for others",
            "I worry about things often"
        ]
        
        all_responses = []
        
        for user_id in self.user_ids:
            # Find user's traits
            traits_df = pd.read_csv("data/processed/user_traits.csv")
            user_row = traits_df[traits_df['user_id'] == user_id].iloc[0]
            
            # Map traits to questions
            trait_mapping = {
                0: "openness",
                1: "conscientiousness",
                2: "extraversion",
                3: "agreeableness", 
                4: "neuroticism",
                5: "openness",
                6: "conscientiousness",
                7: "extraversion",
                8: "agreeableness",
                9: "neuroticism"
            }
            
            # Generate responses
            responses = {}
            for i, question in enumerate(survey_questions):
                trait = trait_mapping[i]
                trait_score = user_row[trait]
                
                # Convert trait score (0-1) to Likert scale (1-5)
                # Add some noise
                likert_score = round(trait_score * 4) + 1
                likert_score = max(1, min(5, likert_score + random.randint(-1, 1)))
                responses[question] = likert_score
            
            all_responses.append({
                "user_id": user_id,
                "timestamp": (datetime.now() - timedelta(days=random.randint(0, 14))).isoformat(),
                "responses": responses
            })
        
        # Save to JSON
        with open("data/raw/survey_responses.json", "w") as f:
            json.dump(all_responses, f, indent=2)
            
        return all_responses
    
    def generate_all_data(self):
        """Generate all synthetic data"""
        print("Generating user traits...")
        self.generate_user_traits()
        
        print("Generating social media posts...")
        self.generate_social_posts()
        
        print("Generating survey responses...")
        self.generate_survey_responses()
        
        print("All synthetic data generated!")