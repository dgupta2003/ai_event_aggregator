import json, time, os, pandas as pd
from src.models import Query, ResultRow
from src.adapters import eventbrite, luma, meetup, who, un, ted
from src.filters import apply_filters
from src.score import accuracy_score, coverage, source_diversity, freshness_ok

ADAPTERS = {
    "eventbrite": lambda q,f: eventbrite.run(q, f),
    "luma": lambda q,f: luma.run(q),
    "meetup": lambda q,f: meetup.run(q, near=(f.get("location_city") if f else None)),
    "who": lambda q,f: who.run(q),
    "un": lambda q,f: un.run(q),
    "ted": lambda q,f: ted.run(q),
}

def run_one(query: Query):
    rows = []
    all_events = []
    for name, fn in ADAPTERS.items():
        t0 = time.time()
        events = fn(query.text, query.filters)
        t1 = time.time()
        filtered = apply_filters(events, query.filters)
        acc = accuracy_score(filtered, events)
        cov = coverage(filtered)
        div = source_diversity(filtered)
        fresh = freshness_ok(filtered)
        rows.append(ResultRow(
            query_id=query.id,
            engine=name,
            response_time_ms=int((t1 - t0) * 1000),
            accuracy=acc,
            coverage=cov,
            source_diversity=div,
            freshness_ok=fresh,
        ).model_dump())
        for e in filtered:
            all_events.append({
                "query_id": query.id, "engine": name, "source": e.source, "title": e.title,
                "url": e.url, "start": e.start.isoformat() if e.start else None,
                "city": e.city, "region": e.region, "country": e.country, "is_virtual": e.is_virtual, "price": e.price
            })
    return rows, all_events

def main():
    with open("queries.json","r") as f:
        data = json.load(f)
    queries = [Query(**q) for q in data["queries"]]
    metrics_rows = []
    events_rows = []
    os.makedirs("outputs", exist_ok=True)
    for q in queries:
        r, e = run_one(q)
        metrics_rows.extend(r)
        events_rows.extend(e)
    mdf = pd.DataFrame(metrics_rows)
    edf = pd.DataFrame(events_rows)
    mdf.to_csv("outputs/metrics.csv", index=False)
    edf.to_csv("outputs/events.csv", index=False)
    summary = mdf.groupby("engine").agg({
        "response_time_ms":"median",
        "accuracy":"mean",
        "coverage":"sum",
        "source_diversity":"sum",
        "freshness_ok":"sum"
    }).reset_index().sort_values(["accuracy","coverage"], ascending=[False, False])
    lines = ["# Benchmark Summary", ""]
    for _, row in summary.iterrows():
        lines.append(f"Engine {row['engine']}  median response time {int(row['response_time_ms'])} ms  mean accuracy {row['accuracy']:.2f}  total coverage {int(row['coverage'])}  freshness hits {int(row['freshness_ok'])}")
    with open("outputs/metrics_summary.md","w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    main()

