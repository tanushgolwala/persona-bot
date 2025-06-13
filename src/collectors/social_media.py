import json
import os
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime, timedelta
import pandas as pd

class SocialMediaCollector:
    def __init__(self):
        self.platforms = ["twitter", "facebook", "instagram"]
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15'
        ]
        
    def collect_user_data(self, username, platform):
        """Collect posts for a given username"""
        if platform.lower() == "twitter":
            return self._collect_twitter_data(username)
        else:
            print(f"Platform {platform} not implemented with web scraping")
            return []
    
    def _collect_twitter_data(self, username, max_tweets=20):
        """Web scrape tweets for the given username"""
        tweets = []
        
        # List of Nitter instances to try
        nitter_instances = [
            f"https://nitter.net/{username}",
            f"https://nitter.unixfox.eu/{username}",
            f"https://nitter.it/{username}",
            f"https://nitter.poast.org/{username}",
            f"https://nitter.privacydev.net/{username}"
        ]
        
        # Randomize user agent
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Try each Nitter instance
        html_content = None
        used_url = None
        
        for url in nitter_instances:
            try:
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    html_content = response.text
                    used_url = url
                    
                    # Save the HTML for debugging if needed
                    os.makedirs("data/debug", exist_ok=True)
                    with open(f"data/debug/nitter_response_{username}.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    
                    # Check for common error messages in the HTML
                    if "User not found" in html_content or "user not found" in html_content.lower():
                        print(f"User {username} not found on Twitter/Nitter")
                        return tweets
                    if "This account's tweets are protected" in html_content or "protected account" in html_content.lower():
                        print(f"Account {username} is protected/private")
                        return tweets
                    if "Rate limit exceeded" in html_content:
                        continue
                        
                    break
            except Exception as e:
                continue
        
        if not html_content:
            print("Failed to retrieve data from any Nitter instance")
            return tweets
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try different selectors for tweet containers
        selectors = [
            '.timeline-item',  # Standard Nitter
            '.tweet-body',     # Some Nitter instances
            '.tweet',          # Possible alternative
            '.timeline .tweet', # Another alternative
            '[data-testid="tweet"]', # Yet another alternative
            '.main-tweet'      # Main tweet on single tweet pages
        ]
        
        tweet_containers = []
        
        for selector in selectors:
            containers = soup.select(selector)
            if containers:
                tweet_containers = containers
                break
        
        if not tweet_containers:
            # Try alternative content detection
            timeline = soup.select_one('.timeline')
            if timeline:
                children = timeline.find_all(recursive=False)
                potential_tweets = [child for child in children if child.get_text().strip()]
                if potential_tweets:
                    tweet_containers = potential_tweets[:max_tweets]
            else:
                # Last resort: look for typical tweet content patterns
                all_divs = soup.find_all('div')
                potential_tweets = []
                for div in all_divs:
                    spans = div.find_all('span')
                    has_timestamp = any('ago' in span.get_text().lower() for span in spans)
                    paragraphs = div.find_all('p')
                    has_text = any(len(p.get_text().strip()) > 20 for p in paragraphs)
                    if has_timestamp and has_text:
                        potential_tweets.append(div)
                
                if potential_tweets:
                    tweet_containers = potential_tweets[:max_tweets]
        
        # Process each tweet
        for container in tweet_containers[:max_tweets]:
            try:
                # Try different selectors for tweet content
                tweet_text = ""
                content_selectors = ['.tweet-content', '.tweet-text', '.content', 'p', '.main-tweet .tweet-content', 'article']
                for content_selector in content_selectors:
                    content_elems = container.select(content_selector)
                    if content_elems:
                        # Combine text from all matching elements
                        tweet_text = " ".join([elem.get_text(strip=True) for elem in content_elems])
                        break
                
                if not tweet_text and container.get_text():
                    tweet_text = container.get_text(strip=True)
                
                # Clean up tweet text (remove excess whitespace, etc)
                tweet_text = " ".join(tweet_text.split())
                
                # Extract timestamp
                timestamp = datetime.now().isoformat()  # Default to now
                
                # Try different selectors for timestamp
                time_selectors = ['.tweet-date a', '.date a', '.timestamp', 'time', 'span[title]', 'a[title]']
                for time_selector in time_selectors:
                    time_elems = container.select(time_selector)
                    for time_elem in time_elems:
                        if time_elem.get('title') and ('ago' in time_elem.get_text().lower() or ':' in time_elem.get('title')):
                            timestamp = time_elem.get('title')
                            break
                        elif time_elem.get('datetime'):
                            timestamp = time_elem.get('datetime')
                            break
                        elif 'ago' in time_elem.get_text().lower():
                            relative_time = time_elem.get_text(strip=True)
                            timestamp = self._convert_relative_time(relative_time)
                            break
                    
                    if timestamp != datetime.now().isoformat():
                        break
                
                # For engagement metrics, try different approaches
                engagement_metrics = {'reply_count': 0, 'retweet_count': 0, 'like_count': 0}
                
                # Try the standard stats selector
                stats = container.select('.tweet-stats .icon-container')
                if stats and len(stats) >= 3:
                    engagement_metrics['reply_count'] = self._parse_count(stats[0].get_text(strip=True))
                    engagement_metrics['retweet_count'] = self._parse_count(stats[1].get_text(strip=True))
                    engagement_metrics['like_count'] = self._parse_count(stats[2].get_text(strip=True))
                else:
                    # Try alternative selectors
                    for metric_type, selectors in {
                        'reply_count': ['.reply-count', '.replies', '[data-testid="reply"]'],
                        'retweet_count': ['.retweet-count', '.retweets', '[data-testid="retweet"]'],
                        'like_count': ['.like-count', '.likes', '[data-testid="like"]']
                    }.items():
                        for selector in selectors:
                            metric_elems = container.select(selector)
                            for metric_elem in metric_elems:
                                if metric_elem:
                                    engagement_metrics[metric_type] = self._parse_count(metric_elem.get_text(strip=True))
                                    break
                
                # If the tweet text is still empty, the container might not be a tweet
                if not tweet_text:
                    continue
                
                # Create tweet object with same structure as original code
                tweet = {
                    "user_id": username,
                    "timestamp": timestamp,
                    "text": tweet_text,
                    "platform": "twitter",
                    "retweet_count": engagement_metrics['retweet_count'],
                    "like_count": engagement_metrics['like_count'],
                    "reply_count": engagement_metrics['reply_count']
                }
                
                tweets.append(tweet)
                
            except Exception as e:
                print(f"Error processing tweet: {str(e)}")
        
        if tweets:
            # Save to JSON
            self._save_to_json(tweets, username)
        
        return tweets
    
    def _convert_relative_time(self, relative_time):
        """Convert relative time string to timestamp"""
        now = datetime.now()
        if not relative_time or not isinstance(relative_time, str):
            return now.isoformat()
        
        relative_time = relative_time.lower()
        try:
            if 'h' in relative_time:
                hours = int(''.join(filter(str.isdigit, relative_time)))
                timestamp = now - timedelta(hours=hours)
            elif 'm' in relative_time:
                minutes = int(''.join(filter(str.isdigit, relative_time)))
                timestamp = now - timedelta(minutes=minutes)
            elif 'd' in relative_time:
                days = int(''.join(filter(str.isdigit, relative_time)))
                timestamp = now - timedelta(days=days)
            elif 'y' in relative_time:
                years = int(''.join(filter(str.isdigit, relative_time)))
                timestamp = now - timedelta(days=years*365)
            else:
                return now.isoformat()
                
            return timestamp.isoformat()
        except:
            return now.isoformat()
    
    def _parse_count(self, count_str):
        """Parse count strings like '1.5K' to integers"""
        if not count_str or not isinstance(count_str, str):
            return 0
            
        try:
            count_str = count_str.strip()
            if not count_str or count_str == '':
                return 0
                
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            else:
                return int(''.join(filter(str.isdigit, count_str)))
        except:
            return 0
    
    def _save_to_json(self, data, username):
        """Save the collected data to a JSON file"""
        # Create directories if they don't exist
        os.makedirs("data/scraped", exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/scraped/twitter_{username}_{timestamp}.json"
        
        # Save data to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"Twitter data for {username} saved to {filename}")