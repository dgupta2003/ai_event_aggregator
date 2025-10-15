"""
Event Data Validator

This module validates and filters event data based on quality and relevance criteria.
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import re

from .unified_schema import UnifiedEvent, EventStatus

logger = logging.getLogger(__name__)


class EventValidator:
    """Validates and filters events based on quality criteria"""
    
    # Quality thresholds
    MIN_QUALITY_SCORE = 0.3  # Minimum acceptable quality score
    MIN_TITLE_LENGTH = 5
    MAX_TITLE_LENGTH = 200
    MIN_DESCRIPTION_LENGTH = 10
    
    # Spam/invalid patterns
    SPAM_PATTERNS = [
        r'click here',
        r'buy now',
        r'limited time',
        r'act now',
        r'\$\$\$',
        r'100% free',
        r'risk free',
        r'no credit card',
    ]
    
    # Invalid title patterns
    INVALID_TITLE_PATTERNS = [
        r'^test\s*$',
        r'^untitled',
        r'^event\s*\d*$',
        r'^\s*$',
    ]
    
    @staticmethod
    def is_valid_title(title: str) -> Tuple[bool, str]:
        """
        Validate event title
        
        Args:
            title: Event title
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not title:
            return False, "Title is empty"
        
        title_lower = title.lower().strip()
        
        # Check length
        if len(title) < EventValidator.MIN_TITLE_LENGTH:
            return False, f"Title too short ({len(title)} chars)"
        
        if len(title) > EventValidator.MAX_TITLE_LENGTH:
            return False, f"Title too long ({len(title)} chars)"
        
        # Check for invalid patterns
        for pattern in EventValidator.INVALID_TITLE_PATTERNS:
            if re.search(pattern, title_lower, re.IGNORECASE):
                return False, f"Invalid title pattern: {pattern}"
        
        return True, "Valid"
    
    @staticmethod
    def is_spam(event: UnifiedEvent) -> Tuple[bool, str]:
        """
        Check if event appears to be spam
        
        Args:
            event: Unified event
            
        Returns:
            Tuple of (is_spam, reason)
        """
        # Check title and description for spam patterns
        text_to_check = f"{event.title} {event.description or ''}"
        text_lower = text_to_check.lower()
        
        for pattern in EventValidator.SPAM_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, f"Spam pattern detected: {pattern}"
        
        # Check for excessive capitalization
        if event.title:
            upper_ratio = sum(1 for c in event.title if c.isupper()) / len(event.title)
            if upper_ratio > 0.7 and len(event.title) > 10:
                return True, "Excessive capitalization"
        
        # Check for excessive special characters
        if event.title:
            special_count = sum(1 for c in event.title if not c.isalnum() and not c.isspace())
            if special_count > len(event.title) * 0.3:
                return True, "Excessive special characters"
        
        return False, "Not spam"
    
    @staticmethod
    def is_past_event(event: UnifiedEvent, grace_hours: int = 2) -> bool:
        """
        Check if event is in the past
        
        Args:
            event: Unified event
            grace_hours: Grace period in hours to still include past events
            
        Returns:
            True if event is past (beyond grace period)
        """
        if not event.start_time:
            return False
        
        now = datetime.now(event.start_time.tzinfo) if event.start_time.tzinfo else datetime.now()
        grace_time = now - timedelta(hours=grace_hours)
        
        # Use end time if available, otherwise start time
        event_time = event.end_time if event.end_time else event.start_time
        
        return event_time < grace_time
    
    @staticmethod
    def has_valid_location(event: UnifiedEvent) -> Tuple[bool, str]:
        """
        Check if event has valid location information
        
        Args:
            event: Unified event
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Online events are valid without physical location
        if event.location.is_online:
            return True, "Online event"
        
        # Physical events should have at least venue name or city
        if event.location.venue_name or event.location.city:
            return True, "Has location info"
        
        # Has coordinates
        if event.location.latitude and event.location.longitude:
            return True, "Has coordinates"
        
        return False, "Missing location information"
    
    @staticmethod
    def has_valid_time(event: UnifiedEvent) -> Tuple[bool, str]:
        """
        Check if event has valid time information
        
        Args:
            event: Unified event
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not event.start_time:
            return False, "Missing start time"
        
        # Check if start time is reasonable (not too far in future)
        now = datetime.now(event.start_time.tzinfo) if event.start_time.tzinfo else datetime.now()
        years_ahead = (event.start_time - now).days / 365
        
        if years_ahead > 2:
            return False, f"Event too far in future ({years_ahead:.1f} years)"
        
        # If end time exists, it should be after start time
        if event.end_time and event.end_time < event.start_time:
            return False, "End time before start time"
        
        return True, "Valid time"
    
    @classmethod
    def validate(cls, event: UnifiedEvent) -> Tuple[bool, List[str]]:
        """
        Validate an event against all criteria
        
        Args:
            event: Unified event
            
        Returns:
            Tuple of (is_valid, list of reasons if invalid)
        """
        reasons = []
        
        # Check title
        title_valid, title_reason = cls.is_valid_title(event.title)
        if not title_valid:
            reasons.append(title_reason)
        
        # Check spam
        is_spam_event, spam_reason = cls.is_spam(event)
        if is_spam_event:
            reasons.append(spam_reason)
        
        # Check if past
        if cls.is_past_event(event):
            reasons.append("Event is in the past")
        
        # Check location
        location_valid, location_reason = cls.has_valid_location(event)
        if not location_valid:
            reasons.append(location_reason)
        
        # Check time
        time_valid, time_reason = cls.has_valid_time(event)
        if not time_valid:
            reasons.append(time_reason)
        
        # Check quality score
        if event.quality_score < cls.MIN_QUALITY_SCORE:
            reasons.append(f"Quality score too low ({event.quality_score:.2f})")
        
        # Check basic validity
        if not event.is_valid():
            reasons.append("Missing required fields")
        
        is_valid = len(reasons) == 0
        
        return is_valid, reasons
    
    @classmethod
    def filter_events(
        cls, 
        events: List[UnifiedEvent],
        include_past: bool = False,
        min_quality: float = None
    ) -> Tuple[List[UnifiedEvent], List[Dict[str, Any]]]:
        """
        Filter events based on validation criteria
        
        Args:
            events: List of unified events
            include_past: Whether to include past events
            min_quality: Minimum quality score (overrides default)
            
        Returns:
            Tuple of (valid_events, rejected_events_with_reasons)
        """
        if min_quality is not None:
            original_threshold = cls.MIN_QUALITY_SCORE
            cls.MIN_QUALITY_SCORE = min_quality
        
        valid_events = []
        rejected_events = []
        
        for event in events:
            # Update status first
            event.update_status()
            
            # Validate
            is_valid, reasons = cls.validate(event)
            
            # Special handling for past events
            if not include_past and event.status == EventStatus.PAST:
                rejected_events.append({
                    'event': event,
                    'reasons': ['Past event (filtered by configuration)']
                })
                continue
            
            if is_valid:
                valid_events.append(event)
            else:
                rejected_events.append({
                    'event': event,
                    'reasons': reasons
                })
        
        # Restore original threshold
        if min_quality is not None:
            cls.MIN_QUALITY_SCORE = original_threshold
        
        logger.info(
            f"Validation complete: {len(valid_events)} valid, "
            f"{len(rejected_events)} rejected from {len(events)} total"
        )
        
        return valid_events, rejected_events
    
    @staticmethod
    def get_quality_distribution(events: List[UnifiedEvent]) -> Dict[str, int]:
        """
        Get distribution of events by quality score ranges
        
        Args:
            events: List of unified events
            
        Returns:
            Dictionary with quality ranges and counts
        """
        distribution = {
            'excellent (0.8-1.0)': 0,
            'good (0.6-0.8)': 0,
            'fair (0.4-0.6)': 0,
            'poor (0.2-0.4)': 0,
            'very_poor (0.0-0.2)': 0
        }
        
        for event in events:
            score = event.quality_score
            
            if score >= 0.8:
                distribution['excellent (0.8-1.0)'] += 1
            elif score >= 0.6:
                distribution['good (0.6-0.8)'] += 1
            elif score >= 0.4:
                distribution['fair (0.4-0.6)'] += 1
            elif score >= 0.2:
                distribution['poor (0.2-0.4)'] += 1
            else:
                distribution['very_poor (0.0-0.2)'] += 1
        
        return distribution

