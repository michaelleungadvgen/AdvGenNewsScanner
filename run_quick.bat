@echo off
REM Quick launcher for NewScanner - runs all scrapers + AI summary

echo Running all scrapers + AI summary...

python newsletter_scanner.py
echo.

python alternative_health_scraper.py  
echo.

python parliament_news_scraper.py
echo.

echo Running AI summarizer...
python ollama_news_summarizer.py
echo.

echo Complete workflow finished!
echo Check comprehensive_news_summary_*.md for AI analysis.
pause