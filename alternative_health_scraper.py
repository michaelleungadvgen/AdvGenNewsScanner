#!/usr/bin/env python3
"""
Alternative Queensland Health News Scraper
Uses RSS feed or alternative methods to scrape Queensland Health news.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
import json


class AlternativeHealthScraper:
    def __init__(self):
        self.base_url = "https://www.health.qld.gov.au"
        self.articles = []
        
    def try_rss_feed(self) -> List[Dict]:
        """Try to find and parse RSS feed"""
        rss_urls = [
            "https://www.health.qld.gov.au/news/rss",
            "https://www.health.qld.gov.au/newsroom/rss",
            "https://www.health.qld.gov.au/feed",
            "https://www.health.qld.gov.au/rss.xml"
        ]
        
        for rss_url in rss_urls:
            try:
                print(f"Trying RSS feed: {rss_url}")
                response = requests.get(rss_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')
                    if items:
                        print(f"Found {len(items)} items in RSS feed")
                        return self.parse_rss_items(items)
            except Exception as e:
                print(f"RSS feed {rss_url} failed: {e}")
                continue
        
        return []
    
    def parse_rss_items(self, items) -> List[Dict]:
        """Parse RSS items into article format"""
        articles = []
        for item in items:
            article = {
                'title': item.find('title').text if item.find('title') else '',
                'url': item.find('link').text if item.find('link') else '',
                'date': item.find('pubDate').text if item.find('pubDate') else '',
                'summary': item.find('description').text if item.find('description') else '',
                'content': ''
            }
            
            # Clean up HTML in summary
            if article['summary']:
                summary_soup = BeautifulSoup(article['summary'], 'html.parser')
                article['summary'] = summary_soup.get_text().strip()
            
            articles.append(article)
        
        return articles
    
    def create_sample_articles(self) -> List[Dict]:
        """Create sample articles for demonstration"""
        return [
            {
                'title': 'Queensland Health News Scraper Demo',
                'url': 'https://www.health.qld.gov.au/newsroom/news',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'summary': 'This is a demonstration of the Queensland Health news scraper. The actual website appears to block automated requests.',
                'content': '''This scraper was designed to extract news content from the Queensland Health newsroom.

However, the website appears to implement bot protection that returns a 403 Forbidden error when accessed programmatically.

Alternative approaches that could be tried:
- Using a headless browser like Selenium
- Looking for RSS feeds or API endpoints
- Requesting permission from Queensland Health for automated access
- Using proxy services or different IP addresses

The scraper includes comprehensive functionality for:
- Extracting article links from listing pages
- Parsing individual article content
- Cleaning and formatting text
- Generating structured markdown output
- Handling various HTML structures and selectors'''
            },
            {
                'title': 'Web Scraping Best Practices',
                'url': 'https://example.com/scraping-practices',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'summary': 'Guidelines for responsible web scraping and handling access restrictions.',
                'content': '''When encountering access restrictions while web scraping:

1. **Respect robots.txt**: Always check the site's robots.txt file
2. **Rate limiting**: Include delays between requests
3. **User agents**: Use appropriate user agent strings
4. **Error handling**: Implement robust error handling
5. **Alternative sources**: Look for RSS feeds or APIs
6. **Legal compliance**: Ensure scraping complies with terms of service
7. **Contact site owners**: Request permission for automated access

This scraper demonstrates these principles while providing a framework that can be adapted when access is available.'''
            }
        ]
    
    def generate_markdown(self, articles: List[Dict]) -> str:
        """Generate markdown from articles"""
        markdown = f"""# Queensland Health News
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

**Note:** This scraper encountered access restrictions (403 Forbidden) when attempting to access the Queensland Health newsroom. The articles below are demonstration content showing the scraper's capabilities.

Source: https://www.health.qld.gov.au/newsroom/news

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
    
    def scrape_news(self) -> List[Dict]:
        """Main scraping method"""
        print("Attempting to scrape Queensland Health news...")
        
        # Try RSS feed first
        articles = self.try_rss_feed()
        
        if not articles:
            print("RSS feeds not available, creating demonstration content...")
            articles = self.create_sample_articles()
        
        return articles


def main():
    """Main function"""
    try:
        scraper = AlternativeHealthScraper()
        articles = scraper.scrape_news()
        
        if articles:
            print(f"Generated {len(articles)} articles for demonstration")
            
            # Generate markdown
            markdown_content = scraper.generate_markdown(articles)
            
            # Save to file
            output_file = "qld_health_news_demo.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Demonstration content saved to {output_file}")
            print("\nPreview:")
            print("=" * 50)
            print(f"Title: {articles[0]['title']}")
            print(f"Summary: {articles[0]['summary']}")
            
        else:
            print("No content could be generated")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()