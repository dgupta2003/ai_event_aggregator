"""
Data Processing Module

This module handles all event data processing:
- Normalization: Converting events from different sources to unified schema
- Deduplication: Identifying and merging duplicate events across sources
- Enrichment: Adding missing data and extracting additional metadata
- Validation: Filtering out low-quality and invalid events
"""

from .unified_schema import (
    UnifiedEvent,
    EventSource,
    EventStatus,
    Location,
    Organizer
)
from .normalizer import EventNormalizer
from .deduplicator import EventDeduplicator
from .enricher import EventEnricher
from .validator import EventValidator
from .processor_manager import ProcessorManager

__all__ = [
    # Schema
    'UnifiedEvent',
    'EventSource',
    'EventStatus',
    'Location',
    'Organizer',
    
    # Pipeline components
    'EventNormalizer',
    'EventDeduplicator',
    'EventEnricher',
    'EventValidator',
    'ProcessorManager',
]

