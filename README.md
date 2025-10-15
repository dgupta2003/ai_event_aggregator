# AI Event Aggregator - Ollama Search Benchmark Suite

A comprehensive benchmarking framework for evaluating the **Ollama Search API** on event discovery queries. This suite validates search accuracy, response time, and result quality using constraint-based evaluation across 20 diverse test queries.

---

## 📋 Overview

This project benchmarks the Ollama Search API's ability to find relevant events based on complex, multi-constraint queries. It includes:

- **Constraint-based validation**: Independently verifies search results against expected topics, locations, platforms, event types, formats, and time windows
- **Comprehensive metrics**: Accuracy, coverage, source diversity, freshness, and response time
- **Production-ready scrapers**: Eventbrite and Luma event crawlers using Crawl4AI
- **Detailed reporting**: JSON and Markdown output with per-query breakdowns

---

## 🚀 Features

### 🔍 **Ollama Search Benchmarking**
- **20 test queries** covering diverse event discovery scenarios
- **6 constraint types**: Topics (AI, sustainability, etc.), locations (NYC, SF, etc.), platforms (Eventbrite, Luma, etc.), event types (hackathons, workshops, etc.), formats (virtual, hybrid), and time windows (specific dates, relative ranges)
- **60% relevance threshold**: Results must match ≥60% of query constraints to be considered relevant
- **Accurate time matching**: Handles complex time expressions like "October 19 at 9 AM", "this weekend", "between Oct 18 and 22"

### 📊 **Metrics Tracked**
1. **Accuracy**: Proportion of search results that are relevant
2. **Coverage**: Number of relevant events discovered
3. **Source Diversity**: Unique domains among relevant results
4. **Freshness**: Percentage of results with future/in-window dates
5. **Response Time**: API latency in milliseconds

### 🐛 **Critical Bug Fixes Applied**
- ✅ **Domain parsing bug**: Fixed `lstrip('www.')` removing characters instead of prefix
- ✅ **Time window logic bug**: Fixed AND operation causing false negatives for time-of-day-only constraints

---

## 📁 Project Structure

```
.
├── web_llm/
│   ├── ollama_benchmark_runner.py    # Main benchmark harness
│   ├── ollama_search.py              # Ollama Search API integration
│   ├── ollama_search_simple.py       # Simplified search script
│   ├── ollama_test_accuracy.py       # Accuracy validation tests
│   ├── TEST_QUERIES.md               # 20 benchmark queries
│   └── BENCHMARK_AUDIT.md            # Bug analysis & fixes
├── scraping/
│   ├── eventbrite_crawl.py           # Eventbrite scraper (Crawl4AI)
│   └── luma_crawl.py                 # Luma scraper (Crawl4AI)
├── .gitignore                        # Excludes data files, outputs
└── README.md                         # This file
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Ollama API key
- Conda (recommended) or virtualenv

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/dgupta2003/ai_event_aggregator.git -b shreyas
   cd ai_event_aggregator
   ```

2. **Create environment**
   ```bash
   conda create -n circle python=3.10
   conda activate circle
   ```

3. **Install dependencies**
   ```bash
   pip install ollama python-dotenv crawl4ai
   ```

4. **Configure API key**
   Create a `.env` file in the project root:
   ```env
   OLLAMA_API_KEY=your_api_key_here
   ```

---

## 🎯 Usage

### Run Benchmark Suite

```bash
cd web_llm
python ollama_benchmark_runner.py
```

**Output:**
- `ollama_benchmark_YYYYMMDD_HHMMSS.json` - Structured results with detailed metrics
- `ollama_benchmark_YYYYMMDD_HHMMSS.md` - Human-readable report

### Sample Output

```
[01] Is there any AI event happening on October 19 at 9 AM in New... -> 100.0% acc, 1848 ms, relevant 3/3
[02] Find all sustainability workshops scheduled in San Francisco... -> 33.3% acc, 1398 ms, relevant 1/3
[03] Are there any climate change awareness events this weekend i... -> 66.7% acc, 1637 ms, relevant 2/3

Saved JSON: /path/to/ollama_benchmark_20251015_134431.json
Saved Markdown: /path/to/ollama_benchmark_20251015_134431.md
```

### Run Scrapers

**Eventbrite:**
```bash
cd scraping
python eventbrite_crawl.py
```

**Luma:**
```bash
cd scraping
python luma_crawl.py
```

---

## 📖 How It Works

### 1. **Query Parsing**
Extracts expected constraints from natural language queries:

