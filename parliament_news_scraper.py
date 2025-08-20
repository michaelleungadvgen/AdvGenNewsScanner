#!/usr/bin/env python3
"""
Australian Parliament House News & Events Scraper
Scrapes news and events from the Australian Parliament House website and generates a markdown file.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import time
import urllib.parse


class ParliamentNewsScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.articles = []
        
    def get_page(self, url: str) -> BeautifulSoup:
        """Get and parse a web page"""
        try:
            time.sleep(1)  # Be respectful to the server
            response = self.session.get(url, timeout=30, allow_redirects=True)
            print(f"Response status for {url}: {response.status_code}")
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_news_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract news and event links from the main page"""
        links = []
        
        # Debug: Print page structure
        print("Analyzing page structure...")
        all_links = soup.find_all('a', href=True)
        print(f"Total links found on page: {len(all_links)}")
        
        # Show sample links for debugging
        sample_links = [link.get('href') for link in all_links[:10]]
        print("Sample hrefs:", sample_links)
        
        # Common selectors for Australian Parliament House website
        article_selectors = [
            'a[href*="/News/"]',
            'a[href*="/news/"]',
            'a[href*="/Media/"]',
            'a[href*="/media/"]',
            'a[href*="/Events/"]',
            'a[href*="/events/"]',
            'a[href*="/Parliamentary_Business/"]',
            'a[href*="/About_Parliament/"]',
            '.news-item a',
            '.media-release a',
            '.event-item a',
            '.article-link',
            '.news-title a',
            '.event-title a',
            'h2 a',
            'h3 a',
            'h4 a',
            '.content-item a',
            'a'  # Catch all links as fallback
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
                    
                    # Filter for news/media/events articles - be more inclusive
                    if any(keyword in href.lower() for keyword in ['/news/', '/media/', '/events/', '/parliamentary_business/', '/about_parliament/']):
                        if href not in links and ('aph.gov.au' in href or href.startswith('/')):
                            links.append(href)
                    # Also include any link that looks like an article or press release
                    elif any(keyword in href.lower() for keyword in ['press', 'release', 'statement', 'announcement']):
                        if href not in links and ('aph.gov.au' in href or href.startswith('/')):
                            links.append(href)
        
        # Also look for links in common content areas
        content_areas = soup.find_all(['div', 'section'], class_=re.compile(r'(news|media|event|content)', re.I))
        for area in content_areas:
            for link in area.find_all('a', href=True):
                href = link.get('href')
                if href and href.startswith('/'):
                    full_url = urllib.parse.urljoin(self.base_url, href)
                    if any(keyword in full_url.lower() for keyword in ['/news/', '/media/', '/events/']):
                        if full_url not in links:
                            links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def extract_article_content(self, url: str) -> Dict:
        """Extract content from a single news article or event"""
        soup = self.get_page(url)
        if not soup:
            return None
        
        article = {
            'url': url,
            'title': '',
            'date': '',
            'content': '',
            'summary': '',
            'type': 'news'  # news, media, event
        }
        
        # Determine article type from URL
        if '/events/' in url.lower():
            article['type'] = 'event'
        elif '/media/' in url.lower():
            article['type'] = 'media'
        
        # Extract title
        title_selectors = [
            'h1',
            '.page-title',
            '.article-title',
            '.news-title',
            '.event-title',
            '.media-title',
            'title'
        ]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title_text = title_elem.get_text().strip()
                # Clean up title
                title_text = re.sub(r'\s+', ' ', title_text)
                if len(title_text) > 10 and 'Parliament of Australia' not in title_text:
                    article['title'] = title_text
                    break
        
        # Extract date
        date_selectors = [
            '.date',
            '.publish-date',
            '.article-date',
            '.event-date',
            '.media-date',
            'time',
            '[class*="date"]',
            '.metadata .date'
        ]
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text().strip()
                # Clean up date text
                date_text = re.sub(r'(Published|Date):?\s*', '', date_text, flags=re.IGNORECASE)
                if date_text and len(date_text) < 50:
                    article['date'] = date_text
                    break
        
        # Extract main content
        content_selectors = [
            '.article-content',
            '.news-content',
            '.event-content',
            '.media-content',
            '.content',
            '.article-body',
            '.main-content',
            'main .content',
            '.page-content'
        ]
        
        content_elem = None
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                break
        
        if not content_elem:
            # Fallback: look for the main content area
            main_elem = soup.find('main') or soup.find('div', class_=re.compile(r'main|content', re.I))
            if main_elem:
                content_elem = main_elem
        
        if content_elem:
            # Remove unwanted elements
            for unwanted in content_elem.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                unwanted.decompose()
            
            # Get text content from paragraphs
            paragraphs = content_elem.find_all(['p', 'div'], string=True)
            content_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 30:  # Filter out very short paragraphs
                    # Clean up text
                    text = re.sub(r'\s+', ' ', text)
                    content_parts.append(text)
            
            article['content'] = '\n\n'.join(content_parts)
            
            # Create summary from first meaningful paragraph
            if content_parts:
                first_paragraph = content_parts[0]
                article['summary'] = first_paragraph[:250] + '...' if len(first_paragraph) > 250 else first_paragraph
        
        # If no content found, try to get any text from the page
        if not article['content']:
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            # Filter out navigation and common elements
            content_lines = [line for line in lines if len(line) > 50 and 
                           not any(nav_word in line.lower() for nav_word in ['navigation', 'menu', 'skip to', 'breadcrumb'])]
            if content_lines:
                article['content'] = '\n\n'.join(content_lines[:10])  # Take first 10 meaningful lines
        
        return article if article['title'] and article['content'] else None
    
    def scrape_news(self, max_articles: int = 25) -> List[Dict]:
        """Scrape news articles and events from the main page"""
        print(f"Fetching content from: {self.base_url}")
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        # Extract article links
        article_links = self.extract_news_links(soup)
        print(f"Found {len(article_links)} potential article links")
        
        # Display some of the links for debugging
        if article_links:
            print("Sample links found:")
            for link in article_links[:5]:
                print(f"  - {link}")
        
        # Limit the number of articles to scrape
        article_links = article_links[:max_articles]
        
        articles = []
        for i, link in enumerate(article_links, 1):
            print(f"Scraping article {i}/{len(article_links)}: {link}")
            article = self.extract_article_content(link)
            if article:
                articles.append(article)
                print(f"  SUCCESS: {article['title'][:60]}...")
            else:
                print(f"  FAILED: Failed to extract content")
            
            # Be polite to the server
            time.sleep(1.5)
        
        return articles
    
    def generate_markdown(self, articles: List[Dict]) -> str:
        """Generate markdown from scraped articles"""
        markdown = f"""# Australian Parliament House News & Events
*Scraped on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

Source: {self.base_url}

Total articles: {len(articles)}

---

## Statistics

"""
        
        # Generate statistics
        news_count = len([a for a in articles if a['type'] == 'news'])
        media_count = len([a for a in articles if a['type'] == 'media'])
        event_count = len([a for a in articles if a['type'] == 'event'])
        
        markdown += f"- News articles: {news_count}\n"
        markdown += f"- Media releases: {media_count}\n"
        markdown += f"- Events: {event_count}\n\n"
        
        markdown += "## Table of Contents\n\n"
        
        # Generate table of contents grouped by type
        for article_type in ['news', 'media', 'event']:
            type_articles = [a for a in articles if a['type'] == article_type]
            if type_articles:
                type_name = article_type.title() + ('s' if article_type == 'news' else ' Releases' if article_type == 'media' else 's')
                markdown += f"### {type_name}\n\n"
                for i, article in enumerate(type_articles, 1):
                    title_anchor = re.sub(r'[^\w\s-]', '', article['title']).strip()
                    title_anchor = re.sub(r'[-\s]+', '-', title_anchor).lower()
                    markdown += f"{i}. [{article['title']}](#{title_anchor})\n"
                markdown += "\n"
        
        markdown += "---\n\n"
        
        # Add articles grouped by type
        for article_type in ['news', 'media', 'event']:
            type_articles = [a for a in articles if a['type'] == article_type]
            if type_articles:
                type_name = article_type.title() + ('s' if article_type == 'news' else ' Releases' if article_type == 'media' else 's')
                markdown += f"## {type_name}\n\n"
                
                for article in type_articles:
                    title_anchor = re.sub(r'[^\w\s-]', '', article['title']).strip()
                    title_anchor = re.sub(r'[-\s]+', '-', title_anchor).lower()
                    
                    markdown += f"### {article['title']}\n\n"
                    
                    if article['date']:
                        markdown += f"**Date:** {article['date']}\n\n"
                    
                    markdown += f"**Type:** {article['type'].title()}\n\n"
                    markdown += f"**Source:** [{article['url']}]({article['url']})\n\n"
                    
                    if article['summary']:
                        markdown += f"**Summary:** {article['summary']}\n\n"
                    
                    markdown += "#### Content\n\n"
                    
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
    """Main function to run the parliament news scraper"""
    base_url = "https://www.aph.gov.au/News_and_Events"
    
    try:
        scraper = ParliamentNewsScraper(base_url)
        
        print("Starting Australian Parliament House news scraping...")
        articles = scraper.scrape_news(max_articles=20)  # Limit to 20 articles for reasonable execution time
        
        if articles:
            print(f"\nSuccessfully scraped {len(articles)} articles")
            
            # Generate markdown
            markdown_content = scraper.generate_markdown(articles)
            
            # Save to file
            output_file = "parliament_news.md"
            scraper.save_to_file(markdown_content, output_file)
            
            print(f"\nMarkdown summary saved to {output_file}")
            print("\nPreview of first article:")
            print("=" * 50)
            if articles:
                print(f"Title: {articles[0]['title']}")
                print(f"Type: {articles[0]['type']}")
                print(f"Date: {articles[0]['date']}")
                print(f"Summary: {articles[0]['summary']}")
        else:
            print("No articles were successfully scraped")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()