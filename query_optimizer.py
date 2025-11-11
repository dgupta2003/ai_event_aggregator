"""
Gemini-Powered Query Optimizer for Ollama Web Search API

Transforms vague user queries into highly specific, constraint-aware,
context-rich search prompts optimized for event discovery.

Handles Gemini API rate limits with exponential backoff and caching.
"""

import os
import json
import time
import re
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY or GEMINI_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Rate limit configuration
MAX_RETRIES = 5
BASE_DELAY = 2.0  # Start with 2 seconds
MAX_DELAY = 60.0  # Max 60 seconds between retries
BATCH_DELAY = 3.0  # Delay between queries to avoid rate limits

# Model configuration
GENERATION_CONFIG = {
    "temperature": 0.3,  # Low temperature for consistent optimization
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
    "response_mime_type": "application/json",
}


SYSTEM_PROMPT = """You are an expert search query optimizer specializing in event discovery.

Your task: Transform user queries into HIGHLY SPECIFIC, CONSTRAINT-AWARE search queries optimized for the Ollama Web Search API.

OPTIMIZATION RULES:

1. **Expand Vague Terms into Specific Concepts**
   - Add domain context, time ranges, constraints
   - Example: "AI events" → "artificial intelligence conferences, hackathons, and workshops in 2025 with registration links and event details"

2. **Add Temporal Precision**
   - Always include year (2025)
   - Add month names for monthly queries
   - Convert relative dates: "this weekend" → "November 9-10, 2025"
   - Convert "next week" → "November 11-17, 2025"
   - TODAY IS: November 6, 2025

3. **Add Location Context**
   - Expand city names: "NYC" → "New York City, NY, USA"
   - Add state/country for disambiguation
   - Specify "United States" to avoid international confusion

4. **Add Platform Constraints**
   - If platform mentioned, add explicit filter
   - Example: "on Eventbrite" → "site:eventbrite.com"
   - Example: "on Luma" → "site:lu.ma"
   - Example: "on Meetup" → "site:meetup.com"

5. **Add Event-Specific Keywords**
   - Include: "event", "registration", "tickets", "RSVP", "attend"
   - Avoid news/articles: prefer "upcoming events" over "event news"

6. **Clarify Event Types**
   - Expand types: "talks" → "panel discussions, fireside chats, keynote presentations"
   - Be specific: "networking" → "networking events, mixers, meet-and-greets"

7. **Add Desired Attributes**
   - Include what searcher wants: "with registration links", "with event dates", "with organizer information"

8. **Multi-Query Decomposition (for broad topics)**
   - For complex queries, provide main query + alternative variations
   - Example alternatives:
     • Different platforms (Eventbrite, Luma, Meetup)
     • Different event types (conference, workshop, meetup)
     • Different time windows (this week, this month, next month)

CRITICAL: Return ONLY valid JSON in this format:
{
  "original_query": "the input query",
  "optimized_query": "highly specific optimized main query",
  "alternative_queries": [
    "alternative variation 1",
    "alternative variation 2",
    "alternative variation 3"
  ],
  "reasoning": "brief explanation of optimization choices",
  "extracted_constraints": {
    "date_range": "Nov 1-5, 2025" or null,
    "location": "San Francisco, CA, USA" or null,
    "platform": "eventbrite" or null,
    "event_type": "workshop" or null,
    "topic": "sustainability" or null
  }
}

EXAMPLES:

Input: "Find AI events happening tomorrow in NYC"
Output:
{
  "original_query": "Find AI events happening tomorrow in NYC",
  "optimized_query": "artificial intelligence AI events conferences workshops hackathons November 7, 2025 New York City NY USA upcoming with registration links tickets RSVP event details",
  "alternative_queries": [
    "AI machine learning events November 7 2025 New York City site:eventbrite.com registration",
    "AI tech events tomorrow NYC November 7 2025 site:lu.ma attend",
    "artificial intelligence meetups November 7 2025 New York site:meetup.com"
  ],
  "reasoning": "Expanded 'AI' to full terms, converted 'tomorrow' to exact date Nov 7 2025, expanded 'NYC' to full location, added event keywords and registration indicators, created platform-specific alternatives",
  "extracted_constraints": {
    "date_range": "November 7, 2025",
    "location": "New York City, NY, USA",
    "platform": null,
    "event_type": null,
    "topic": "artificial intelligence"
  }
}

Input: "sustainability workshops between November 1 and 5"
Output:
{
  "original_query": "sustainability workshops between November 1 and 5",
  "optimized_query": "sustainability sustainable development workshops training sessions November 1-5, 2025 upcoming events with registration links event details dates organizers",
  "alternative_queries": [
    "sustainability workshops November 1 2 3 4 5, 2025 site:eventbrite.com tickets",
    "sustainable development training November 2025 first week events attend",
    "climate sustainability workshop November 1-5 2025 environmental events"
  ],
  "reasoning": "Expanded 'sustainability' with related terms, kept specific date range, added 'workshops' synonyms, included event indicators and desired attributes, created variations with platforms and related topics",
  "extracted_constraints": {
    "date_range": "November 1-5, 2025",
    "location": null,
    "platform": null,
    "event_type": "workshop",
    "topic": "sustainability"
  }
}

Now optimize the user's query."""


