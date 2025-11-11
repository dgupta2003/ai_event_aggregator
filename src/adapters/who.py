from typing import List
from ..fetchers import fetch_html, soup_or_none
from ..models import Event
from ..utils import parse_date_safe

BASE = "https://www.who.int/news-room/events"

def run(query: str) -> List[Event]:
    html = fetch_html(BASE)
    soup = soup_or_none(html)
    if not soup:
        return []
    out: List[Event] = []
    cards = soup.select("a[href*='/events/']")
    for a in cards:
        title = a.get_text(" ", strip=True)
        url = "https://www.who.int" + a.get("href", "")
        date = None
        parent = a.find_parent()
        if parent:
            t = parent.get_text(" ", strip=True)
            date = parse_date_safe(t)
        out.append(Event(source="who", title=title, url=url, start=date, country="Global"))
    return out
