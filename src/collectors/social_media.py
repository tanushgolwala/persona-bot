import json
import os
import pandas as pd
import random
from datetime import datetime, timedelta
import tweepy  # Twitter API library
import time
import dotenv

dotenv.load_dotenv()

class SocialMediaCollector:
    def __init__(self):
        self.platforms = ["twitter", "facebook", "instagram"]
        # Twitter API credentials
        self.twitter_bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
        
        # Initialize Twitter client if credentials are available
        if self.twitter_bearer_token:
            self.twitter_client = tweepy.Client(bearer_token=self.twitter_bearer_token)
        else:
            self.twitter_client = None
            print("Warning: Twitter API credentials not set")
        
    def collect_user_data(self, username, platform):
        """Collect posts for a given username"""
        if platform.lower() == "twitter" and self.twitter_client:
            return self._collect_twitter_data(username)
        else:
            # Fall back to the synthetic data for other platforms or if Twitter API is not configured
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
    
    def _collect_twitter_data(self, username, max_tweets=20, retry_count=3):
        """Collect tweets for the given username using Twitter API v2"""
        for attempt in range(retry_count):
            try:
                # First, get the user ID from the username
                user_response = self.twitter_client.get_user(username=username)
                if not user_response or not user_response.data:
                    print(f"User {username} not found on Twitter")
                    return self._generate_fallback_data(username, "twitter")
                    
                user_id = user_response.data.id
                
                # Get user tweets with pagination
                all_tweets = []
                pagination_token = None
                remaining_tweets = max_tweets
                
                while remaining_tweets > 0:
                    batch_size = min(100, remaining_tweets)  # API max is 100 per request
                    
                    tweets_response = self.twitter_client.get_users_tweets(
                        id=user_id,
                        max_results=batch_size,
                        pagination_token=pagination_token,
                        tweet_fields=["created_at", "public_metrics"]
                    )
                    
                    if not tweets_response or not tweets_response.data:
                        break
                        
                    all_tweets.extend(tweets_response.data)
                    remaining_tweets -= len(tweets_response.data)
                    
                    # Check if there are more pages
                    if hasattr(tweets_response, 'meta') and 'next_token' in tweets_response.meta:
                        pagination_token = tweets_response.meta['next_token']
                    else:
                        break  # No more tweets to fetch
                
                if not all_tweets:
                    print(f"No tweets found for user {username}")
                    return self._generate_fallback_data(username, "twitter")
                
                # Format tweets to match our existing structure
                formatted_tweets = []
                for tweet in all_tweets:
                    tweet_data = {
                        "user_id": str(user_id),
                        "timestamp": tweet.created_at.isoformat(),
                        "text": tweet.text,
                        "platform": "twitter"
                    }
                    
                    # Add metrics if available
                    if hasattr(tweet, 'public_metrics') and tweet.public_metrics:
                        tweet_data.update({
                            "retweet_count": tweet.public_metrics.get("retweet_count", 0),
                            "like_count": tweet.public_metrics.get("like_count", 0),
                            "reply_count": tweet.public_metrics.get("reply_count", 0)
                        })
                        
                    formatted_tweets.append(tweet_data)
                    
                return formatted_tweets
                
            except tweepy.TooManyRequests:
                # Rate limit exceeded, wait and retry
                if attempt < retry_count - 1:
                    print(f"Rate limit exceeded. Waiting before retry {attempt+1}/{retry_count}")
                    time.sleep(60)  # Wait 60 seconds before retry
                else:
                    print("Rate limit exceeded. Falling back to synthetic data")
                    return self._generate_fallback_data(username, "twitter")
                    
            except tweepy.Unauthorized:
                print("Twitter API authentication failed")
                return self._generate_fallback_data(username, "twitter")
                
            except Exception as e:
                print(f"Error retrieving Twitter data for {username}: {e}")
                # Only retry for certain errors
                if "Connection" in str(e) and attempt < retry_count - 1:
                    time.sleep(5)  # Wait 5 seconds before retry
                else:
                    # Fall back to synthetic data for other errors
                    return self._generate_fallback_data(username, "twitter")
        
        # If we've exhausted all retries
        return self._generate_fallback_data(username, "twitter")
    
    def _generate_fallback_data(self, username, platform):
        """Generate fallback data when API fails"""
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