@dataclass
class OptimizedQuery:
    """Optimized query result"""
    original_query: str
    optimized_query: str
    alternative_queries: List[str]
    reasoning: str
    extracted_constraints: Dict[str, Optional[str]]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class QueryOptimizer:
    """Gemini-powered query optimizer with rate limit handling"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            system_instruction=SYSTEM_PROMPT
        )
        self.cache = {}  # Simple in-memory cache
        self.request_count = 0
        self.last_request_time = 0
    
    def optimize_query(self, query: str, use_cache: bool = True) -> OptimizedQuery:
        """
        Optimize a single query with rate limit handling
        
        Args:
            query: Original user query
            use_cache: Use cached result if available
            
        Returns:
            OptimizedQuery object
        """
        # Check cache
        if use_cache and query in self.cache:
            print(f"  ✓ Using cached optimization for: {query[:60]}...")
            return self.cache[query]
        
        # Rate limit protection: Ensure minimum delay between requests
        self._enforce_rate_limit()
        
        # Retry with exponential backoff
        for attempt in range(MAX_RETRIES):
            try:
                print(f"  → Optimizing query (attempt {attempt + 1}/{MAX_RETRIES})...")
                
                response = self.model.generate_content(f"Optimize this query: {query}")
                
                # Parse JSON response
                result_data = json.loads(response.text)
                
                # Create OptimizedQuery object
                optimized = OptimizedQuery(
                    original_query=result_data.get("original_query", query),
                    optimized_query=result_data.get("optimized_query", query),
                    alternative_queries=result_data.get("alternative_queries", []),
                    reasoning=result_data.get("reasoning", ""),
                    extracted_constraints=result_data.get("extracted_constraints", {})
                )
                
                # Cache result
                self.cache[query] = optimized
                self.request_count += 1
                
                print(f"  ✓ Optimized successfully")
                return optimized
                
            except json.JSONDecodeError as e:
                print(f"  ✗ JSON parsing error: {e}")
                if attempt < MAX_RETRIES - 1:
                    delay = self._calculate_backoff(attempt)
                    print(f"  ⏳ Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    # Fallback: Return original query
                    return self._fallback_optimization(query)
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                    delay = self._calculate_backoff(attempt)
                    print(f"  ⚠️  Rate limit hit! Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    print(f"  ✗ Error: {e}")
                    if attempt < MAX_RETRIES - 1:
                        delay = self._calculate_backoff(attempt)
                        print(f"  ⏳ Retrying in {delay:.1f}s...")
                        time.sleep(delay)
                    else:
                        return self._fallback_optimization(query)
        
        # All retries exhausted
        print(f"  ✗ All retries exhausted, using fallback optimization")
        return self._fallback_optimization(query)
    
    def optimize_batch(
        self, 
        queries: List[str], 
        batch_delay: float = BATCH_DELAY,
        save_progress: bool = True,
        output_file: str = "optimized_queries.json"
    ) -> List[OptimizedQuery]:
        """
        Optimize multiple queries with progress saving
        
        Args:
            queries: List of queries to optimize
            batch_delay: Delay between queries (seconds)
            save_progress: Save after each query
            output_file: Output JSON file path
            
        Returns:
            List of OptimizedQuery objects
        """
        results = []
        total = len(queries)
        
        print(f"\n{'='*80}")
        print(f"OPTIMIZING {total} QUERIES")
        print(f"{'='*80}\n")
        
        for i, query in enumerate(queries, 1):
            print(f"[{i}/{total}] {query[:70]}...")
            
            try:
                optimized = self.optimize_query(query)
                results.append(optimized)
                
                # Save progress after each query
                if save_progress:
                    self._save_results(results, output_file)
                
                # Delay before next query (except last one)
                if i < total:
                    print(f"  ⏳ Waiting {batch_delay}s before next query...\n")
                    time.sleep(batch_delay)
                else:
                    print()
                    
            except KeyboardInterrupt:
                print(f"\n⚠️  Interrupted! Saving {len(results)} optimized queries...")
                self._save_results(results, output_file)
                raise
            except Exception as e:
                print(f"  ✗ Unexpected error: {e}")
                # Add fallback and continue
                results.append(self._fallback_optimization(query))
                if save_progress:
                    self._save_results(results, output_file)
        
        print(f"{'='*80}")
        print(f"✅ OPTIMIZATION COMPLETE: {len(results)}/{total} queries")
        print(f"{'='*80}\n")
        
        return results
    
    def _enforce_rate_limit(self):
        """Ensure minimum delay between API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < BATCH_DELAY:
            sleep_time = BATCH_DELAY - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
        return delay
    
    def _fallback_optimization(self, query: str) -> OptimizedQuery:
        """Simple rule-based fallback when Gemini fails"""
        # Add basic enhancements
        enhanced = query
        
        # Add year if missing
        if "2025" not in enhanced and "2024" not in enhanced:
            enhanced += " 2025"
        
        # Add event keyword if missing
        event_keywords = ["event", "conference", "workshop", "meetup", "hackathon"]
        if not any(kw in enhanced.lower() for kw in event_keywords):
            enhanced += " event"
        
        # Add registration keyword
        if "registration" not in enhanced.lower() and "register" not in enhanced.lower():
            enhanced += " registration"
        
        return OptimizedQuery(
            original_query=query,
            optimized_query=enhanced,
            alternative_queries=[enhanced],
            reasoning="Fallback: Basic rule-based enhancement (Gemini unavailable)",
            extracted_constraints={}
        )
    
    def _save_results(self, results: List[OptimizedQuery], output_file: str):
        """Save results to JSON file"""
        output_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_queries": len(results),
            "model": self.model_name,
            "optimized_queries": [r.to_dict() for r in results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Progress saved to: {output_file}")


def load_test_queries(md_path: str) -> List[str]:
    """Load queries from TEST_QUERIES.md"""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    queries = []
    for line in lines:
        m = re.match(r"^\s*\d{1,2}\.\s+(.*\S)\s*$", line)
        if m:
            queries.append(m.group(1).strip())
    
    return queries


# ---------------------------
# CLI
# ---------------------------
if __name__ == '__main__':
    import sys
    
    # Load test queries
    test_queries_path = os.path.join(
        os.path.dirname(__file__), 
        'web_llm', 
        'TEST_QUERIES.md'
    )
    
    if not os.path.exists(test_queries_path):
        print(f"ERROR: TEST_QUERIES.md not found at {test_queries_path}")
        sys.exit(1)
    
    queries = load_test_queries(test_queries_path)
    print(f"✓ Loaded {len(queries)} test queries\n")
    
    # Initialize optimizer
    optimizer = QueryOptimizer(model_name="gemini-2.0-flash-exp")
    
    # Optimize all queries with rate limit handling
    output_file = "optimized_queries.json"
    
    try:
        results = optimizer.optimize_batch(
            queries,
            batch_delay=3.0,  # 3 second delay between queries
            save_progress=True,
            output_file=output_file
        )
        
        # Final save
        optimizer._save_results(results, output_file)
        
        print(f"\n✅ All queries optimized!")
        print(f"📄 Results saved to: {output_file}")
        print(f"📊 Total API calls: {optimizer.request_count}")
        
        # Print sample
        print(f"\n{'='*80}")
        print("SAMPLE OPTIMIZED QUERY:")
        print(f"{'='*80}")
        if results:
            sample = results[0]
            print(f"Original:  {sample.original_query}")
            print(f"Optimized: {sample.optimized_query}")
            print(f"Reasoning: {sample.reasoning}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print(f"📄 Partial results saved to: {output_file}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
