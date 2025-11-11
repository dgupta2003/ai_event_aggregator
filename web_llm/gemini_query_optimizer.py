"""
Gemini-powered Query Rewriter for Ollama Web Search API

Transforms vague or broad user queries into highly specific, constraint-aware,
context-rich search prompts optimized for event discovery.

Uses Google's Gemini API to intelligently rewrite queries following these rules:
1. Write highly specific queries with full context
2. Multi-query decomposition for broad topics
3. Clarify ambiguous terms by embedding context
4. Add constraint-aware structure (location, time, attributes)
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY or GEMINI_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Model configuration
GENERATION_CONFIG = {
    "temperature": 0.3,  # Slightly creative but consistent
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
    "response_mime_type": "application/json",
}

# System prompt for query optimization
QUERY_OPTIMIZER_PROMPT = """You are an expert search query optimizer specializing in event discovery and web search optimization.

Your task is to rewrite user queries into highly optimized search queries for the Ollama Web Search API.

OPTIMIZATION RULES:

1. **Write Highly Specific Queries**
   - Expand vague or general terms into detailed, fully-described concepts
   - Add time ranges, domains, goals, or constraints when relevant
   - Include specific event types, platforms, locations
   - Example:
     Input: "AI events"
     Output: "artificial intelligence conferences, hackathons, and workshops in 2025 with registration links and event descriptions"

2. **Multi-Query Decomposition**
   - If the query is broad, create multiple targeted sub-queries
   - Generate 3-5 sub-queries that cover different aspects
   - Example:
     Main: "sustainability events"
     Sub-queries:
       • "climate change awareness conferences 2025 with registration"
       • "renewable energy innovation workshops this month"
       • "sustainability hackathons for students calendar"

3. **Clarify Ambiguous Terms**
   - Add domain qualifiers (e.g., "tech conference" not just "conference")
   - Specify format (virtual, hybrid, in-person)
   - Add platform context (Eventbrite, Luma, Meetup)
   - Example:
     Input: "events in SF"
     Output: "technology and innovation events in San Francisco California with specific dates and venues"

4. **Constraint-Aware Structure**
   - Extract and emphasize:
     • Location: "in [City], [State/Country]"
     • Date/Time: "in [Month Year]", "between [Date1] and [Date2]", "this weekend"
     • Event Type: "hackathon", "workshop", "conference", "meetup"
     • Platform: "on Eventbrite", "on Luma", "on Meetup"
     • Format: "virtual", "hybrid", "in-person"
     • Attributes: "with registration links", "free events", "for students"
   - Example:
     Weak: "tech events tomorrow"
     Strong: "technology meetups and networking events happening tomorrow [DATE] with registration links and event details"

5. **Event-Specific Keywords**
   - Add event indicators: "registration", "tickets", "rsvp", "attend", "schedule"
   - Include action words: "find", "list", "discover", "upcoming"
   - Avoid generic terms that return news/articles

6. **Temporal Precision**
   - Convert relative dates to absolute:
     • "tomorrow" → "[specific date]"
     • "this weekend" → "[Saturday-Sunday dates]"
     • "next month" → "[Month Year]"
   - Always include year (2025) if discussing future events
   - Use month names, not numbers

TODAY'S DATE: {today}

Respond with JSON in this exact format:
{{
  "primary_query": "the main optimized query",
  "sub_queries": ["sub-query 1", "sub-query 2", "sub-query 3"],
  "optimization_notes": "brief explanation of what was improved",
  "extracted_constraints": {{
    "location": "extracted location or null",
    "date_range": "extracted date range or null",
    "event_type": "extracted event type or null",
    "platform": "extracted platform or null",
    "format": "virtual/hybrid/in-person or null"
  }}
}}

Be aggressive in adding specificity. The goal is to get the most relevant, actionable event results possible."""


@dataclass
class OptimizedQuery:
    """Result of query optimization"""
    original_query: str
    primary_query: str
    sub_queries: List[str]
    optimization_notes: str
    extracted_constraints: Dict[str, Optional[str]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GeminiQueryOptimizer:
    """Gemini-powered query optimizer for event search"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini query optimizer
        
        Args:
            model_name: Gemini model to use (default: gemini-2.0-flash-exp for best reasoning)
        """
        self.model_name = model_name
        self.today = datetime.now().strftime("%B %d, %Y")
        
        # Format system prompt with today's date
        system_prompt = QUERY_OPTIMIZER_PROMPT.format(today=self.today)
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            system_instruction=system_prompt
        )
    
    def optimize_query(self, original_query: str) -> OptimizedQuery:
        """
        Optimize a single query
        
        Args:
            original_query: The raw user query
            
        Returns:
            OptimizedQuery with primary query, sub-queries, and constraints
        """
        prompt = f"""Optimize this event search query:

ORIGINAL QUERY: {original_query}

TODAY'S DATE: {self.today}

