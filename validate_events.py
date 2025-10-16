# validate_events.py
import csv, json, re, sys, time
from datetime import datetime
from collections import Counter, defaultdict
from urllib.parse import urlparse
import requests

CSV_PATH = "nyc_tech_events_october.csv"  # change if needed
TIMEOUT = 6
HEADERS = {"User-Agent": "Mozilla/5.0 (Data QA)"}

TECH_TERMS = [
    "tech","ai","ml","data","software","developer","engineering","cloud",
    "startup","blockchain","cyber","robot","product","devops","coding",
    "web3","python","javascript","spatial","datascience","hacker","design"
]
NYC_ALIASES = {
    "new york","new york city","nyc","manhattan","brooklyn","queens",
    "bronx","staten island","dumbo","murray hill","chelsea","midtown west",
    "midtown east","hell's kitchen","morningside heights","fidi","financial district",
    "east village","upper east side","upper west side","soho","tribeca"
}

def read_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({k:(v.strip() if isinstance(v,str) else v) for k,v in row.items()})
    return rows

def is_iso_oct_2025(d):
    try:
        dt = datetime.fromisoformat(d)
        return dt.year == 2025 and dt.month == 10
    except Exception:
        return False

def good_domain(url):
    try:
        netloc = urlparse(url).netloc.lower()
        return ("eventbrite." in netloc) or ("lu.ma" in netloc)
    except Exception:
        return False

def quick_head(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT, headers=HEADERS)
        # Some sites block HEAD; fallback to GET for 405/403 once
        if r.status_code in (403, 405):
            r = requests.get(url, stream=True, timeout=TIMEOUT, headers=HEADERS)
        return r.status_code
    except Exception:
        return 0

def looks_techy(title):
    t = (title or "").lower()
    return any(term in t for term in TECH_TERMS)

def normalize_city(c):
    c = (c or "").strip().lower()
    return "New York City" if c in NYC_ALIASES else (c.title() if c else "")

def main():
    rows = read_csv(CSV_PATH)
    n = len(rows)
    print(f"Loaded {n} rows from {CSV_PATH}")

    # Required fields
    missing_title = [i for i,r in enumerate(rows) if not r.get("title")]
    missing_date  = [i for i,r in enumerate(rows) if not r.get("date")]
    missing_url   = [i for i,r in enumerate(rows) if not r.get("event_url")]
    missing_plat  = [i for i,r in enumerate(rows) if not r.get("platform")]

    # Date validity
    bad_dates = [i for i,r in enumerate(rows) if r.get("date") and not is_iso_oct_2025(r["date"])]

    # Domain validity
    bad_domain = [i for i,r in enumerate(rows) if r.get("event_url") and not good_domain(r["event_url"])]

    # Duplicates
    key = lambda r: ( (r.get("title","").lower().strip()), r.get("date"), r.get("platform") )
    counts = Counter(key(r) for r in rows)
    dups = [i for i,r in enumerate(rows) if counts[key(r)] > 1]

    # URL health sample (limit to 12 to avoid rate issues)
    sample = rows[:12] if n > 12 else rows
    url_status = {}
    for r in sample:
        u = r.get("event_url")
        if not u: 
            continue
        if u in url_status: 
            continue
        status = quick_head(u)
        url_status[u] = status
        time.sleep(0.3)  # be polite

    # Relevance heuristic
    not_techy = [i for i,r in enumerate(rows) if not looks_techy(r.get("title",""))]

    # Coverage by platform
    by_platform = Counter((r.get("platform") or "").strip() for r in rows)

    # City normalization preview
    city_changes = []
    for i,r in enumerate(rows[:15]):  # just show first 15
        before = r.get("city","")
        after  = normalize_city(before)
        if before and before != after:
            city_changes.append((i, before, after))

    # Score (simple weighted)
    score = 100
    score -= 3*len(missing_title)
    score -= 3*len(missing_date)
    score -= 2*len(missing_url)
    score -= 2*len(missing_plat)
    score -= 2*len(bad_dates)
    score -= 2*len(bad_domain)
    score -= 1*len(set(dups))  # unique dup keys
    # URL health penalty for statuses not in {200, 301, 302}
    bad_urls = sum(1 for s in url_status.values() if s not in (200,301,302))
    score -= 2*bad_urls
    score = max(score, 0)

    print("\n=== DATA QUALITY SUMMARY ===")
    print(f"Rows: {n}")
    print(f"Required fields missing → title:{len(missing_title)} date:{len(missing_date)} url:{len(missing_url)} platform:{len(missing_plat)}")
    print(f"Dates not in Oct 2025: {len(bad_dates)}")
    print(f"Bad domains (non-Eventbrite/Luma): {len(bad_domain)}")
    print(f"Duplicate rows: {len(set(dups))} duplicate keys affecting {len(dups)} rows")
    print(f"URL health (sample {len(url_status)}): {Counter(url_status.values())}")
    print(f"Looks techy (title heuristic): non-techy titles: {len(not_techy)}")
    print(f"By platform: {dict(by_platform)}")
    print(f"City normalization examples (first 15 rows): {city_changes}")
    print(f"\nQuality Score (0–100): {score}")

    # Write a small markdown report
    report = {
        "rows": n,
        "missing_title": len(missing_title),
        "missing_date": len(missing_date),
        "missing_url": len(missing_url),
        "missing_platform": len(missing_plat),
        "bad_dates": len(bad_dates),
        "bad_domain": len(bad_domain),
        "duplicate_keys": len(set(dups)),
        "duplicate_rows": len(dups),
        "url_status_counts": Counter(url_status.values()),
        "non_techy_titles": len(not_techy),
        "by_platform": dict(by_platform),
        "quality_score": score
    }

    md = [
        "# NYC Tech Events — Data Quality Report",
        f"- Total rows: **{report['rows']}**",
        f"- Missing → title:{report['missing_title']}, date:{report['missing_date']}, url:{report['missing_url']}, platform:{report['missing_platform']}",
        f"- Dates not in Oct 2025: **{report['bad_dates']}**",
        f"- Bad domains: **{report['bad_domain']}**",
        f"- Duplicates: **{report['duplicate_keys']} keys** (across {report['duplicate_rows']} rows)",
        f"- URL status sample: **{dict(report['url_status_counts'])}**",
        f"- Non-techy titles (heuristic): **{report['non_techy_titles']}**",
        f"- By platform: **{report['by_platform']}**",
        f"- **Quality Score:** **{report['quality_score']} / 100**",
        "",
        "## Notes",
        "- Dates strictly validated against **October 2025**.",
        "- Trusted domains: `eventbrite.*`, `lu.ma`.",
        "- Duplicates computed over `(title, date, platform)`.",
        "- URL health checked via HEAD/GET on a small sample for politeness.",
    ]
    with open("DATA_QUALITY_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("\nWrote DATA_QUALITY_REPORT.md")

if __name__ == "__main__":
    main()
