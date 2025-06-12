# src/collectors/social_media.py
import json
import os
import pandas as pd
import random
from datetime import datetime, timedelta

class SocialMediaCollector:
    def __init__(self):
        self.platforms = ["twitter", "facebook", "instagram"]
        
    def collect_user_data(self, username, platform):
        """Collect posts for a given username"""
        # For the prototype, we'll use the synthetic data
        try:
            with open("data/raw/social_posts.json", 'r') as f:
                all_posts = json.load(f)
                
            # For demo purposes, link any username to one of our synthetic users
            user_id = f"user{hash(username) % 20 + 1}"
                
            # Get posts for this "user"
            user_posts = [post for post in all_posts if post['user_id'] == user_id and post['platform'].lower() == platform.lower()]
            
            if not user_posts:
                # If no posts found, return some random posts
                user_posts = random.sample(all_posts, min(5, len(all_posts)))
                
            return user_posts
        
        except Exception as e:
            print(f"Error retrieving social media data: {e}")
            
            # Generate some dummy posts if file not found
            dummy_posts = []
            for i in range(5):
                days_ago = random.randint(0, 30)
                post_time = datetime.now() - timedelta(days=days_ago)
                
                dummy_posts.append({
                    "user_id": f"user{hash(username) % 20 + 1}",
                    "timestamp": post_time.isoformat(),
                    "text": f"This is a dummy post for {username} on {platform}. #{i+1}",
                    "platform": platform
                })
                
            return dummy_posts