from typing import List, Set
from .models import Event

def accuracy_score(filtered: List[Event], original: List[Event]) -> float:
    if not original:
        return 0.0
    good = 0.0
    for e in filtered:
        title_ok = len((e.title or "")) > 8
        date_ok = e.start is not None
        url_ok = (e.url or "").startswith("http")
        good += 0.8 if (title_ok and url_ok) else 0.4
        if date_ok:
            good += 0.4
    base = len(original)
    return min(1.0, good / max(1.0, base))

def coverage(filtered: List[Event]) -> int:
    return len(filtered)

def source_diversity(filtered: List[Event]) -> int:
    s: Set[str] = set(e.source for e in filtered)
    return len(s)

def freshness_ok(filtered: List[Event]) -> int:
    import datetime
    today = datetime.date.today()
    ok = 0
    for e in filtered:
        if e.start and e.start.date() >= today - datetime.timedelta(days=1):
            ok += 1
    return ok
