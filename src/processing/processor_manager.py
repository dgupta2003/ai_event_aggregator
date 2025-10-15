"""
Processing Pipeline Manager

This module orchestrates the entire data processing pipeline:
1. Load raw data
2. Normalize to unified schema
3. Deduplicate across sources
4. Enrich with additional data
5. Validate and filter
6. Save processed data
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .unified_schema import UnifiedEvent
from .normalizer import EventNormalizer
from .deduplicator import EventDeduplicator
from .enricher import EventEnricher
from .validator import EventValidator

try:
    from ..config import get_config
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.config import get_config

logger = logging.getLogger(__name__)


class ProcessorManager:
    """Manages the complete event processing pipeline"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger("processor_manager")
        
        # Set up directories
        self.raw_data_dir = Path(self.config.app.data_dir) / "raw"
        self.processed_data_dir = Path(self.config.app.data_dir) / "processed"
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline stats
        self.stats = {
            'raw_events': 0,
            'normalized': 0,
            'deduplicated': 0,
            'enriched': 0,
            'validated': 0,
            'rejected': 0
        }
    
    def load_raw_data(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Load raw event data from file
        
        Args:
            filepath: Path to raw data file
            
        Returns:
            List of raw event dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different file formats
            if isinstance(data, dict):
                events = data.get('data', [])
            elif isinstance(data, list):
                events = data
            else:
                raise ValueError(f"Unexpected data format: {type(data)}")
            
            self.logger.info(f"Loaded {len(events)} raw events from {filepath}")
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to load raw data from {filepath}: {e}")
            return []
    
    def load_all_raw_data(self, city: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load all raw data files from the raw data directory
        
        Args:
            city: Filter by city name (optional)
            
        Returns:
            List of all raw events
        """
        all_events = []
        
        # Find all JSON files in raw data directory
        pattern = f"*{city}*.json" if city else "*.json"
        raw_files = list(self.raw_data_dir.glob(pattern))
        
        self.logger.info(f"Found {len(raw_files)} raw data files")
        
        for filepath in raw_files:
            events = self.load_raw_data(str(filepath))
            all_events.extend(events)
        
        self.stats['raw_events'] = len(all_events)
        self.logger.info(f"Loaded {len(all_events)} total raw events")
        
        return all_events
    
    def normalize_events(self, raw_events: List[Dict[str, Any]]) -> List[UnifiedEvent]:
        """
        Normalize raw events to unified schema
        
        Args:
            raw_events: List of raw event dictionaries
            
        Returns:
            List of normalized unified events
        """
        self.logger.info(f"Normalizing {len(raw_events)} raw events...")
        
        normalized = EventNormalizer.normalize_batch(raw_events)
        self.stats['normalized'] = len(normalized)
        
        self.logger.info(f"Normalized {len(normalized)} events")
        return normalized
    
    def deduplicate_events(self, events: List[UnifiedEvent]) -> List[UnifiedEvent]:
        """
        Deduplicate events across sources
        
        Args:
            events: List of unified events
            
        Returns:
            List of deduplicated events
        """
        self.logger.info(f"Deduplicating {len(events)} events...")
        
        deduplicated = EventDeduplicator.deduplicate(events)
        self.stats['deduplicated'] = len(deduplicated)
        
        self.logger.info(
            f"Deduplication complete: {len(events)} → {len(deduplicated)} "
            f"({len(events) - len(deduplicated)} duplicates removed)"
        )
        return deduplicated
    
    def enrich_events(self, events: List[UnifiedEvent]) -> List[UnifiedEvent]:
        """
        Enrich events with additional data
        
        Args:
            events: List of unified events
            
        Returns:
            List of enriched events
        """
        self.logger.info(f"Enriching {len(events)} events...")
        
        enriched = EventEnricher.enrich_batch(events)
        self.stats['enriched'] = len(enriched)
        
        # Log enrichment stats
        enrich_stats = EventEnricher.get_enrichment_stats(enriched)
        self.logger.info(
            f"Enrichment complete: "
            f"{enrich_stats['tech_related']} tech-related, "
            f"{enrich_stats['with_category']} categorized, "
            f"avg quality: {enrich_stats['average_quality']:.2f}"
        )
        
        return enriched
    
    def validate_events(
        self, 
        events: List[UnifiedEvent],
        include_past: bool = False,
        min_quality: float = 0.3
    ) -> List[UnifiedEvent]:
        """
        Validate and filter events
        
        Args:
            events: List of unified events
            include_past: Whether to include past events
            min_quality: Minimum quality score threshold
            
        Returns:
            List of validated events
        """
        self.logger.info(f"Validating {len(events)} events...")
        
        valid, rejected = EventValidator.filter_events(
            events,
            include_past=include_past,
            min_quality=min_quality
        )
        
        self.stats['validated'] = len(valid)
        self.stats['rejected'] = len(rejected)
        
        # Log quality distribution
        quality_dist = EventValidator.get_quality_distribution(valid)
        self.logger.info(f"Quality distribution: {quality_dist}")
        
        # Log rejection reasons
        if rejected:
            rejection_reasons = {}
            for item in rejected:
                for reason in item['reasons']:
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            
            self.logger.info(f"Rejection reasons: {rejection_reasons}")
        
        return valid
    
    def save_processed_data(
        self, 
        events: List[UnifiedEvent],
        city: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Save processed events to file
        
        Args:
            events: List of processed unified events
            city: City name for filename
            filename: Custom filename (optional)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            city_str = f"{city}_" if city else ""
            filename = f"processed_events_{city_str}{timestamp}.json"
        
        filepath = self.processed_data_dir / filename
        
        # Convert events to dictionaries
        events_data = [event.to_dict() for event in events]
        
        # Create output structure
        output = {
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'total_events': len(events),
                'city': city,
                'pipeline_stats': self.stats
            },
            'events': events_data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(events)} processed events to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save processed data: {e}")
            return ""
    
    def process_pipeline(
        self,
        city: Optional[str] = None,
        include_past: bool = False,
        min_quality: float = 0.3,
        save_output: bool = True
    ) -> List[UnifiedEvent]:
        """
        Run the complete processing pipeline
        
        Args:
            city: City to process (None for all)
            include_past: Include past events
            min_quality: Minimum quality threshold
            save_output: Whether to save output file
            
        Returns:
            List of processed events
        """
        self.logger.info("="*60)
        self.logger.info("Starting Event Processing Pipeline")
        self.logger.info("="*60)
        
        # Reset stats
        self.stats = {
            'raw_events': 0,
            'normalized': 0,
            'deduplicated': 0,
            'enriched': 0,
            'validated': 0,
            'rejected': 0
        }
        
        # Step 1: Load raw data
        self.logger.info("\n[1/5] Loading raw data...")
        raw_events = self.load_all_raw_data(city)
        
        if not raw_events:
            self.logger.warning("No raw events found. Pipeline stopped.")
            return []
        
        # Step 2: Normalize
        self.logger.info("\n[2/5] Normalizing events...")
        normalized = self.normalize_events(raw_events)
        
        # Step 3: Deduplicate
        self.logger.info("\n[3/5] Deduplicating events...")
        deduplicated = self.deduplicate_events(normalized)
        
        # Step 4: Enrich
        self.logger.info("\n[4/5] Enriching events...")
        enriched = self.enrich_events(deduplicated)
        
        # Step 5: Validate
        self.logger.info("\n[5/5] Validating events...")
        validated = self.validate_events(enriched, include_past, min_quality)
        
        # Save output
        if save_output and validated:
            self.logger.info("\nSaving processed data...")
            filepath = self.save_processed_data(validated, city)
        
        # Print summary
        self.logger.info("\n" + "="*60)
        self.logger.info("Pipeline Complete - Summary:")
        self.logger.info("="*60)
        self.logger.info(f"Raw events:        {self.stats['raw_events']}")
        self.logger.info(f"Normalized:        {self.stats['normalized']}")
        self.logger.info(f"After dedup:       {self.stats['deduplicated']}")
        self.logger.info(f"After enrichment:  {self.stats['enriched']}")
        self.logger.info(f"Valid (final):     {self.stats['validated']}")
        self.logger.info(f"Rejected:          {self.stats['rejected']}")
        self.logger.info("="*60)
        
        return validated
    
    def process_file(
        self,
        filepath: str,
        save_output: bool = True,
        include_past: bool = False,
        min_quality: float = 0.3
    ) -> List[UnifiedEvent]:
        """
        Process a single raw data file
        
        Args:
            filepath: Path to raw data file
            save_output: Whether to save output
            include_past: Include past events
            min_quality: Minimum quality threshold
            
        Returns:
            List of processed events
        """
        self.logger.info(f"Processing file: {filepath}")
        
        # Load specific file
        raw_events = self.load_raw_data(filepath)
        
        if not raw_events:
            return []
        
        # Run pipeline steps
        normalized = self.normalize_events(raw_events)
        deduplicated = self.deduplicate_events(normalized)
        enriched = self.enrich_events(deduplicated)
        validated = self.validate_events(enriched, include_past, min_quality)
        
        # Save output
        if save_output and validated:
            # Extract city from filename if possible
            filename_parts = Path(filepath).stem.split('_')
            city = filename_parts[1] if len(filename_parts) > 1 else None
            
            self.save_processed_data(validated, city)
        
        return validated


def main():
    """Main function for running the processing pipeline"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create processor
    processor = ProcessorManager()
    
    # Run pipeline
    processed_events = processor.process_pipeline(
        city=None,  # Process all cities
        include_past=False,
        min_quality=0.3,
        save_output=True
    )
    
    print(f"\n✅ Processing complete! {len(processed_events)} events ready.")
    print(f"📁 Check the data/processed/ directory for output files.")


if __name__ == "__main__":
    main()

