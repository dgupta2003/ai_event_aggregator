#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, csv, re, time
import requests
from collections import Counter, defaultdict
from dateutil.parser import parse as dtparse
from dotenv import load_dotenv

# --- Load .env / API key ---
load_dotenv()
API_KEY = os.environ.get("PPLX_API_KEY")
assert API_KEY, "Set PPLX_API_KEY in your .env (PPLX_API_KEY=sk-...) or export it."

# --- HTTP config ---
URL = "https://api.perplexity.ai/chat/completions"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# --- Models known to work currently ---
MODEL_CANDIDATES = [
    "sonar",                 # search-capable
    "sonar-pro",
    "sonar-reasoning",
    "sonar-reasoning-pro",
    "sonar-deep-research"
]

SYSTEM = "You return ONLY compact JSON. No prose, no markdown, no code fences."

# Prompt templates: pass 1 targets Eventbrite, pass 2 targets Luma.
PROMPT_EVENTBRITE = """
Use web search and return NYC technology events between 2025-10-01 and 2025-10-31.
STRICTLY use direct event detail links from Eventbrite only. Use site filters:
- Use: site:eventbrite.com OR site:eventbrite.ca OR site:eventbrite.co.uk (any eventbrite TLD).
Return STRICT JSON:

{"events":[{"title":"...","date":"YYYY-MM-DD","time":"HH:MM AM/PM or null","venue":"string or null","city":"New York City","price":"string or null","link":"https://...","source":"Eventbrite"}]}

Rules:
- NYC only. October 2025 only.
- Direct event detail pages only (no category/list pages).
- No duplicates.
- If a field is missing, set it to null.
- Return 6–12 items.
Return only the JSON object.
""".strip()

PROMPT_LUMA = """
Use web search and return NYC technology events between 2025-10-01 and 2025-10-31.
STRICTLY use direct event detail links from Luma only. Use site filters:
- Use: site:lu.ma
Return STRICT JSON:

{"events":[{"title":"...","date":"YYYY-MM-DD","time":"HH:MM AM/PM or null","venue":"string or null","city":"New York City","price":"string or null","link":"https://...","source":"Luma"}]}

Rules:
- NYC only. October 2025 only.
- Direct event detail pages only (no discover/list pages).
- No duplicates.
- If a field is missing, set it to null.
- Return 6–12 items if available; else return what is available.
Return only the JSON object.
""".strip()

def call_perplexity(user_prompt: str):
    """Try candidate models until one succeeds; return JSON response or raise."""
    last_err = None
    for model in MODEL_CANDIDATES:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,    # be deterministic
            "max_tokens": 1400,
            "stream": False
        }
        try:
            r = requests.post(URL, headers=HEADERS, json=payload, timeout=90)
        except requests.RequestException as e:
            print(f"[{model}] request error: {e}", file=sys.stderr)
            last_err = e
            continue

        if r.status_code == 200:
            try:
                return r.json()
            except Exception as e:
                print(f"[{model}] JSON decode error: {e}", file=sys.stderr)
                last_err = e
                continue
        else:
            body = r.text.strip()
            print(f"[{model}] HTTP {r.status_code} → {body[:500]}", file=sys.stderr)
            last_err = r

        time.sleep(0.3)

    raise SystemExit(f"All model attempts failed. Last error: {getattr(last_err, 'status_code', 'n/a')}")

def extract_content(resp_json):
    try:
        return resp_json["choices"][0]["message"]["content"]
    except Exception as e:
        raise SystemExit(f"Unexpected response layout: {e}\nFull response: {json.dumps(resp_json, indent=2)[:1200]}")

def strip_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()

def coerce_json(s: str):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        start, end = s.find("{"), s.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(s[start:end+1])
        raise

def is_oct_2025(iso: str) -> bool:
    try:
        d = dtparse(iso).date()
        return d.year == 2025 and d.month == 10
    except Exception:
        return False

def good_domain(link: str) -> bool:
    link = (link or "").lower()
    # accept any eventbrite TLD and lu.ma
    return ("eventbrite." in link) or ("lu.ma" in link)

def normalize_source(link: str, source: str | None) -> str | None:
    if source and source.strip():
        return source.strip()
    ll = (link or "").lower()
    if "eventbrite." in ll: return "Eventbrite"
    if "lu.ma" in ll: return "Luma"
    return None

def normalize_batch(events):
    """Validate, lock to NYC + Oct 2025 + allowed domains, dedupe."""
    seen = set()
    normalized = []
    dropped = defaultdict(int)
    rejected_links = []

    for e in events:
        title = (e.get("title") or "").strip()
        date  = (e.get("date")  or "").strip()
        link  = (e.get("link")  or "").strip()
        time_s = e.get("time")
        venue  = e.get("venue")
        city   = "New York City"
        price  = e.get("price")
        source = normalize_source(link, e.get("source"))

        if not (title and link and date):
            dropped["no_title_or_link"] += 1
            if link: rejected_links.append(link)
            continue

        if not is_oct_2025(date):
            dropped["not_oct_2025"] += 1
            rejected_links.append(link)
            continue

        if not good_domain(link):
            dropped["bad_domain"] += 1
            rejected_links.append(link)
            continue

        key = (title.lower(), date, (source or "").lower())
        if key in seen:
            dropped["dupe"] += 1
            continue
        seen.add(key)

        normalized.append({
            "title": title,
            "date": date,
            "time": time_s,
            "venue": venue,
            "city": city,
            "price": price,
            "link": link,
            "source": source
        })

    return normalized, dict(dropped), rejected_links

def fetch_pass(user_prompt):
    resp_json = call_perplexity(user_prompt)
    content = extract_content(resp_json)
    content = strip_fences(content)
    data = coerce_json(content)
    events = data.get("events", []) if isinstance(data, dict) else []
    if not isinstance(events, list):
        raise SystemExit("Model did not return {'events': [...]} structure.")
    return events

def main():
    # Pass 1: Eventbrite only
    eb_events = fetch_pass(PROMPT_EVENTBRITE)
    eb_norm, eb_drop, eb_rejected = normalize_batch(eb_events)

    # Pass 2: Luma only
    luma_events = fetch_pass(PROMPT_LUMA)
    luma_norm, luma_drop, luma_rejected = normalize_batch(luma_events)

    # Merge and final dedupe
    all_norm = eb_norm + luma_norm
    final_seen = set()
    final = []
    for e in all_norm:
        key = (e["title"].lower(), e["date"], (e.get("source") or "").lower())
        if key not in final_seen:
            final_seen.add(key)
            final.append(e)

    # Save outputs
    with open("perplexity_events.json", "w", encoding="utf-8") as f:
        json.dump({"events": final}, f, ensure_ascii=False, indent=2)

    with open("perplexity_events.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title","date","time","venue","city","price","link","source"])
        w.writeheader()
        w.writerows(final)

    by_src = Counter((e.get("source") or "Unknown") for e in final)

    print(f"Saved {len(final)} events to perplexity_events.(json|csv)")
    print(f"By source: {dict(by_src)}")
    print(f"Dropped (Eventbrite pass): {eb_drop}")
    print(f"Dropped (Luma pass): {luma_drop}")

    # Helpful if you got 0: show a few rejected links to see what domains Perplexity found
    if (len(final) == 0) and (eb_drop.get('bad_domain',0) or luma_drop.get('bad_domain',0)):
        print("\nExamples of rejected links (wrong domains):")
        for link in (eb_rejected[:5] + luma_rejected[:5]):
            print(" -", link)

if __name__ == "__main__":
    main()
