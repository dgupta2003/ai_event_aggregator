import os
import json
from datetime import datetime

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.search import SearchParameters

# Your API key
client = Client(api_key=os.getenv("XAI_API_KEY"))

# Create chat with live search
chat = client.chat.create(
    model="grok-3",  # Free model with search
    search_parameters=SearchParameters(
        mode="auto",  # Auto web/X search
        from_date=datetime(2025, 11, 5),  # Tomorrow only
        to_date=datetime(2025, 11, 6),    # Narrow to Nov 5
        return_citations=True,
    ),
)

# Simple query for tech events in Austin tomorrow
chat.append(user("""
Search live for all tech events (conferences, meetups, workshops, networking) in Austin, TX on November 5, 2025.
Use Eventbrite, Meetup, Luma, etc. for real results.
Return ONLY JSON: {"events": [{"name": str, "time": str, "location": str, "description": str (brief), "url": str}, ...]}.
Aim for 20+ if available.
No other text.
"""))

# Get response
response = chat.sample()

# Clean JSON
content = response.content.strip()
if content.startswith("```json"):
    content = content.replace("```json", "").replace("```", "").strip()

# Parse events
try:
    data = json.loads(content)
    events = data.get("events", [])
except json.JSONDecodeError:
    events = []  # Graceful fail

# Simple citations (skip protobuf hassle)
citations = []  # Add manually if needed; focus on events

# Save
output = {
    "query": "Tech events in Austin on Nov 5, 2025",
    "events": events,
    "run_at": datetime.now().isoformat()
}

with open("austin_tech_events.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Found {len(events)} events. Saved to austin_tech_events.json")
print(json.dumps(output, indent=2)[:1000])  # Preview
