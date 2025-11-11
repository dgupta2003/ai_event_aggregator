import json
from typing import List
from bs4 import BeautifulSoup
from ..models import Event
from ..utils import parse_date_safe, clean_text

def events_from_jsonld(soup: BeautifulSoup, source: str) -> List[Event]:
    out: List[Event] = []
    for tag in soup.select("script[type='application/ld+json']"):
        raw = tag.string or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for it in items:
            if not isinstance(it, dict):
                continue
            t = it.get("@type") or it.get("@context")
            if isinstance(t, list):
                t = " ".join(map(str, t))
            if not t or ("Event" not in str(t)):
                continue
            title = clean_text(it.get("name", ""))
            url = it.get("url") or ""
            start = parse_date_safe(it.get("startDate", "") or it.get("startTime", ""))
            city = None
            region = None
            loc = it.get("location") or {}
            if isinstance(loc, dict):
                addr = loc.get("address") or {}
                city = addr.get("addressLocality")
                region = addr.get("addressRegion")
            out.append(Event(source=source, title=title, url=url, start=start, city=city, region=region, raw=it))
    return out

