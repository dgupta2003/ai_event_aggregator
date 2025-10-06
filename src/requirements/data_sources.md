# Data Sources Analysis

## Target Platforms

### 1. Eventbrite
- **API Available**: ✅ Yes
- **Rate Limits**: 1000 requests/hour
- **Authentication**: API Key required
- **Search Endpoint**: `/events/search`
- **Geographic Support**: Global (city, country, state)
- **Date Filtering**: ✅ Start/end dates
- **Category Filtering**: ✅ Multiple categories available
- **Data Fields Available**:
  - Event ID, Title, Description
  - Start/End Date/Time
  - Venue (name, address, city, country)
  - Category, Subcategory
  - Organizer info
  - Ticket pricing
  - Event capacity
  - Online/Offline indicator

### 2. Meetup
- **API Available**: ✅ Yes (OAuth 2.0)
- **Rate Limits**: 200 requests/hour
- **Authentication**: OAuth 2.0 (more complex setup)
- **Search Endpoint**: `/find/upcoming_events`
- **Geographic Support**: Global (city, country, state)
- **Date Filtering**: ✅ Start/end dates
- **Category Filtering**: ✅ Group categories
- **Data Fields Available**:
  - Event ID, Name, Description
  - Start/End Date/Time
  - Venue (name, address, city, country)
  - Group info (name, category, member count)
  - Event capacity
  - RSVP count
  - Online/Offline indicator

### 3. Luma
- **API Available**: ❌ No (requires scraping)
- **Scraping Method**: Apify Actor or Playwright
- **Geographic Support**: Global (city-based search)
- **Date Filtering**: Limited (mostly upcoming events)
- **Category Filtering**: Limited
- **Data Fields Available**:
  - Event Title, Description
  - Date/Time
  - Location (city, venue)
  - Organizer info
  - Event type (workshop, meetup, etc.)

### 4. Partiful
- **API Available**: ❌ No (requires scraping)
- **Scraping Method**: Apify Actor or Playwright
- **Geographic Support**: Global (city-based search)
- **Date Filtering**: Limited
- **Category Filtering**: Limited
- **Data Fields Available**:
  - Event Name, Description
  - Date/Time
  - Location
  - Organizer info
  - Event capacity

## Geographic Coverage Strategy

### Supported Cities (Initial)
- **Tier 1**: New York, San Francisco, London, Toronto
- **Tier 2**: Los Angeles, Chicago, Boston, Seattle, Austin
- **Tier 3**: Any city with sufficient tech community

### City Data Requirements
Each city needs:
- **City Name**: Exact name used by each platform
- **Country Code**: ISO 3166-1 alpha-2 (US, CA, GB, etc.)
- **State/Province**: For US/Canada (NY, CA, ON, etc.)
- **Timezone**: For accurate date/time handling
- **Alternative Names**: Common variations (NYC vs New York City)

## Data Collection Strategy

### Priority Order
1. **Eventbrite** - Most reliable API, good geographic coverage
2. **Meetup** - Strong community focus, good for meetups
3. **Luma** - Emerging platform, good for smaller events
4. **Partiful** - Social events, good for networking

### Collection Frequency
- **Initial**: Full historical data for target month
- **Ongoing**: Daily updates for upcoming events
- **Cleanup**: Remove events older than 60 days
