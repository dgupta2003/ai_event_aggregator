#!/usr/bin/env python3
"""
LLM Judge for Evaluating Scraper Results

Uses Google's Gemini API to evaluate the relevance of search results to user queries.
Implements the judge system with structured JSON output.
"""

import os
import csv
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Generation configuration for the judge
GENERATION_CONFIG = {
    "temperature": 0.2,  # Low temperature for consistent, focused judgments
    "max_output_tokens": 2048,
    "response_mime_type": "application/json",  # Request JSON output
}

# System prompt for the judge
JUDGE_SYSTEM_PROMPT = """You are an expert evaluator assessing the relevance of web search results to user queries about events.

Your task is to determine if a search result is RELEVANT or NOT RELEVANT to the given query.

Consider a result RELEVANT if it:

1. Matches the main topic/subject of the query

2. Matches the location (if specified)

3. Matches the time period (if specified)

4. Matches the event type (conference, workshop, meetup, etc.) if specified

5. Matches the platform/organizer (if specified)

6. Contains actionable event information (not just generic listings)

Consider a result NOT RELEVANT if it:

- Is about a different topic

- Is in a wrong location or time period

- Is a general directory/listing without specific event details

- Is news/articles about events rather than the events themselves

- Lacks key information requested in the query

CONFIDENCE SCORING:

Calculate confidence based on how many of the 6 criteria above are met:

- Each criterion has equal weight (1/6 ≈ 0.167)

- Only count criteria that are specified in the query

- Confidence = (number of matched criteria) / (number of applicable criteria)

- Example: If query specifies topic, location, and time (3 criteria), and result matches all 3, confidence = 1.0

- Example: If query specifies topic, location, time, type (4 criteria), and result matches 3, confidence = 0.75

Respond ONLY with a JSON object in this exact format:

{

  "relevant": true or false,

  "confidence": 0.0 to 1.0,

  "reasoning": "brief explanation of your decision",

  "matched_aspects": ["aspect1", "aspect2", ...],

  "missing_aspects": ["aspect1", "aspect2", ...]

}

Be strict but fair. Partial matches can be relevant if they meet the core intent of the query."""


class LLMJudge:
    """LLM-based judge for evaluating result relevance"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM judge
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Create the model with judge system prompt
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',  # Fast and cost-effective
            system_instruction=JUDGE_SYSTEM_PROMPT
        )
        
        print("✅ LLM Judge initialized (Gemini 2.0 Flash)")
    
    def judge_result(self, query: str, result: str) -> Dict[str, Any]:
        """
        Judge a single result for its relevance to a query
        
        Args:
            query: User query
            result: The search result to evaluate
            
        Returns:
            Dict with judgment (relevant, confidence, reasoning, etc.)
        """
        try:
            # Create the prompt for Gemini
            prompt = f"""Query: {query}

Result to evaluate:
{result}

