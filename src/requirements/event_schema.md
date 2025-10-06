# Standardized Event Data Schema

## Core Event Fields

### Required Fields
```json
{
  "id": "unique_event_id",
  "title": "Event Title",
  "description": "Full event description",
  "start_time": "2025-10-15T18:00:00Z",
  "end_time": "2025-10-15T20:00:00Z",
  "source": "eventbrite|meetup|luma|partiful",
  "source_id": "original_id_from_source",
  "url": "https://eventbrite.com/e/...",
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-01T10:00:00Z"
}
```

### Location Fields
```json
{
  "venue_name": "Tech Hub NYC",
  "venue_address": "123 Tech Street",
  "city": "New York",
  "state": "NY",
  "country": "US",
  "postal_code": "10001",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "is_online": false,
  "online_url": null
}
```

### Classification Fields
```json
{
  "category": "conference|meetup|workshop|hackathon|networking",
  "subcategory": "ai|web_dev|data_science|startup|blockchain",
  "tags": ["python", "machine-learning", "networking"],
  "is_tech_related": true,
  "confidence_score": 0.95,
  "audience_level": "beginner|intermediate|advanced|all"
}
```

### Additional Fields
```json
{
  "organizer_name": "NYC Tech Meetup",
  "organizer_email": "contact@example.com",
  "capacity": 100,
  "current_attendees": 45,
  "price": 0.00,
  "currency": "USD",
  "registration_required": true,
  "language": "en",
  "image_url": "https://example.com/image.jpg"
}
```

## Data Type Definitions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | String | Unique identifier | "evt_001" |
| title | String | Event title | "AI Meetup NYC" |
| description | Text | Full description | "Join us for..." |
| start_time | DateTime | ISO 8601 format | "2025-10-15T18:00:00Z" |
| end_time | DateTime | ISO 8601 format | "2025-10-15T20:00:00Z" |
| source | Enum | Data source platform | "eventbrite" |
| source_id | String | Original ID from source | "123456789" |
| url | String | Event page URL | "https://..." |
| venue_name | String | Venue or location name | "Tech Hub" |
| city | String | City name | "New York" |
| state | String | State/Province code | "NY" |
| country | String | Country code | "US" |
| latitude | Float | GPS latitude | 40.7128 |
| longitude | Float | GPS longitude | -74.0060 |
| is_online | Boolean | Virtual event flag | false |
| category | Enum | Event category | "meetup" |
| subcategory | Enum | Event subcategory | "ai" |
| tags | Array | Event tags | ["python", "ai"] |
| is_tech_related | Boolean | AI classification result | true |
| confidence_score | Float | AI confidence (0-1) | 0.95 |
| price | Float | Event price | 0.00 |
| currency | String | Currency code | "USD" |
| capacity | Integer | Max attendees | 100 |
| current_attendees | Integer | Current RSVPs | 45 |

## Data Validation Rules

### Required Field Validation
- All required fields must be present and non-empty
- start_time must be before end_time
- URL must be valid and accessible
- Source must be one of: eventbrite, meetup, luma, partiful

### Data Quality Checks
- Title length: 5-200 characters
- Description length: 10-5000 characters
- Price must be >= 0
- Capacity must be > 0
- Coordinates must be valid lat/lng pairs
- Dates must be in the future (for upcoming events)

### Deduplication Logic
Events are considered duplicates if:
- Same source + source_id
- OR (same title + same start_time + same city)
- OR (same URL)

## Platform-Specific Mappings

### Eventbrite → Standard Schema
```python
{
  "id": f"eventbrite_{event['id']}",
  "title": event["name"]["text"],
  "description": event["description"]["text"],
  "start_time": event["start"]["utc"],
  "end_time": event["end"]["utc"],
  "source": "eventbrite",
  "source_id": event["id"],
  "url": event["url"],
  "venue_name": event["venue"]["name"],
  "city": event["venue"]["address"]["city"],
  "state": event["venue"]["address"]["region"],
  "country": event["venue"]["address"]["country"],
  "latitude": event["venue"]["latitude"],
  "longitude": event["venue"]["longitude"],
  "is_online": event["online_event"],
  "capacity": event["capacity"],
  "price": event["ticket_availability"]["minimum_ticket_price"]["major_value"]
}
```

### Meetup → Standard Schema
```python
{
  "id": f"meetup_{event['id']}",
  "title": event["name"],
  "description": event["description"],
  "start_time": event["time"],
  "end_time": event["time"] + event["duration"],
  "source": "meetup",
  "source_id": event["id"],
  "url": event["link"],
  "venue_name": event["venue"]["name"],
  "city": event["venue"]["city"],
  "state": event["venue"]["state"],
  "country": event["venue"]["country"],
  "latitude": event["venue"]["lat"],
  "longitude": event["venue"]["lon"],
  "is_online": event["venue"] is None,
  "capacity": event.get("rsvp_limit", 0),
  "current_attendees": event["yes_rsvp_count"]
}
```
