# NewScanner 🗞️🤖

**Automated News Intelligence Platform with AI-Powered Multilingual Summarization**

NewScanner is a comprehensive news scraping and analysis toolkit that automatically gathers content from Australian government and news sources, then generates intelligent summaries using local Ollama AI in multiple languages.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/AI-Ollama-green.svg)](https://ollama.ai/)

## 🚀 Features

### 📰 **Multi-Source News Scraping**
- **Brisbane Newsletter Scanner** - Auto-detects and processes latest Living in Brisbane PDFs
- **Queensland Health News** - Scrapes health department updates and announcements  
- **Australian Parliament News** - Extracts parliamentary news and events
- **Smart PDF Processing** - Automatically finds latest newsletters without manual URL updates

### 🤖 **AI-Powered Analysis**
- **Local Ollama Integration** - Uses your local AI models for privacy and control
- **Intelligent Summarization** - Extracts key headlines, dates, and community impact
- **Comprehensive Analysis** - Cross-source correlation and trend identification
- **No External APIs** - Everything runs locally on your machine

### 🌍 **Multilingual Support**
- **15+ Languages Supported** - Chinese, Japanese, Korean, Spanish, French, German, and more
- **Smart Language Detection** - Flexible language codes (e.g., `zh`, `chinese`, `mandarin`)
- **Localized Headers** - Native language interfaces for Chinese and Japanese
- **Default English** - No configuration needed for English summaries

### ⚡ **Automated Workflow**
- **One-Click Execution** - Run all scrapers and AI analysis with single batch file
- **Progress Tracking** - Real-time status updates and detailed logging
- **Error Handling** - Robust fallbacks and comprehensive error reporting
- **Output Management** - Timestamped files with organized directory structure

## 📦 Installation

### Prerequisites
- **Python 3.8+** installed on your system
- **Ollama** running locally ([Download here](https://ollama.ai/))
- **Git** (optional, for cloning)

### Quick Setup

1. **Clone or Download**
   ```bash
   git clone https://github.com/your-repo/NewScanner.git
   cd NewScanner
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Ollama**
   ```bash
   # Install and start Ollama
   ollama serve
   
   # Pull a recommended model
   ollama pull llama3.1:8b
   ```

4. **Run NewScanner**
   ```bash
   # Windows
   run_all_scrapers.bat
   
   # Or quick version
   run_quick.bat
   ```

## 🎯 Usage

### Basic Usage
```bash
# Run complete workflow (scraping + AI analysis)
python -c "exec(open('run_all_scrapers.bat').read())"

# Or use individual components
python improved_newsletter_scanner.py      # Brisbane newsletters
python parliament_news_scraper.py          # Parliament news
python alternative_health_scraper.py       # Health news
python ollama_news_summarizer.py          # AI summarization
```

### Multilingual Summaries
```bash
# English (default)
python ollama_news_summarizer.py

# Chinese
python ollama_news_summarizer.py chinese

# Japanese  
python ollama_news_summarizer.py japanese

# Spanish
python ollama_news_summarizer.py spanish

# View all supported languages
python ollama_news_summarizer.py help
```

### Advanced Configuration
```python
# Custom Ollama settings
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1:8b"  # or your preferred model
TARGET_LANGUAGE = "chinese"  # optional

summarizer = OllamaNewsSummarizer(OLLAMA_URL, MODEL, TARGET_LANGUAGE)
```

## 📁 Project Structure

```
NewScanner/
├── 📄 README.md                          # This file
├── 📄 LICENSE                            # MIT License
├── 📄 requirements.txt                   # Python dependencies
├── 📄 run_all_scrapers.bat              # Complete workflow (Windows)
├── 📄 run_quick.bat                      # Quick execution (Windows)
│
├── 🔧 Core Scrapers
│   ├── newsletter_scanner.py             # Original Brisbane scanner
│   ├── improved_newsletter_scanner.py    # Enhanced auto-detection
│   ├── parliament_news_scraper.py        # Parliament House news
│   ├── health_news_scraper.py           # Queensland Health (main)
│   └── alternative_health_scraper.py     # Health fallback
│
├── 🤖 AI Analysis
│   └── ollama_news_summarizer.py        # Multilingual AI summarizer
│
├── 📊 Output Files
│   ├── *.md                             # Generated summaries
│   └── logs/                            # Execution logs
│
└── 📚 Documentation
    └── examples/                        # Usage examples
```

## 🔧 Configuration

### Ollama Models
Recommended models for best results:
- **llama3.1:8b** - Best balance of speed and quality
- **llama3.2** - Latest features
- **mistral** - Good for European languages
- **codellama** - Enhanced for technical content

### Supported Languages
| Language | Codes | Example |
|----------|-------|---------|
| English | `(default)` | `python ollama_news_summarizer.py` |
| Chinese | `chinese`, `zh`, `mandarin` | `python ollama_news_summarizer.py chinese` |
| Japanese | `japanese`, `ja`, `jp` | `python ollama_news_summarizer.py japanese` |
| Korean | `korean`, `ko`, `kr` | `python ollama_news_summarizer.py korean` |
| Spanish | `spanish`, `es` | `python ollama_news_summarizer.py spanish` |
| French | `french`, `fr` | `python ollama_news_summarizer.py french` |
| German | `german`, `de` | `python ollama_news_summarizer.py german` |

## 📋 Examples

### Sample Output
```markdown
# Comprehensive News Summary (Language: Chinese (中文))
*由 Ollama 生成于 2025-08-20 12:13*

## 执行摘要
**基础设施发展**
- 布里斯班地铁从6月30日开始运营M1路线
- 阿德莱德街隧道即将开通，连接内北和东南快速公交线

**环境倡议**  
- 布里斯班市议会向所有符合条件的家庭提供绿色垃圾桶
- 每年从垃圾填埋场转移超过43,000吨废物
```

### Integration Example
```python
from ollama_news_summarizer import OllamaNewsSummarizer

# Create multilingual summarizer
summarizer = OllamaNewsSummarizer(
    ollama_url="http://localhost:11434",
    model="llama3.1:8b", 
    target_language="chinese"
)

# Run analysis
success = summarizer.run_summarization()
if success:
    print("✅ Analysis complete!")
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Bug Reports** - Found an issue? Open a GitHub issue
2. **💡 Feature Requests** - Have an idea? We'd love to hear it
3. **🔧 Code Contributions** - Fork, improve, and submit a PR
4. **🌍 Translations** - Help add more language support
5. **📚 Documentation** - Improve guides and examples

### Development Setup
```bash
# Clone repo
git clone https://github.com/your-repo/NewScanner.git

# Install in development mode  
pip install -e .

# Run tests
python -m pytest tests/
```

## 📊 Performance

| Component | Processing Time | Output |
|-----------|----------------|---------|
| Brisbane Newsletter | ~30 seconds | Auto-detected latest PDF |
| Parliament News | ~45 seconds | 5-10 articles |
| Health News | ~20 seconds | Demo content |
| AI Summarization | ~60 seconds | Multilingual analysis |
| **Total Workflow** | **~3 minutes** | **Complete intelligence report** |

## 🔒 Privacy & Security

- **🏠 Local Processing** - All AI analysis runs on your machine
- **🔐 No External APIs** - Data never leaves your system
- **📊 No Tracking** - Zero telemetry or data collection
- **🛡️ Open Source** - Full transparency in code and operations

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Dependencies Licenses
- `requests` - Apache 2.0 License
- `PyPDF2` - BSD 3-Clause License  
- `beautifulsoup4` - MIT License

All dependencies are MIT-compatible.

## 🙏 Acknowledgments

- **Ollama Team** - For the amazing local AI platform
- **Brisbane City Council** - For open access to community newsletters
- **Australian Parliament** - For transparent public information
- **Queensland Health** - For accessible health communications
- **Open Source Community** - For the incredible libraries that make this possible

## 📞 Support

- **📖 Documentation** - Check this README and inline code comments
- **🐛 Issues** - Report bugs via GitHub Issues
- **💬 Discussions** - Join GitHub Discussions for questions
- **📧 Contact** - [Your contact information]

---

**Made with ❤️ by AdvanGeneration Pty Ltd**

*Empowering communities with intelligent news analysis*