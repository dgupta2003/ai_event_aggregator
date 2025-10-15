"""
Event Data Enricher

This module enriches event data by adding missing information,
geocoding addresses, and extracting additional metadata.
"""

import logging
from typing import List, Optional, Dict, Any
import re

from .unified_schema import UnifiedEvent
try:
    from ..requirements.cities_config import is_tech_related
except ImportError:
    from requirements.cities_config import is_tech_related

logger = logging.getLogger(__name__)


class EventEnricher:
    """Enriches event data with additional information"""
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Convert to lowercase and split
        text = text.lower()
        
        # Common tech-related keywords to look for
        tech_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'data science', 'analytics', 'big data',
            'python', 'javascript', 'react', 'node', 'java', 'go', 'rust',
            'web development', 'mobile', 'frontend', 'backend', 'full stack',
            'devops', 'cloud', 'aws', 'azure', 'gcp', 'kubernetes', 'docker',
            'blockchain', 'crypto', 'web3', 'nft',
            'cybersecurity', 'security', 'privacy',
            'startup', 'entrepreneur', 'vc', 'funding',
            'hackathon', 'workshop', 'bootcamp', 'conference', 'meetup',
            'networking', 'career', 'hiring', 'recruiting'
        ]
        
        found_keywords = []
        for keyword in tech_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # Remove duplicates
    
    @staticmethod
    def infer_category(event: UnifiedEvent) -> Optional[str]:
        """
        Infer event category from title and description
        
        Args:
            event: Unified event
            
        Returns:
            Inferred category or None
        """
        text = f"{event.title} {event.description or ''}".lower()
        
        # Category patterns
        categories = {
            'ai_ml': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network'],
            'data_science': ['data science', 'analytics', 'data engineering', 'big data'],
            'web_dev': ['web development', 'frontend', 'backend', 'full stack', 'react', 'vue', 'angular'],
            'mobile': ['mobile', 'ios', 'android', 'flutter', 'react native'],
            'devops': ['devops', 'kubernetes', 'docker', 'ci/cd', 'cloud'],
            'blockchain': ['blockchain', 'crypto', 'web3', 'ethereum', 'bitcoin'],
            'security': ['cybersecurity', 'security', 'infosec', 'penetration testing'],
            'startup': ['startup', 'entrepreneur', 'founder', 'vc', 'pitch'],
            'networking': ['networking', 'career', 'professional development'],
            'hackathon': ['hackathon', 'hack', 'code sprint'],
            'workshop': ['workshop', 'tutorial', 'hands-on', 'training'],
            'conference': ['conference', 'summit', 'convention']
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    @staticmethod
    def enrich_tags(event: UnifiedEvent) -> UnifiedEvent:
        """
        Enrich event tags by extracting keywords from title and description
        
        Args:
            event: Unified event
            
        Returns:
            Event with enriched tags
        """
        text = f"{event.title} {event.description or ''}"
        keywords = EventEnricher.extract_keywords(text)
        
        # Merge with existing tags
        all_tags = list(set(event.tags + keywords))
        event.tags = all_tags[:20]  # Limit to 20 tags
        
        return event
    
    @staticmethod
    def enrich_category(event: UnifiedEvent) -> UnifiedEvent:
        """
        Enrich event category if missing
        
        Args:
            event: Unified event
            
        Returns:
            Event with enriched category
        """
        if not event.category or event.category in ['tech', 'event', 'unknown']:
            inferred = EventEnricher.infer_category(event)
            if inferred:
                event.category = inferred
        
        return event
    
    @staticmethod
    def check_tech_relevance(event: UnifiedEvent) -> UnifiedEvent:
        """
        Check if event is tech-related using keyword matching
        
        Args:
            event: Unified event
            
        Returns:
            Event with tech relevance flag
        """
        text = f"{event.title} {event.description or ''}"
        categories = [event.category] if event.category else []
        
        event.is_tech_related = is_tech_related(text, categories)
        
        # Set basic confidence
        if event.is_tech_related:
            # Higher confidence if multiple signals
            signals = 0
            if any(keyword in text.lower() for keyword in ['tech', 'software', 'developer', 'engineer']):
                signals += 1
            if event.category and 'tech' in event.category.lower():
                signals += 1
            if len(event.tags) > 3:
                signals += 1
            
            event.ai_confidence = min(0.6 + (signals * 0.1), 0.9)  # 0.6 to 0.9
        
        return event
    
    @staticmethod
    def normalize_location(event: UnifiedEvent) -> UnifiedEvent:
        """
        Normalize location information
        
        Args:
            event: Unified event
            
        Returns:
            Event with normalized location
        """
        # Clean venue name
        if event.location.venue_name:
            # Remove excessive whitespace
            event.location.venue_name = ' '.join(event.location.venue_name.split())
            
            # Capitalize properly
            event.location.venue_name = event.location.venue_name.title()
        
        # Clean city name
        if event.location.city:
            event.location.city = ' '.join(event.location.city.split()).title()
        
        # Standardize state codes
        if event.location.state and len(event.location.state) > 2:
            # Map common state names to codes (US)
            state_map = {
                'new york': 'NY',
                'california': 'CA',
                'texas': 'TX',
                'florida': 'FL',
                'illinois': 'IL',
                'massachusetts': 'MA',
                'washington': 'WA',
                'oregon': 'OR'
            }
            state_lower = event.location.state.lower()
            if state_lower in state_map:
                event.location.state = state_map[state_lower]
        
        return event
    
    @staticmethod
    def add_computed_fields(event: UnifiedEvent) -> UnifiedEvent:
        """
        Add computed fields to event
        
        Args:
            event: Unified event
            
        Returns:
            Event with computed fields
        """
        # Already handled by UnifiedEvent methods:
        # - days_until_event()
        # - is_this_week()
        # - is_this_month()
        # - update_status()
        
        # Ensure status is up to date
        event.update_status()
        
        # Ensure quality score is calculated
        if event.quality_score == 0.0:
            event.calculate_quality_score()
        
        return event
    
    @classmethod
    def enrich(cls, event: UnifiedEvent) -> UnifiedEvent:
        """
        Apply all enrichment steps to an event
        
        Args:
            event: Unified event
            
        Returns:
            Enriched event
        """
        # Apply enrichments
        event = cls.enrich_tags(event)
        event = cls.enrich_category(event)
        event = cls.check_tech_relevance(event)
        event = cls.normalize_location(event)
        event = cls.add_computed_fields(event)
        
        return event
    
    @classmethod
    def enrich_batch(cls, events: List[UnifiedEvent]) -> List[UnifiedEvent]:
        """
        Enrich a batch of events
        
        Args:
            events: List of unified events
            
        Returns:
            List of enriched events
        """
        enriched = []
        
        for event in events:
            try:
                enriched_event = cls.enrich(event)
                enriched.append(enriched_event)
            except Exception as e:
                logger.error(f"Error enriching event '{event.title}': {e}")
                # Add original event if enrichment fails
                enriched.append(event)
        
        logger.info(f"Enriched {len(enriched)} events")
        return enriched
    
    @staticmethod
    def get_enrichment_stats(events: List[UnifiedEvent]) -> Dict[str, Any]:
        """
        Get statistics about enrichment quality
        
        Args:
            events: List of enriched events
            
        Returns:
            Dictionary with enrichment stats
        """
        total = len(events)
        
        stats = {
            'total_events': total,
            'with_category': sum(1 for e in events if e.category),
            'with_tags': sum(1 for e in events if e.tags and len(e.tags) > 0),
            'tech_related': sum(1 for e in events if e.is_tech_related),
            'with_coordinates': sum(1 for e in events if e.location.latitude),
            'average_quality': sum(e.quality_score for e in events) / total if total > 0 else 0,
            'average_tags_per_event': sum(len(e.tags) for e in events) / total if total > 0 else 0
        }
        
        return stats

