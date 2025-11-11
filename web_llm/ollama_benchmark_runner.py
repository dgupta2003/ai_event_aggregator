"""
Ollama Search API Benchmark Runner

- Parses benchmark queries from TEST_QUERIES.md (1–20)
- Runs Ollama web_search for each query
- Computes metrics: response time, accuracy, coverage, source diversity, freshness
- Saves detailed JSON and Markdown summary

Strictly uses Ollama Search API outputs (title/url/content) — no web_fetch or LLM chat
"""

from __future__ import annotations
import os
import re
import json
import time
import math
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, date
from urllib.parse import urlparse
from ollama import Client
from dotenv import load_dotenv

# ---------------------------
# Environment & Client Setup
# ---------------------------
load_dotenv()
API_KEY = os.getenv("OLLAMA_API_KEY")
if not API_KEY:
    raise ValueError("OLLAMA_API_KEY not found in .env file")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# ---------------------------
# Constants & Helpers
# ---------------------------
NOW = datetime.now()
TODAY = NOW.date()
CURRENT_YEAR = TODAY.year

MONTHS = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}

EVENT_TYPES = {
    'hackathon': ['hackathon', 'hackathon(s)?'],
    'workshop': ['workshop', 'workshops?'],
    'conference': ['conference', 'summit', 'symposium', 'expo', 'convention'],
    'meetup': ['meetup', 'meet-up', 'meet up'],
    'webinar': ['webinar', 'virtual event', 'online event', 'livestream', 'live stream'],
    'festival': ['festival', 'fest'],
    'networking': ['networking', 'mixer', 'happy hour', 'connect', 'meet & greet', 'meet and greet'],
    'panel': ['panel', 'fireside chat', 'discussion'],
    'demo day': ['demo day', 'pitch day', 'demo-day'],
}

PLATFORM_HOSTS = {
    'eventbrite': ['eventbrite.com'],
    'luma': ['lu.ma'],
    'meetup': ['meetup.com'],
    'facebook': ['facebook.com'],
    'allevents': ['allevents.in'],
    'ticketmaster': ['ticketmaster.com'],
    'dice': ['dice.fm'],
    'universe': ['universe.com'],
    'splashthat': ['splashthat.com'],
    'eventcreate': ['eventcreate.com'],
    'hopin': ['hopin.com'],
    'bizzabo': ['bizzabo.com'],
    'partiful': ['partiful.com'],
    'ra': ['ra.co'],
    'who': ['who.int'],
    'un': ['un.org', 'unitednations.org'],
    'ted': ['ted.com', 'tedx'],
}

TOPIC_KEYWORDS = {
    'ai': ['ai', 'artificial intelligence', 'gen ai', 'generative ai'],
    'sustainability': ['sustainability', 'sustainable'],
    'climate': ['climate', 'climate change'],
    'mental health': ['mental health', 'wellbeing', 'well-being'],
    'renewable energy': ['renewable', 'renewables', 'clean energy', 'solar', 'wind'],
    'education': ['education', 'edtech', 'ed-tech', 'ed tech'],
    'music': ['music', 'festival', 'concert'],
    'social change': ['social change', 'social impact'],
    'robotics': ['robotics', 'robot'],
    'entrepreneurship': ['entrepreneurship', 'startup', 'start-up', 'founder'],
    'technology': ['technology', 'tech'],
    'design thinking': ['design thinking']
}

FORMAT_KEYWORDS = {
    'virtual': ['virtual', 'online', 'remote'],
    'hybrid': ['hybrid']
}

CITY_KEYWORDS = [
    # Common cities mentioned in queries
    'new york', 'nyc', 'san francisco', 'chicago', 'austin', 'los angeles', 'la', 'brooklyn',
    'california', 'europe'
]

DATE_RE = re.compile(
    r"\b(?:(?P<month_name>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
    r"sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+"
    r"(?P<day>\d{1,2})(?:,\s*(?P<year>\d{4}))?"
    r"|(?P<month_num>\d{1,2})[/-](?P<day_num>\d{1,2})(?:[/-](?P<year_num>\d{2,4}))?)\b",
    re.IGNORECASE
)
TIME_RE = re.compile(r"\b(?P<hour>\d{1,2})(?::(?P<min>\d{2}))?\s*(?P<ampm>am|pm)\b", re.IGNORECASE)

