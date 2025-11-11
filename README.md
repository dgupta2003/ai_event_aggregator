# Search API Event Benchmark with Crawl4AI

This mini project runs your event test queries against multiple sources, crawls pages with Crawl4AI when available, applies strong filters for date, time, topic, and location, then scores accuracy and coverage.

## Quick start

python -m venv .venv
source .venv/bin/activate  # on Windows use .venv\Scripts\activate
pip install -r requirements.txt

# run all queries and produce CSV and JSON in the outputs folder
python run_benchmark.py

Outputs
- outputs/events.csv
- outputs/metrics.csv
- outputs/metrics_summary.md

## Notes

- Crawl4AI is used automatically if installed. If it is not available during install on your machine, the code will still run with a safe fallback HTTP client.
- No paid keys required. The adapters hit public listing pages on Eventbrite, Luma, Meetup, WHO, UN, and TED related sites with query parameters when possible.
