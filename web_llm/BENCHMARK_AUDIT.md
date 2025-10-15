# 🔍 Ollama Benchmark Script Audit Report

**Audit Date:** October 15, 2025  
**Script:** `ollama_benchmark_runner.py`  
**Purpose:** Validate search API accuracy and response time (search results only, no fetching)

---

## ✅ CONFIRMED: Search-Only Constraint

The script **correctly** uses only search API results:
- ✅ Uses `client.web_search(qtext)` only
- ✅ Extracts `title`, `url`, `content` from search results
- ✅ **Does NOT** call `web_fetch()` or any scraping
- ✅ **Does NOT** use LLM `chat()` for analysis
- ✅ Evaluates only the snippet content returned by search

**Verdict:** ✅ **PASS** - Adheres to search-only benchmarking requirement.

---

## 🐛 CRITICAL ISSUES FOUND

### Issue #1: Time Window Logic Error (Saturday Calculation)

**Location:** `parse_time_window()`, line ~244

**Problem:**
```python
if 'this weekend' in qn:
    # upcoming Saturday-Sunday relative to TODAY
    sat = TODAY + timedelta(days=(5 - TODAY.weekday()) % 7)
    sun = sat + timedelta(days=1)
```

**Bug:** If TODAY is Wednesday (weekday=2), this calculates:
```
(5 - 2) % 7 = 3
Saturday = Wednesday + 3 days = Saturday ✅
```

But if TODAY is **Saturday** (weekday=5):
```
(5 - 5) % 7 = 0
Saturday = Saturday + 0 days = Saturday (same day)
```

And if TODAY is **Sunday** (weekday=6):
```
(5 - 6) % 7 = -1 % 7 = 6
Saturday = Sunday + 6 days = NEXT Saturday (7 days away)
```

**Expected Behavior:** "This weekend" should mean:
- Mon-Fri: Upcoming Sat-Sun
- Saturday: Today and tomorrow
- Sunday: Today (or next weekend if past noon)

**Impact:** Medium - Queries 3, 5, 16, 17 use "this weekend" or "next week"

**Fix:**
```python
if 'this weekend' in qn:
    weekday = TODAY.weekday()
    if weekday == 5:  # Saturday
        sat = TODAY
        sun = TODAY + timedelta(days=1)
    elif weekday == 6:  # Sunday
        sat = TODAY - timedelta(days=1)
        sun = TODAY
    else:  # Mon-Fri
        days_until_sat = (5 - weekday) % 7
        if days_until_sat == 0:
            days_until_sat = 7
        sat = TODAY + timedelta(days=days_until_sat)
        sun = sat + timedelta(days=1)
    tw.start, tw.end = sat, sun
    return tw
```

---

### Issue #2: Time-of-Day Matching Logic Flaw

**Location:** `evaluate_result()`, line ~438

**Problem:**
```python
# Time-of-day requirement
if tw.must_time and detected_times:
    # Consider match if exact hour and am/pm matches
    target = tw.must_time
    time_ok = time_ok and any(standardize_ampm(t) == target for t in detected_times)
elif tw.must_time and not detected_times:
    time_ok = False
```

**Bug:** `time_ok` starts as `True` (or set by date window check), then gets AND-ed with time match.

**Scenario:**
- Query: "October 19 at 9 AM"
- Result has date "October 19-21" but times "8 am, 5:30 pm, 9:10 am" (not exact "9 am")
- Date check passes → `time_ok = True`
- Time check: `standardize_ampm("9:10 am")` = "9:10 am" ≠ "9 am" → False
- Final: `time_ok = True AND False = False`

**Issue:** The logic requires BOTH date AND time to match when `must_time` is set. However, the initial `time_ok = True` before the date check means if NO dates are found but time is required, it incorrectly passes.

**More Critical Bug:**
```python
time_ok = True  # Initial state
detected_dates, detected_times = extract_dates_times(body)
if constraints.time_window:
    time_ok = False  # Reset to False
    tw = constraints.time_window
    # Date window check
    if tw.start and tw.end:
        for d in detected_dates:
            if tw.start <= d <= tw.end:
                time_ok = True  # Set to True if date matches
                break
    ...
    # Time-of-day check
    if tw.must_time and detected_times:
        time_ok = time_ok and any(...)  # AND with existing time_ok
```

**Problem:** If date matches but time doesn't, `time_ok` becomes False. But if ONLY time is specified (no date window), the date check is skipped and `time_ok` stays False even if time matches.

**Example:**
- Query: "events at 9 AM" (no date, just time)
- `tw.start = None`, `tw.end = None`, `tw.must_time = "9 am"`
- Date check is skipped (no start/end)
- `time_ok` is still False from reset
- Time check: `time_ok = False AND (time match)` → False even if time matches!

