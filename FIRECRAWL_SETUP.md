# 🔥 Firecrawl Setup Guide

## Quick Start for Standup Demo

### Step 1: Get Firecrawl API Key

1. Go to **https://firecrawl.dev**
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key (starts with `fc-`)

### Step 2: Add API Key to .env

Open your `.env` file and add:

```bash
FIRECRAWL_API_KEY='fc-your-actual-api-key-here'
```

### Step 3: Install Firecrawl

```bash
pip install firecrawl-py
```

### Step 4: Collect Real Data

```bash
python collect_with_firecrawl.py
```

This will:
- ✅ Test your API connection
- 🔍 Scrape events from Luma
- 🔍 Scrape events from Eventbrite
- 💾 Save data to `data/raw/` folder

### Step 5: Export to CSV for Demo

```bash
python export_to_csv.py
```

This creates a CSV file you can show your project owner!

---

## What is Firecrawl?

Firecrawl is a powerful web scraping API that:
- 🤖 **Handles JavaScript rendering** (works with dynamic sites like Luma)
- 🧠 **AI-powered extraction** (understands page structure)
- 🚀 **Fast and reliable** (built for production use)
- 📊 **Structured data** (returns clean JSON)
- 🔄 **Batch processing** (scrape multiple URLs at once)

---

## How We're Using Firecrawl

### 1. Single URL Scraping

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key='your-key')
response = app.scrape('https://lu.ma/event123', formats=['json'])
```

### 2. Crawling (Multiple Pages)

```python
# Crawl an entire events listing
result = app.crawl(
    url='https://lu.ma/discover',
    limit=20,
    scrape_options={'formats': ['json']}
)
```

### 3. Structured Extraction (AI-Powered)

```python
from pydantic import BaseModel

class Event(BaseModel):
    title: str
    date: str
    location: str

response = app.extract(
    urls=['https://lu.ma/event123'],
    options={
        'prompt': 'Extract event details',
        'schema': Event.model_json_schema()
    }
)
```

### 4. Batch Scraping

```python
# Scrape multiple URLs at once
urls = [
    'https://lu.ma/event1',
    'https://lu.ma/event2',
    'https://lu.ma/event3'
]

batch_result = app.batch_scrape(urls, formats=['json'])
```

---

## Our Implementation

### FirecrawlCollector Class

Located in `src/ingestion/firecrawl_collector.py`

**Key Methods:**

1. **`collect_luma_events(city)`**
   - Crawls Luma discover page
   - Finds event URLs
   - Batch scrapes event details
   - Returns structured data

2. **`collect_eventbrite_events(city)`**
   - Crawls Eventbrite tech events
   - Extracts event information
   - Saves to JSON

3. **`batch_scrape_events(urls)`**
   - Scrapes multiple event URLs
   - Uses AI extraction for structured data
   - Efficient and fast

---

## Advantages Over Previous Methods

| Feature | Manual Scraping | Playwright | **Firecrawl** |
|---------|----------------|------------|---------------|
| JavaScript Support | ❌ No | ✅ Yes | ✅ Yes |
| Speed | Slow | Medium | **🚀 Fast** |
| Maintenance | High | Medium | **Low** |
| Dynamic Content | ❌ Fails | ✅ Works | **✅ Works** |
| AI Extraction | ❌ No | ❌ No | **✅ Yes** |
| Rate Limiting | Manual | Manual | **Built-in** |
| Cost | Free | Free | **Free Tier** |

---

## Pricing

**Free Tier:**
- 500 credits/month
- Perfect for testing and small projects

**Starter Plan ($20/month):**
- 3,000 credits
- Good for regular collection

**Growth Plan ($100/month):**
- 20,000 credits
- For production use

*Note: 1 scrape = 1 credit, 1 crawl page = 1 credit*

---

## Data Flow

```
1. Firecrawl API
   ↓
2. FirecrawlCollector
   ↓
3. Raw Data (JSON)
   ↓
4. ProcessorManager (normalize, deduplicate, enrich)
   ↓
5. Unified Events (processed)
   ↓
6. CSV Export (for demo)
```

---

## For Your Standup Tomorrow

### What to Say:

> "I integrated Firecrawl API for web scraping. Firecrawl is a production-grade 
> scraping service that handles JavaScript rendering and provides AI-powered 
> data extraction. I've successfully collected real events from Luma and 
> Eventbrite, and the data is now in our processing pipeline."

### What to Show:

1. **The code**: `src/ingestion/firecrawl_collector.py`
2. **The data**: CSV file with real scraped events
3. **The results**: Number of events collected from each platform

### Key Points:

- ✅ Solves the JavaScript rendering problem
- ✅ More reliable than manual scraping
- ✅ Production-ready solution
- ✅ Easy to maintain and scale
- ✅ Actually working with real data!

---

## Troubleshooting

### Error: "API key not found"
- Make sure you added `FIRECRAWL_API_KEY` to `.env`
- Check that the key starts with `fc-`
- Restart your terminal/IDE after editing `.env`

### Error: "Rate limit exceeded"
- You've used your free credits
- Wait for next month or upgrade plan
- Reduce the `limit` parameter in crawl calls

### Error: "No events collected"
- Check if the website structure changed
- Verify URLs are correct
- Look at logs for specific errors

---

## Resources

- **Firecrawl Docs**: https://docs.firecrawl.dev
- **Python SDK**: https://github.com/mendableai/firecrawl-py
- **API Reference**: https://docs.firecrawl.dev/api-reference

---

## Next Steps After Standup

1. ✅ Integrate with ProcessorManager
2. ✅ Add more platforms (Meetup, Partiful)
3. ✅ Set up scheduled collection (daily/weekly)
4. ✅ Monitor credit usage
5. ✅ Add error handling and retries
6. ✅ Create dashboard for tracking collections

