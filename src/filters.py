from typing import List, Dict
from .models import Event
from .utils import keyword_hit, within_range, resolve_relative_window
from datetime import datetime, date

def apply_filters(events: List[Event], filters: Dict) -> List[Event]:
    out = events

    # topic
    topic_terms = filters.get("topic") or []
    if topic_terms:
        out = [e for e in out if keyword_hit((e.title or "") + " " + str(e.raw or {}), topic_terms)]

    # type
    types = filters.get("type") or []
    if types:
        out = [e for e in out if keyword_hit(e.title or "", types)]

    # host keywords
    host = filters.get("host_keywords") or []
    if host:
        out = [e for e in out if keyword_hit(str(e.raw or "") + " " + (e.title or ""), host)]

    # audience
    audience = filters.get("audience") or []
    if audience:
        out = [e for e in out if keyword_hit((e.title or "") + " " + str(e.raw or {}), audience)]

    # format
    fmts = filters.get("format") or []
    if fmts:
        def match_fmt(e: Event) -> bool:
            txt = ((e.title or "") + " " + str(e.raw or "")).lower()
            if ("virtual" in fmts or "online" in fmts) and ("online" in txt or "virtual" in txt):
                return True
            if "hybrid" in fmts and "hybrid" in txt:
                return True
            if ("in-person" in fmts or "in person" in fmts) and "in person" in txt:
                return True
            return False
        out = [e for e in out if match_fmt(e)]

    # price
    prices = filters.get("price") or []
    if prices:
        def match_price(e: Event) -> bool:
            txt = ((e.title or "") + " " + str(e.raw or "")).lower()
            if "free" in prices and "free" in txt:
                return True
            return False
        out = [e for e in out if match_price(e)]

    # location
    city = (filters.get("location_city") or "").lower()
    region = (filters.get("location_region") or "").lower()
    if city:
        out = [e for e in out if (e.city or "").lower().startswith(city) or city in (e.title or "").lower()]
    if region:
        out = [e for e in out if (e.region or "").lower().startswith(region) or region in (e.title or "").lower()]

    # absolute date range only if provided
    df = filters.get("date_from")
    dt = filters.get("date_to")
    if df or dt:
        dfrom = datetime.fromisoformat(df).date() if df else date(1900,1,1)
        dto = datetime.fromisoformat(dt).date() if dt else date(2100,1,1)
        out = [e for e in out if e.start and within_range(e.start, dfrom, dto)]

    # exact date and time only if provided
    de = filters.get("date_exact")
    te = filters.get("time_exact")
    if de:
        dfrom = datetime.fromisoformat(de).date()
        dto = dfrom
        out = [e for e in out if e.start and within_range(e.start, dfrom, dto)]
    if te:
        out = [e for e in out if e.start and e.start.strftime("%H:%M") == te]

    # relative window only if provided
    rw = filters.get("relative_window")
    if rw:
        dfrom, dto = resolve_relative_window(rw)
        out = [e for e in out if e.start and within_range(e.start, dfrom, dto)]

    return out