Evaluate this result's relevance to the query. Respond with ONLY a JSON object in the exact format specified in your instructions."""

            # Generate response using Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=GENERATION_CONFIG
            )
            
            # Extract text from response
            response_text = response.text
            
            # Parse JSON response - handle if there's markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]   # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()
            
            judgment = json.loads(response_text)
            
            # Add metadata (don't add 'query' since we already have query_text)
            judgment['result'] = result
            judgment['judged_at'] = datetime.now().isoformat()
            
            return judgment
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON decode error: {e}")
            print(f"Raw response: {response_text if 'response_text' in locals() else 'No response'}")
            return {
                'relevant': False,
                'confidence': 0.0,
                'reasoning': 'JSON parsing error',
                'matched_aspects': [],
                'missing_aspects': [],
                'error': str(e)
            }
        except Exception as e:
            print(f"❌ Error judging result: {e}")
            return {
                'relevant': False,
                'confidence': 0.0,
                'reasoning': f'Error: {str(e)}',
                'matched_aspects': [],
                'missing_aspects': [],
                'error': str(e)
            }
    
    def judge_results_batch(self, query_results: List[Dict[str, str]], delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Judge multiple query-result pairs in batch
        
        Args:
            query_results: List of dicts with 'query' and 'result' keys
            delay: Delay between API calls in seconds
            
        Returns:
            List of judgment dicts
        """
        judgments = []
        
        print(f"\n🔍 Judging {len(query_results)} results...")
        
        for i, pair in enumerate(query_results, 1):
            query = pair.get('query', '')
            result = pair.get('result', '')
            
            print(f"  [{i}/{len(query_results)}] Judging result...")
            
            judgment = self.judge_result(query, result)
            judgments.append(judgment)
            
            # Rate limiting
            if i < len(query_results):
                time.sleep(delay)
        
        return judgments
    
    def extract_individual_results(self, top_results: str) -> List[str]:
        """
        Extract individual results from the bullet-pointed results string
        
        Args:
            top_results: The top_results field from the CSV
            
        Returns:
            List of individual result strings
        """
        if not top_results or top_results.strip() in ['', '• No matching events found', '• No clear event titles found']:
            return []
        
        # Split by bullet points
        results = [r.strip() for r in top_results.split('\n') if r.strip().startswith('•')]
        
        # Remove the bullet point marker
        results = [r[1:].strip() for r in results]
        
        return results


class QueryResultsJudge:
    """Main class for evaluating query results CSV files"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.judge = LLMJudge(api_key=api_key)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def load_query_results(self, csv_file: str) -> List[Dict[str, Any]]:
        """
        Load query results from CSV file
        
        Args:
            csv_file: Path to query results CSV
            
        Returns:
            List of query result dicts
        """
        data = []
        
        print(f"📂 Loading query results from: {csv_file}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        print(f"✅ Loaded {len(data)} query results")
        return data
    
    def judge_query_results(self, query_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Judge all query results
        
        Args:
            query_results: List of query result dicts from CSV
            
        Returns:
            List of judgment dicts
        """
        all_judgments = []
        
        print("\n⚖️  Starting judgment process...")
        
        for idx, query_data in enumerate(query_results, 1):
            query_num = query_data.get('query_number', idx)
            query_text = query_data.get('query_text', '')
            top_results = query_data.get('top_results', '')
            
            print(f"\n📋 Query {query_num}: {query_text[:60]}...")
            
            # Extract individual results
            results = self.judge.extract_individual_results(top_results)
            
            if not results:
                print(f"  ⚠️  No results to judge")
                all_judgments.append({
                    'query_number': query_num,
                    'query_text': query_text,
                    'result': 'No results',
                    'relevant': False,
                    'confidence': 0.0,
                    'reasoning': 'No results returned',
                    'matched_aspects': [],
                    'missing_aspects': []
                })
                continue
            
            print(f"  Found {len(results)} result(s) to judge")
            
            # Judge each result
            for i, result in enumerate(results, 1):
                print(f"    [{i}/{len(results)}] Judging result...")
                
                judgment = self.judge.judge_result(query_text, result)
                judgment['query_number'] = query_num
                judgment['query_text'] = query_text
                judgment['result_index'] = i
                
                all_judgments.append(judgment)
                
                # Show judgment
                relevant_emoji = "✅" if judgment['relevant'] else "❌"
                print(f"      {relevant_emoji} {judgment['relevant']} (confidence: {judgment['confidence']:.2f})")
                
                # Rate limiting - Gemini free tier has limits (60 req/min), but be respectful
                time.sleep(1.5)
        
        return all_judgments
    
    def save_judgments(self, judgments: List[Dict[str, Any]], output_dir: str = "outputs/csv") -> str:
        """
        Save judgments to CSV and JSON files
        
        Args:
            judgments: List of judgment dicts
            output_dir: Directory to save output files
            
        Returns:
            Path to the saved CSV file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as CSV
        csv_file = f"{output_dir}/llm_judgments_{timestamp}.csv"
        
        if judgments:
            fieldnames = [
                'query_number', 'query_text', 'result', 'result_index', 'relevant', 'confidence',
                'reasoning', 'matched_aspects', 'missing_aspects', 'error', 'judged_at'
            ]
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for judgment in judgments:
                    # Convert list fields to strings and add defaults - only include fields in fieldnames
                    row = {k: v for k, v in judgment.items() if k in fieldnames}
                    row['matched_aspects'] = '; '.join(row.get('matched_aspects', []))
                    row['missing_aspects'] = '; '.join(row.get('missing_aspects', []))
                    row['error'] = row.get('error', '')
                    row['result_index'] = row.get('result_index', '')
                    
                    # Limit result field length for CSV
                    if 'result' in row and row['result'] and len(row['result']) > 200:
                        row['result'] = row['result'][:197] + "..."
                    
                    writer.writerow(row)
            
            print(f"\n💾 Judgments saved to: {csv_file}")
        
        # Save as JSON for detailed analysis
        json_file = f"{output_dir}/llm_judgments_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(judgments, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Detailed judgments saved to: {json_file}")
        
        return csv_file
    
    def calculate_relevance_stats(self, judgments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate relevance statistics including precision
        
        Args:
            judgments: List of judgment dicts
            
        Returns:
            Dict with statistics including precision
        """
        total = len(judgments)
        relevant = sum(1 for j in judgments if j.get('relevant', False))
        not_relevant = total - relevant
        
        # Precision = number of relevant results / total number of results
        precision = (relevant / total) if total > 0 else 0.0
        
        avg_confidence = sum(j.get('confidence', 0.0) for j in judgments) / total if total > 0 else 0.0
        
        # Group by query number
        by_query = {}
        for judgment in judgments:
            qnum = judgment.get('query_number', 'unknown')
            if qnum not in by_query:
                by_query[qnum] = {'relevant': 0, 'total': 0}
            by_query[qnum]['total'] += 1
            if judgment.get('relevant', False):
                by_query[qnum]['relevant'] += 1
        
        query_scores = {}
        query_precisions = {}
        for qnum, stats in by_query.items():
            query_scores[qnum] = (stats['relevant'] / stats['total']) * 100 if stats['total'] > 0 else 0
            query_precisions[qnum] = (stats['relevant'] / stats['total']) if stats['total'] > 0 else 0.0
        
        return {
            'total_results_judged': total,
            'relevant_count': relevant,
            'not_relevant_count': not_relevant,
            'relevance_rate': (relevant / total) * 100 if total > 0 else 0,
            'precision': precision,  # Precision metric
            'avg_confidence': avg_confidence,
            'query_scores': query_scores,
            'query_precisions': query_precisions
        }
    
    def print_summary_report(self, judgments: List[Dict[str, Any]]):
        """Print a summary report of judgments including precision"""
        stats = self.calculate_relevance_stats(judgments)
        
        print("\n" + "="*80)
        print("📊 LLM JUDGE SUMMARY REPORT")
        print("="*80)
        print()
        print(f"Total Results Judged: {stats['total_results_judged']}")
        print(f"✅ Relevant: {stats['relevant_count']} ({stats['relevance_rate']:.1f}%)")
        print(f"❌ Not Relevant: {stats['not_relevant_count']} ({100 - stats['relevance_rate']:.1f}%)")
        print(f"🎯 Precision: {stats['precision']:.3f} ({stats['precision']*100:.1f}%)")
        print(f"📈 Average Confidence: {stats['avg_confidence']:.2f}")
        print()
        
        print("🏆 Query Performance (with Precision):")
        print("-"*80)
        print(f"{'Query':<4} | {'Relevance %':<12} | {'Precision':<10} | {'Status'}")
        print("-"*80)
        
        sorted_queries = sorted(stats['query_scores'].items(), key=lambda x: x[1], reverse=True)
        
        for qnum, score in sorted_queries:
            precision = stats['query_precisions'].get(qnum, 0.0)
            status = "🟢 Excellent" if score >= 80 else "🟡 Good" if score >= 50 else "🟠 Fair" if score >= 25 else "🔴 Poor"
            print(f"{qnum:<4} | {score:>11.1f}% | {precision:>9.3f} | {status}")
        
        print("="*80)
        print(f"\n💡 Precision = Relevant Results / Total Results = {stats['relevant_count']} / {stats['total_results_judged']} = {stats['precision']:.3f}")
        print("="*80)


def main():
    """Main execution function"""
    import sys
    
    print("="*80)
    print("⚖️  LLM JUDGE FOR QUERY RESULTS")
    print("="*80)
    print()
    
    # Get input CSV file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Auto-detect latest query_results file
        csv_dir = "outputs/csv"
        files = [f for f in os.listdir(csv_dir) if f.startswith("query_results_") and f.endswith(".csv")]
        if not files:
            print("❌ No query_results CSV found. Please run create_query_results.py first.")
            return
        
        input_file = os.path.join(csv_dir, sorted(files)[-1])
        print(f"📂 Auto-detected: {input_file}")
    
    # Initialize judge
    judge_app = QueryResultsJudge()
    
    # Load query results
    query_results = judge_app.load_query_results(input_file)
    
    # Judge results
    judgments = judge_app.judge_query_results(query_results)
    
    # Save judgments
    output_file = judge_app.save_judgments(judgments)
    
    # Print summary
    judge_app.print_summary_report(judgments)
    
    print("\n✅ JUDGMENT COMPLETE!")
    print(f"📁 Results saved to: {output_file}")
    print("="*80)


if __name__ == "__main__":
    main()

