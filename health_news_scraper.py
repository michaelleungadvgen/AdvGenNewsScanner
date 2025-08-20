#!/usr/bin/env python3
"""
Queensland Health News Scraper
Scrapes news articles from the Queensland Health newsroom and generates a markdown file.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import time
import urllib.parse


class HealthNewsScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.articles = []
        
    def get_page(self, url: str) -> BeautifulSoup:
        """Get and parse a web page"""
        try:
            # Add delay and retry logic
            time.sleep(2)
            response = self.session.get(url, timeout=30, allow_redirects=True)
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 403:
                print("403 Forbidden - Website may be blocking automated requests")
                print("Trying alternative approach...")
                
                # Try with different session
                alt_session = requests.Session()
                alt_session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (compatible; NewsScraper/1.0; +http://example.com/bot)',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache'
                })
                response = alt_session.get(url, timeout=30)
            
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            print(f"Status code: {getattr(e.response, 'status_code', 'N/A')}")
            return None
    
    def extract_article_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract article links from the news listing page"""
        links = []
        
        # Look for news article links
        article_selectors = [
            'a[href*="/news/"]',
            '.news-item a',
            '.article-link',
            '.news-title a',
            'h3 a',
            'h2 a'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = urllib.parse.urljoin(self.base_url, href)
                    elif not href.startswith('http'):
                        href = urllib.parse.urljoin(self.base_url, href)
                    
                    # Filter for news articles
                    if '/news/' in href and href not in links:
                        links.append(href)
        
        return links
    
    def extract_article_content(self, url: str) -> Dict:
        """Extract content from a single news article"""
        soup = self.get_page(url)
        if not soup:
            return None
        
        article = {
            'url': url,
            'title': '',
            'date': '',
            'content': '',
            'summary': ''
        }
        
        # Extract title
        title_selectors = ['h1', '.page-title', '.article-title', '.news-title', 'title']
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                article['title'] = title_elem.get_text().strip()
                break
        
        # Extract date
        date_selectors = [
            '.date',
            '.publish-date',
            '.article-date',
            'time',
            '.news-date',
            '[class*="date"]'
        ]
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text().strip()
                # Clean up date text
                date_text = re.sub(r'Published:?\s*', '', date_text, flags=re.IGNORECASE)
                article['date'] = date_text
                break
        
        # Extract main content
        content_selectors = [
            '.article-content',
            '.news-content',
            '.content',
            '.article-body',
            'main',
            '.main-content'
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if not content_elem:
            # Fallback: look for the largest text block
            paragraphs = soup.find_all('p')
            if paragraphs:
                content_elem = soup.new_tag('div')
                for p in paragraphs:
                    content_elem.append(p)
        
        if content_elem:
            # Remove unwanted elements
            for unwanted in content_elem.find_all(['script', 'style', 'nav', 'footer', 'header']):
                unwanted.decompose()
            
            # Get text content
            paragraphs = content_elem.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 20:  # Filter out very short paragraphs
                    content_parts.append(text)
            
            article['content'] = '\n\n'.join(content_parts)
            
            # Create summary from first paragraph
            if content_parts:
                article['summary'] = content_parts[0][:200] + '...' if len(content_parts[0]) > 200 else content_parts[0]
        
        return article if article['title'] and article['content'] else None
    
    def scrape_news(self, max_articles: int = 20) -> List[Dict]:
        """Scrape news articles from the main news page"""
        print(f"Fetching news from: {self.base_url}")
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        # Extract article links
        article_links = self.extract_article_links(soup)
        print(f"Found {len(article_links)} potential article links")
        
        # Limit the number of articles to scrape
        article_links = article_links[:max_articles]
        
        articles = []
        for i, link in enumerate(article_links, 1):
            print(f"Scraping article {i}/{len(article_links)}: {link}")
            article = self.extract_article_content(link)
            if article:
                articles.append(article)
                print(f"  ✓ {article['title'][:60]}...")
            else:
                print(f"  ✗ Failed to extract content")
            
            # Be polite to the server
            time.sleep(1)
        
        return articles
    
    def generate_markdown(self, articles: List[Dict]) -> str:
        """Generate markdown from scraped articles"""
        markdown = f"""# Queensland Health News
*Scraped on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

Source: {self.base_url}

Total articles: {len(articles)}

---

## Table of Contents

"""
        
        # Generate table of contents
        for i, article in enumerate(articles, 1):
            title_anchor = re.sub(r'[^\w\s-]', '', article['title']).strip()
            title_anchor = re.sub(r'[-\s]+', '-', title_anchor).lower()
            markdown += f"{i}. [{article['title']}](#{title_anchor})\n"
        
        markdown += "\n---\n\n"
        
        # Add articles
        for i, article in enumerate(articles, 1):
            title_anchor = re.sub(r'[^\w\s-]', '', article['title']).strip()
            title_anchor = re.sub(r'[-\s]+', '-', title_anchor).lower()
            
            markdown += f"## {i}. {article['title']}\n\n"
            
            if article['date']:
                markdown += f"**Date:** {article['date']}\n\n"
            
            markdown += f"**Source:** [{article['url']}]({article['url']})\n\n"
            
            if article['summary']:
                markdown += f"**Summary:** {article['summary']}\n\n"
            
            markdown += "### Content\n\n"
            
            # Split content into paragraphs for better formatting
            content_paragraphs = article['content'].split('\n\n')
            for paragraph in content_paragraphs:
                if paragraph.strip():
                    markdown += f"{paragraph.strip()}\n\n"
            
            markdown += "---\n\n"
        
        return markdown
    
    def save_to_file(self, content: str, filename: str):
        """Save content to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Content saved to {filename}")


def main():
    """Main function to run the news scraper"""
    base_url = "https://www.health.qld.gov.au/newsroom/news"
    
    try:
        scraper = HealthNewsScraper(base_url)
        
        print("Starting Queensland Health news scraping...")
        articles = scraper.scrape_news(max_articles=15)  # Limit to 15 articles for reasonable execution time
        
        if articles:
            print(f"\nSuccessfully scraped {len(articles)} articles")
            
            # Generate markdown
            markdown_content = scraper.generate_markdown(articles)
            
            # Save to file
            output_file = "qld_health_news.md"
            scraper.save_to_file(markdown_content, output_file)
            
            print(f"\nMarkdown summary saved to {output_file}")
            print("\nPreview of first article:")
            print("=" * 50)
            if articles:
                print(f"Title: {articles[0]['title']}")
                print(f"Date: {articles[0]['date']}")
                print(f"Summary: {articles[0]['summary']}")
        else:
            print("No articles were successfully scraped")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()