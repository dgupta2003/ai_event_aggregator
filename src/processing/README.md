# Event Processing Pipeline

This module handles the complete event data processing pipeline, transforming raw event data from multiple sources into clean, deduplicated, enriched, and validated events.

## 🏗️ Architecture

The processing pipeline consists of 5 main stages:

```
Raw Data → Normalize → Deduplicate → Enrich → Validate → Processed Data
```

## 📦 Components

### 1. **UnifiedEvent Schema** (`unified_schema.py`)

The core data model that all events are normalized to:

```python
from src.processing import UnifiedEvent, EventSource, EventStatus

event = UnifiedEvent(
    unified_id="eventbrite_123456",
    source=EventSource.EVENTBRITE,
    source_id="123456",
    title="AI Meetup NYC",
    start_time=datetime.now(),
    ...
)
```

**Key Features:**
- Single unified schema for all event sources
- Location and Organizer sub-models
- Quality score calculation (0-1)
- Auto status updates (upcoming/ongoing/past)
- Helper methods: `days_until_event()`, `is_this_week()`, `is_valid()`

### 2. **EventNormalizer** (`normalizer.py`)

Converts platform-specific events to unified schema:

```python
from src.processing import EventNormalizer

# Normalize single event
unified_event = EventNormalizer.normalize(raw_event)

# Normalize batch
unified_events = EventNormalizer.normalize_batch(raw_events)
```

**Supports:**
- Eventbrite events
- Meetup events  
- Luma events
- Partiful events

**Handles:**
- Date/time parsing (ISO, milliseconds, various formats)
- Location extraction and normalization
- Organizer information mapping
- Tags and category mapping

### 3. **EventDeduplicator** (`deduplicator.py`)

Identifies and merges duplicate events from different sources:

```python
from src.processing import EventDeduplicator

# Find duplicates
duplicates = EventDeduplicator.deduplicate(events)
```

**Matching Logic:**
- Title similarity (85% threshold)
- Time window (within 2 hours)
- Venue similarity (75% threshold or coordinates)
- Smart merging: keeps event with highest quality, fills missing fields from duplicates

**Example:**
```
"AI Workshop @ Tech Hub" (Eventbrite) 
    + "AI Workshop at Tech Hub" (Meetup)
    → Merged event with best data from both
```

### 4. **EventEnricher** (`enricher.py`)

Adds missing information and extracts metadata:

```python
from src.processing import EventEnricher

# Enrich single event
enriched_event = EventEnricher.enrich(event)

# Enrich batch
enriched_events = EventEnricher.enrich_batch(events)
```

**Enrichment Steps:**
- **Keyword Extraction**: Finds tech keywords in title/description
- **Category Inference**: AI/ML, Data Science, Web Dev, Blockchain, etc.
- **Tech Relevance Check**: Flags tech-related events with confidence score
- **Location Normalization**: Cleans venue names, standardizes state codes
- **Tag Enhancement**: Merges existing tags with extracted keywords (max 20)

### 5. **EventValidator** (`validator.py`)

Validates and filters events based on quality criteria:

```python
from src.processing import EventValidator

# Validate events
valid_events, rejected = EventValidator.filter_events(
    events,
    include_past=False,
    min_quality=0.3
)
```

**Validation Checks:**
- ✅ Title length (5-200 chars)
- ✅ No spam patterns (click here, buy now, etc.)
- ✅ Valid dates (not too far in future)
- ✅ Has location info (venue/city or coordinates)
- ✅ Quality score above threshold
- ✅ Not in the past (configurable)

**Quality Score Factors:**
- Title & description completeness
- Location data (venue, city, coordinates)
- Time information (start/end)
- Organizer info
- Tags & categories
- Capacity/attendance data

### 6. **ProcessorManager** (`processor_manager.py`)

Orchestrates the complete pipeline:

```python
from src.processing import ProcessorManager

processor = ProcessorManager()

# Process all raw data
processed_events = processor.process_pipeline(
    city="New York City",
    include_past=False,
    min_quality=0.3,
    save_output=True
)

# Or process a single file
processed = processor.process_file("data/raw/eventbrite_nyc.json")
```

## 🚀 Quick Start

### Run the Complete Pipeline

```bash
# Activate virtual environment
source venv/bin/activate

# Run the processor
python -m src.processing.processor_manager

# Or use the test script
python test_processing_pipeline.py
```

### Use as a Module

