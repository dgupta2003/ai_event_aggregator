"""
Event Data Normalizer

This module converts events from different sources (Eventbrite, Meetup, Luma, Partiful)
into the unified event schema.
"""

import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime

from .unified_schema import UnifiedEvent, EventSource, Location, Organizer

logger = logging.getLogger(__name__)


class EventNormalizer:
    """Converts platform-specific events to unified schema"""
    
    @staticmethod
    def generate_unified_id(source: str, source_id: str, url: str) -> str:
        """
        Generate a unique ID for an event
        
        Args:
            source: Event source (eventbrite, meetup, etc)
            source_id: Original ID from platform
            url: Event URL
            
        Returns:
            Unique unified ID
        """
        # Use source + source_id as primary key, fall back to URL hash
        if source_id:
            key = f"{source}_{source_id}"
        else:
            # For scraped events without IDs, use URL hash
            key = f"{source}_{hashlib.md5(url.encode()).hexdigest()[:12]}"
        
        return key
    
    @staticmethod
    def parse_datetime(dt_string: str) -> Optional[datetime]:
        """
        Parse various datetime formats to datetime object
        
        Args:
            dt_string: Date/time string in various formats
            
        Returns:
            datetime object or None
        """
        if not dt_string:
            return None
        
        try:
            # Handle ISO format with Z
            if dt_string.endswith('Z'):
                dt_string = dt_string.replace('Z', '+00:00')
            
            return datetime.fromisoformat(dt_string)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse datetime: {dt_string} - {e}")
            return None
    
    @classmethod
    def normalize(cls, raw_event: Dict[str, Any]) -> Optional[UnifiedEvent]:
        """
        Normalize an event from any source to unified schema
        
        Args:
            raw_event: Raw event data from collector
            
        Returns:
            UnifiedEvent or None if normalization fails
        """
        source = raw_event.get('source', 'unknown')
        
        try:
            if source == 'eventbrite':
                return cls._normalize_eventbrite(raw_event)
            elif source == 'meetup':
                return cls._normalize_meetup(raw_event)
            elif source == 'luma':
                return cls._normalize_luma(raw_event)
            elif source == 'partiful':
                return cls._normalize_partiful(raw_event)
            else:
                logger.warning(f"Unknown source: {source}")
                return None
        except Exception as e:
            logger.error(f"Error normalizing event from {source}: {e}")
            return None
    
    @classmethod
    def _normalize_eventbrite(cls, event: Dict[str, Any]) -> UnifiedEvent:
        """Normalize Eventbrite event"""
        source_id = event.get('source_id', '')
        url = event.get('url', '')
        
        # Parse dates
        start_time = cls.parse_datetime(event.get('start_time'))
        end_time = cls.parse_datetime(event.get('end_time'))
        collected_at = cls.parse_datetime(event.get('created_at'))
        
        # Build location
        location = Location(
            venue_name=event.get('venue_name'),
            address=event.get('venue_address'),
            city=event.get('city'),
            state=event.get('state'),
            country=event.get('country'),
            postal_code=event.get('postal_code'),
            latitude=event.get('latitude'),
            longitude=event.get('longitude'),
            is_online=event.get('is_online', False)
        )
        
        # Build organizer
        organizer = Organizer(
            name=event.get('organizer_name')
        )
        
        # Create unified event
        unified = UnifiedEvent(
            unified_id=cls.generate_unified_id('eventbrite', source_id, url),
            source=EventSource.EVENTBRITE,
            source_id=source_id,
            url=url,
            title=event.get('title', ''),
            description=event.get('description'),
            start_time=start_time,
            end_time=end_time,
            location=location,
            organizer=organizer,
            category=event.get('category'),
            tags=event.get('tags', []),
            capacity=event.get('capacity', 0) if event.get('capacity') else None,
            is_free=event.get('price', 0) == 0,
            price=event.get('price'),
            currency=event.get('currency', 'USD'),
            collected_at=collected_at
        )
        
        # Update status and quality
        unified.update_status()
        unified.calculate_quality_score()
        
        return unified
    
    @classmethod
    def _normalize_meetup(cls, event: Dict[str, Any]) -> UnifiedEvent:
        """Normalize Meetup event"""
        source_id = event.get('source_id', '')
        url = event.get('url', '')
        
        # Parse dates
        start_time = cls.parse_datetime(event.get('start_time'))
        end_time = cls.parse_datetime(event.get('end_time'))
        collected_at = cls.parse_datetime(event.get('created_at'))
        
        # Build location
        location = Location(
            venue_name=event.get('venue_name'),
            address=event.get('venue_address'),
            city=event.get('city'),
            state=event.get('state'),
            country=event.get('country'),
            postal_code=event.get('postal_code'),
            latitude=event.get('latitude'),
            longitude=event.get('longitude'),
            is_online=event.get('is_online', False)
        )
        
        # Build organizer (group name for Meetup)
        organizer = Organizer(
            name=event.get('organizer_name')
        )
        
        # Create unified event
        unified = UnifiedEvent(
            unified_id=cls.generate_unified_id('meetup', source_id, url),
            source=EventSource.MEETUP,
            source_id=source_id,
            url=url,
            title=event.get('title', ''),
            description=event.get('description'),
            start_time=start_time,
            end_time=end_time,
            location=location,
            organizer=organizer,
            category=event.get('category'),
            tags=event.get('tags', []),
            capacity=event.get('capacity'),
            current_attendees=event.get('current_attendees'),
            is_free=True,  # Meetup events are typically free
            price=event.get('price', 0.0),
            currency=event.get('currency', 'USD'),
            collected_at=collected_at
        )
        
        # Update status and quality
        unified.update_status()
        unified.calculate_quality_score()
        
        return unified
    
    @classmethod
    def _normalize_luma(cls, event: Dict[str, Any]) -> UnifiedEvent:
        """Normalize Luma event"""
        source_id = event.get('source_id', '')
        url = event.get('url', '')
        
        # Parse dates (Luma dates might be less structured)
        start_time = cls.parse_datetime(event.get('start_time'))
        end_time = cls.parse_datetime(event.get('end_time'))
        collected_at = cls.parse_datetime(event.get('created_at'))
        
        # Build location (Luma might have minimal location data)
        location = Location(
            venue_name=event.get('venue_name'),
            city=event.get('city'),
            is_online=not bool(event.get('venue_name'))  # Assume online if no venue
        )
        
        # Build organizer
        organizer = Organizer(
            name=event.get('organizer_name')
        )
        
        # Create unified event
        unified = UnifiedEvent(
            unified_id=cls.generate_unified_id('luma', source_id, url),
            source=EventSource.LUMA,
            source_id=source_id,
            url=url,
            title=event.get('title', ''),
            description=event.get('description'),
            start_time=start_time,
            end_time=end_time,
            location=location,
            organizer=organizer,
            category=event.get('category'),
            tags=event.get('tags', []),
            collected_at=collected_at
        )
        
        # Update status and quality
        unified.update_status()
        unified.calculate_quality_score()
        
        return unified
    
    @classmethod
    def _normalize_partiful(cls, event: Dict[str, Any]) -> UnifiedEvent:
        """Normalize Partiful event"""
        source_id = event.get('source_id', '')
        url = event.get('url', '')
        
        # Parse dates
        start_time = cls.parse_datetime(event.get('start_time'))
        end_time = cls.parse_datetime(event.get('end_time'))
        collected_at = cls.parse_datetime(event.get('created_at'))
        
        # Build location
        location = Location(
            venue_name=event.get('venue_name'),
            city=event.get('city')
        )
        
        # Build organizer
        organizer = Organizer(
            name=event.get('organizer_name')
        )
        
        # Create unified event
        unified = UnifiedEvent(
            unified_id=cls.generate_unified_id('partiful', source_id, url),
            source=EventSource.PARTIFUL,
            source_id=source_id,
            url=url,
            title=event.get('title', ''),
            description=event.get('description'),
            start_time=start_time,
            end_time=end_time,
            location=location,
            organizer=organizer,
            category=event.get('category'),
            tags=event.get('tags', []),
            collected_at=collected_at
        )
        
        # Update status and quality
        unified.update_status()
        unified.calculate_quality_score()
        
        return unified
    
    @classmethod
    def normalize_batch(cls, raw_events: list[Dict[str, Any]]) -> list[UnifiedEvent]:
        """
        Normalize a batch of events
        
        Args:
            raw_events: List of raw event dictionaries
            
        Returns:
            List of UnifiedEvent objects
        """
        normalized = []
        failed = 0
        
        for raw_event in raw_events:
            unified = cls.normalize(raw_event)
            if unified and unified.is_valid():
                normalized.append(unified)
            else:
                failed += 1
        
        logger.info(f"Normalized {len(normalized)} events, {failed} failed validation")
        return normalized

