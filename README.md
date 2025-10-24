# 🔥 Firecrawl Events Scraper

A Python-based event scraping system using the Firecrawl API to collect and organize tech events from multiple platforms.

## 🎯 Overview

This project demonstrates how to use Firecrawl API to scrape event data from platforms like Luma, Eventbrite, and Meetup, then organize the results according to specific query categories for benchmarking and analysis.

## ✨ Key Features

- **Multi-Platform Scraping**: Luma, Eventbrite, Meetup across multiple cities
- **Query-Based Organization**: Results organized by 20 test queries from TEST_QUERIES.md
- **Clean Data Export**: CSV outputs with bullet-pointed results
- **Real Event Data**: 757+ events collected with titles, dates, and links

## 📊 Results

### Latest Run (October 23, 2025)
- **757 events** collected across 10 platforms
- **100% platform success rate**
- **107 events** (14.1%) matched query categories
- **Categories**: AI events (53), Tech meetups (47), Sustainability (12), Workshops (9)

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install firecrawl-py python-dotenv pandas

# Set up environment variables
cp env_template.txt .env
# Edit .env and add your FIRECRAWL_API_KEY
```

### 2. Run the Scraper
```bash
# Run the main scraper
python improved_firecrawl_scraper.py

# Organize results by queries
python create_query_results.py

# View results
python show_results.py
```

## 📁 Project Structure

```
firecrawl-events-scraper/
├── improved_firecrawl_scraper.py    # Main scraping script
├── create_query_results.py           # Query organization script
├── show_results.py                  # Results display script
├── firecrawl_collector.py           # Firecrawl collector class
├── base_collector.py                # Base collector utilities
├── cities_config.py                 # City configuration
├── requirements.txt                 # Dependencies
├── env_template.txt                 # Environment template
├── outputs/
│   ├── csv/                         # CSV exports
│   └── json/                        # JSON exports
└── docs/
    ├── FIRECRAWL_SETUP.md           # Setup guide
    ├── FIRECRAWL_BENCHMARK_RESULTS.md
    └── FIRECRAWL_SEARCH_SUMMARY.md
```

## 📈 Output Files

### CSV Files
- `firecrawl_categorized_events_*.csv` - Main event data with categories
- `firecrawl_platforms_*.csv` - Platform performance metrics
- `query_results_*.csv` - Results organized by 20 test queries

### JSON Files
- `firecrawl_improved_results_*.json` - Complete results with metadata

## 🎯 Query Categories

The scraper organizes results by 4 query categories:

1. **Queries 1-5**: Time + Location Filters
2. **Queries 6-10**: Topic-Specific Queries
3. **Queries 11-15**: Organizer/Platform Filters
4. **Queries 16-20**: Event Format/Type Filters

## 🔧 Configuration

### Supported Cities
- New York City
- San Francisco
- Chicago
- Austin
- Los Angeles

### Supported Platforms
- **Luma**: Community events and meetups
- **Eventbrite**: Tech events and workshops
- **Meetup**: Local tech meetups

## 📊 Sample Results

**Query 1 (AI events Oct 19 NYC):**
- • Matcha Vintage Dimatchai Pop-Up at KALEIDOS (Sat, Oct 25) - [Luma Nyc Discovery Page]
- • GTC DC AI Pioneers Cocktail Reception (Mon, Oct 27) - [Luma Nyc Discovery Page]

**Query 3 (Climate events Chicago):**
- • Chicago · Joy District (Fri, Nov 14) - https://www.eventbrite.com/d/chicago/tech-events/
- • Chicago · Host women in tech in your HQ (Thu, Nov 13) - https://www.eventbrite.com/e/outgeek-women-in-t...

## 🛠️ Dependencies

- `firecrawl-py` - Firecrawl API client
- `python-dotenv` - Environment variable management
- `pandas` - Data manipulation
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing

## 📝 API Key Setup

1. Get your Firecrawl API key from [firecrawl.dev](https://firecrawl.dev)
2. Add it to your `.env` file:
   ```
   FIRECRAWL_API_KEY=your_api_key_here
   ```

## 🎓 Capstone Project Context

This project was developed as part of a capstone project to demonstrate:
- **API Integration**: Using Firecrawl for web scraping
- **Data Organization**: Structuring results by query categories
- **Real-World Application**: Collecting actual event data for analysis
- **Clean Output**: Professional CSV exports for stakeholders

## 📞 Contact

Developed for capstone project demonstration of Firecrawl API capabilities in event data collection and organization.