```python
from src.processing import ProcessorManager

# Initialize
processor = ProcessorManager()

# Run pipeline
events = processor.process_pipeline(
    city="New York City",
    include_past=False,
    min_quality=0.3
)

# Access stats
print(processor.stats)
# {
#     'raw_events': 100,
#     'normalized': 90,
#     'deduplicated': 75,
#     'enriched': 75,
#     'validated': 60,
#     'rejected': 15
# }
```

## 📊 Pipeline Statistics

Typical processing results:

| Stage | Input | Output | Notes |
|-------|-------|--------|-------|
| **Raw Data** | 100 events | - | From 4 sources |
| **Normalize** | 100 events | 85 events | 15 fail validation (missing fields) |
| **Deduplicate** | 85 events | 70 events | ~18% duplication rate |
| **Enrich** | 70 events | 70 events | Tags, categories, tech flags added |
| **Validate** | 70 events | 55 events | 15 rejected (past/spam/low quality) |
| **Final** | - | 55 events | Clean, ready for database |

## 📁 Output Format

Processed events are saved to `data/processed/`:

```json
{
  "metadata": {
    "processed_at": "2025-10-13T12:00:00",
    "total_events": 55,
    "city": "New York City",
    "pipeline_stats": {
      "raw_events": 100,
      "normalized": 85,
      "deduplicated": 70,
      "enriched": 70,
      "validated": 55,
      "rejected": 15
    }
  },
  "events": [
    {
      "unified_id": "eventbrite_123456",
      "source": "eventbrite",
      "title": "AI Meetup NYC",
      "start_time": "2025-10-20T18:00:00+00:00",
      "location": {
        "venue_name": "Tech Hub",
        "city": "New York",
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "quality_score": 0.85,
      "is_tech_related": true,
      "ai_confidence": 0.8,
      "category": "ai_ml",
      "tags": ["ai", "machine learning", "networking"],
      "status": "upcoming"
    }
  ]
}
```

## 🔍 Quality Score Breakdown

The quality score (0-1) is calculated based on:

| Factor | Points | Total |
|--------|--------|-------|
| Title (>5 chars) | 2.0 | 2.0 |
| Description (>50 chars) | 1.5 | 1.5 |
| Start time present | 2.0 | 2.0 |
| Venue name | 1.0 | 1.0 |
| City | 1.0 | 1.0 |
| Coordinates (lat/lng) | 1.0 | 1.0 |
| End time | 0.5 | 0.5 |
| Organizer name | 1.0 | 1.0 |
| Tags (>0) | 1.0 | 1.0 |
| Category | 0.5 | 0.5 |
| Capacity/attendance | 0.5 | 0.5 |
| Pricing info | 0.5 | 0.5 |
| Tech classification | 1.0 | 1.0 |
| **Total** | | **15.0** |

**Score = Total Points / 15.0**

Quality Ranges:
- 0.8-1.0: Excellent (complete data)
- 0.6-0.8: Good (most fields present)
- 0.4-0.6: Fair (basic info)
- 0.2-0.4: Poor (minimal data)
- 0.0-0.2: Very Poor (nearly empty)

## 🧪 Testing

```bash
# Run full test suite
python test_processing_pipeline.py

# Test individual components
python -c "
from src.processing import EventNormalizer, EventDeduplicator
# Your test code here
"
```

## 🛠️ Configuration

Adjust thresholds in each module:

```python
# Deduplicator
EventDeduplicator.TITLE_SIMILARITY_THRESHOLD = 0.85  # Default: 0.85
EventDeduplicator.TIME_WINDOW_HOURS = 2  # Default: 2 hours

# Validator
EventValidator.MIN_QUALITY_SCORE = 0.3  # Default: 0.3
EventValidator.MIN_TITLE_LENGTH = 5  # Default: 5 chars
```

## 📈 Next Steps

After processing, you can:

1. **Load into Database** (Phase 5)
   ```python
   # Coming soon: database integration
   ```

2. **AI Classification** (Phase 4)
   ```python
   # Use OpenAI to further classify events
   ```

3. **Serve via API** (Phase 6)
   ```python
   # FastAPI endpoints for frontend
   ```

## 🐛 Common Issues

**Issue: All events rejected as "past"**
```python
# Include past events for testing
processor.process_pipeline(include_past=True)
```

**Issue: Low quality scores**
```python
# Lower quality threshold
processor.process_pipeline(min_quality=0.2)
```

**Issue: Too many duplicates**
```python
# Adjust similarity threshold
EventDeduplicator.TITLE_SIMILARITY_THRESHOLD = 0.9  # More strict
```

---

Built with ❤️ as part of the AI Events Aggregator project

