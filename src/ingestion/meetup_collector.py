"""
Meetup API data collector

This module handles collecting event data from Meetup's API.
Note: Meetup requires OAuth 2.0 authentication which is more complex than Eventbrite.
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


class MeetupCollector(BaseCollector):
    """Collector for Meetup events"""
    
    def __init__(self, api_key: str):
        super().__init__(
            source_name="meetup",
            api_key=api_key,
            rate_limit=200  # Meetup allows 200 requests/hour
        )
        self.base_url = "https://api.meetup.com"
        self.logger = logging.getLogger("collector.meetup")
    
    def collect_events(self, city: str, start_date: datetime, end_date: datetime) -> CollectionResult:
        """
        Collect events from Meetup for a specific city and date range
        
        Args:
            city: City name to search for events
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CollectionResult with collected data
        """
        self.logger.info(f"Starting Meetup collection for {city}")
        
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
        city_names = city_config.meetup_names
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
        
        # Remove duplicates
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
        Search for events using Meetup API
        
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
                'key': self.api_key,
                'city': city,
                'country': 'US',  # We'll make this configurable later
                'time': f"{int(start_date.timestamp() * 1000)},{int(end_date.timestamp() * 1000)}",  # Meetup uses milliseconds
                'category': '34',  # Technology category
                'page': '50',  # Max events per page
                'status': 'upcoming',
                'fields': 'event_hosts,featured_photo'
            }
            
            # Make search request
            url = f"{self.base_url}/find/upcoming_events"
            response_data = self.make_request(url, params=params)
            api_calls += 1
            
            if not response_data:
                errors.append(f"Failed to get events for {city}")
                return {'events': [], 'errors': errors, 'api_calls': api_calls}
            
            # Process events
            events.extend(self._process_events_page(response_data))
            
            # Note: Meetup's find/upcoming_events doesn't support pagination the same way
            # We might need to make additional requests for more events if needed
            
        except Exception as e:
            errors.append(f"Error searching events for {city}: {str(e)}")
            self.logger.error(f"Meetup search error: {e}")
        
        return {
            'events': events,
            'errors': errors,
            'api_calls': api_calls
        }
    
    def _process_events_page(self, events_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process events from Meetup API response
        
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
        Extract and normalize event information from Meetup API response
        
        Args:
            event_data: Raw event data from Meetup
            
        Returns:
            Normalized event data
        """
        # Extract basic information
        event_id = event_data.get('id', '')
        name = event_data.get('name', '')
        description = event_data.get('description', '')
        
        # Extract dates (Meetup uses milliseconds)
        start_time_ms = event_data.get('time', 0)
        duration_ms = event_data.get('duration', 0)
        
        start_time = datetime.fromtimestamp(start_time_ms / 1000).isoformat() + 'Z'
        end_time = datetime.fromtimestamp((start_time_ms + duration_ms) / 1000).isoformat() + 'Z'
        
        # Extract venue information
        venue_data = event_data.get('venue', {})
        venue_name = venue_data.get('name', '')
        
        # Extract group information
        group_data = event_data.get('group', {})
        group_name = group_data.get('name', '')
        
        # Build normalized event
        event = {
            'id': f"meetup_{event_id}",
            'source_id': str(event_id),
            'source': 'meetup',
            'title': self.clean_text(name),
            'description': self.clean_text(description),
            'start_time': start_time,
            'end_time': end_time,
            'url': event_data.get('link', ''),
            
            # Location information
            'venue_name': venue_name,
            'venue_address': venue_data.get('address_1', ''),
            'city': venue_data.get('city', ''),
            'state': venue_data.get('state', ''),
            'country': venue_data.get('country', ''),
            'postal_code': venue_data.get('zip', ''),
            'latitude': venue_data.get('lat'),
            'longitude': venue_data.get('lon'),
            'is_online': not venue_data,  # If no venue, it's likely online
            
            # Event details
            'organizer_name': group_name,
            'capacity': event_data.get('rsvp_limit', 0),
            'current_attendees': event_data.get('yes_rsvp_count', 0),
            'price': 0.0,  # Meetup events are typically free
            'currency': 'USD',
            'language': 'en',
            
            # Classification (basic)
            'category': 'meetup',
            'tags': [tag.get('name', '') for tag in event_data.get('topics', [])],
            
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
            params = {
                'key': self.api_key,
                'sign': 'true'
            }
            
            # Make a simple request to test authentication
            url = f"{self.base_url}/2/groups"
            response_data = self.make_request(url, params=params)
            
            if response_data:
                self.logger.info("Meetup API connection successful")
                return True
            else:
                self.logger.error("Meetup API connection failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Meetup API test failed: {e}")
            return False
