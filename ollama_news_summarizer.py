#!/usr/bin/env python3
"""
Ollama News Summarizer
Collects all markdown files from scrapers and uses local Ollama to create comprehensive news summaries.
"""

import requests
import json
import os
import glob
from datetime import datetime
from typing import List, Dict
import time


class OllamaNewsSummarizer:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2", target_language: str = ""):
        self.ollama_url = ollama_url
        self.model = model
        self.target_language = target_language.strip()
        self.markdown_files = []
        self.summaries = []
        
        # Language code mapping for better user experience
        self.language_map = {
            "chinese": "Chinese (中文)",
            "mandarin": "Chinese (中文)",
            "zh": "Chinese (中文)",
            "ch": "Chinese (中文)",
            "traditional": "Traditional Chinese (繁體中文)",
            "simplified": "Simplified Chinese (简体中文)",
            "japanese": "Japanese (日本語)",
            "jp": "Japanese (日本語)",
            "ja": "Japanese (日本語)",
            "korean": "Korean (한국어)",
            "ko": "Korean (한국어)",
            "kr": "Korean (한국어)",
            "spanish": "Spanish (Español)",
            "es": "Spanish (Español)",
            "french": "French (Français)",
            "fr": "French (Français)",
            "german": "German (Deutsch)",
            "de": "German (Deutsch)",
            "italian": "Italian (Italiano)",
            "it": "Italian (Italiano)",
            "portuguese": "Portuguese (Português)",
            "pt": "Portuguese (Português)",
            "russian": "Russian (Русский)",
            "ru": "Russian (Русский)",
            "arabic": "Arabic (العربية)",
            "ar": "Arabic (العربية)",
            "hindi": "Hindi (हिन्दी)",
            "hi": "Hindi (हिन्दी)",
            "thai": "Thai (ไทย)",
            "th": "Thai (ไทย)",
            "vietnamese": "Vietnamese (Tiếng Việt)",
            "vi": "Vietnamese (Tiếng Việt)",
            "indonesian": "Indonesian (Bahasa Indonesia)",
            "id": "Indonesian (Bahasa Indonesia)",
            "malay": "Malay (Bahasa Melayu)",
            "ms": "Malay (Bahasa Melayu)",
        }
        
        # Normalize target language
        if self.target_language:
            self.target_language = self.language_map.get(self.target_language.lower(), self.target_language)
        
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/version", timeout=5)
            if response.status_code == 200:
                print(f"SUCCESS: Connected to Ollama at {self.ollama_url}")
                return True
            else:
                print(f"ERROR: Ollama responded with status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"ERROR: Cannot connect to Ollama: {e}")
            print("Make sure Ollama is running with: ollama serve")
            return False
    
    def check_model_available(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json()
                available_models = [model['name'] for model in models.get('models', [])]
                
                if self.model in available_models:
                    print(f"SUCCESS: Model '{self.model}' is available")
                    return True
                else:
                    print(f"ERROR: Model '{self.model}' not found")
                    print(f"Available models: {available_models}")
                    
                    # Try to pull the model
                    print(f"Attempting to pull model '{self.model}'...")
                    return self.pull_model()
            else:
                print(f"ERROR: Failed to get model list: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"ERROR: Error checking models: {e}")
            return False
    
    def pull_model(self) -> bool:
        """Pull the model if it's not available"""
        try:
            print(f"Pulling model '{self.model}' (this may take a while)...")
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model},
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if 'status' in data:
                            print(f"  {data['status']}")
                        if data.get('status') == 'success':
                            print(f"SUCCESS: Model '{self.model}' successfully pulled")
                            return True
            else:
                print(f"ERROR: Failed to pull model: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Error pulling model: {e}")
            return False
    
    def find_markdown_files(self) -> List[str]:
        """Find all markdown files generated by scrapers"""
        markdown_patterns = [
            "*.md",
            "*_summary.md",
            "*_news.md"
        ]
        
        markdown_files = []
        for pattern in markdown_patterns:
            files = glob.glob(pattern)
            markdown_files.extend(files)
        
        # Remove duplicates and filter for our specific files
        markdown_files = list(set(markdown_files))
        
        # Filter for files generated by our scrapers
        scraper_files = []
        for file in markdown_files:
            if any(keyword in file.lower() for keyword in ['brisbane', 'health', 'parliament', 'newsletter']):
                scraper_files.append(file)
        
        self.markdown_files = scraper_files
        print(f"Found {len(scraper_files)} markdown files: {scraper_files}")
        return scraper_files
    
    def read_markdown_content(self, file_path: str) -> Dict:
        """Read and parse markdown file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'filename': file_path,
                'content': content,
                'size': len(content),
                'lines': len(content.split('\n'))
            }
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def send_to_ollama(self, prompt: str, content: str) -> str:
        """Send content to Ollama for processing"""
        try:
            full_prompt = f"{prompt}\n\nContent to analyze:\n{content}"
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            print(f"Sending request to Ollama (content length: {len(content)} chars)...")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"Ollama API error: {response.status_code}")
                return f"Error: API returned status {response.status_code}"
                
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return f"Error: {e}"
    
    def summarize_individual_file(self, file_data: Dict) -> Dict:
        """Summarize an individual markdown file"""
        language_suffix = f" in {self.target_language}" if self.target_language else ""
        print(f"Summarizing {file_data['filename']}{language_suffix}...")
        
        if self.target_language:
            prompt = f"""Please provide a concise summary of this news content in {self.target_language}. Focus on:
1. Key headlines and main stories
2. Important dates and events
3. Major announcements or decisions
4. Community impact or significance

Keep the summary factual and well-organized. Aim for 3-5 bullet points per major story.

IMPORTANT: Write the entire summary in {self.target_language}, including all headings, bullet points, and explanations."""
        else:
            prompt = """Please provide a concise summary of this news content. Focus on:
1. Key headlines and main stories
2. Important dates and events
3. Major announcements or decisions
4. Community impact or significance

Keep the summary factual and well-organized. Aim for 3-5 bullet points per major story."""
        
        summary = self.send_to_ollama(prompt, file_data['content'])
        
        return {
            'filename': file_data['filename'],
            'summary': summary,
            'original_size': file_data['size']
        }
    
    def create_comprehensive_summary(self) -> str:
        """Create a comprehensive summary from all individual summaries"""
        language_suffix = f" in {self.target_language}" if self.target_language else ""
        print(f"Creating comprehensive summary from all sources{language_suffix}...")
        
        combined_summaries = "\n\n".join([
            f"## {summary['filename']}\n{summary['summary']}" 
            for summary in self.summaries
        ])
        
        if self.target_language:
            prompt = f"""You are analyzing news summaries from multiple Australian government and news sources. Please create a comprehensive overview in {self.target_language} that:

1. Identifies the most important stories across all sources
2. Groups related stories or themes together
3. Highlights any major trends or patterns
4. Provides context about the significance of events
5. Notes any conflicting information or different perspectives

Structure your response with clear headings and bullet points. Focus on what matters most to Australian citizens and communities.

IMPORTANT: Write the entire comprehensive summary in {self.target_language}, including all headings, bullet points, analysis, and conclusions."""
        else:
            prompt = """You are analyzing news summaries from multiple Australian government and news sources. Please create a comprehensive overview that:

1. Identifies the most important stories across all sources
2. Groups related stories or themes together
3. Highlights any major trends or patterns
4. Provides context about the significance of events
5. Notes any conflicting information or different perspectives

Structure your response with clear headings and bullet points. Focus on what matters most to Australian citizens and communities."""
        
        comprehensive_summary = self.send_to_ollama(prompt, combined_summaries)
        return comprehensive_summary
    
    def generate_final_report(self, comprehensive_summary: str) -> str:
        """Generate the final markdown report"""
        language_note = f" (Language: {self.target_language})" if self.target_language else ""
        
        if self.target_language:
            if "Chinese" in self.target_language:
                title = "综合新闻摘要"
                generated_by = "由 Ollama 生成于"
                model_used = "使用模型"
                sources_analyzed = "分析来源"
                executive_summary = "执行摘要"
                individual_summaries = "个人来源摘要"
                original_file_size = "原始文件大小"
                processing_time = "处理时间"
                total_content = "分析的总内容"
                tech_details = "技术细节"
                summary_note = "此摘要使用本地 Ollama AI 生成，分析了来自澳大利亚政府和新闻来源的抓取新闻内容。"
            elif "Japanese" in self.target_language:
                title = "総合ニュース要約"
                generated_by = "Ollama により生成"
                model_used = "使用モデル"
                sources_analyzed = "分析ソース数"
                executive_summary = "エグゼクティブサマリー"
                individual_summaries = "個別ソース要約"
                original_file_size = "元のファイルサイズ"
                processing_time = "処理時間"
                total_content = "分析された総コンテンツ"
                tech_details = "技術詳細"
                summary_note = "この要約は、オーストラリア政府およびニュースソースからスクレイピングされたニュースコンテンツを分析するためにローカル Ollama AI を使用して生成されました。"
            else:
                # Use English headers for other languages
                title = "Comprehensive News Summary"
                generated_by = "Generated by Ollama on"
                model_used = "Model Used"
                sources_analyzed = "Sources Analyzed"
                executive_summary = "Executive Summary"
                individual_summaries = "Individual Source Summaries"
                original_file_size = "Original file size"
                processing_time = "Processing Time"
                total_content = "Total Content Analyzed"
                tech_details = "Technical Details"
                summary_note = "This summary was generated using local Ollama AI to analyze scraped news content from Australian government and news sources."
        else:
            title = "Comprehensive News Summary"
            generated_by = "Generated by Ollama on"
            model_used = "Model Used"
            sources_analyzed = "Sources Analyzed"
            executive_summary = "Executive Summary"
            individual_summaries = "Individual Source Summaries"
            original_file_size = "Original file size"
            processing_time = "Processing Time"
            total_content = "Total Content Analyzed"
            tech_details = "Technical Details"
            summary_note = "This summary was generated using local Ollama AI to analyze scraped news content from Australian government and news sources."
        
        report = f"""# {title}{language_note}
*{generated_by} {datetime.now().strftime('%Y-%m-%d %H:%M')}*

**{model_used}:** {self.model}  
**{sources_analyzed}:** {len(self.markdown_files)} files

---

## {executive_summary}

{comprehensive_summary}

---

## {individual_summaries}

"""
        
        for summary in self.summaries:
            report += f"""### {summary['filename']}
*Original file size: {summary['original_size']:,} characters*

{summary['summary']}

---

"""
        
        report += f"""## Technical Details

- **Processing Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Ollama Model:** {self.model}
- **Sources Processed:** {len(self.markdown_files)}
- **Total Content Analyzed:** {sum(s['original_size'] for s in self.summaries):,} characters

---

*This summary was generated using local Ollama AI to analyze scraped news content from Australian government and news sources.*
"""
        
        return report
    
    def run_summarization(self) -> bool:
        """Main method to run the complete summarization process"""
        print("=" * 60)
        print("           Ollama News Summarizer")
        print("=" * 60)
        print()
        
        if self.target_language:
            print(f"Target Language: {self.target_language}")
            print()
        
        # Check Ollama connection
        if not self.check_ollama_connection():
            return False
        
        # Check model availability
        if not self.check_model_available():
            return False
        
        # Find markdown files
        markdown_files = self.find_markdown_files()
        if not markdown_files:
            print("No markdown files found to summarize")
            return False
        
        # Process each file
        print(f"\nProcessing {len(markdown_files)} files...")
        for file_path in markdown_files:
            file_data = self.read_markdown_content(file_path)
            if file_data:
                summary = self.summarize_individual_file(file_data)
                self.summaries.append(summary)
                time.sleep(1)  # Be nice to Ollama
        
        if not self.summaries:
            print("No files were successfully processed")
            return False
        
        # Create comprehensive summary
        comprehensive_summary = self.create_comprehensive_summary()
        
        # Generate final report
        final_report = self.generate_final_report(comprehensive_summary)
        
        # Save report with language suffix
        language_suffix = f"_{self.target_language.lower().split()[0]}" if self.target_language else ""
        output_file = f"comprehensive_news_summary{language_suffix}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_report)
        
        print(f"\nSUCCESS: Comprehensive summary saved to: {output_file}")
        print(f"SUCCESS: Processed {len(self.summaries)} sources")
        print(f"SUCCESS: Total content analyzed: {sum(s['original_size'] for s in self.summaries):,} characters")
        
        return True


def main():
    """Main function"""
    import sys
    
    # You can customize these settings
    OLLAMA_URL = "http://localhost:11434"
    MODEL = "llama3.1:8b"  # Using one of your available models
    TARGET_LANGUAGE = ""  # Default to English
    
    # Check for command line language argument
    if len(sys.argv) > 1:
        TARGET_LANGUAGE = sys.argv[1]
        print(f"Target language specified: {TARGET_LANGUAGE}")
    
    # Display available language options
    if TARGET_LANGUAGE.lower() in ["help", "-h", "--help"]:
        print("Available language options:")
        print("  (empty/default) - English")
        print("  chinese/zh - Chinese")
        print("  japanese/ja - Japanese")
        print("  korean/ko - Korean")
        print("  spanish/es - Spanish")
        print("  french/fr - French")
        print("  german/de - German")
        print("  italian/it - Italian")
        print("  portuguese/pt - Portuguese")
        print("  russian/ru - Russian")
        print("  arabic/ar - Arabic")
        print("  hindi/hi - Hindi")
        print("  thai/th - Thai")
        print("  vietnamese/vi - Vietnamese")
        print("  indonesian/id - Indonesian")
        print("  malay/ms - Malay")
        print("\nUsage: python ollama_news_summarizer.py [language]")
        print("Example: python ollama_news_summarizer.py chinese")
        return
    
    try:
        summarizer = OllamaNewsSummarizer(OLLAMA_URL, MODEL, TARGET_LANGUAGE)
        success = summarizer.run_summarization()
        
        if success:
            print("\n" + "=" * 60)
            print("           Summarization Complete!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("           Summarization Failed")
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n\nSummarization cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()