"""
LLM-as-a-Judge for Optimized Query Benchmark

Evaluates both original and optimized query results using Gemini,
comparing LLM judgments against our relevance scoring.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY or GEMINI_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Model configuration for reproducibility
GENERATION_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
    "response_mime_type": "application/json",
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
- Rate confidence from 0.0 to 1.0 based on how well the result matches the query
- 1.0 = Perfect match (all specified criteria met)
- 0.5-0.9 = Partial match (most criteria met)
- 0.0-0.4 = Poor match (few criteria met or generic listing)

Respond ONLY with a JSON object in this exact format:
{
  "relevant": true or false,
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation of your decision",
  "matched_aspects": ["aspect1", "aspect2", ...],
  "missing_aspects": ["aspect1", "aspect2", ...]
}

Be strict but fair. Generic event listings/directories should be marked NOT RELEVANT."""


@dataclass
class JudgmentResult:
    """Result of LLM judge evaluation"""
    relevant: bool
    confidence: float
    reasoning: str
    matched_aspects: List[str]
    missing_aspects: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GeminiJudge:
    """LLM-as-a-Judge using Gemini to evaluate search result relevance"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp", seed: Optional[int] = 42):
        self.model_name = model_name
        self.seed = seed
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=GENERATION_CONFIG,
            system_instruction=JUDGE_SYSTEM_PROMPT
        )
    
    def evaluate_result(
        self,
        query: str,
        result_title: str,
        result_url: str,
        result_content: str
    ) -> JudgmentResult:
        """Evaluate a single search result against the query"""
        prompt = self._build_evaluation_prompt(query, result_title, result_url, result_content)
        
        try:
            response = self.model.generate_content(prompt)
            judgment_data = json.loads(response.text)
            
            return JudgmentResult(
                relevant=judgment_data.get("relevant", False),
                confidence=float(judgment_data.get("confidence", 0.0)),
                reasoning=judgment_data.get("reasoning", ""),
                matched_aspects=judgment_data.get("matched_aspects", []),
                missing_aspects=judgment_data.get("missing_aspects", [])
            )
            
        except json.JSONDecodeError as e:
            return JudgmentResult(
                relevant=False,
                confidence=0.0,
                reasoning=f"Error parsing LLM response: {str(e)}",
                matched_aspects=[],
                missing_aspects=["parsing_error"]
            )
        except Exception as e:
            return JudgmentResult(
                relevant=False,
                confidence=0.0,
                reasoning=f"Error during evaluation: {str(e)}",
                matched_aspects=[],
                missing_aspects=["evaluation_error"]
            )
    
    def evaluate_batch(
        self,
        query: str,
        results: List[Dict[str, str]]
    ) -> List[JudgmentResult]:
        """Evaluate multiple search results for the same query"""
        judgments = []
        for i, result in enumerate(results):
            judgment = self.evaluate_result(
                query=query,
                result_title=result.get('title', ''),
                result_url=result.get('url', ''),
                result_content=result.get('content', '')
            )
            judgments.append(judgment)
            
            # Add delay between evaluations to avoid rate limits
            if i < len(results) - 1:
                time.sleep(1.5)
        
        return judgments
    
    def _build_evaluation_prompt(
        self,
        query: str,
        title: str,
        url: str,
        content: str
    ) -> str:
        """Build the evaluation prompt for the LLM"""
        return f"""Evaluate this search result's relevance to the query.

TODAY'S DATE: November 6, 2025

QUERY:
{query}

SEARCH RESULT:
Title: {title}
URL: {url}
Content: {content[:1000]}{'...' if len(content) > 1000 else ''}