Provide the optimized query in JSON format."""
        
        try:
            # Generate optimized query
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            optimization_data = json.loads(response.text)
            
            # Create result
            return OptimizedQuery(
                original_query=original_query,
                primary_query=optimization_data.get("primary_query", original_query),
                sub_queries=optimization_data.get("sub_queries", []),
                optimization_notes=optimization_data.get("optimization_notes", ""),
                extracted_constraints=optimization_data.get("extracted_constraints", {})
            )
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            print(f"Warning: JSON parsing failed for query '{original_query}': {e}")
            return OptimizedQuery(
                original_query=original_query,
                primary_query=original_query,
                sub_queries=[],
                optimization_notes=f"Error: Failed to parse optimization response",
                extracted_constraints={}
            )
        except Exception as e:
            # Handle other errors
            print(f"Warning: Optimization failed for query '{original_query}': {e}")
            return OptimizedQuery(
                original_query=original_query,
                primary_query=original_query,
                sub_queries=[],
                optimization_notes=f"Error: {str(e)}",
                extracted_constraints={}
            )
    
    def optimize_batch(self, queries: List[str]) -> List[OptimizedQuery]:
        """
        Optimize multiple queries
        
        Args:
            queries: List of raw user queries
            
        Returns:
            List of OptimizedQuery objects
        """
        import time
        
        optimized = []
        for i, query in enumerate(queries, 1):
            print(f"Optimizing query {i}/{len(queries)}: {query[:60]}...")
            result = self.optimize_query(query)
            optimized.append(result)
            
            # Add delay to avoid rate limiting
            if i < len(queries):
                time.sleep(1.0)
        
        return optimized


def load_test_queries(md_path: str) -> List[str]:
    """Load queries from TEST_QUERIES.md file"""
    import re
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    queries = []
    for line in lines:
        # Match numbered queries like "1. Query text here"
        m = re.match(r"^\s*(\d{1,2})\.\s+(.*\S)\s*$", line)
        if m:
            idx = int(m.group(1))
            text = m.group(2).strip()
            if 1 <= idx <= 20:
                queries.append(text)
    
    return queries


def save_optimized_queries(optimized: List[OptimizedQuery], output_path: str):
    """Save optimized queries to JSON file"""
    data = {
        'optimization_date': datetime.now().isoformat(),
        'total_queries': len(optimized),
        'queries': [opt.to_dict() for opt in optimized]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_comparison_markdown(optimized: List[OptimizedQuery], output_path: str):
    """Save before/after comparison in Markdown format"""
    lines = [
        "# Query Optimization Results",
        f"\nGenerated: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}",
        f"\nTotal Queries: {len(optimized)}",
        "\n---\n"
    ]
    
    for i, opt in enumerate(optimized, 1):
        lines.append(f"\n## Query {i}")
        lines.append(f"\n**Original:**")
        lines.append(f"> {opt.original_query}")
        lines.append(f"\n**Optimized (Primary):**")
        lines.append(f"> {opt.primary_query}")
        
        if opt.sub_queries:
            lines.append(f"\n**Sub-Queries:**")
            for j, sub in enumerate(opt.sub_queries, 1):
                lines.append(f"{j}. {sub}")
        
        lines.append(f"\n**Optimization Notes:**")
        lines.append(f"{opt.optimization_notes}")
        
        if opt.extracted_constraints:
            lines.append(f"\n**Extracted Constraints:**")
            for key, value in opt.extracted_constraints.items():
                if value:
                    lines.append(f"- {key}: {value}")
        
        lines.append("\n---")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


# CLI
if __name__ == '__main__':
    import sys
    
    print("="*80)
    print("GEMINI QUERY OPTIMIZER FOR OLLAMA WEB SEARCH")
    print("="*80)
    print()
    
    # Initialize optimizer
    print("Initializing Gemini Query Optimizer...")
    optimizer = GeminiQueryOptimizer(model_name="gemini-2.0-flash-exp")
    print(f"✓ Using model: {optimizer.model_name}")
    print(f"✓ Today's date: {optimizer.today}\n")
    
    # Load test queries
    md_path = 'web_llm/TEST_QUERIES.md'
    if not os.path.exists(md_path):
        md_path = 'TEST_QUERIES.md'
    
    if os.path.exists(md_path):
        print(f"Loading queries from: {md_path}")
        queries = load_test_queries(md_path)
        print(f"✓ Loaded {len(queries)} queries\n")
    else:
        print("No TEST_QUERIES.md found. Using sample queries...")
        queries = [
            "Is there any AI event happening on November 12 at 9 AM in New York City?",
            "Find all sustainability workshops scheduled in San Francisco between November 1 and 5.",
            "Are there any climate change awareness events this weekend in Chicago?"
        ]
    
    # Optimize queries
    print("="*80)
    print("OPTIMIZING QUERIES")
    print("="*80)
    print()
    
    optimized = optimizer.optimize_batch(queries)
    
    # Save results
    json_output = 'optimized_queries.json'
    md_output = 'optimized_queries_comparison.md'
    
    save_optimized_queries(optimized, json_output)
    save_comparison_markdown(optimized, md_output)
    
    print()
    print("="*80)
    print("RESULTS SAVED")
    print("="*80)
    print(f"✓ JSON: {json_output}")
    print(f"✓ Markdown: {md_output}")
    print()
    
    # Print sample
    if optimized:
        print("="*80)
        print("SAMPLE OPTIMIZATION")
        print("="*80)
        sample = optimized[0]
        print(f"\nOriginal:")
        print(f"  {sample.original_query}")
        print(f"\nOptimized:")
        print(f"  {sample.primary_query}")
        if sample.sub_queries:
            print(f"\nSub-Queries:")
            for i, sub in enumerate(sample.sub_queries[:3], 1):
                print(f"  {i}. {sub}")
        print()
    
    print("✅ Done!")
