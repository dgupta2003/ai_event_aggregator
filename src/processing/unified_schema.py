"""
Unified Event Schema

This module defines the standardized event schema that all collected events
are normalized to, regardless of their original source.
"""

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EventSource(str, Enum):
    """Supported event sources"""
    EVENTBRITE = "eventbrite"
    MEETUP = "meetup"
    LUMA = "luma"
    PARTIFUL = "partiful"
    UNKNOWN = "unknown"


class EventStatus(str, Enum):
    """Event status"""
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    PAST = "past"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class Location:
    """Standardized location information"""
    venue_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_online: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Organizer:
    """Event organizer information"""
    name: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UnifiedEvent:
    """
    Unified event schema - the single source of truth for all events
    regardless of their original platform
    """
    # Core identification
    unified_id: str  # Our unique ID across all sources
    source: EventSource
    source_id: str  # Original ID from the platform
    url: str
    
    # Event details
    title: str
    description: Optional[str] = None
    start_time: datetime = None  # Always in UTC
    end_time: Optional[datetime] = None  # Always in UTC
    
    # Location
    location: Location = None
    
    # Organization
    organizer: Organizer = None
    
    # Event metadata
    category: Optional[str] = None
    tags: List[str] = None
    
    # Capacity and attendance
    capacity: Optional[int] = None
    current_attendees: Optional[int] = None
    
    # Pricing
    is_free: bool = True
    price: Optional[float] = None
    currency: Optional[str] = "USD"
    
    # Status and quality
    status: EventStatus = EventStatus.UNKNOWN
    quality_score: float = 0.0  # 0-1 score based on data completeness
    
    # Tech relevance (for AI classification later)
    is_tech_related: Optional[bool] = None
    ai_confidence: Optional[float] = None
    ai_categories: List[str] = None
    
    # Metadata
    collected_at: datetime = None
    processed_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    # Deduplication tracking
    duplicate_of: Optional[str] = None  # Points to another unified_id if this is a duplicate
    duplicate_sources: List[str] = None  # List of source_ids if merged from multiple sources
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.tags is None:
            self.tags = []
        if self.ai_categories is None:
            self.ai_categories = []
        if self.duplicate_sources is None:
            self.duplicate_sources = []
        if self.location is None:
            self.location = Location()
        if self.organizer is None:
            self.organizer = Organizer()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        
        # Convert enums to strings
        data['source'] = self.source.value
        data['status'] = self.status.value
        
        # Convert datetimes to ISO format
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        if self.collected_at:
            data['collected_at'] = self.collected_at.isoformat()
        if self.processed_at:
            data['processed_at'] = self.processed_at.isoformat()
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedEvent':
        """Create UnifiedEvent from dictionary"""
        # Convert string enums back to enum types
        if 'source' in data and isinstance(data['source'], str):
            data['source'] = EventSource(data['source'])
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = EventStatus(data['status'])
        
        # Convert ISO strings back to datetime
        for field in ['start_time', 'end_time', 'collected_at', 'processed_at', 'last_updated']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        # Handle nested objects
        if 'location' in data and isinstance(data['location'], dict):
            data['location'] = Location(**data['location'])
        if 'organizer' in data and isinstance(data['organizer'], dict):
            data['organizer'] = Organizer(**data['organizer'])
        
        return cls(**data)
    
    def calculate_quality_score(self) -> float:
        """
        Calculate data quality score (0-1) based on completeness
        
        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 0.0
        max_score = 15.0  # Total possible points
        
        # Core fields (required)
        if self.title and len(self.title) > 5:
            score += 2.0
        if self.start_time:
            score += 2.0
        if self.url:
            score += 1.0
        
        # Description
        if self.description and len(self.description) > 50:
            score += 1.5
        elif self.description:
            score += 0.5
        
        # Location
        if self.location.venue_name:
            score += 1.0
        if self.location.city:
            score += 1.0
        if self.location.latitude and self.location.longitude:
            score += 1.0
        
        # Time
        if self.end_time:
            score += 0.5
        
        # Organization
        if self.organizer.name:
            score += 1.0
        
        # Additional details
        if self.tags and len(self.tags) > 0:
            score += 1.0
        if self.category:
            score += 0.5
        
        # Capacity/attendance info
        if self.capacity or self.current_attendees:
            score += 0.5
        
        # Pricing info
        if self.price is not None or self.is_free:
            score += 0.5
        
        # Tech classification
        if self.is_tech_related is not None:
            score += 1.0
        
        self.quality_score = score / max_score
        return self.quality_score
    
    def update_status(self):
        """Update event status based on current time"""
        if not self.start_time:
            self.status = EventStatus.UNKNOWN
            return
        
        now = datetime.now(self.start_time.tzinfo) if self.start_time.tzinfo else datetime.now()
        
        if self.end_time:
            if now > self.end_time:
                self.status = EventStatus.PAST
            elif now >= self.start_time and now <= self.end_time:
                self.status = EventStatus.ONGOING
            else:
                self.status = EventStatus.UPCOMING
        else:
            # No end time, assume past if start time has passed
            if now > self.start_time:
                self.status = EventStatus.PAST
            else:
                self.status = EventStatus.UPCOMING
    
    def is_valid(self) -> bool:
        """Check if event has minimum required fields"""
        return bool(
            self.title and
            self.start_time and
            self.url and
            len(self.title) > 3
        )
    
    def days_until_event(self) -> Optional[int]:
        """Calculate days until event starts"""
        if not self.start_time:
            return None
        
        now = datetime.now(self.start_time.tzinfo) if self.start_time.tzinfo else datetime.now()
        delta = self.start_time - now
        return delta.days
    
    def is_this_week(self) -> bool:
        """Check if event is happening this week"""
        days = self.days_until_event()
        return days is not None and 0 <= days <= 7
    
    def is_this_month(self) -> bool:
        """Check if event is happening this month"""
        days = self.days_until_event()
        return days is not None and 0 <= days <= 30

