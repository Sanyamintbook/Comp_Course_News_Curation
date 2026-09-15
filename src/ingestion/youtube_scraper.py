import urllib.request
import urllib.parse
import re
import json

class YouTubeScraper:
    def __init__(self, banned_words=None):
        self.banned_words = banned_words or set()
        
    def fetch_videos(self, query: str, max_results: int = 5):
        """Scrapes YouTube for the top educational videos based on a query."""
        try:
            q_encoded = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={q_encoded}"
            
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            try:
                res = requests.get(url, headers=headers, timeout=5)
                html = res.text
            except Exception as e:
                print(f"YouTube request timed out or failed: {e}")
                return []
            
            # Extract ytInitialData
            match = re.search(r'var ytInitialData = (\{.*?\});</script>', html)
            if not match:
                return []
                
            data = json.loads(match.group(1))
            videos = []
            
            # Navigate the JSON tree to find video renderers
            try:
                contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                for item in contents:
                    if 'videoRenderer' in item:
                        vid = item['videoRenderer']
                        title = vid.get('title', {}).get('runs', [{}])[0].get('text', 'No Title')
                        video_id = vid.get('videoId', '')
                        published = vid.get('publishedTimeText', {}).get('simpleText', 'Unknown')
                        
                        # Filter out banned words
                        if any(banned in title.lower() for banned in self.banned_words):
                            continue
                            
                        videos.append({
                            "title": f"🎥 {title}",
                            "link": f"https://www.youtube.com/watch?v={video_id}",
                            "published": published,
                            "subject": "Video Course",
                            "distance": 0.001
                        })
                        
                        if len(videos) >= max_results:
                            break
            except Exception as e:
                print(f"Error parsing YouTube JSON: {e}")
                
            return videos
            
        except Exception as e:
            print(f"YouTube scraper failed: {e}")
            return []
