import json, csv, re
from datetime import datetime
from urllib.parse import urljoin
from scrapegraphai.graphs import SmartScraperMultiGraph  # multi-URL graph

PROMPT = """
Extract upcoming technology-related events in New York City that happen in October 2025.
Return a JSON list named `events`. Each item must include:
- title (string)
- date (ISO YYYY-MM-DD; if not visible, set null)
- time (exact time string as shown on the page; if not visible, set null)
- venue (string or null)
- city (string)
- price (string like "Free" or "$15", or null)
- event_url (absolute URL)
- organizer (string or null)
- platform ("Eventbrite" or "Luma", inferred from domain)
Only include events whose MAIN event date is in October 2025. If multiple dates appear, choose the primary event date.
Ensure `event_url` is absolute. Do not invent values. If a field cannot be found, set it to null.
"""


# Eventbrite & Luma NYC tech discovery pages (add/remove pages as needed)
eventbrite_base = "https://www.eventbrite.com/d/ny--new-york/technology--events/?page="
luma_discover   = "https://lu.ma/discover?c=technology&loc=New%20York%2C%20NY"

SOURCES = [eventbrite_base + str(i) for i in range(1, 4)] + [luma_discover]

CFG = {
    "llm": {
        "model": "gpt-4o-mini",   # provider inferred from model
        # "api_key": "sk-..."     # optional; env var OPENAI_API_KEY is fine
    },
    "browser": {
        "enabled": True,
        "headless": True,
        "wait_until": "networkidle",
        "timeout_ms": 60000
    },
    "fetch": { "concurrency": 2, "delay_ms": 800 }
}



graph = SmartScraperMultiGraph(prompt=PROMPT, source=SOURCES, config=CFG)  # multi-URL usage
raw = graph.run()  # returns the answer to your prompt

# The result may already be a dict/object; normalize to dict -> list
events = raw.get("events", raw if isinstance(raw, list) else [])

# --- Post-processing ---
# --- Post-processing ---
import re
from datetime import datetime
from urllib.parse import urljoin

def to_iso_or_none(s):
    if not s:
        return None
    # common formats → ISO
    for fmt in ("%Y-%m-%d", "%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%d %b %Y"):
        try:
            return datetime.strptime(s.strip(), fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    # yyyy-mm-dd pattern fallback
    m = re.search(r"\b(20\d{2})[-/ ](0?[1-9]|1[0-2])[-/ ](0?[1-9]|[12]\d|3[01])\b", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y:04d}-{mo:02d}-{d:02d}"
    return None

raw_events = raw.get("events", raw if isinstance(raw, list) else [])

kept, dropped_no_date, dropped_wrong_month_year, dropped_bad_domain = 0, 0, 0, 0
normalized = []

for e in raw_events:
    title = (e.get("title") or "").strip()
    date_iso = to_iso_or_none(e.get("date"))
    if not date_iso:
        dropped_no_date += 1
        continue

    try:
        dt = datetime.fromisoformat(date_iso)
    except Exception:
        dropped_no_date += 1
        continue

    # ⬇️ LOCK to October 2025 (change here if you ever need a different month/year)
    if not (dt.year == 2025 and dt.month == 10):
        dropped_wrong_month_year += 1
        continue

    url = (e.get("event_url") or "").strip()
    # Keep only trusted domains
    if not (("eventbrite." in url) or ("lu.ma" in url)):
        dropped_bad_domain += 1
        continue

    platform = "Eventbrite" if "eventbrite." in url else "Luma"

    # ensure absolute URL if any relative slipped through
    if url.startswith("/"):
        base = "https://www.eventbrite.com" if platform == "Eventbrite" else "https://lu.ma"
        url = urljoin(base, url)

    time_val = e.get("time")
    if isinstance(time_val, str) and time_val.strip().lower().startswith("keep page text"):
        time_val = None

    normalized.append({
        "title": title or None,
        "date": date_iso,
        "time": time_val,
        "venue": e.get("venue"),
        "city": e.get("city") or "New York",
        "price": e.get("price"),
        "event_url": url or None,
        "organizer": e.get("organizer"),
        "platform": platform
    })

# Deduplicate by (title, date, platform)
seen, deduped = set(), []
for e in normalized:
    key = ((e["title"] or "").lower(), e["date"], e["platform"])
    if key not in seen:
        seen.add(key)
        deduped.append(e)

kept = len(deduped)
print(f"[Summary] total_in={len(raw_events)} kept={kept} "
      f"dropped_no_date={dropped_no_date} dropped_wrong_month_year={dropped_wrong_month_year} "
      f"dropped_bad_domain={dropped_bad_domain}")

# Save JSON & CSV
import json, csv
with open("nyc_tech_events_october.json", "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)

fields = ["title","date","time","venue","city","price","event_url","organizer","platform"]
with open("nyc_tech_events_october.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(deduped)

print(f"Saved {len(deduped)} October 2025 NYC tech events to nyc_tech_events_october.(json|csv)")
