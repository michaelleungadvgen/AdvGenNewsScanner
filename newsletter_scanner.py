#!/usr/bin/env python3
"""
Brisbane Newsletter Scanner
Scans the Living in Brisbane newsletter PDF and generates a markdown summary.
"""

import requests
import PyPDF2
import io
import re
from typing import List, Dict
from datetime import datetime


class NewsletterScanner:
    def __init__(self, pdf_url: str):
        self.pdf_url = pdf_url
        self.content = ""
        self.sections = {}
        
    def download_pdf(self) -> bytes:
        """Download PDF from URL and return bytes"""
        try:
            response = requests.get(self.pdf_url, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise Exception(f"Failed to download PDF: {e}")
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
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
        
        # Common section patterns for Brisbane newsletters
        section_patterns = [
            r'(?i)(community events?)',
            r'(?i)(council news)',
            r'(?i)(development)',
            r'(?i)(transport)',
            r'(?i)(parks? and recreation)',
            r'(?i)(library)',
            r'(?i)(waste)',
            r'(?i)(contact)',
            r'(?i)(mayor)',
            r'(?i)(local business)',
            r'(?i)(environment)',
            r'(?i)(safety)',
            r'(?i)(planning)',
        ]
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        current_section = "General"
        sections[current_section] = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if this paragraph starts a new section
            section_found = False
            for pattern in section_patterns:
                if re.search(pattern, paragraph[:50]):  # Check first 50 chars
                    current_section = re.search(pattern, paragraph[:50]).group(1).title()
                    sections[current_section] = []
                    section_found = True
                    break
            
            if paragraph:
                sections[current_section].append(paragraph)
        
        # Convert lists to strings
        for section in sections:
            sections[section] = '\n\n'.join(sections[section])
        
        return sections
    
    def generate_markdown(self, sections: Dict[str, str]) -> str:
        """Generate markdown summary from sections"""
        markdown = f"""# Brisbane Newsletter Summary
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*

Source: {self.pdf_url}

---

"""
        
        # Add table of contents
        markdown += "## Table of Contents\n\n"
        for section in sections.keys():
            if sections[section].strip():
                markdown += f"- [{section}](#{section.lower().replace(' ', '-')})\n"
        markdown += "\n---\n\n"
        
        # Add sections
        for section_name, content in sections.items():
            if content.strip():
                markdown += f"## {section_name}\n\n"
                
                # Split content into key points
                points = content.split('\n\n')
                for point in points:
                    point = point.strip()
                    if point:
                        # Check if it looks like a heading
                        if len(point) < 100 and not point.endswith('.'):
                            markdown += f"### {point}\n\n"
                        else:
                            markdown += f"{point}\n\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def scan(self) -> str:
        """Main method to scan PDF and return markdown summary"""
        print("Downloading PDF...")
        pdf_bytes = self.download_pdf()
        
        print("Extracting text...")
        raw_text = self.extract_text(pdf_bytes)
        
        print("Cleaning text...")
        clean_text = self.clean_text(raw_text)
        
        print("Parsing sections...")
        sections = self.parse_sections(clean_text)
        
        print("Generating markdown...")
        markdown = self.generate_markdown(sections)
        
        return markdown


def main():
    """Main function to run the newsletter scanner"""
    pdf_url = "https://www.brisbane.qld.gov.au/content/dam/brisbanecitycouncil/corpwebsite/about-council/documents/living-in-brisbane-august-2025-east.pdf.coredownload.pdf"
    
    try:
        scanner = NewsletterScanner(pdf_url)
        markdown_summary = scanner.scan()
        
        # Save to file
        output_file = "brisbane_newsletter_summary.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_summary)
        
        print(f"Summary saved to {output_file}")
        print("\nPreview:")
        print("=" * 50)
        print(markdown_summary[:500] + "...")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()