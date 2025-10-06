"""
Eventbrite API data collector

This module handles collecting event data from Eventbrite's API.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests

from .base_collector import BaseCollector, CollectionResult
try:
    from ..requirements.cities_config import get_city_config
except ImportError:
    from requirements.cities_config import get_city_config


class EventbriteCollector(BaseCollector):
    """Collector for Eventbrite events"""
    
    def __init__(self, api_key: str):
        super().__init__(
            source_name="eventbrite",
            api_key=api_key,
            rate_limit=1000  # Eventbrite allows 1000 requests/hour
        )
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.logger = logging.getLogger("collector.eventbrite")
    
    def collect_events(self, city: str, start_date: datetime, end_date: datetime) -> CollectionResult:
        """
        Collect events from Eventbrite for a specific city and date range
        
        Args:
            city: City name to search for events
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CollectionResult with collected data
        """
        self.logger.info(f"Starting Eventbrite collection for {city}")
        
        # Get city configuration
        city_config = get_city_config(city)
        if not city_config:
            return CollectionResult(
                success=False,
                data=[],
                errors=[f"City '{city}' not supported"],
                source=self.source_name,
                city=city,
                collected_at=datetime.now()
            )
        
        all_events = []
        errors = []
        api_calls_made = 0
        
        # Try different city name variations
        city_names = city_config.eventbrite_names
        if city not in city_names:
            city_names.append(city)
        
        for city_variant in city_names:
            self.logger.info(f"Searching for events in '{city_variant}'")
            
            # Search for events
            events_result = self._search_events(city_variant, start_date, end_date)
            api_calls_made += events_result['api_calls']
            
            if events_result['events']:
                all_events.extend(events_result['events'])
                self.logger.info(f"Found {len(events_result['events'])} events for '{city_variant}'")
            
            if events_result['errors']:
                errors.extend(events_result['errors'])
        
        # Remove duplicates based on event ID
        unique_events = self._deduplicate_events(all_events)
        
        # Save raw data
        filepath = self.save_raw_data(unique_events, city)
        
        result = CollectionResult(
            success=len(unique_events) > 0,
            data=unique_events,
            errors=errors,
            source=self.source_name,
            city=city,
            collected_at=datetime.now(),
            total_events=len(unique_events),
            api_calls_made=api_calls_made
        )
        
        self.log_collection_stats(result)
        return result
    
    def _search_events(self, city: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Search for events using Eventbrite API
        
        Args:
            city: City name to search
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with events, errors, and API call count
        """
        events = []
        errors = []
        api_calls = 0
        
        try:
            # Build search parameters
            params = {
                'location.address': city,
                'location.within': '50mi',  # 50 mile radius
                'start_date.range_start': start_date.isoformat(),
                'start_date.range_end': end_date.isoformat(),
                'categories': '102',  # Science & Technology category
                'expand': 'venue,organizer',
                'page_size': 50,  # Max events per page
            }
            
            # Add API key to headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Make initial search request
            url = f"{self.base_url}/events/search"
            response_data = self.make_request(url, params=params, headers=headers)
            api_calls += 1
            
            if not response_data:
                errors.append(f"Failed to get events for {city}")
                return {'events': [], 'errors': errors, 'api_calls': api_calls}
            
            # Process events from first page
            events.extend(self._process_events_page(response_data.get('events', [])))
            
            # Handle pagination
            pagination = response_data.get('pagination', {})
            has_more_items = pagination.get('has_more_items', False)
            page_count = pagination.get('page_count', 1)
            
            self.logger.info(f"Found {len(events)} events on first page. Total pages: {page_count}")
            
            # Get additional pages if needed
            current_page = 1
            while has_more_items and current_page < 10:  # Limit to 10 pages max
                current_page += 1
                
                # Add page parameter
                params['page'] = current_page
                
                page_data = self.make_request(url, params=params, headers=headers)
                api_calls += 1
                
                if page_data:
                    events.extend(self._process_events_page(page_data.get('events', [])))
                    pagination = page_data.get('pagination', {})
                    has_more_items = pagination.get('has_more_items', False)
                else:
                    errors.append(f"Failed to get page {current_page} for {city}")
                    break
                
                self.logger.info(f"Processed page {current_page}, total events: {len(events)}")
        
        except Exception as e:
            errors.append(f"Error searching events for {city}: {str(e)}")
            self.logger.error(f"Eventbrite search error: {e}")
        
        return {
            'events': events,
            'errors': errors,
            'api_calls': api_calls
        }
    
    def _process_events_page(self, events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a page of events from Eventbrite API
        
        Args:
            events_data: Raw events data from API
            
        Returns:
            List of processed events
        """
        processed_events = []
        
        for event_data in events_data:
            try:
                # Extract event information
                event = self._extract_event_info(event_data)
                
                # Validate event data
                if self.validate_event_data(event):
                    processed_events.append(event)
                else:
                    self.logger.warning(f"Skipping invalid event: {event.get('title', 'Unknown')}")
            
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                continue
        
        return processed_events
    
    def _extract_event_info(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and normalize event information from Eventbrite API response
        
        Args:
            event_data: Raw event data from Eventbrite
            
        Returns:
            Normalized event data
        """
        # Extract basic information
        event_id = event_data.get('id', '')
        name = event_data.get('name', {}).get('text', '')
        description = event_data.get('description', {}).get('text', '')
        
        # Extract dates
        start_time = event_data.get('start', {}).get('utc', '')
        end_time = event_data.get('end', {}).get('utc', '')
        
        # Extract venue information
        venue_data = event_data.get('venue', {})
        venue_name = venue_data.get('name', '')
        venue_address = venue_data.get('address', {})
        
        # Extract organizer information
        organizer_data = event_data.get('organizer', {})
        organizer_name = organizer_data.get('name', '')
        
        # Extract pricing information
        ticket_availability = event_data.get('ticket_availability', {})
        is_free = ticket_availability.get('is_free', True)
        
        # Build normalized event
        event = {
            'id': f"eventbrite_{event_id}",
            'source_id': event_id,
            'source': 'eventbrite',
            'title': self.clean_text(name),
            'description': self.clean_text(description),
            'start_time': start_time,
            'end_time': end_time,
            'url': event_data.get('url', ''),
            
            # Location information
            'venue_name': venue_name,
            'venue_address': venue_address.get('address_1', ''),
            'city': venue_address.get('city', ''),
            'state': venue_address.get('region', ''),
            'country': venue_address.get('country', ''),
            'postal_code': venue_address.get('postal_code', ''),
            'latitude': venue_data.get('latitude'),
            'longitude': venue_data.get('longitude'),
            'is_online': event_data.get('online_event', False),
            
            # Event details
            'organizer_name': organizer_name,
            'capacity': event_data.get('capacity', 0),
            'price': 0.0 if is_free else None,  # We'd need to get actual price from tickets
            'currency': 'USD',
            'language': event_data.get('locale', 'en'),
            
            # Classification (basic)
            'category': 'technology',  # We'll improve this with AI later
            'tags': [],  # We'll extract these later
            
            # Metadata
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        return event
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate events based on source ID
        
        Args:
            events: List of events
            
        Returns:
            List of unique events
        """
        seen_ids = set()
        unique_events = []
        
        for event in events:
            event_id = event.get('source_id', '')
            if event_id and event_id not in seen_ids:
                seen_ids.add(event_id)
                unique_events.append(event)
        
        self.logger.info(f"Deduplication: {len(events)} -> {len(unique_events)} events")
        return unique_events
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Make a simple request to test authentication
            url = f"{self.base_url}/users/me"
            response_data = self.make_request(url, headers=headers)
            
            if response_data:
                self.logger.info("Eventbrite API connection successful")
                return True
            else:
                self.logger.error("Eventbrite API connection failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Eventbrite API test failed: {e}")
            return False
