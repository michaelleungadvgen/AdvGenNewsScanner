#!/usr/bin/env python3
"""
Improved Brisbane Newsletter Scanner
Automatically finds and scans the latest Living in Brisbane newsletter PDF.
"""

import requests
import PyPDF2
import io
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse


class ImprovedNewsletterScanner:
    def __init__(self, newsletter_page_url: str = "https://www.brisbane.qld.gov.au/about-council/news-and-community-updates/living-in-brisbane-newsletter"):
        self.newsletter_page_url = newsletter_page_url
        self.pdf_url = None
        self.content = ""
        self.sections = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def find_latest_pdf_url(self) -> Optional[str]:
        """Scrape the newsletter page to find the latest PDF link"""
        try:
            print(f"Searching for latest newsletter at: {self.newsletter_page_url}")
            response = self.session.get(self.newsletter_page_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for PDF links with various selectors
            pdf_selectors = [
                'a[href$=".pdf"]',
                'a[href*=".pdf"]',
                'a[href*="living-in-brisbane"]',
                'a[href*="newsletter"]',
                '.download-link a',
                '.pdf-link',
                '.document-link a'
            ]
            
            pdf_links = []
            for selector in pdf_selectors:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href and '.pdf' in href.lower():
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            href = urllib.parse.urljoin(self.newsletter_page_url, href)
                        elif not href.startswith('http'):
                            href = urllib.parse.urljoin(self.newsletter_page_url, href)
                        
                        # Filter for Brisbane newsletter PDFs
                        if any(keyword in href.lower() for keyword in ['living-in-brisbane', 'newsletter', 'brisbane']):
                            pdf_links.append({
                                'url': href,
                                'text': element.get_text().strip(),
                                'title': element.get('title', ''),
                                'element': element
                            })
            
            if not pdf_links:
                # Fallback: look for any PDF links and check their context
                all_pdf_links = soup.select('a[href*=".pdf"]')
                for link in all_pdf_links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            href = urllib.parse.urljoin(self.newsletter_page_url, href)
                        elif not href.startswith('http'):
                            href = urllib.parse.urljoin(self.newsletter_page_url, href)
                        
                        pdf_links.append({
                            'url': href,
                            'text': link.get_text().strip(),
                            'title': link.get('title', ''),
                            'element': link
                        })
            
            if pdf_links:
                print(f"Found {len(pdf_links)} PDF links:")
                for i, link in enumerate(pdf_links, 1):
                    print(f"  {i}. {link['text'][:60]}...")
                    print(f"     URL: {link['url']}")
                
                # Try to find the most recent/relevant one
                latest_pdf = self.select_latest_pdf(pdf_links)
                if latest_pdf:
                    print(f"Selected: {latest_pdf['text']}")
                    return latest_pdf['url']
            
            print("No PDF links found on the newsletter page")
            return None
            
        except Exception as e:
            print(f"Error finding PDF URL: {e}")
            return None
    
    def select_latest_pdf(self, pdf_links: List[Dict]) -> Optional[Dict]:
        """Select the most likely latest newsletter PDF from the list"""
        if not pdf_links:
            return None
        
        # Scoring system to find the best match
        scored_links = []
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        for link in pdf_links:
            score = 0
            url_lower = link['url'].lower()
            text_lower = link['text'].lower()
            
            # Higher score for current year
            if str(current_year) in url_lower or str(current_year) in text_lower:
                score += 10
            
            # Higher score for recent months
            months = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december']
            
            for i, month in enumerate(months, 1):
                if month in text_lower or month in url_lower:
                    if i >= current_month - 2:  # Current month or last 2 months
                        score += 8
                    else:
                        score += 3
            
            # Higher score for "latest", "current", etc.
            if any(keyword in text_lower for keyword in ['latest', 'current', 'new']):
                score += 5
            
            # Higher score for living-in-brisbane specifically
            if 'living-in-brisbane' in url_lower:
                score += 15
            
            # Higher score for newsletter
            if 'newsletter' in url_lower or 'newsletter' in text_lower:
                score += 5
            
            scored_links.append((score, link))
        
        # Sort by score (highest first)
        scored_links.sort(key=lambda x: x[0], reverse=True)
        
        print(f"PDF scoring results:")
        for score, link in scored_links[:3]:  # Show top 3
            print(f"  Score {score}: {link['text'][:50]}...")
        
        return scored_links[0][1] if scored_links else None
    
    def download_pdf(self, pdf_url: str) -> bytes:
        """Download PDF from URL and return bytes"""
        try:
            print(f"Downloading PDF: {pdf_url}")
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Check if it's actually a PDF
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and len(response.content) < 1000:
                raise Exception("Downloaded file doesn't appear to be a valid PDF")
            
            print(f"Downloaded {len(response.content):,} bytes")
            return response.content
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {e}")
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            text_content = ""
            for i, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text_content += page_text + "\n"
                print(f"Extracted {len(page_text)} characters from page {i}")
            
            return text_content
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page breaks and form feeds
        text = re.sub(r'[\f\r]', '\n', text)
        # Clean up line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def parse_sections(self, text: str) -> Dict[str, str]:
        """Parse text into logical sections"""
        sections = {}
        
        # Enhanced section patterns for Brisbane newsletters
        section_patterns = [
            r'(?i)(lord mayor[\'s]*\s*(?:message|update|word))',
            r'(?i)(community events?)',
            r'(?i)(council news)',
            r'(?i)(development.*(?:update|news))',
            r'(?i)(transport.*(?:update|news))',
            r'(?i)(parks?\s*and\s*recreation)',
            r'(?i)(library.*(?:news|update))',
            r'(?i)(waste.*(?:collection|service))',
            r'(?i)(contact.*(?:us|information))',
            r'(?i)(local business)',
            r'(?i)(environment.*(?:news|update))',
            r'(?i)(safety.*(?:update|news))',
            r'(?i)(planning.*(?:update|news))',
            r'(?i)(festivals?)',
            r'(?i)(grants?)',
            r'(?i)(infrastructure)',
            r'(?i)(what[\'s]*\s*on)',
            r'(?i)(events?\s*calendar)',
            r'(?i)(suburb.*(?:news|update))',
            r'(?i)(roads?.*(?:work|update))',
        ]
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        current_section = "General News"
        sections[current_section] = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph or len(paragraph) < 20:
                continue
                
            # Check if this paragraph starts a new section
            section_found = False
            for pattern in section_patterns:
                match = re.search(pattern, paragraph[:100])  # Check first 100 chars
                if match:
                    section_name = match.group(1).title()
                    # Clean up section name
                    section_name = re.sub(r'\s+', ' ', section_name)
                    current_section = section_name
                    if current_section not in sections:
                        sections[current_section] = []
                    section_found = True
                    break
            
            if paragraph:
                sections[current_section].append(paragraph)
        
        # Convert lists to strings and remove empty sections
        cleaned_sections = {}
        for section, content_list in sections.items():
            if content_list:
                cleaned_sections[section] = '\n\n'.join(content_list)
        
        return cleaned_sections
    
    def generate_markdown(self, sections: Dict[str, str], pdf_url: str) -> str:
        """Generate markdown summary from sections"""
        markdown = f"""# Brisbane Newsletter Summary
*Automatically generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

**Source PDF:** {pdf_url}

**Auto-discovered from:** {self.newsletter_page_url}

---

"""
        
        # Add table of contents
        markdown += "## Table of Contents\n\n"
        for section in sections.keys():
            if sections[section].strip():
                anchor = section.lower().replace(' ', '-').replace("'", "")
                markdown += f"- [{section}](#{anchor})\n"
        markdown += "\n---\n\n"
        
        # Add sections
        for section_name, content in sections.items():
            if content.strip():
                anchor = section_name.lower().replace(' ', '-').replace("'", "")
                markdown += f"## {section_name}\n\n"
                
                # Split content into key points
                points = content.split('\n\n')
                for point in points:
                    point = point.strip()
                    if point:
                        # Check if it looks like a heading
                        if len(point) < 100 and not point.endswith('.') and point.isupper():
                            markdown += f"### {point.title()}\n\n"
                        elif len(point) < 80 and not point.endswith('.') and point.count(' ') < 10:
                            markdown += f"**{point}**\n\n"
                        else:
                            markdown += f"{point}\n\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def scan(self) -> str:
        """Main method to auto-find and scan latest PDF"""
        print("=" * 60)
        print("  Brisbane Newsletter Auto-Scanner")
        print("=" * 60)
        
        # Find latest PDF URL
        pdf_url = self.find_latest_pdf_url()
        if not pdf_url:
            # Fallback to the hardcoded URL from original scanner
            print("Using fallback URL...")
            pdf_url = "https://www.brisbane.qld.gov.au/content/dam/brisbanecitycouncil/corpwebsite/about-council/documents/living-in-brisbane-august-2025-east.pdf.coredownload.pdf"
        
        self.pdf_url = pdf_url
        
        print("Downloading PDF...")
        pdf_bytes = self.download_pdf(pdf_url)
        
        print("Extracting text...")
        raw_text = self.extract_text(pdf_bytes)
        
        print("Cleaning text...")
        clean_text = self.clean_text(raw_text)
        
        print("Parsing sections...")
        sections = self.parse_sections(clean_text)
        print(f"Found {len(sections)} sections: {list(sections.keys())}")
        
        print("Generating markdown...")
        markdown = self.generate_markdown(sections, pdf_url)
        
        return markdown


def main():
    """Main function to run the improved newsletter scanner"""
    try:
        scanner = ImprovedNewsletterScanner()
        markdown_summary = scanner.scan()
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        output_file = f"brisbane_newsletter_summary_{timestamp}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_summary)
        
        print(f"\nSummary saved to {output_file}")
        print("\nPreview:")
        print("=" * 50)
        print(markdown_summary[:800] + "...")
        
        # Also save as the standard filename for the batch script
        with open("brisbane_newsletter_summary.md", 'w', encoding='utf-8') as f:
            f.write(markdown_summary)
        print("Also saved as brisbane_newsletter_summary.md")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()