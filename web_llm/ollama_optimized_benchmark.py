"""
Ollama Search API Benchmark Runner - OPTIMIZED QUERIES

Tests Gemini-optimized queries vs original queries to measure improvement.
Focuses on first 5 queries for quick iteration.

Metrics compared:
- Accuracy improvement
- Relevance quality
- Platform diversity
- Time/date precision
- Generic listing reduction
"""

from __future__ import annotations
import os
import re
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
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
# Constants
# ---------------------------
NOW = datetime.now()
TODAY = NOW.date()
CURRENT_YEAR = TODAY.year

PLATFORM_HOSTS = {
    'eventbrite': ['eventbrite.com'],
    'luma': ['lu.ma'],
    'meetup': ['meetup.com'],
    'facebook': ['facebook.com'],
    'allevents': ['allevents.in'],
}

# Generic listing detection patterns
GENERIC_URL_PATTERNS = [
    '/find/', '/search/', '/calendar/', '/list/', '/events/', '/browse/',
    '/discover/', '/explore/', '/all-events', '/categories/', '/tags/'
]

GENERIC_TITLE_PATTERNS = [
    'events calendar', 'all events', 'events near', 'upcoming events',
    'find events', 'browse events', 'event listings', 'search events',
    'event directory', 'events in', 'things to do'
]

# ---------------------------
# Data Classes
# ---------------------------
@dataclass
class OptimizedQuery:
    """Loaded from optimized_queries.json"""
    original_query: str
    optimized_query: str
    alternative_queries: List[str]
    reasoning: str
    extracted_constraints: Dict[str, Optional[str]]


@dataclass
class ResultEval:
    """Evaluation of a single search result"""
    url: str
    title: str
    content_preview: str
    domain: str
    is_generic_listing: bool
    has_future_dates: bool
    detected_dates: List[str]
    platform: Optional[str]
    relevance_score: float  # 0-1 based on keywords/context


@dataclass
class ComparisonMetrics:
    """Comparison between original and optimized query results"""
    query_id: int
    original_query: str
    optimized_query: str
    
    # Original query results
    original_response_time_ms: int
    original_total_results: int
    original_relevant_results: int
    original_accuracy: float
    original_generic_count: int
    original_platform_diversity: int
    original_future_events: int
    
    # Optimized query results
    optimized_response_time_ms: int
    optimized_total_results: int
    optimized_relevant_results: int
    optimized_accuracy: float
    optimized_generic_count: int
    optimized_platform_diversity: int
    optimized_future_events: int
    
    # Improvement metrics
    accuracy_improvement: float  # percentage points
    generic_reduction: int  # count reduction
    platform_diversity_gain: int
    future_events_gain: int
    
    # Detailed results
    original_evals: List[ResultEval]
    optimized_evals: List[ResultEval]


# ---------------------------
# Helper Functions
# ---------------------------

def domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
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


def is_generic_listing(title: str, url: str) -> bool:
    """
    Detect if result is a generic event directory/calendar page
    rather than a specific event
    """
    title_lower = title.lower()
    url_lower = url.lower()
    
    # Check URL patterns
    if any(pattern in url_lower for pattern in GENERIC_URL_PATTERNS):
        return True
    
    # Check title patterns
    if any(pattern in title_lower for pattern in GENERIC_TITLE_PATTERNS):
        return True
    
    return False


def extract_dates_simple(text: str) -> List[date]:
    """Simple date extraction (month name + day)"""
    dates = []
    
    # Pattern: November 12, 2025 or Nov 12, 2025
    pattern = r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t)?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2})(?:,\s*(\d{4}))?\b'
    
    months = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
        'jul': 7, 'july': 7, 'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9, 'oct': 10, 'october': 10,
        'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }
    
    for match in re.finditer(pattern, text.lower()):
        month_name = match.group(1)
        day = int(match.group(2))
        year = int(match.group(3)) if match.group(3) else CURRENT_YEAR
        
        month = months.get(month_name.replace('.', ''))
        if month:
            try:
                dates.append(date(year, month, day))
            except ValueError:
                pass
    
    return dates


def calculate_relevance_score(result: Dict[str, Any], query: str) -> float:
    """
    Simple relevance scoring based on keyword presence
    Higher score = more relevant
    """
    title = (result.get('title', '') or '').lower()
    content = (result.get('content', '') or '').lower()
    query_lower = query.lower()
    
    # Extract key terms from query (simple tokenization)
    query_terms = set(re.findall(r'\b[a-z]{3,}\b', query_lower))
    
    # Remove common words
    common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'event', 'events'}
    query_terms = query_terms - common_words
    
    if not query_terms:
        return 0.5
    
    # Count term matches in title (weighted higher)
    title_matches = sum(1 for term in query_terms if term in title)
    content_matches = sum(1 for term in query_terms if term in content)
    
    # Weighted score
    title_weight = 0.6
    content_weight = 0.4
    
    title_score = (title_matches / len(query_terms)) * title_weight
    content_score = min(content_matches / len(query_terms), 1.0) * content_weight
    
    return min(title_score + content_score, 1.0)


