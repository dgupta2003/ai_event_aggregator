# Expected Output Specifications

## Output Formats

### 1. CSV Export
**File**: `data/processed/events_YYYY-MM-DD.csv`

**Columns**:
```
id,title,description,start_time,end_time,source,url,venue_name,city,state,country,
latitude,longitude,is_online,category,subcategory,tags,is_tech_related,confidence_score,
price,currency,capacity,current_attendees,organizer_name,created_at,updated_at
```

**Sample Row**:
```csv
evt_001,"AI Meetup NYC","Join us for an evening of AI discussions",2025-10-15T18:00:00Z,2025-10-15T20:00:00Z,eventbrite,https://eventbrite.com/e/ai-meetup-nyc,Tech Hub NYC,New York,NY,US,40.7128,-74.0060,false,meetup,ai,"python,ai,networking",true,0.95,0.00,USD,100,45,NYC AI Group,2025-10-01T10:00:00Z,2025-10-01T10:00:00Z
```

### 2. JSON API Response
**Endpoint**: `/api/v1/events`

**Response Format**:
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": "evt_001",
        "title": "AI Meetup NYC",
        "description": "Join us for an evening of AI discussions",
        "start_time": "2025-10-15T18:00:00Z",
        "end_time": "2025-10-15T20:00:00Z",
        "source": "eventbrite",
        "url": "https://eventbrite.com/e/ai-meetup-nyc",
        "location": {
          "venue_name": "Tech Hub NYC",
          "venue_address": "123 Tech Street",
          "city": "New York",
          "state": "NY",
          "country": "US",
          "latitude": 40.7128,
          "longitude": -74.0060,
          "is_online": false
        },
        "classification": {
          "category": "meetup",
          "subcategory": "ai",
          "tags": ["python", "ai", "networking"],
          "is_tech_related": true,
          "confidence_score": 0.95,
          "audience_level": "intermediate"
        },
        "details": {
          "organizer_name": "NYC AI Group",
          "organizer_email": "contact@nycaigroup.com",
          "capacity": 100,
          "current_attendees": 45,
          "price": 0.00,
          "currency": "USD",
          "registration_required": true,
          "language": "en"
        },
        "metadata": {
          "created_at": "2025-10-01T10:00:00Z",
          "updated_at": "2025-10-01T10:00:00Z",
          "data_quality_score": 0.92
        }
      }
    ],
    "pagination": {
      "total": 150,
      "page": 1,
      "per_page": 20,
      "total_pages": 8
    },
    "filters_applied": {
      "city": "New York",
      "category": "meetup",
      "date_range": "2025-10-01 to 2025-10-31",
      "tech_related_only": true
    }
  },
  "meta": {
    "api_version": "v1",
    "generated_at": "2025-10-01T10:00:00Z",
    "data_sources": ["eventbrite", "meetup", "luma", "partiful"],
    "total_sources_checked": 4,
    "sources_with_data": 3
  }
}
```

### 3. Streamlit Dashboard
**Features**:
- **Event List View**: Sortable table with all events
- **Map View**: Interactive map showing event locations
- **Filter Panel**: 
  - City selector (dropdown)
  - Date range picker
  - Category filters (checkboxes)
  - Tech-related toggle
  - Price range slider
  - Source checkboxes
- **Search Bar**: Full-text search across titles and descriptions
- **Event Details**: Modal popup with full event information
- **Export Options**: Download as CSV/JSON
- **Statistics Panel**: Event counts by source, category, etc.

### 4. Database Schema
**Table**: `events`

```sql
CREATE TABLE events (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    source VARCHAR(20) NOT NULL CHECK (source IN ('eventbrite', 'meetup', 'luma', 'partiful')),
    source_id VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    
    -- Location fields
    venue_name VARCHAR(200),
    venue_address TEXT,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    country VARCHAR(10) NOT NULL,
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_online BOOLEAN DEFAULT FALSE,
    online_url TEXT,
    
    -- Classification fields
    category VARCHAR(50),
    subcategory VARCHAR(50),
    tags TEXT[], -- PostgreSQL array
    is_tech_related BOOLEAN DEFAULT FALSE,
    confidence_score DECIMAL(3, 2),
    audience_level VARCHAR(20),
    
    -- Additional fields
    organizer_name VARCHAR(200),
    organizer_email VARCHAR(200),
    capacity INTEGER,
    current_attendees INTEGER,
    price DECIMAL(10, 2),
    currency VARCHAR(3),
    registration_required BOOLEAN DEFAULT FALSE,
    language VARCHAR(10),
    image_url TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_quality_score DECIMAL(3, 2)
);

-- Indexes for performance
CREATE INDEX idx_events_city ON events(city);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_source ON events(source);
CREATE INDEX idx_events_tech_related ON events(is_tech_related);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_location ON events(latitude, longitude);
```

## API Endpoints Specification

### GET /api/v1/events
**Query Parameters**:
- `city` (optional): Filter by city
- `category` (optional): Filter by category
- `subcategory` (optional): Filter by subcategory
- `source` (optional): Filter by data source
- `tech_related_only` (optional): Boolean, show only tech events
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `price_min` (optional): Minimum price
- `price_max` (optional): Maximum price
- `is_online` (optional): Boolean, online events only
- `search` (optional): Full-text search
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

### GET /api/v1/events/{event_id}
**Response**: Single event details

### GET /api/v1/cities
**Response**: List of supported cities

### GET /api/v1/stats
**Response**: Statistics about the dataset

## Data Quality Metrics

### Completeness Score
- Required fields present: 100%
- Optional fields present: 60%+
- Geographic data complete: 80%+
- Contact information: 40%+

### Accuracy Score
- Valid URLs: 95%+
- Valid dates: 100%
- Valid coordinates: 90%+
- Valid emails: 85%+

### Freshness Score
- Data updated within 24 hours: 100%
- Events within target timeframe: 95%+
- Duplicates removed: 100%

## Performance Targets

### API Response Times
- Single event lookup: < 100ms
- Event list (20 items): < 500ms
- Event list (100 items): < 1000ms
- Full-text search: < 2000ms

### Data Processing
- Daily ingestion: < 30 minutes
- Real-time updates: < 5 minutes
- Database queries: < 500ms average

### Storage Requirements
- Raw data: ~1GB per month per city
- Processed data: ~500MB per month per city
- Database size: ~2GB per year for NYC