# ---------------------------
# Data Classes
# ---------------------------
@dataclass
class TimeWindow:
    start: Optional[date] = None
    end: Optional[date] = None
    must_time: Optional[str] = None  # e.g., '9 AM'

@dataclass
class Constraints:
    topics: Set[str] = field(default_factory=set)
    locations: Set[str] = field(default_factory=set)
    platforms: Set[str] = field(default_factory=set)
    types: Set[str] = field(default_factory=set)
    formats: Set[str] = field(default_factory=set)
    time_window: Optional[TimeWindow] = None

@dataclass
class ResultEval:
    url: str
    title: str
    content_preview: str
    domain: str
    matched: Dict[str, bool]
    confidence: float
    detected_dates: List[str] = field(default_factory=list)
    detected_times: List[str] = field(default_factory=list)

@dataclass
class QueryMetrics:
    query_id: int
    query_text: str
    response_time_ms: int
    total_results: int
    relevant_results: int
    accuracy: float  # proportion relevant
    coverage: int  # number of relevant events
    source_diversity: int  # distinct domains among relevant
    freshness: Optional[float]  # proportion of relevant with future or in-window dates
    platforms_present: Dict[str, int]
    result_evals: List[ResultEval]

# ---------------------------
# Parsing Functions
# ---------------------------

def load_test_queries(md_path: str) -> List[Tuple[int, str]]:
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    queries: List[Tuple[int, str]] = []
    for line in lines:
        m = re.match(r"^\s*(\d{1,2})\.\s+(.*\S)\s*$", line)
        if m:
            idx = int(m.group(1))
            text = m.group(2).strip()
            queries.append((idx, text))
    # Ensure 1..20 present (some headings may include numbers; we trust file content)
    queries = [(i, q) for (i, q) in queries if 1 <= i <= 20]
    queries.sort(key=lambda x: x[0])
    return queries


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def parse_time_window(q: str) -> TimeWindow:
    qn = normalize(q)
    tw = TimeWindow()

    # Specific datetime: "on October 19 at 9 AM"
    m = re.search(r"on\s+([a-z]{3,9}\.?(?:\s+\d{1,2})(?:,\s*\d{4})?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))", qn)
    if m:
        date_str = m.group(1)
        time_str = m.group(2)
        d = parse_date_token(date_str)
        if d:
            tw.start = tw.end = d
            tw.must_time = standardize_ampm(time_str)
            return tw

    # Between two dates: "between October 18 and 22"
    m = re.search(r"between\s+([a-z]{3,9}\.?)\s+(\d{1,2})\s+and\s+(\d{1,2})", qn)
    if m:
        month = m.group(1)
        d1 = int(m.group(2))
        d2 = int(m.group(3))
        month_num = MONTHS.get(month.replace('.', ''), None)
        if month_num:
            y = CURRENT_YEAR
            tw.start = date(y, month_num, d1)
            tw.end = date(y, month_num, d2)
            return tw

    # Month specified like "November 2025"
    m = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})", qn)
    if m:
        mn = MONTHS[m.group(1)]
        y = int(m.group(2))
        start = date(y, mn, 1)
        end = date(y, mn, days_in_month(y, mn))
        tw.start, tw.end = start, end
        return tw

    # Relative ranges: this weekend, this week, next week, this month
    if 'this weekend' in qn:
        # upcoming Saturday-Sunday relative to TODAY
        sat = TODAY + timedelta(days=(5 - TODAY.weekday()) % 7)
        sun = sat + timedelta(days=1)
        tw.start, tw.end = sat, sun
        return tw
    if 'tomorrow' in qn:
        t = TODAY + timedelta(days=1)
        tw.start = tw.end = t
        return tw
    if 'today' in qn:
        tw.start = tw.end = TODAY
        return tw
    if 'this week' in qn:
        start = TODAY - timedelta(days=TODAY.weekday())
        end = start + timedelta(days=6)
        tw.start, tw.end = start, end
        return tw
    if 'next week' in qn:
        start = TODAY - timedelta(days=TODAY.weekday()) + timedelta(days=7)
        end = start + timedelta(days=6)
        tw.start, tw.end = start, end
        return tw
    if 'this month' in qn:
        start = date(CURRENT_YEAR, TODAY.month, 1)
        end = date(CURRENT_YEAR, TODAY.month, days_in_month(CURRENT_YEAR, TODAY.month))
        tw.start, tw.end = start, end
        return tw
    if 'this year' in qn:
        start = date(CURRENT_YEAR, 1, 1)
        end = date(CURRENT_YEAR, 12, 31)
        tw.start, tw.end = start, end
        return tw

    # Fallback: None
    return tw