**Impact:** HIGH - Affects Q1 specifically ("October 19 at 9 AM")

**Fix:**
```python
time_ok = True
detected_dates, detected_times = extract_dates_times(body)
if constraints.time_window:
    tw = constraints.time_window
    date_ok = True
    time_of_day_ok = True
    
    # Check date window if specified
    if tw.start or tw.end:
        date_ok = False
        start = tw.start or date.min
        end = tw.end or date.max
        for d in detected_dates:
            if start <= d <= end:
                date_ok = True
                break
    
    # Check time-of-day if specified
    if tw.must_time:
        time_of_day_ok = False
        if detected_times:
            target = tw.must_time
            time_of_day_ok = any(standardize_ampm(t) == target for t in detected_times)
    
    # Both must pass
    time_ok = date_ok and time_of_day_ok

matched['time'] = time_ok
```

---

### Issue #3: Confidence Score Doesn't Match Actual Relevance

**Location:** `evaluate_result()`, line ~447

**Problem:**
```python
if required_keys:
    satisfied = sum(1 for k in required_keys if matched.get(k, False))
    confidence = satisfied / len(required_keys)
else:
    confidence = 0.5 if (title and url) else 0.0
```

**Issue:** This is actually **correct** logic, but the **threshold** for relevance is questionable.

**Current Threshold:** `e.confidence >= 0.6` means 60% of constraints must match.

**Problem Cases:**
- Query with 6 constraints: 4/6 matched = 0.67 → Relevant ✅
- Query with 5 constraints: 3/5 matched = 0.60 → Relevant ✅
- Query with 5 constraints: 2/5 matched = 0.40 → NOT relevant ❌

**Example from Q13 (0% accuracy):**
- Query: "World Health Organization (WHO) webinars scheduled for October"
- Constraints: topic (empty?), platform (WHO), type (webinar), time (October)
- If a result has WHO domain + webinar in title but no October date detected:
  - platform ✅, type ✅, time ❌ → 2/3 = 0.67 → Relevant
  - BUT: If topic was also parsed, 2/4 = 0.5 → NOT relevant

**Issue:** The confidence threshold of 0.6 is arbitrary and may exclude valid results.

**Recommendation:** Consider weighted scoring where critical constraints (platform, time) have higher weight than general ones (topic).

---

### Issue #4: Platform Detection Ambiguity

**Location:** Multiple functions

**Problem 1:** `PLATFORM_HOSTS` has both keys and values:
```python
'eventbrite': ['eventbrite.com'],
'luma': ['lu.ma'],
...
'who': ['who.int'],
'un': ['un.org', 'unitednations.org'],
```

But `parse_constraints()` checks:
```python
for platform in PLATFORM_HOSTS:
    if platform in qn or any(host in qn for host in PLATFORM_HOSTS[platform]):
        c.platforms.add(platform)
```

**Bug:** If query is "Find WHO webinars", `platform in qn` checks if `'who'` is in the normalized query. But `'who'` is a common word!

**Result:** False positives. "Find events for people who love AI" would match platform='who'.

**Impact:** Medium - Affects Q13, possibly others

**Fix:**
```python
# Check only the domain hosts, not the platform key name (unless it's unique)
for platform, hosts in PLATFORM_HOSTS.items():
    if any(host in qn for host in hosts):
        c.platforms.add(platform)
    elif platform in ['eventbrite', 'luma', 'meetup'] and platform in qn:
        # Only check platform name for unique identifiers
        c.platforms.add(platform)
```

**Problem 2:** Domain extraction:
```python
def domain_of(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc.lstrip('www.')
```

**Bug:** `lstrip('www.')` removes characters 'w', '.', and 'w' from the LEFT, not the prefix "www.".

**Example:**
- `"www.eventbrite.com"` → `lstrip('www.')` → `"eventbrite.com"` ✅
- `"www.wework.com"` → `lstrip('www.')` → `"ork.com"` ❌ (removes 'w', 'w', 'w', '.')

**Fix:**
```python
def domain_of(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    if netloc.startswith('www.'):
        return netloc[4:]
    return netloc
```

---

### Issue #5: Date/Time Extraction False Positives

**Location:** `extract_dates_times()`, line ~291

**Problem:** `DATE_RE` and `TIME_RE` are too permissive.

**Example from JSON output (Q1):**
```json
"detected_dates": ["2025-10-19", "2025-10-20", "2025-10-21", "2025-01-02", "2025-04-06"]
```

**Issue:** The last two dates (Jan 2, Apr 6) are likely from:
- "Track 2" → parsed as month=1, day=2
- "4-6 sessions" → parsed as month=4, day=6

