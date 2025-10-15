"""
Event Deduplicator

This module identifies and handles duplicate events from different sources.
The same event can appear on Eventbrite, Meetup, Luma, etc. - we need to merge them.
"""

import logging
from typing import List, Dict, Set, Tuple
from datetime import timedelta
from difflib import SequenceMatcher

from .unified_schema import UnifiedEvent

logger = logging.getLogger(__name__)


class EventDeduplicator:
    """Identifies and merges duplicate events from different sources"""
    
    # Similarity thresholds
    TITLE_SIMILARITY_THRESHOLD = 0.85  # 85% similar titles
    TIME_WINDOW_HOURS = 2  # Events within 2 hours considered same time
    VENUE_SIMILARITY_THRESHOLD = 0.75  # 75% similar venue names
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score 0-1
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize text
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, text1, text2).ratio()
    
    @staticmethod
    def are_times_similar(event1: UnifiedEvent, event2: UnifiedEvent) -> bool:
        """
        Check if two events have similar start times
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            True if times are within threshold
        """
        if not event1.start_time or not event2.start_time:
            return False
        
        time_diff = abs((event1.start_time - event2.start_time).total_seconds() / 3600)
        return time_diff <= EventDeduplicator.TIME_WINDOW_HOURS
    
    @staticmethod
    def are_venues_similar(event1: UnifiedEvent, event2: UnifiedEvent) -> bool:
        """
        Check if two events have similar venues
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            True if venues are similar
        """
        # Both online
        if event1.location.is_online and event2.location.is_online:
            return True
        
        # One online, one not
        if event1.location.is_online != event2.location.is_online:
            return False
        
        # Compare venue names
        venue1 = event1.location.venue_name or ""
        venue2 = event2.location.venue_name or ""
        
        if not venue1 or not venue2:
            # If we have coordinates, compare those
            if (event1.location.latitude and event2.location.latitude and
                event1.location.longitude and event2.location.longitude):
                
                # Calculate rough distance (simplified)
                lat_diff = abs(event1.location.latitude - event2.location.latitude)
                lng_diff = abs(event1.location.longitude - event2.location.longitude)
                
                # Within ~0.01 degrees (~1km)
                return lat_diff < 0.01 and lng_diff < 0.01
            
            return False
        
        similarity = EventDeduplicator.calculate_text_similarity(venue1, venue2)
        return similarity >= EventDeduplicator.VENUE_SIMILARITY_THRESHOLD
    
    @classmethod
    def are_duplicates(cls, event1: UnifiedEvent, event2: UnifiedEvent) -> Tuple[bool, float]:
        """
        Determine if two events are duplicates
        
        Args:
            event1: First event
            event2: Second event
            
        Returns:
            Tuple of (is_duplicate: bool, confidence: float)
        """
        # Don't compare event to itself
        if event1.unified_id == event2.unified_id:
            return False, 0.0
        
        # Check title similarity
        title_similarity = cls.calculate_text_similarity(event1.title, event2.title)
        if title_similarity < cls.TITLE_SIMILARITY_THRESHOLD:
            return False, 0.0
        
        # Check time similarity
        times_match = cls.are_times_similar(event1, event2)
        if not times_match:
            return False, 0.0
        
        # Check venue similarity
        venues_match = cls.are_venues_similar(event1, event2)
        
        # Calculate overall confidence
        confidence = (title_similarity * 0.5 + 
                     (1.0 if times_match else 0.0) * 0.3 +
                     (1.0 if venues_match else 0.0) * 0.2)
        
        # If title and time match, likely duplicate even without venue match
        is_duplicate = title_similarity >= cls.TITLE_SIMILARITY_THRESHOLD and times_match
        
        # But higher confidence if all three match
        if venues_match:
            confidence = max(confidence, 0.9)
        
        return is_duplicate, confidence
    
    @classmethod
    def find_duplicates(cls, events: List[UnifiedEvent]) -> Dict[str, List[str]]:
        """
        Find all duplicate events in a list
        
        Args:
            events: List of unified events
            
        Returns:
            Dictionary mapping primary event ID to list of duplicate IDs
        """
        duplicates: Dict[str, List[str]] = {}
        processed: Set[str] = set()
        
        for i, event1 in enumerate(events):
            if event1.unified_id in processed:
                continue
            
            event_duplicates = []
            
            for event2 in events[i+1:]:
                if event2.unified_id in processed:
                    continue
                
                is_dup, confidence = cls.are_duplicates(event1, event2)
                
                if is_dup:
                    event_duplicates.append(event2.unified_id)
                    processed.add(event2.unified_id)
                    logger.debug(
                        f"Found duplicate: '{event1.title}' ({event1.source.value}) "
                        f"== '{event2.title}' ({event2.source.value}) "
                        f"[confidence: {confidence:.2f}]"
                    )
            
            if event_duplicates:
                duplicates[event1.unified_id] = event_duplicates
        
        logger.info(f"Found {len(duplicates)} events with duplicates")
        return duplicates
    
    @classmethod
    def merge_events(cls, primary: UnifiedEvent, duplicates: List[UnifiedEvent]) -> UnifiedEvent:
        """
        Merge duplicate events into a single unified event
        
        Strategy: Use the event with highest quality score as base,
        then fill in missing fields from duplicates
        
        Args:
            primary: Primary event (highest quality)
            duplicates: List of duplicate events
            
        Returns:
            Merged unified event
        """
        # Start with primary event
        merged = primary
        
        # Track all source IDs
        all_source_ids = [primary.source_id]
        all_source_ids.extend([dup.source_id for dup in duplicates])
        merged.duplicate_sources = all_source_ids
        
        # Merge fields from duplicates (prefer non-null values)
        for dup in duplicates:
            # Description - prefer longer, more detailed
            if dup.description and (not merged.description or len(dup.description) > len(merged.description)):
                merged.description = dup.description
            
            # End time - if missing
            if not merged.end_time and dup.end_time:
                merged.end_time = dup.end_time
            
            # Location details
            if not merged.location.venue_name and dup.location.venue_name:
                merged.location.venue_name = dup.location.venue_name
            
            if not merged.location.address and dup.location.address:
                merged.location.address = dup.location.address
            
            if not merged.location.latitude and dup.location.latitude:
                merged.location.latitude = dup.location.latitude
                merged.location.longitude = dup.location.longitude
            
            # Organizer
            if not merged.organizer.name and dup.organizer.name:
                merged.organizer.name = dup.organizer.name
            
            if not merged.organizer.url and dup.organizer.url:
                merged.organizer.url = dup.organizer.url
            
            # Capacity - prefer higher capacity
            if dup.capacity and (not merged.capacity or dup.capacity > merged.capacity):
                merged.capacity = dup.capacity
            
            # Attendees - prefer more recent count
            if dup.current_attendees:
                merged.current_attendees = dup.current_attendees
            
            # Tags - merge unique tags
            merged.tags = list(set(merged.tags + dup.tags))
            
            # Pricing - prefer more specific info
            if dup.price is not None and merged.price is None:
                merged.price = dup.price
                merged.is_free = False
        
        # Recalculate quality score after merging
        merged.calculate_quality_score()
        
        logger.debug(
            f"Merged event '{merged.title}' from {len(duplicates) + 1} sources, "
            f"quality: {merged.quality_score:.2f}"
        )
        
        return merged
    
    @classmethod
    def deduplicate(cls, events: List[UnifiedEvent]) -> List[UnifiedEvent]:
        """
        Deduplicate a list of events and return merged unique events
        
        Args:
            events: List of unified events
            
        Returns:
            List of deduplicated events
        """
        if not events:
            return []
        
        logger.info(f"Starting deduplication of {len(events)} events")
        
        # Find duplicate groups
        duplicate_map = cls.find_duplicates(events)
        
        # Create event lookup
        event_lookup = {event.unified_id: event for event in events}
        
        # Track which events to keep
        deduplicated = []
        processed_ids: Set[str] = set()
        
        for event in events:
            if event.unified_id in processed_ids:
                continue
            
            # Check if this event has duplicates
            if event.unified_id in duplicate_map:
                # This is a primary event with duplicates
                duplicate_ids = duplicate_map[event.unified_id]
                duplicate_events = [event_lookup[dup_id] for dup_id in duplicate_ids if dup_id in event_lookup]
                
                # Merge all duplicates into primary
                merged = cls.merge_events(event, duplicate_events)
                deduplicated.append(merged)
                
                # Mark all as processed
                processed_ids.add(event.unified_id)
                processed_ids.update(duplicate_ids)
            else:
                # No duplicates, keep as-is
                deduplicated.append(event)
                processed_ids.add(event.unified_id)
        
        logger.info(
            f"Deduplication complete: {len(events)} → {len(deduplicated)} events "
            f"({len(events) - len(deduplicated)} duplicates removed)"
        )
        
        return deduplicated