```python
Query: "Find AI hackathons happening on October 19 at 9 AM in NYC"

Parsed Constraints:
- Topics: {'ai'}
- Locations: {'new york'}
- Types: {'hackathon'}
- Time Window: October 19, 2025 at 9 AM
```

### 2. **Search Execution**
Sends query to Ollama Search API unchanged (no preprocessing):

```python
results = client.web_search(query)  # Direct API call
```

### 3. **Result Evaluation**
Each search result is scored against constraints:

```python
Result: "Quantum + AI | October 19-21, 2025 | New York City"

Matched Constraints:
✓ Topic (contains "AI")
✓ Location (contains "New York")
✓ Type (event detected)
✓ Time (Oct 19 + 9 AM found)

Confidence: 100% → RELEVANT
```

### 4. **Metrics Computation**
Aggregates scores across all results:

```python
Accuracy = relevant_results / total_results
Coverage = count(relevant_results)
Diversity = count(unique_domains)
Freshness = results_with_future_dates / total_relevant
```

---

## 🧪 Test Queries

The benchmark includes 20 diverse queries testing:

- **Specific events**: "AI event on October 19 at 9 AM in NYC"
- **Date ranges**: "Between October 18 and 22"
- **Relative times**: "This weekend", "Tomorrow", "Next week"
- **Platform-specific**: "Events on Eventbrite", "Luma events"
- **Multi-constraint**: "Virtual AI conferences free this weekend"
- **Institutional**: "WHO webinars", "UN sustainability summits"

View full list: [`web_llm/TEST_QUERIES.md`](web_llm/TEST_QUERIES.md)

---

## 📊 Benchmark Results

### Summary Statistics (Sample Run - Q1-5)

| Metric | Value |
|--------|-------|
| **Avg Accuracy** | 60% |
| **Avg Response Time** | 1,690 ms |
| **Avg Coverage** | 1.8 events |
| **Avg Source Diversity** | 1.6 domains |
| **Avg Freshness** | 37.5% |

**Top Platforms Detected**: Eventbrite, Meetup, IQT Event, Climate Action Museum

> **Note**: Full benchmark (Q1-20) limited by Ollama API hourly rate limits. Run in batches with 2-second delays between queries.

---

## 🔧 Configuration

### Adjust Parameters

Edit `ollama_benchmark_runner.py`:

```python
# Maximum results per query (default: 10)
outputs = run_benchmark(md_path, max_results=10)

# Delay between queries to avoid rate limiting (default: 2s)
time.sleep(2.0)

# Relevance threshold (default: 0.6 = 60%)
relevant = [e for e in evals if e.confidence >= 0.6]
```

### Add Custom Queries

Edit `web_llm/TEST_QUERIES.md`:

```markdown
21. Your custom query here
22. Another custom query
```

---

## 🐛 Known Issues & Limitations

1. **Ollama API Rate Limits**: 
   - Hourly usage cap (402 error after ~5-10 queries)
   - **Workaround**: Run benchmark in batches, wait 1 hour between runs

2. **Date Extraction False Positives**:
   - Regex matches patterns like "Track 2/3" as "Feb 3"
   - **Impact**: Medium (affects freshness metric)
   - **Status**: Documented in BENCHMARK_AUDIT.md

3. **Weekend Calculation Edge Case**:
   - "This weekend" on Saturday returns same day instead of next Sat-Sun
   - **Impact**: Low (rare scenario)
   - **Status**: Low priority fix

View full bug analysis: [`web_llm/BENCHMARK_AUDIT.md`](web_llm/BENCHMARK_AUDIT.md)

---

## 🤝 Contributing

This is a research/capstone project. For questions or collaboration:

1. Fork the `shreyas` branch
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

This project is part of an academic capstone. Contact repository owner for usage terms.

---

## 👥 Authors

- **Shreyas Bachiraju** - Benchmark suite development, bug fixes, scrapers
- **Repository**: [ai_event_aggregator](https://github.com/dgupta2003/ai_event_aggregator) (branch: `shreyas`)

---

## 🙏 Acknowledgments

- **Ollama** for Search API access
- **Crawl4AI** for web scraping framework
- **Eventbrite & Luma** for event platform data

---

## 📞 Support

For issues or questions:
- Open a GitHub issue on the `shreyas` branch
- Review [`BENCHMARK_AUDIT.md`](web_llm/BENCHMARK_AUDIT.md) for technical details
- Check [`TEST_QUERIES.md`](web_llm/TEST_QUERIES.md) for query examples

---

**Last Updated**: October 15, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production-ready with known limitations documented
