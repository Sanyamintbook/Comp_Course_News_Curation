import feedparser
from bs4 import BeautifulSoup
import requests
import re
from typing import List, Dict

class NewsScraper:
    def __init__(self, rss_urls: List[str], banned_words: set = None):
        self.rss_urls = rss_urls
        self.banned_words = banned_words or set()

    def clean_html(self, raw_html: str) -> str:
        """Removes HTML tags and cleans up whitespace."""
        if not raw_html:
            return ""
        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ")
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def fetch_latest_news(self) -> List[Dict]:
        """Fetches and cleans news articles from the provided RSS feeds."""
        articles = []
        for url in self.rss_urls:
            try:
                # Use requests with a browser User-Agent to prevent 403 Forbidden / 429 blocks from Google News
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                feed = feedparser.parse(response.content)
                
                if getattr(feed, 'bozo', 0) == 1 and not feed.entries:
                    print(f"Warning: Issue parsing feed {url}: {feed.bozo_exception}")
                
                for entry in feed.entries:  # Get ALL available news instead of limiting to 5
                    # Some feeds put content in 'content', others in 'summary'
                    content_raw = ""
                    if 'content' in entry:
                        content_raw = entry.content[0].value
                    elif 'summary' in entry:
                        content_raw = entry.summary
                    
                    clean_content = self.clean_html(content_raw)
                    
                    if not clean_content or len(clean_content) < 10:
                        # Skip empty or very short articles
                        continue
                        
                    # Strict Content Filtering (Checks Title and Content against Banned Words)
                    if self.banned_words:
                        combined_text = (entry.title + " " + clean_content).lower()
                        if any(banned in combined_text for banned in self.banned_words):
                            print(f"Blocked article due to content filter: {entry.title}")
                            continue
                        
                    article = {
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get('published', 'Unknown date'),
                        "content": clean_content,
                        "source": url
                    }
                    articles.append(article)
            except Exception as e:
                print(f"Error fetching from {url}: {str(e)}")
                
        return articles

if __name__ == "__main__":
    # Test with a sample educational science feed
    urls = [
        "https://www.sciencedaily.com/rss/top/science.xml"
    ]
    scraper = NewsScraper(urls)
    news = scraper.fetch_latest_news()
    for item in news:
        print(f"Title: {item['title']}\nPublished: {item['published']}\nSnippet: {item['content'][:150]}...\n")