Provide your evaluation in JSON format."""


def evaluate_optimized_benchmark(json_path: str, judge: GeminiJudge, output_path: str = None) -> Dict[str, Any]:
    """
    Evaluate optimized benchmark results with LLM judge
    
    Args:
        json_path: Path to optimized benchmark JSON file
        judge: GeminiJudge instance
        output_path: Optional path to save results
    
    Returns:
        Dict with LLM judgments and comparison metrics
    """
    # Load benchmark data
    print(f"Loading optimized benchmark results from: {json_path}")
    with open(json_path, 'r') as f:
        benchmark_data = json.load(f)
    
    total_queries = len(benchmark_data['comparisons'])
    print(f"✓ Loaded {total_queries} query comparisons\n")
    
    all_results = {
        'test_date': benchmark_data['timestamp'],
        'llm_model': judge.model_name,
        'temperature': 0.2,
        'queries': []
    }
    
    # Aggregate statistics
    total_orig_llm_relevant = 0
    total_opt_llm_relevant = 0
    total_orig_baseline_relevant = 0
    total_opt_baseline_relevant = 0
    total_results_evaluated = 0
    
    for comparison in benchmark_data['comparisons']:
        query_id = comparison['query_id']
        original_query = comparison['original_query']
        optimized_query = comparison['optimized_query']
        
        print(f"{'='*80}")
        print(f"Query #{query_id}")
        print(f"{'='*80}")
        print(f"Original:  {original_query[:70]}...")
        print(f"Optimized: {optimized_query[:70]}...")
        print(f"{'='*80}\n")
        
        # Evaluate ORIGINAL query results
        print(f"→ Evaluating ORIGINAL query results ({len(comparison['original_evals'])} results)...")
        original_search_results = [
            {
                'title': eval_data['title'],
                'url': eval_data['url'],
                'content': eval_data['content_preview']
            }
            for eval_data in comparison['original_evals']
        ]
        
        original_llm_judgments = judge.evaluate_batch(original_query, original_search_results)
        time.sleep(2.0)  # Extra delay between queries
        
        # Evaluate OPTIMIZED query results
        print(f"→ Evaluating OPTIMIZED query results ({len(comparison['optimized_evals'])} results)...")
        optimized_search_results = [
            {
                'title': eval_data['title'],
                'url': eval_data['url'],
                'content': eval_data['content_preview']
            }
            for eval_data in comparison['optimized_evals']
        ]
        
        optimized_llm_judgments = judge.evaluate_batch(optimized_query, optimized_search_results)
        time.sleep(2.0)  # Extra delay between queries
        
        # Calculate metrics for original
        orig_llm_relevant = sum(1 for j in original_llm_judgments if j.relevant)
        orig_llm_accuracy = orig_llm_relevant / len(original_llm_judgments) if original_llm_judgments else 0.0
        orig_llm_avg_confidence = sum(j.confidence for j in original_llm_judgments) / len(original_llm_judgments) if original_llm_judgments else 0.0
        
        # Calculate metrics for optimized
        opt_llm_relevant = sum(1 for j in optimized_llm_judgments if j.relevant)
        opt_llm_accuracy = opt_llm_relevant / len(optimized_llm_judgments) if optimized_llm_judgments else 0.0
        opt_llm_avg_confidence = sum(j.confidence for j in optimized_llm_judgments) / len(optimized_llm_judgments) if optimized_llm_judgments else 0.0
        
        # Compare with baseline relevance scores
        orig_baseline_relevant = comparison['original_relevant_results']
        opt_baseline_relevant = comparison['optimized_relevant_results']
        
        # Store results
        query_eval = {
            'query_id': query_id,
            'original_query': original_query,
            'optimized_query': optimized_query,
            'original_metrics': {
                'llm_relevant': orig_llm_relevant,
                'llm_accuracy': round(orig_llm_accuracy, 3),
                'llm_avg_confidence': round(orig_llm_avg_confidence, 3),
                'baseline_relevant': orig_baseline_relevant,
                'baseline_accuracy': comparison['original_accuracy'],
                'total_results': len(original_llm_judgments)
            },
            'optimized_metrics': {
                'llm_relevant': opt_llm_relevant,
                'llm_accuracy': round(opt_llm_accuracy, 3),
                'llm_avg_confidence': round(opt_llm_avg_confidence, 3),
                'baseline_relevant': opt_baseline_relevant,
                'baseline_accuracy': comparison['optimized_accuracy'],
                'total_results': len(optimized_llm_judgments)
            },
            'improvements': {
                'llm_accuracy_gain': round((opt_llm_accuracy - orig_llm_accuracy) * 100, 1),  # percentage points
                'baseline_accuracy_gain': comparison['accuracy_improvement'],
                'llm_relevant_gain': opt_llm_relevant - orig_llm_relevant,
                'baseline_relevant_gain': opt_baseline_relevant - orig_baseline_relevant
            },
            'original_judgments': [],
            'optimized_judgments': []
        }
        
        # Print summary
        print(f"\n--- ORIGINAL Query LLM Results ---")
        print(f"  LLM Relevant: {orig_llm_relevant}/{len(original_llm_judgments)} ({orig_llm_accuracy:.1%})")
        print(f"  LLM Avg Confidence: {orig_llm_avg_confidence:.3f}")
        print(f"  Baseline Relevant: {orig_baseline_relevant}/{len(original_llm_judgments)} ({comparison['original_accuracy']:.1%})")
        
        print(f"\n--- OPTIMIZED Query LLM Results ---")
        print(f"  LLM Relevant: {opt_llm_relevant}/{len(optimized_llm_judgments)} ({opt_llm_accuracy:.1%})")
        print(f"  LLM Avg Confidence: {opt_llm_avg_confidence:.3f}")
        print(f"  Baseline Relevant: {opt_baseline_relevant}/{len(optimized_llm_judgments)} ({comparison['optimized_accuracy']:.1%})")
        
        print(f"\n--- IMPROVEMENT (Optimized vs Original) ---")
        print(f"  LLM Accuracy Gain: {query_eval['improvements']['llm_accuracy_gain']:+.1f} percentage points")
        print(f"  Baseline Accuracy Gain: {query_eval['improvements']['baseline_accuracy_gain']:+.1f} percentage points")
        print(f"  LLM Relevant Gain: {query_eval['improvements']['llm_relevant_gain']:+d}")
        
        # Store detailed judgments for original
        for i, (judgment, eval_data) in enumerate(zip(original_llm_judgments, comparison['original_evals']), 1):
            baseline_relevant = eval_data['relevance_score'] >= 0.5
            
            query_eval['original_judgments'].append({
                'result_num': i,
                'url': eval_data['url'],
                'title': eval_data['title'],
                'llm_judgment': judgment.to_dict(),
                'baseline_score': eval_data['relevance_score'],
                'baseline_relevant': baseline_relevant,
                'is_generic': eval_data['is_generic_listing'],
                'agreement': judgment.relevant == baseline_relevant
            })
        
        # Store detailed judgments for optimized
        for i, (judgment, eval_data) in enumerate(zip(optimized_llm_judgments, comparison['optimized_evals']), 1):
            baseline_relevant = eval_data['relevance_score'] >= 0.5
            
            query_eval['optimized_judgments'].append({
                'result_num': i,
                'url': eval_data['url'],
                'title': eval_data['title'],
                'llm_judgment': judgment.to_dict(),
                'baseline_score': eval_data['relevance_score'],
                'baseline_relevant': baseline_relevant,
                'is_generic': eval_data['is_generic_listing'],
                'agreement': judgment.relevant == baseline_relevant
            })
        
        all_results['queries'].append(query_eval)
        
        # Update totals
        total_orig_llm_relevant += orig_llm_relevant
        total_opt_llm_relevant += opt_llm_relevant
        total_orig_baseline_relevant += orig_baseline_relevant
        total_opt_baseline_relevant += opt_baseline_relevant
        total_results_evaluated += len(original_llm_judgments)
        
        print()  # Blank line between queries
    
    # Calculate overall statistics
    all_results['overall_summary'] = {
        'total_queries': total_queries,
        'total_results_per_type': total_results_evaluated,
        'original_llm_relevant': total_orig_llm_relevant,
        'optimized_llm_relevant': total_opt_llm_relevant,
        'original_baseline_relevant': total_orig_baseline_relevant,
        'optimized_baseline_relevant': total_opt_baseline_relevant,
        'llm_accuracy_improvement': round(
            (total_opt_llm_relevant / total_results_evaluated - total_orig_llm_relevant / total_results_evaluated) * 100, 1
        ) if total_results_evaluated > 0 else 0.0,
        'baseline_accuracy_improvement': benchmark_data['summary']['avg_accuracy_improvement_pp'],
        'original_llm_accuracy': round(total_orig_llm_relevant / total_results_evaluated, 3) if total_results_evaluated > 0 else 0.0,
        'optimized_llm_accuracy': round(total_opt_llm_relevant / total_results_evaluated, 3) if total_results_evaluated > 0 else 0.0,
        'original_baseline_accuracy': benchmark_data['summary']['avg_original_accuracy'],
        'optimized_baseline_accuracy': benchmark_data['summary']['avg_optimized_accuracy']
    }
    
    # Print final summary
    summary = all_results['overall_summary']
    print(f"{'='*80}")
    print("FINAL SUMMARY: LLM Judge Evaluation of Optimized Queries")
    print(f"{'='*80}")
    print(f"Total Queries: {summary['total_queries']}")
    print(f"Total Results per Query Type: {summary['total_results_per_type']}")
    print(f"\nORIGINAL Queries:")
    print(f"  LLM Relevant: {summary['original_llm_relevant']} ({summary['original_llm_accuracy']:.1%})")
    print(f"  Baseline Relevant: {summary['original_baseline_relevant']} ({summary['original_baseline_accuracy']:.1%})")
    print(f"\nOPTIMIZED Queries:")
    print(f"  LLM Relevant: {summary['optimized_llm_relevant']} ({summary['optimized_llm_accuracy']:.1%})")
    print(f"  Baseline Relevant: {summary['optimized_baseline_relevant']} ({summary['optimized_baseline_accuracy']:.1%})")
    print(f"\nIMPROVEMENT (Optimized vs Original):")
    print(f"  LLM Accuracy Gain: {summary['llm_accuracy_improvement']:+.1f} percentage points")
    print(f"  Baseline Accuracy Gain: {summary['baseline_accuracy_improvement']:+.1f} percentage points")
    print(f"{'='*80}\n")
    
    # Save results
    if output_path is None:
        output_path = json_path.replace('.json', '_llm_judge.json')
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"✅ JSON results saved to: {output_path}\n")
    
    # Save text summary
    txt_output_path = output_path.replace('.json', '.txt')
    save_text_summary(all_results, txt_output_path)
    print(f"✅ Text summary saved to: {txt_output_path}\n")
    
    return all_results


def save_text_summary(results: Dict[str, Any], output_path: str):
    """Save a human-readable text summary"""
    with open(output_path, 'w') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("LLM JUDGE EVALUATION - OPTIMIZED QUERY BENCHMARK\n")
        f.write("="*80 + "\n\n")
        f.write(f"Model: {results['llm_model']}\n")
        f.write(f"Temperature: {results['temperature']}\n")
        f.write(f"Test Date: {results['test_date']}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("OVERALL SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        summary = results['overall_summary']
        f.write(f"Total Queries: {summary['total_queries']}\n")
        f.write(f"Total Results per Query Type: {summary['total_results_per_type']}\n\n")
        
        f.write("ORIGINAL Queries:\n")
        f.write(f"  - LLM Relevant: {summary['original_llm_relevant']} ({summary['original_llm_accuracy']:.1%})\n")
        f.write(f"  - Baseline Relevant: {summary['original_baseline_relevant']} ({summary['original_baseline_accuracy']:.1%})\n\n")
        
        f.write("OPTIMIZED Queries:\n")
        f.write(f"  - LLM Relevant: {summary['optimized_llm_relevant']} ({summary['optimized_llm_accuracy']:.1%})\n")
        f.write(f"  - Baseline Relevant: {summary['optimized_baseline_relevant']} ({summary['optimized_baseline_accuracy']:.1%})\n\n")
        
        f.write("IMPROVEMENT (Optimized vs Original):\n")
        f.write(f"  - LLM Accuracy Gain: {summary['llm_accuracy_improvement']:+.1f} percentage points\n")
        f.write(f"  - Baseline Accuracy Gain: {summary['baseline_accuracy_improvement']:+.1f} percentage points\n\n")
        
        # Per-Query Results
        f.write("\n" + "="*80 + "\n")
        f.write("PER-QUERY DETAILED RESULTS\n")
        f.write("="*80 + "\n\n")
        
        for query_data in results['queries']:
            f.write(f"\n{'='*80}\n")
            f.write(f"QUERY #{query_data['query_id']}\n")
            f.write(f"{'='*80}\n")
            f.write(f"ORIGINAL:  {query_data['original_query']}\n")
            f.write(f"OPTIMIZED: {query_data['optimized_query']}\n\n")
            
            # Metrics comparison
            orig_m = query_data['original_metrics']
            opt_m = query_data['optimized_metrics']
            imp = query_data['improvements']
            
            f.write("METRICS COMPARISON:\n")
            f.write(f"                     | Original | Optimized | Improvement\n")
            f.write(f"  LLM Relevant:      | {orig_m['llm_relevant']:^8} | {opt_m['llm_relevant']:^9} | {imp['llm_relevant_gain']:+d}\n")
            f.write(f"  LLM Accuracy:      | {orig_m['llm_accuracy']*100:>6.1f}% | {opt_m['llm_accuracy']*100:>7.1f}% | {imp['llm_accuracy_gain']:+.1f}pp\n")
            f.write(f"  Baseline Relevant: | {orig_m['baseline_relevant']:^8} | {opt_m['baseline_relevant']:^9} | {imp['baseline_relevant_gain']:+d}\n")
            f.write(f"  Baseline Accuracy: | {orig_m['baseline_accuracy']*100:>6.1f}% | {opt_m['baseline_accuracy']*100:>7.1f}% | {imp['baseline_accuracy_gain']:+.1f}pp\n\n")
            
            # Disagreements for original
            orig_disagreements = [j for j in query_data['original_judgments'] if not j['agreement']]
            if orig_disagreements:
                f.write(f"ORIGINAL Query Disagreements (LLM vs Baseline): {len(orig_disagreements)}\n")
                for dis in orig_disagreements[:3]:  # Show max 3
                    f.write(f"  - [{dis['title'][:60]}...]\n")
                    f.write(f"    LLM: {'RELEVANT' if dis['llm_judgment']['relevant'] else 'NOT RELEVANT'} ({dis['llm_judgment']['confidence']:.2f})\n")
                    f.write(f"    Baseline: {'RELEVANT' if dis['baseline_relevant'] else 'NOT RELEVANT'} ({dis['baseline_score']:.2f})\n")
                    f.write(f"    Reasoning: {dis['llm_judgment']['reasoning'][:100]}...\n")
                f.write("\n")
            
            # Disagreements for optimized
            opt_disagreements = [j for j in query_data['optimized_judgments'] if not j['agreement']]
            if opt_disagreements:
                f.write(f"OPTIMIZED Query Disagreements (LLM vs Baseline): {len(opt_disagreements)}\n")
                for dis in opt_disagreements[:3]:  # Show max 3
                    f.write(f"  - [{dis['title'][:60]}...]\n")
                    f.write(f"    LLM: {'RELEVANT' if dis['llm_judgment']['relevant'] else 'NOT RELEVANT'} ({dis['llm_judgment']['confidence']:.2f})\n")
                    f.write(f"    Baseline: {'RELEVANT' if dis['baseline_relevant'] else 'NOT RELEVANT'} ({dis['baseline_score']:.2f})\n")
                    f.write(f"    Reasoning: {dis['llm_judgment']['reasoning'][:100]}...\n")
                f.write("\n")
        
        # Footer
        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")


# CLI
if __name__ == '__main__':
    # Initialize judge
    print("Initializing Gemini Judge...")
    judge = GeminiJudge(model_name="gemini-2.0-flash-exp", seed=42)
    print(f"✓ Using model: {judge.model_name}")
    print(f"✓ Temperature: 0.2 (for reproducibility)\n")
    
    # Path to optimized benchmark results
    benchmark_json = '/Users/shreyasbachiraju/uni/circle_capstone/web_llm/ollama_optimized_benchmark_20251106_034303.json'
    
    if not os.path.exists(benchmark_json):
        print(f"ERROR: {benchmark_json} not found")
        exit(1)
    
    # Run LLM judge evaluation
    print("🚀 Starting LLM Judge evaluation on optimized benchmark results...")
    print("This will evaluate both original and optimized query results...\n")
    
    start_time = time.time()
    
    results = evaluate_optimized_benchmark(benchmark_json, judge)
    
    elapsed = time.time() - start_time
    print(f"✅ Evaluation complete! Total time: {elapsed:.1f}s")
    print("Done! 🎉")
