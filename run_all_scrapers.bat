@echo off
REM NewScanner - Batch file to run all Python scrapers
REM Created: 2025-08-20

echo ================================================
echo           NewScanner - All Scrapers
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Set timestamp for log files
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "timestamp=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%-%dt:~12,2%"

echo Starting scraper execution at %date% %time%
echo.

REM Check if required packages are installed
echo Checking Python dependencies...
python -c "import requests, bs4, PyPDF2" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)
echo Dependencies OK
echo.

REM 1. Brisbane Newsletter Scanner
echo [1/4] Running Brisbane Newsletter Scanner...
echo -----------------------------------------------
python newsletter_scanner.py > "logs\newsletter_%timestamp%.log" 2>&1
if errorlevel 1 (
    echo ERROR: Newsletter scanner failed. Check logs\newsletter_%timestamp%.log
) else (
    echo SUCCESS: Newsletter scanner completed
    if exist "brisbane_newsletter_summary.md" (
        echo   Output: brisbane_newsletter_summary.md
    )
)
echo.

REM 2. Queensland Health News Scraper (Alternative version)
echo [2/4] Running Queensland Health News Scraper...
echo -----------------------------------------------
python alternative_health_scraper.py > "logs\health_%timestamp%.log" 2>&1
if errorlevel 1 (
    echo ERROR: Health news scraper failed. Check logs\health_%timestamp%.log
) else (
    echo SUCCESS: Health news scraper completed
    if exist "qld_health_news_demo.md" (
        echo   Output: qld_health_news_demo.md
    )
)
echo.

REM 3. Parliament News Scraper
echo [3/4] Running Parliament News Scraper...
echo -----------------------------------------------
python parliament_news_scraper.py > "logs\parliament_%timestamp%.log" 2>&1
if errorlevel 1 (
    echo ERROR: Parliament news scraper failed. Check logs\parliament_%timestamp%.log
) else (
    echo SUCCESS: Parliament news scraper completed
    if exist "parliament_news.md" (
        echo   Output: parliament_news.md
    )
)
echo.

REM 4. Optional: Main Health News Scraper (if user wants to try)
echo [4/5] Running Main Health News Scraper (may fail due to access restrictions)...
echo -----------------------------------------------
python health_news_scraper.py > "logs\health_main_%timestamp%.log" 2>&1
if errorlevel 1 (
    echo NOTE: Main health scraper failed as expected (access restrictions)
) else (
    echo SUCCESS: Main health scraper completed
    if exist "qld_health_news.md" (
        echo   Output: qld_health_news.md
    )
)
echo.

REM 5. Ollama AI News Summarizer
echo [5/5] Running Ollama AI News Summarizer...
echo -----------------------------------------------
echo Checking if Ollama is running and processing all markdown files...
python ollama_news_summarizer.py > "logs\ollama_summary_%timestamp%.log" 2>&1
if errorlevel 1 (
    echo ERROR: Ollama summarizer failed. Check logs\ollama_summary_%timestamp%.log
    echo Make sure Ollama is running with: ollama serve
) else (
    echo SUCCESS: AI summary generated
    for %%f in (comprehensive_news_summary_*.md) do (
        echo   AI Summary: %%f
    )
)
echo.

REM Summary
echo ================================================
echo                   SUMMARY
echo ================================================
echo Execution completed at %date% %time%
echo.
echo Generated files:
if exist "brisbane_newsletter_summary.md" echo   - brisbane_newsletter_summary.md
if exist "qld_health_news_demo.md" echo   - qld_health_news_demo.md
if exist "parliament_news.md" echo   - parliament_news.md
if exist "qld_health_news.md" echo   - qld_health_news.md
for %%f in (comprehensive_news_summary_*.md) do (
    echo   - %%f [AI SUMMARY]
)
echo.
echo Log files are available in the 'logs' directory
echo Press any key to view the generated files...
pause >nul

REM Open output directory
explorer .

echo.
echo Complete workflow finished!
echo 1. News scraped from multiple sources
echo 2. AI summary generated using Ollama
echo Check the comprehensive_news_summary_*.md file for the AI analysis.
pause