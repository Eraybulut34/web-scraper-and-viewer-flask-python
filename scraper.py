import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import time
from typing import Dict, List, Optional
from config import Config
from utils import setup_logger, retry, get_random_user_agent, sanitize_text

logger = setup_logger(__name__)

class NewsDatabase:
    """Database handler for news articles."""
    
    def __init__(self):
        """Initialize database connection with retry mechanism."""
        self.conn = None
        self.cur = None
        self._connect()
        self._create_tables()
    
    @retry(max_attempts=3, delay=2)
    def _connect(self) -> None:
        """Establish database connection with retry mechanism."""
        self.conn = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
        self.cur = self.conn.cursor()
        logger.info("Successfully connected to database")

    def _create_tables(self) -> None:
        """Create necessary database tables if they don't exist."""
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    image_url TEXT,
                    category TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_news_category ON news(category);
                CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at);
            """)
            self.conn.commit()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def save_news(self, news_data: Dict) -> bool:
        """Save news article to database."""
        try:
            self.cur.execute("""
                INSERT INTO news (title, content, url, image_url, category)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    image_url = EXCLUDED.image_url,
                    category = EXCLUDED.category
                RETURNING id
            """, (
                news_data['title'],
                news_data['content'],
                news_data['url'],
                news_data['image_url'],
                news_data['category']
            ))
            news_id = self.cur.fetchone()[0]
            self.conn.commit()
            logger.info(f"News saved successfully: {news_data['title']} (ID: {news_id})")
            return True
        except Exception as e:
            logger.error(f"Error saving news: {str(e)}")
            self.conn.rollback()
            return False

    def close(self) -> None:
        """Close database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

class NewsScraper:
    """News scraper implementation."""
    
    def __init__(self):
        """Initialize scraper with configuration."""
        self.base_url = "https://example.com"
        self.db = NewsDatabase()
        logger.info("News scraper initialized")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with random user agent."""
        return {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    @retry(max_attempts=3, delay=1)
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make HTTP request with retry mechanism."""
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            raise

    def get_news_list(self) -> List[str]:
        """Get list of news article URLs."""
        try:
            soup = self._make_request(self.base_url)
            if not soup:
                return []
            
            news_container = soup.find('div', class_='news-slider')
            if not news_container:
                logger.error("News container not found")
                return []

            news_links = []
            for item in news_container.find_all('a', class_='news-item'):
                if 'href' in item.attrs:
                    news_links.append(item['href'])
            
            logger.info(f"Found {len(news_links)} news articles")
            return news_links
        except Exception as e:
            logger.error(f"Error getting news list: {str(e)}")
            return []

    def scrape_news_detail(self, url: str) -> Optional[Dict]:
        """Scrape individual news article."""
        try:
            soup = self._make_request(url)
            if not soup:
                return None

            title = soup.find('h1')
            title = sanitize_text(title.text) if title else ""
            
            category = url.split('/')[3] if len(url.split('/')) > 3 else "genel"
            
            content_paragraphs = soup.find_all('p', class_='article-text')
            content = "\n".join([sanitize_text(p.text) for p in content_paragraphs]) if content_paragraphs else ""
            
            image = soup.find('meta', property='og:image')
            image_url = image['content'] if image else ""

            if not all([title, content]):
                logger.warning(f"Incomplete article data for URL: {url}")
                return None

            return {
                'title': title,
                'content': content,
                'url': url,
                'image_url': image_url,
                'category': category
            }
        except Exception as e:
            logger.error(f"Error scraping news detail from {url}: {str(e)}")
            return None

    def run(self) -> None:
        """Main scraper execution method."""
        try:
            news_links = self.get_news_list()
            if not news_links:
                logger.warning("No news links found")
                return

            for link in news_links:
                try:
                    full_url = link if link.startswith('http') else f"{self.base_url}{link}"
                    news_data = self.scrape_news_detail(full_url)
                    
                    if news_data:
                        self.db.save_news(news_data)
                    
                    time.sleep(Config.SCRAPE_INTERVAL)
                except Exception as e:
                    logger.error(f"Error processing link {link}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error in scraper execution: {str(e)}")
        finally:
            self.db.close()

if __name__ == "__main__":
    try:
        scraper = NewsScraper()
        scraper.run()
    except KeyboardInterrupt:
        logger.info("Scraper stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}") 