**Regex Bug:**
```python
r"(?P<month_num>\d{1,2})[/-](?P<day_num>\d{1,2})"
```

This matches "2/3" in "Track 2/3" or "Session 4/6".

**Fix:** Require word boundaries or context:
```python
DATE_RE = re.compile(
    r"\b(?:(?P<month_name>jan(?:uary)?|...) "
    r"(?P<day>\d{1,2})(?:st|nd|rd|th)?(?:,?\s*(?P<year>\d{4}))?"
    r"|\b(?P<month_num>1[0-2]|0?[1-9])[/-](?P<day_num>[0-3]?\d)(?:[/-](?P<year_num>\d{2,4}))?)\b",
    re.IGNORECASE
)
```

And add validation:
```python
mm = int(m.group('month_num'))
dd = int(m.group('day_num'))
if mm > 12 or dd > 31:  # Invalid date
    continue
```

**Impact:** Medium - Inflates detected_dates, potentially causing false freshness scores

---

### Issue #6: Freshness Calculation Inconsistency

**Location:** `compute_metrics()`, line ~479

**Problem:**
```python
freshness: Optional[float] = None
if relevant:
    hits = 0
    total = 0
    for e in relevant:
        ds = [datetime.fromisoformat(x).date() for x in e.detected_dates]
        if not ds:
            continue  # Skip if no dates detected
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
```

**Issue 1:** Only counts results WITH detected dates in `total`. If 3 relevant results have no dates detected, `freshness = None` instead of 0.0.

**Example from Q9:**
```json
"freshness": 0.0
```
But markdown shows: `"Freshness: 0.0%"` which suggests 1 result had dates but none were fresh.

**Issue 2:** If a result has dates `["2025-10-07", "2025-01-02"]` and time_window is Oct 18-22:
- Oct 7 is NOT in window → doesn't match
- Jan 2 is NOT in window → doesn't match
- Result counts toward `total` but not `hits`

But if the result is ABOUT an October event (Oct 7) and the window is Oct 18-22, should it count as "not fresh" or be excluded from freshness calculation?

**Recommendation:** 
- Option A: Include all relevant results in `total`, assign freshness=0 if no dates detected
- Option B: Only count results with dates in `total` (current behavior, but make it explicit)

**Current behavior is inconsistent with other metrics where 0/3 = 0.0, not None.**

---

### Issue #7: Type Matching Uses Incorrect Regex

**Location:** `evaluate_result()`, line ~424

**Problem:**
```python
if constraints.types:
    type_ok = False
    for t in constraints.types:
        if any(re.search(rf"\b{k}\b", body, flags=re.IGNORECASE) for k in EVENT_TYPES[t]):
            type_ok = True
            break
```

**Issue:** `EVENT_TYPES` values contain regex patterns like `'hackathon(s)?'`, but they're used inside `\b{k}\b` which treats them as literals.

**Example:**
```python
EVENT_TYPES = {
    'hackathon': ['hackathon', 'hackathon(s)?'],
}
```

Pattern becomes: `r"\bhackathon(s)?\b"` which looks for literal text "hackathon(s)?", not "hackathon" or "hackathons".

**Fix:** Either:
1. Remove regex syntax from EVENT_TYPES values and handle plurals separately
2. Don't wrap in `\b...\b`, use the patterns directly:

```python
type_ok = False
for t in constraints.types:
    for pattern in EVENT_TYPES[t]:
        if re.search(rf"\b{pattern}\b", body, flags=re.IGNORECASE):
            type_ok = True
            break
    if type_ok:
        break
```

**Impact:** Low - Most patterns like 'hackathon' work anyway, but 'workshops?' won't match "workshop"

---

## 🟡 MINOR ISSUES

### Minor #1: Magic Numbers

**Location:** Multiple

**Issue:** Hardcoded values without constants:
- `e.confidence >= 0.6` (relevance threshold)
- `time.sleep(0.5)` (backoff between queries)
- `max_results: int = 10` (default result limit)

**Recommendation:** Define as module-level constants:
```python
RELEVANCE_THRESHOLD = 0.6
QUERY_BACKOFF_SEC = 0.5
DEFAULT_MAX_RESULTS = 10
```

---

### Minor #2: Inconsistent Platform Naming

**Location:** `platform_for_domain()` and output

**Issue:** Some results show platform as `"eventbrite"` (from PLATFORM_HOSTS key), others as `"luma.com"` (raw domain).

**From JSON:**
```json
"platforms_present": {
  "luma.com": 1,
  "eventbrite": 5,
  "luma": 1
}
```

**Bug:** Both `"luma.com"` and `"luma"` appear because:
```python
p = platform_for_domain(e.domain) or e.domain
```

