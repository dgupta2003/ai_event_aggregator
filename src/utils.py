from datetime import datetime, timedelta, date
from dateutil import parser as dtp
import pytz
from typing import Optional, Tuple, List, Dict
import re

TZ = pytz.timezone("America/Phoenix")

SOFT_HYPHEN = "\u00ad"
ZERO_WIDTH_PATTERN = r"[\u200b\u200c\u200d\u2060\ufeff]"

TZINFOS: Dict[str, int] = {
    "CET": 1 * 3600,
    "CEST": 2 * 3600,
    "PDT": -7 * 3600,
    "PST": -8 * 3600,
    "EDT": -4 * 3600,
    "EST": -5 * 3600,
    "UTC": 0,
    "GMT": 0,
}

def clean_text(t: str) -> str:
    if not t:
        return ""
    t = t.replace(SOFT_HYPHEN, "")
    t = re.sub(ZERO_WIDTH_PATTERN, "", t)
    return " ".join(t.split())

def now_local() -> datetime:
    return datetime.now(TZ)

def resolve_relative_window(window: Optional[str]) -> Tuple[date, date]:
    today = now_local().date()
    if not window:
        return date(1900,1,1), date(2100,1,1)
    if window == "tomorrow":
        start = today + timedelta(days=1)
        end = start
        return start, end
    if window == "weekend":
        days_ahead = (5 - today.weekday()) % 7
        sat = today + timedelta(days=days_ahead)
        sun = sat + timedelta(days=1)
        return sat, sun
    if window == "this_week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    if window == "next_week":
        start = today - timedelta(days=today.weekday()) + timedelta(days=7)
        end = start + timedelta(days=6)
        return start, end
    if window == "this_month":
        start = today.replace(day=1)
        if start.month == 12:
            next_first = start.replace(year=start.year+1, month=1, day=1)
        else:
            next_first = start.replace(month=start.month+1, day=1)
        end = next_first - timedelta(days=1)
        return start, end
    return date(1900,1,1), date(2100,1,1)

def parse_date_safe(text: str):
    try:
        return dtp.parse(text, fuzzy=True, tzinfos=TZINFOS)
    except Exception:
        return None

def keyword_hit(text: str, terms: List[str]) -> bool:
    t = text.lower()
    return any(term.lower() in t for term in terms)

def within_range(dt, dfrom, dto) -> bool:
    if not dt:
        return False
    d = dt.date()
    return dfrom <= d <= dto