def evaluate_result(result: Dict[str, Any], query: str) -> ResultEval:
    """Evaluate a single search result"""
    title = result.get('title', '') or 'No Title'
    url = result.get('url', '') or '#'
    content = result.get('content', '') or ''
    
    domain = domain_of(url)
    platform = platform_for_domain(domain)
    
    # Check if generic listing
    is_generic = is_generic_listing(title, url)
    
    # Extract dates and check if future
    full_text = f"{title} {content}"
    detected_dates = extract_dates_simple(full_text)
    has_future = any(d >= TODAY for d in detected_dates)
    
    # Calculate relevance
    relevance = calculate_relevance_score(result, query)
    
    # Penalize generic listings
    if is_generic:
        relevance *= 0.3
    
    return ResultEval(
        url=url,
        title=title,
        content_preview=(content[:200] + '...') if len(content) > 200 else content,
        domain=domain,
        is_generic_listing=is_generic,
        has_future_dates=has_future,
        detected_dates=[d.isoformat() for d in detected_dates[:3]],
        platform=platform,
        relevance_score=round(relevance, 3)
    )


def run_single_query(query: str, max_results: int = 10) -> Tuple[List[ResultEval], int]:
    """
    Run a single query and return evaluations + response time
    
    Returns:
        (evaluations, response_time_ms)
    """
    t0 = time.time()
    try:
        resp = client.web_search(query, max_results=max_results)
        raw_results = resp.get('results', [])
    except Exception as e:
        print(f"    ERROR: {type(e).__name__}: {str(e)}")
        raw_results = []
    elapsed_ms = int((time.time() - t0) * 1000)
    
    # Normalize results
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
    
    # Evaluate all results
    evals = [evaluate_result(r, query) for r in results]
    
    return evals, elapsed_ms


def compare_queries(
    query_id: int,
    original_query: str,
    optimized_query: str,
    max_results: int = 10
) -> ComparisonMetrics:
    """
    Run both original and optimized queries, compare results
    """
    print(f"\n[{query_id}] Comparing queries...")
    print(f"  Original:  {original_query[:70]}...")
    print(f"  Optimized: {optimized_query[:70]}...")
    
    # Run original query
    print("  → Running original query...")
    orig_evals, orig_time = run_single_query(original_query, max_results)
    time.sleep(2.0)  # Rate limit protection
    
    # Run optimized query
    print("  → Running optimized query...")
    opt_evals, opt_time = run_single_query(optimized_query, max_results)
    time.sleep(2.0)  # Rate limit protection
    
    # Calculate metrics for original
    orig_relevant = [e for e in orig_evals if e.relevance_score >= 0.5]
    orig_generic = sum(1 for e in orig_evals if e.is_generic_listing)
    orig_platforms = len(set(e.platform for e in orig_relevant if e.platform))
    orig_future = sum(1 for e in orig_evals if e.has_future_dates)
    orig_accuracy = len(orig_relevant) / max(1, len(orig_evals))
    
    # Calculate metrics for optimized
    opt_relevant = [e for e in opt_evals if e.relevance_score >= 0.5]
    opt_generic = sum(1 for e in opt_evals if e.is_generic_listing)
    opt_platforms = len(set(e.platform for e in opt_relevant if e.platform))
    opt_future = sum(1 for e in opt_evals if e.has_future_dates)
    opt_accuracy = len(opt_relevant) / max(1, len(opt_evals))
    
    # Calculate improvements
    accuracy_improvement = (opt_accuracy - orig_accuracy) * 100  # percentage points
    generic_reduction = orig_generic - opt_generic
    platform_gain = opt_platforms - orig_platforms
    future_gain = opt_future - orig_future
    
    print(f"  ✓ Original: {orig_accuracy*100:.1f}% acc, {orig_generic} generic, {orig_future} future")
    print(f"  ✓ Optimized: {opt_accuracy*100:.1f}% acc, {opt_generic} generic, {opt_future} future")
    print(f"  → Improvement: {accuracy_improvement:+.1f}pp acc, {generic_reduction:+d} generic, {future_gain:+d} future")
    
    return ComparisonMetrics(
        query_id=query_id,
        original_query=original_query,
        optimized_query=optimized_query,
        original_response_time_ms=orig_time,
        original_total_results=len(orig_evals),
        original_relevant_results=len(orig_relevant),
        original_accuracy=round(orig_accuracy, 3),
        original_generic_count=orig_generic,
        original_platform_diversity=orig_platforms,
        original_future_events=orig_future,
        optimized_response_time_ms=opt_time,
        optimized_total_results=len(opt_evals),
        optimized_relevant_results=len(opt_relevant),
        optimized_accuracy=round(opt_accuracy, 3),
        optimized_generic_count=opt_generic,
        optimized_platform_diversity=opt_platforms,
        optimized_future_events=opt_future,
        accuracy_improvement=round(accuracy_improvement, 1),
        generic_reduction=generic_reduction,
        platform_diversity_gain=platform_gain,
        future_events_gain=future_gain,
        original_evals=orig_evals,
        optimized_evals=opt_evals
    )