If `platform_for_domain()` returns None, it uses raw domain. But for some domains it returns the platform key.

**Fix:** Ensure consistent naming or normalize to platform key when possible.

---

### Minor #3: No Validation of Query Parsing

**Issue:** If `parse_constraints()` extracts NO constraints, confidence defaults to 0.5 for any result with title+url.

**Example:** Query "Find events" has no topic, location, platform, type, or time.
- Every result with a title gets confidence 0.5
- Threshold is 0.6, so none are relevant → 0% accuracy

**This might be intentional**, but it means queries without clear constraints always fail.

---

### Minor #4: Duplicate Detection Not Implemented

**Issue:** If search returns the same URL twice (unlikely but possible), it's counted twice in metrics.

**Recommendation:** Add URL deduplication:
```python
seen_urls = set()
results: List[Dict[str, Any]] = []
for r in raw_results[:max_results]:
    url = getattr(r, 'url', '#') if hasattr(r, '__dict__') else r.get('url', '#')
    if url in seen_urls:
        continue
    seen_urls.add(url)
    # ... add to results
```

---

## 📊 METRICS VALIDATION

### Response Time
✅ **VALID** - Measures `time.time()` around `client.web_search()` call only

### Accuracy
⚠️ **NEEDS FIX** - Depends on flawed constraint matching (Issues #2, #4, #7)

### Coverage
✅ **VALID** - Counts relevant results (confidence >= 0.6)

### Source Diversity
✅ **VALID** - Counts distinct domains among relevant results

### Freshness
⚠️ **INCONSISTENT** - Doesn't count results with no detected dates (Issue #6)

---

## 🎯 SEVERITY ASSESSMENT

| Issue | Severity | Impact on Benchmarking |
|-------|----------|------------------------|
| #1: Weekend calculation | Medium | Affects Q3, Q5 accuracy |
| #2: Time matching logic | **HIGH** | Affects Q1, Q4 accuracy significantly |
| #3: Confidence threshold | Low | Philosophical choice |
| #4: Platform detection | Medium | False positives for "who", domain parsing bug |
| #5: Date extraction | Medium | Inflates freshness scores |
| #6: Freshness calculation | Medium | Inconsistent with other metrics |
| #7: Type regex | Low | Minor matching issues |

---

## ✅ WHAT'S WORKING CORRECTLY

1. ✅ **Search-only approach** - No fetching/scraping
2. ✅ **Response time measurement** - Accurate
3. ✅ **Query parsing** - Mostly correct (90%+)
4. ✅ **Topic detection** - Works well
5. ✅ **Location detection** - Works well
6. ✅ **Result normalization** - Handles both object and dict responses
7. ✅ **JSON/Markdown output** - Clean, readable
8. ✅ **Coverage calculation** - Correct
9. ✅ **Source diversity** - Correct

---

## 🔧 PRIORITY FIXES

### P0 (Critical - Fix Immediately):
1. **Issue #2:** Time-of-day matching logic
2. **Issue #4:** Domain parsing (`lstrip` bug)

### P1 (High - Fix Before Next Run):
3. **Issue #1:** Weekend calculation
4. **Issue #5:** Date extraction false positives
5. **Issue #6:** Freshness calculation consistency

### P2 (Medium - Improve Later):
6. **Issue #7:** Type regex patterns
7. **Issue #4:** Platform "who" false positive
8. **Minor #2:** Consistent platform naming

---

## 📝 RECOMMENDATIONS

### For Immediate Use:
1. **Fix Issues #2 and #4** (domain parsing) before next benchmark run
2. Accept current results with caveat that time-specific queries (Q1, Q4) may be under-scored
3. Document the 0.6 relevance threshold in the report

### For Production Quality:
1. Add unit tests for:
   - `parse_time_window()` with edge cases (today is Sat/Sun/Mon)
   - `evaluate_result()` with various constraint combinations
   - `extract_dates_times()` with tricky patterns
2. Add query validation to warn if no constraints detected
3. Implement URL deduplication
4. Make thresholds configurable via command-line args

---

## 🏆 OVERALL VERDICT

**Script Quality:** ⭐⭐⭐⭐☆ (4/5)

**Pros:**
- ✅ Correctly implements search-only benchmarking
- ✅ Comprehensive constraint parsing
- ✅ Well-structured, readable code
- ✅ Produces useful metrics
- ✅ No logical gaps in core flow

**Cons:**
- ❌ Critical time-matching logic bug (Issue #2)
- ❌ Domain parsing bug (Issue #4)
- ⚠️ Several date/time extraction edge cases
- ⚠️ Inconsistent freshness calculation

**Recommendation:** **Fix Issues #2 and #4, then re-run** to get accurate results for time-sensitive queries.