def standardize_ampm(s: str) -> str:
    s = s.strip().lower().replace(".", "")
    s = re.sub(r"\s+", " ", s)
    # normalize 9am -> 9 am
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)$", s)
    if m:
        hh = int(m.group(1))
        mm = m.group(2) or '00'
        ap = m.group(3)
        return f"{hh}:{mm} {ap}" if mm != '00' else f"{hh} {ap}"
    return s


def days_in_month(y: int, m: int) -> int:
    if m == 12:
        return 31
    first_next = date(y + (m // 12), (m % 12) + 1, 1)
    last_this = first_next - timedelta(days=1)
    return last_this.day


def parse_date_token(token: str) -> Optional[date]:
    token = token.strip().lower().replace(',', '')
    # Try month name
    parts = token.split()
    if len(parts) >= 2 and parts[0] in MONTHS:
        m = MONTHS[parts[0]]
        d = int(re.sub(r"\D", "", parts[1]))
        y = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else CURRENT_YEAR
        try:
            return date(y, m, d)
        except Exception:
            return None
    # Try mm/dd[/yyyy]
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?$", token)
    if m:
        mm = int(m.group(1))
        dd = int(m.group(2))
        yy = m.group(3)
        if yy:
            y = int(yy)
            if y < 100:
                y += 2000
        else:
            y = CURRENT_YEAR
        try:
            return date(y, mm, dd)
        except Exception:
            return None
    return None


def extract_dates_times(text: str) -> Tuple[List[date], List[str]]:
    text = text or ''
    ds: List[date] = []
    ts: List[str] = []
    for m in DATE_RE.finditer(text):
        if m.group('month_name'):
            month = MONTHS.get(m.group('month_name').replace('.', '').lower())
            day = int(m.group('day'))
            y = int(m.group('year')) if m.group('year') else CURRENT_YEAR
            try:
                ds.append(date(y, month, day))
            except Exception:
                pass
        else:
            mm = int(m.group('month_num'))
            dd = int(m.group('day_num'))
            yy = m.group('year_num')
            if yy:
                y = int(yy)
                if y < 100:
                    y += 2000
            else:
                y = CURRENT_YEAR
            try:
                ds.append(date(y, mm, dd))
            except Exception:
                pass
    for t in TIME_RE.finditer(text):
        h = t.group('hour')
        m = t.group('min') or '00'
        ap = t.group('ampm').lower()
        ts.append(f"{h}:{m} {ap}" if m != '00' else f"{h} {ap}")
    # Deduplicate while preserving order
    def dedup(seq):
        seen = set()
        out = []
        for x in seq:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return out
    return dedup(ds), dedup(ts)


def parse_constraints(query: str) -> Constraints:
    qn = normalize(query)
    c = Constraints()

    # Topics
    for topic, kws in TOPIC_KEYWORDS.items():
        if any(kw in qn for kw in kws):
            c.topics.add(topic)

    # Locations
    for loc in CITY_KEYWORDS:
        if loc in qn:
            c.locations.add(loc)

    # Platforms
    for platform in PLATFORM_HOSTS:
        if platform in qn or any(host in qn for host in PLATFORM_HOSTS[platform]):
            c.platforms.add(platform)

    # Types
    for t, kws in EVENT_TYPES.items():
        if any(re.search(rf"\b{k}\b", qn) for k in kws):
            c.types.add(t)

    # Formats
    for f, kws in FORMAT_KEYWORDS.items():
        if any(kw in qn for kw in kws):
            c.formats.add(f)

    # Time window
    tw = parse_time_window(query)
    c.time_window = tw if (tw.start or tw.end or tw.must_time) else None

    return c

# ---------------------------
# Evaluation Functions
# ---------------------------

def domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        # Remove 'www.' prefix if present
        if netloc.startswith('www.'):
            return netloc[4:]
        return netloc
    except Exception:
        return ''


def platform_for_domain(domain: str) -> Optional[str]:
    for platform, hosts in PLATFORM_HOSTS.items():
        for h in hosts:
            if h in domain:
                return platform
    return None


def text_contains_any(text: str, phrases: List[str]) -> bool:
    tn = normalize(text)
    return any(p in tn for p in phrases)


def evaluate_result(result: Dict[str, Any], constraints: Constraints) -> ResultEval:
    title = result.get('title', '') or ''
    url = result.get('url', '') or ''
    content = result.get('content', '') or ''
    body = f"{title}\n{content}"
    dn = domain_of(url)

    matched: Dict[str, bool] = {}

    # Topic match: any topic keyword
    topic_ok = True
    if constraints.topics:
        topic_ok = False
        for t in constraints.topics:
            if text_contains_any(body, TOPIC_KEYWORDS[t]):
                topic_ok = True
                break
    matched['topic'] = topic_ok

    # Location match
    loc_ok = True
    if constraints.locations:
        loc_ok = any(loc in normalize(body) or loc in url.lower() for loc in constraints.locations)
    matched['location'] = loc_ok

    # Platform match
    plat_ok = True
    if constraints.platforms:
        rplat = platform_for_domain(dn)
        plat_ok = rplat in constraints.platforms
    matched['platform'] = plat_ok

    # Type match
    type_ok = True
    if constraints.types:
        type_ok = False
        for t in constraints.types:
            if any(re.search(rf"\b{k}\b", body, flags=re.IGNORECASE) for k in EVENT_TYPES[t]):
                type_ok = True
                break
    matched['type'] = type_ok

    # Format match
    fmt_ok = True
    if constraints.formats:
        fmt_ok = any(kw in normalize(body) for fmt in constraints.formats for kw in FORMAT_KEYWORDS[fmt])
    matched['format'] = fmt_ok

    # Time window match
    time_ok = True
    detected_dates, detected_times = extract_dates_times(body)
    if constraints.time_window:
        tw = constraints.time_window
        date_ok = True  # Assume date passes unless we have date constraints
        time_of_day_ok = True  # Assume time passes unless we have time constraints
        
        # Date window check (independent)
        if tw.start or tw.end:
            date_ok = False
            if tw.start and tw.end:
                for d in detected_dates:
                    if tw.start <= d <= tw.end:
                        date_ok = True
                        break
            elif tw.start and not tw.end:
                for d in detected_dates:
                    if d == tw.start:
                        date_ok = True
                        break
        
        # Time-of-day check (independent)
        if tw.must_time:
            time_of_day_ok = False
            if detected_times:
                target = tw.must_time
                if any(standardize_ampm(t) == target for t in detected_times):
                    time_of_day_ok = True
        
        # Both must pass
        time_ok = date_ok and time_of_day_ok
    matched['time'] = time_ok

    # Confidence: fraction of constraints satisfied (only counting those that exist)
    required_keys = []
    if constraints.topics: required_keys.append('topic')
    if constraints.locations: required_keys.append('location')
    if constraints.platforms: required_keys.append('platform')
    if constraints.types: required_keys.append('type')
    if constraints.formats: required_keys.append('format')
    if constraints.time_window: required_keys.append('time')

    if required_keys:
        satisfied = sum(1 for k in required_keys if matched.get(k, False))
        confidence = satisfied / len(required_keys)
    else:
        # If no constraints recognized, use weak relevance heuristic: non-empty title+url
        confidence = 0.5 if (title and url) else 0.0

    return ResultEval(
        url=url,
        title=title,
        content_preview=(content[:300] + '...') if len(content) > 300 else content,
        domain=dn,
        matched=matched,
        confidence=round(confidence, 3),
        detected_dates=[d.isoformat() for d in detected_dates[:5]],
        detected_times=detected_times[:5],
    )


def compute_metrics(query_id: int, query_text: str, results: List[Dict[str, Any]], constraints: Constraints, elapsed_sec: float) -> QueryMetrics:
    evals: List[ResultEval] = [evaluate_result(r, constraints) for r in results]
    # Relevant threshold
    relevant = [e for e in evals if e.confidence >= 0.6]

    # Platforms present (counts) among relevant
    platforms_present: Dict[str, int] = {}
    for e in relevant:
        p = platform_for_domain(e.domain) or e.domain
        platforms_present[p] = platforms_present.get(p, 0) + 1

    # Freshness: proportion with future dates or within time window
    freshness: Optional[float] = None
    if relevant:
        hits = 0
        total = 0
        for e in relevant:
            # Use detected dates if any
            ds = [datetime.fromisoformat(x).date() for x in e.detected_dates]
            if not ds:
                continue
            total += 1
            if constraints.time_window and (constraints.time_window.start or constraints.time_window.end):
                tw = constraints.time_window
                start = tw.start or TODAY
                end = tw.end or (tw.start or TODAY)
                if any(start <= d <= end for d in ds):
                    hits += 1
            else:
                if any(d >= TODAY for d in ds):
                    hits += 1
        freshness = round(hits / total, 3) if total > 0 else None

    accuracy = round(len(relevant) / max(1, len(evals)), 3)

    return QueryMetrics(
        query_id=query_id,
        query_text=query_text,
        response_time_ms=int(elapsed_sec * 1000),
        total_results=len(results),
        relevant_results=len(relevant),
        accuracy=accuracy,
        coverage=len(relevant),
        source_diversity=len(set(e.domain for e in relevant)),
        freshness=freshness,
        platforms_present=platforms_present,
        result_evals=evals,
    )

# ---------------------------
# Runner
# ---------------------------

def run_benchmark(md_path: str, max_results: int = 10) -> Dict[str, Any]:
    queries = load_test_queries(md_path)
    if not queries:
        raise RuntimeError("No test queries found in TEST_QUERIES.md (1–20)")

    all_metrics: List[QueryMetrics] = []

    for qid, qtext in queries:
        constraints = parse_constraints(qtext)

        t0 = time.time()
        try:
            resp = client.web_search(qtext, max_results=max_results)
            raw_results = resp.get('results', [])
        except Exception as e:
            print(f"    ERROR: {type(e).__name__}: {str(e)}")
            raw_results = []
        elapsed = time.time() - t0

        # Normalize results to dicts and cap
        results: List[Dict[str, Any]] = []
        for r in raw_results[:max_results]:
            if hasattr(r, '__dict__'):
                results.append({
                    'title': getattr(r, 'title', 'No Title'),
                    'url': getattr(r, 'url', '#'),
                    'content': getattr(r, 'content', '')
                })
            elif isinstance(r, dict):
                results.append({
                    'title': r.get('title', 'No Title'),
                    'url': r.get('url', '#'),
                    'content': r.get('content', '')
                })
        metrics = compute_metrics(qid, qtext, results, constraints, elapsed)
        all_metrics.append(metrics)
        # Progress line
        print(f"[{qid:02d}] {qtext[:60]}... -> {metrics.accuracy*100:.1f}% acc, {metrics.response_time_ms} ms, relevant {metrics.relevant_results}/{metrics.total_results}")
        
        # Delay between queries (after timing) to avoid rate limiting
        time.sleep(2.0)  # 2 second backoff to prevent API rate limits

    # Aggregate summary
    summary = aggregate_summary(all_metrics)

    # Persist outputs
    ts = NOW.strftime('%Y%m%d_%H%M%S')
    out_json = os.path.join(os.getcwd(), f"ollama_benchmark_{ts}.json")
    out_md = os.path.join(os.getcwd(), f"ollama_benchmark_{ts}.md")

    save_json(all_metrics, summary, out_json)
    save_markdown(all_metrics, summary, out_md)

    print(f"\nSaved JSON: {out_json}")
    print(f"Saved Markdown: {out_md}")

    return {
        'json': out_json,
        'markdown': out_md,
        'summary': summary
    }

# ---------------------------
# Reporting
# ---------------------------

def aggregate_summary(metrics: List[QueryMetrics]) -> Dict[str, Any]:
    if not metrics:
        return {}
    avg_accuracy = sum(m.accuracy for m in metrics) / len(metrics)
    avg_resp_ms = sum(m.response_time_ms for m in metrics) / len(metrics)
    avg_coverage = sum(m.coverage for m in metrics) / len(metrics)
    avg_diversity = sum(m.source_diversity for m in metrics) / len(metrics)

    freshness_vals = [m.freshness for m in metrics if m.freshness is not None]
    avg_freshness = (sum(freshness_vals) / len(freshness_vals)) if freshness_vals else None

    # Platform counts across all queries (relevant only)
    platform_totals: Dict[str, int] = {}
    for m in metrics:
        for p, c in m.platforms_present.items():
            platform_totals[p] = platform_totals.get(p, 0) + c

    return {
        'queries': len(metrics),
        'avg_accuracy': round(avg_accuracy, 3),
        'avg_response_time_ms': int(avg_resp_ms),
        'avg_coverage': round(avg_coverage, 2),
        'avg_source_diversity': round(avg_diversity, 2),
        'avg_freshness': round(avg_freshness, 3) if avg_freshness is not None else None,
        'platform_totals': platform_totals
    }


def save_json(metrics: List[QueryMetrics], summary: Dict[str, Any], path: str) -> None:
    payload = {
        'test_date': NOW.isoformat(),
        'summary': summary,
        'results': [
            {
                **{k: v for k, v in asdict(m).items() if k != 'result_evals'},
                'result_evals': [asdict(e) for e in m.result_evals]
            } for m in metrics
        ]
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)


def save_markdown(metrics: List[QueryMetrics], summary: Dict[str, Any], path: str) -> None:
    lines: List[str] = []
    lines.append("# Ollama Search API Benchmark Report\n")
    lines.append(f"Generated: {NOW.strftime('%B %d, %Y %H:%M:%S')}\n")
    lines.append("\n## Summary\n")
    lines.append(f"- Queries: {summary.get('queries')}\n")
    lines.append(f"- Avg Accuracy: {summary.get('avg_accuracy')*100:.1f}%\n")
    lines.append(f"- Avg Response Time: {summary.get('avg_response_time_ms')} ms\n")
    lines.append(f"- Avg Coverage: {summary.get('avg_coverage')}\n")
    lines.append(f"- Avg Source Diversity: {summary.get('avg_source_diversity')}\n")
    af = summary.get('avg_freshness')
    if af is not None:
        lines.append(f"- Avg Freshness: {af*100:.1f}%\n")
    lines.append("- Platforms Totals: " + ", ".join(f"{p}:{c}" for p, c in summary.get('platform_totals', {}).items()) + "\n")

    lines.append("\n## Per-Query Metrics\n")
    for m in metrics:
        lines.append(f"\n### {m.query_id}. {m.query_text}\n")
        lines.append(f"- Response Time: {m.response_time_ms} ms\n")
        lines.append(f"- Accuracy: {m.accuracy*100:.1f}%\n")
        lines.append(f"- Coverage (relevant): {m.coverage}/{m.total_results}\n")
        lines.append(f"- Source Diversity: {m.source_diversity}\n")
        if m.freshness is not None:
            lines.append(f"- Freshness: {m.freshness*100:.1f}%\n")
        if m.platforms_present:
            lines.append(f"- Platforms: {', '.join(f'{k}:{v}' for k, v in m.platforms_present.items())}\n")
        # All results sorted by confidence
        all_results = sorted(m.result_evals, key=lambda x: x.confidence, reverse=True)
        if all_results:
            lines.append("- All Results:")
            for e in all_results:
                relevance_marker = "✓" if e.confidence >= 0.6 else "✗"
                lines.append(f"  - {relevance_marker} [{e.title}]({e.url}) — conf {e.confidence}, matched {e.matched}")
        else:
            lines.append("- All Results: None")

    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))


# ---------------------------
# CLI
# ---------------------------
if __name__ == '__main__':
    md_path = os.path.join(os.path.dirname(__file__), 'TEST_QUERIES.md')
    outputs = run_benchmark(md_path)
    print("\nBenchmark complete.")