def run_benchmark(optimized_queries_path: str, num_queries: int = 5) -> List[ComparisonMetrics]:
    """
    Run benchmark on first N optimized queries
    """
    # Load optimized queries
    with open(optimized_queries_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    optimized_list = data['optimized_queries'][:num_queries]
    
    print(f"{'='*80}")
    print(f"OLLAMA OPTIMIZED QUERY BENCHMARK")
    print(f"Testing {num_queries} optimized queries")
    print(f"{'='*80}")
    
    all_comparisons: List[ComparisonMetrics] = []
    
    for i, opt_data in enumerate(optimized_list, 1):
        comparison = compare_queries(
            query_id=i,
            original_query=opt_data['original_query'],
            optimized_query=opt_data['optimized_query'],
            max_results=10
        )
        all_comparisons.append(comparison)
    
    return all_comparisons


def generate_summary(comparisons: List[ComparisonMetrics]) -> Dict[str, Any]:
    """Generate aggregate summary statistics"""
    if not comparisons:
        return {}
    
    n = len(comparisons)
    
    # Average improvements
    avg_accuracy_improvement = sum(c.accuracy_improvement for c in comparisons) / n
    avg_generic_reduction = sum(c.generic_reduction for c in comparisons) / n
    avg_platform_gain = sum(c.platform_diversity_gain for c in comparisons) / n
    avg_future_gain = sum(c.future_events_gain for c in comparisons) / n
    
    # Original vs optimized averages
    avg_orig_accuracy = sum(c.original_accuracy for c in comparisons) / n
    avg_opt_accuracy = sum(c.optimized_accuracy for c in comparisons) / n
    
    # Count wins/losses
    accuracy_wins = sum(1 for c in comparisons if c.accuracy_improvement > 0)
    generic_wins = sum(1 for c in comparisons if c.generic_reduction > 0)
    future_wins = sum(1 for c in comparisons if c.future_events_gain > 0)
    
    return {
        'total_queries': n,
        'avg_accuracy_improvement_pp': round(avg_accuracy_improvement, 1),
        'avg_generic_reduction': round(avg_generic_reduction, 1),
        'avg_platform_diversity_gain': round(avg_platform_gain, 1),
        'avg_future_events_gain': round(avg_future_gain, 1),
        'avg_original_accuracy': round(avg_orig_accuracy, 3),
        'avg_optimized_accuracy': round(avg_opt_accuracy, 3),
        'accuracy_wins': accuracy_wins,
        'generic_reduction_wins': generic_wins,
        'future_events_wins': future_wins
    }


def save_results(comparisons: List[ComparisonMetrics], summary: Dict[str, Any]) -> Tuple[str, str]:
    """Save results to JSON and Markdown"""
    ts = NOW.strftime('%Y%m%d_%H%M%S')
    json_path = f"ollama_optimized_benchmark_{ts}.json"
    md_path = f"ollama_optimized_benchmark_{ts}.md"
    
    # Save JSON
    json_data = {
        'timestamp': NOW.isoformat(),
        'summary': summary,
        'comparisons': [
            {
                **{k: v for k, v in asdict(c).items() if k not in ['original_evals', 'optimized_evals']},
                'original_evals': [asdict(e) for e in c.original_evals],
                'optimized_evals': [asdict(e) for e in c.optimized_evals]
            }
            for c in comparisons
        ]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    
    # Save Markdown
    lines = [
        "# Ollama Optimized Query Benchmark Report\n",
        f"Generated: {NOW.strftime('%B %d, %Y %H:%M:%S')}\n",
        "\n## Summary\n",
        f"- Total Queries Tested: {summary['total_queries']}\n",
        f"- **Average Accuracy Improvement: {summary['avg_accuracy_improvement_pp']:+.1f} percentage points**\n",
        f"- Average Generic Listing Reduction: {summary['avg_generic_reduction']:+.1f}\n",
        f"- Average Platform Diversity Gain: {summary['avg_platform_diversity_gain']:+.1f}\n",
        f"- Average Future Events Gain: {summary['avg_future_events_gain']:+.1f}\n",
        f"- Original Average Accuracy: {summary['avg_original_accuracy']*100:.1f}%\n",
        f"- Optimized Average Accuracy: {summary['avg_optimized_accuracy']*100:.1f}%\n",
        f"- Accuracy Wins: {summary['accuracy_wins']}/{summary['total_queries']}\n",
        f"- Generic Reduction Wins: {summary['generic_reduction_wins']}/{summary['total_queries']}\n",
        f"- Future Events Wins: {summary['future_events_wins']}/{summary['total_queries']}\n",
        "\n## Per-Query Comparisons\n"
    ]
    
    for c in comparisons:
        lines.extend([
            f"\n### {c.query_id}. {c.original_query}\n",
            f"**Optimized:** {c.optimized_query}\n\n",
            "| Metric | Original | Optimized | Improvement |\n",
            "|--------|----------|-----------|-------------|\n",
            f"| Accuracy | {c.original_accuracy*100:.1f}% | {c.optimized_accuracy*100:.1f}% | **{c.accuracy_improvement:+.1f}pp** |\n",
            f"| Relevant Results | {c.original_relevant_results}/{c.original_total_results} | {c.optimized_relevant_results}/{c.optimized_total_results} | {c.optimized_relevant_results - c.original_relevant_results:+d} |\n",
            f"| Generic Listings | {c.original_generic_count} | {c.optimized_generic_count} | **{c.generic_reduction:+d}** |\n",
            f"| Platform Diversity | {c.original_platform_diversity} | {c.optimized_platform_diversity} | {c.platform_diversity_gain:+d} |\n",
            f"| Future Events | {c.original_future_events} | {c.optimized_future_events} | {c.future_events_gain:+d} |\n",
            f"| Response Time | {c.original_response_time_ms}ms | {c.optimized_response_time_ms}ms | {c.optimized_response_time_ms - c.original_response_time_ms:+d}ms |\n",
            "\n**Original Query Top Results:**\n"
        ])
        
        for i, e in enumerate(c.original_evals[:3], 1):
            marker = "✓" if e.relevance_score >= 0.5 else "✗"
            generic_flag = " [GENERIC]" if e.is_generic_listing else ""
            lines.append(f"{i}. {marker} [{e.title}]({e.url}) — score {e.relevance_score}{generic_flag}\n")
        
        lines.append("\n**Optimized Query Top Results:**\n")
        for i, e in enumerate(c.optimized_evals[:3], 1):
            marker = "✓" if e.relevance_score >= 0.5 else "✗"
            generic_flag = " [GENERIC]" if e.is_generic_listing else ""
            lines.append(f"{i}. {marker} [{e.title}]({e.url}) — score {e.relevance_score}{generic_flag}\n")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("".join(lines))
    
    return json_path, md_path


# ---------------------------
# CLI
# ---------------------------
if __name__ == '__main__':
    optimized_queries_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'optimized_queries.json'
    )
    
    if not os.path.exists(optimized_queries_path):
        print(f"ERROR: {optimized_queries_path} not found")
        print("Run query_optimizer.py first to generate optimized queries")
        exit(1)
    
    # Run benchmark on first 5 queries
    comparisons = run_benchmark(optimized_queries_path, num_queries=5)
    
    # Generate summary
    summary = generate_summary(comparisons)
    
    # Save results
    json_path, md_path = save_results(comparisons, summary)
    
    print(f"\n{'='*80}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*80}")
    print(f"\n📊 SUMMARY:")
    print(f"   Accuracy Improvement: {summary['avg_accuracy_improvement_pp']:+.1f} percentage points")
    print(f"   Generic Reduction: {summary['avg_generic_reduction']:+.1f}")
    print(f"   Future Events Gain: {summary['avg_future_events_gain']:+.1f}")
    print(f"   Original Accuracy: {summary['avg_original_accuracy']*100:.1f}%")
    print(f"   Optimized Accuracy: {summary['avg_optimized_accuracy']*100:.1f}%")
    print(f"\n📄 Results saved to:")
    print(f"   JSON: {json_path}")
    print(f"   Markdown: {md_path}")
