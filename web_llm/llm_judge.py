"""
LLM-as-a-Judge: Gemini-based evaluation of search result relevance

Uses Google's Gemini API to independently assess whether search results
are relevant to the original query. This provides an alternative validation
method compared to constraint-based evaluation.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API (try both GEMINI_API_KEY and GEMINI_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY or GEMINI_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Model configuration for reproducibility
GENERATION_CONFIG = {
    "temperature": 0.2,  # Low temperature for consistent, focused judgments
    "top_p": 0.95,
    "top_k": 40,
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
    
    def __init__(self, model_name: str = "gemini-2.5-flash", seed: Optional[int] = 42):
        """
        Initialize Gemini judge
        
        Args:
            model_name: Gemini model to use (default: gemini-2.5-flash for speed)
            seed: Random seed for reproducibility (Note: Gemini doesn't directly support seed,
                  but low temperature helps with consistency)
        """
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
        """
        Evaluate a single search result against the query
        
        Args:
            query: The original search query
            result_title: Title of the search result
            result_url: URL of the search result
            result_content: Content snippet from the search result
            
        Returns:
            JudgmentResult with relevance assessment
        """
        # Construct evaluation prompt
        prompt = self._build_evaluation_prompt(query, result_title, result_url, result_content)
        
        try:
            # Generate judgment
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            judgment_data = json.loads(response.text)
            
            # Validate and create result
            return JudgmentResult(
                relevant=judgment_data.get("relevant", False),
                confidence=float(judgment_data.get("confidence", 0.0)),
                reasoning=judgment_data.get("reasoning", ""),
                matched_aspects=judgment_data.get("matched_aspects", []),
                missing_aspects=judgment_data.get("missing_aspects", [])
            )
            
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return JudgmentResult(
                relevant=False,
                confidence=0.0,
                reasoning=f"Error parsing LLM response: {str(e)}",
                matched_aspects=[],
                missing_aspects=["parsing_error"]
            )
        except Exception as e:
            # Handle other errors
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
        """
        Evaluate multiple search results for the same query
        
        Args:
            query: The original search query
            results: List of dicts with 'title', 'url', 'content' keys
            
        Returns:
            List of JudgmentResult objects
        """
        judgments = []
        for result in results:
            judgment = self.evaluate_result(
                query=query,
                result_title=result.get('title', ''),
                result_url=result.get('url', ''),
                result_content=result.get('content', '')
            )
            judgments.append(judgment)
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

TODAY'S DATE: October 26, 2025

QUERY:
{query}

SEARCH RESULT:
Title: {title}
URL: {url}
Content: {content[:1000]}{'...' if len(content) > 1000 else ''}

Provide your evaluation in JSON format."""
    
    def calculate_accuracy(self, judgments: List[JudgmentResult]) -> Dict[str, Any]:
        """
        Calculate aggregate metrics from judgments
        
        Args:
            judgments: List of judgment results
            
        Returns:
            Dict with accuracy metrics including precision
        """
        if not judgments:
            return {
                'total_results': 0,
                'relevant_count': 0,
                'accuracy': 0.0,
                'precision': 0.0,
                'avg_confidence': 0.0
            }
        
        relevant_count = sum(1 for j in judgments if j.relevant)
        avg_confidence = sum(j.confidence for j in judgments) / len(judgments)
        
        # Precision = relevant results / total results evaluated
        precision = relevant_count / len(judgments)
        
        return {
            'total_results': len(judgments),
            'relevant_count': relevant_count,
            'accuracy': relevant_count / len(judgments),  # Same as precision for this use case
            'precision': precision,  # Explicitly calculated: TP / (TP + FP)
            'avg_confidence': avg_confidence,
            'confidence_of_relevant': sum(j.confidence for j in judgments if j.relevant) / max(1, relevant_count)
        }


def compare_with_constraint_based(
    llm_judgments: List[JudgmentResult],
    constraint_evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compare LLM judge results with constraint-based evaluation
    
    Args:
        llm_judgments: Results from Gemini judge
        constraint_evaluations: Results from constraint-based evaluation
        
    Returns:
        Comparison metrics
    """
    if len(llm_judgments) != len(constraint_evaluations):
        raise ValueError("Judgment and evaluation lists must have same length")
    
    agreements = 0
    disagreements = 0
    
    for llm_j, const_e in zip(llm_judgments, constraint_evaluations):
        # Consider constraint-based relevant if confidence >= 0.6
        const_relevant = const_e.get('confidence', 0.0) >= 0.6
        
        if llm_j.relevant == const_relevant:
            agreements += 1
        else:
            disagreements += 1
    
    total = len(llm_judgments)
    return {
        'total_comparisons': total,
        'agreements': agreements,
        'disagreements': disagreements,
        'agreement_rate': agreements / total if total > 0 else 0.0,
        'llm_relevant_count': sum(1 for j in llm_judgments if j.relevant),
        'constraint_relevant_count': sum(1 for e in constraint_evaluations if e.get('confidence', 0.0) >= 0.6)
    }


def evaluate_ollama_benchmark(json_path: str, judge: GeminiJudge, output_path: str = None) -> Dict[str, Any]:
    """
    Load Ollama benchmark results and evaluate with LLM judge
    
    Args:
        json_path: Path to Ollama benchmark JSON file
        judge: GeminiJudge instance
        output_path: Optional path to save results (default: llm_judge_evaluation.json)
    
    Returns:
        Dict with LLM judgments and comparison metrics
    """
    import time
    
    # Load benchmark data
    print(f"Loading benchmark results from: {json_path}")
    with open(json_path, 'r') as f:
        benchmark_data = json.load(f)
    
    total_queries = len(benchmark_data['results'])
    total_results = sum(r['total_results'] for r in benchmark_data['results'])
    print(f"✓ Loaded {total_queries} queries with {total_results} total results\n")
    
    all_results = {
        'test_date': benchmark_data['test_date'],
        'llm_model': judge.model_name,
        'temperature': 0.2,
        'queries': []
    }
    
    total_llm_relevant = 0
    total_constraint_relevant = 0
    total_agreements = 0
    total_results_evaluated = 0
    
    for query_result in benchmark_data['results']:
        query_id = query_result['query_id']
        query_text = query_result['query_text']
        
        print(f"{'='*80}")
        print(f"Query #{query_id}: {query_text}")
        print(f"{'='*80}")
        
        # Prepare results for batch evaluation
        search_results = []
        constraint_evals = []
        
        for eval_data in query_result['result_evals']:
            search_results.append({
                'title': eval_data['title'],
                'url': eval_data['url'],
                'content': eval_data['content_preview']
            })
            constraint_evals.append({
                'confidence': eval_data['confidence'],
                'matched': eval_data['matched']
            })
        
        # Run LLM judge on all results
        print(f"Evaluating {len(search_results)} results with LLM judge...")
        llm_judgments = judge.evaluate_batch(query_text, search_results)
        
        # Add delay to avoid rate limiting
        time.sleep(1.5)
        
        # Calculate metrics
        llm_metrics = judge.calculate_accuracy(llm_judgments)
        
        # Compare with constraint-based
        comparison = compare_with_constraint_based(llm_judgments, constraint_evals)
        
        # Store results
        query_eval = {
            'query_id': query_id,
            'query_text': query_text,
            'llm_metrics': llm_metrics,
            'constraint_metrics': {
                'accuracy': query_result['accuracy'],
                'relevant_count': query_result['relevant_results'],
                'total_results': query_result['total_results']
            },
            'comparison': comparison,
            'judgments': []
        }
        
        # Print summary
        print(f"\n--- LLM Judge Results ---")
        print(f"  Relevant: {llm_metrics['relevant_count']}/{llm_metrics['total_results']}")
        print(f"  LLM Accuracy: {llm_metrics['accuracy']:.1%}")
        print(f"  LLM Precision: {llm_metrics['precision']:.1%}")
        print(f"  Avg Confidence: {llm_metrics['avg_confidence']:.2f}")
        
        print(f"\n--- Constraint-Based Results ---")
        print(f"  Relevant: {query_result['relevant_results']}/{query_result['total_results']}")
        print(f"  Accuracy: {query_result['accuracy']:.1%}")
        
        print(f"\n--- Comparison ---")
        print(f"  Agreement Rate: {comparison['agreement_rate']:.1%}")
        print(f"  Agreements: {comparison['agreements']}/{comparison['total_comparisons']}")
        print(f"  Disagreements: {comparison['disagreements']}")
        
        # Store detailed judgments
        for i, (judgment, constraint, result) in enumerate(zip(llm_judgments, constraint_evals, search_results), 1):
            const_relevant = constraint['confidence'] >= 0.6
            agree = judgment.relevant == const_relevant
            
            judgment_detail = {
                'result_num': i,
                'url': result['url'],
                'title': result['title'],
                'llm_judgment': {
                    'relevant': judgment.relevant,
                    'confidence': judgment.confidence,
                    'reasoning': judgment.reasoning,
                    'matched_aspects': judgment.matched_aspects,
                    'missing_aspects': judgment.missing_aspects
                },
                'constraint_evaluation': {
                    'confidence': constraint['confidence'],
                    'relevant': const_relevant,
                    'matched': constraint['matched']
                },
                'agreement': agree
            }
            
            query_eval['judgments'].append(judgment_detail)
            
            # Print disagreements
            if not agree:
                print(f"\n  ⚠️  DISAGREEMENT on Result #{i}:")
                print(f"      Title: {result['title'][:80]}...")
                print(f"      LLM: {'RELEVANT' if judgment.relevant else 'NOT RELEVANT'} (conf={judgment.confidence:.2f})")
                print(f"      Constraint: {'RELEVANT' if const_relevant else 'NOT RELEVANT'} (conf={constraint['confidence']:.2f})")
                print(f"      LLM Reasoning: {judgment.reasoning[:150]}...")
        
        all_results['queries'].append(query_eval)
        
        # Update totals
        total_llm_relevant += llm_metrics['relevant_count']
        total_constraint_relevant += comparison['constraint_relevant_count']
        total_agreements += comparison['agreements']
        total_results_evaluated += comparison['total_comparisons']
        
        print()  # Blank line between queries
    
    # Calculate overall statistics
    all_results['overall_summary'] = {
        'total_queries': total_queries,
        'total_results_evaluated': total_results_evaluated,
        'llm_total_relevant': total_llm_relevant,
        'constraint_total_relevant': total_constraint_relevant,
        'total_agreements': total_agreements,
        'total_disagreements': total_results_evaluated - total_agreements,
        'overall_agreement_rate': total_agreements / total_results_evaluated if total_results_evaluated > 0 else 0.0,
        'llm_overall_accuracy': total_llm_relevant / total_results_evaluated if total_results_evaluated > 0 else 0.0,
        'llm_overall_precision': total_llm_relevant / total_results_evaluated if total_results_evaluated > 0 else 0.0,  # Same as accuracy in this context
        'constraint_overall_accuracy': total_constraint_relevant / total_results_evaluated if total_results_evaluated > 0 else 0.0
    }
    
    # Print final summary
    summary = all_results['overall_summary']
    print(f"{'='*80}")
    print("FINAL SUMMARY: LLM Judge vs Constraint-Based Evaluation")
    print(f"{'='*80}")
    print(f"Total Queries: {summary['total_queries']}")
    print(f"Total Results Evaluated: {summary['total_results_evaluated']}")
    print(f"\nLLM Judge:")
    print(f"  Relevant Results: {summary['llm_total_relevant']}")
    print(f"  Overall Accuracy: {summary['llm_overall_accuracy']:.1%}")
    print(f"\nConstraint-Based:")
    print(f"  Relevant Results: {summary['constraint_total_relevant']}")
    print(f"  Overall Accuracy: {summary['constraint_overall_accuracy']:.1%}")
    print(f"\nAgreement:")
    print(f"  Agreements: {summary['total_agreements']}/{summary['total_results_evaluated']}")
    print(f"  Disagreements: {summary['total_disagreements']}")
    print(f"  Agreement Rate: {summary['overall_agreement_rate']:.1%}")
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
    """Save a human-readable text summary of LLM judge evaluation"""
    with open(output_path, 'w') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("LLM JUDGE EVALUATION SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(f"Model: {results['llm_model']}\n")
        f.write(f"Temperature: {results['temperature']}\n")
        f.write(f"Test Date: {results['test_date']}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("OVERALL SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        summary = results['overall_summary']
        f.write(f"Total Queries: {summary['total_queries']}\n")
        f.write(f"Total Results Evaluated: {summary['total_results_evaluated']}\n\n")
        
        f.write("LLM Judge Performance:\n")
        f.write(f"  - Relevant Results: {summary['llm_total_relevant']}\n")
        f.write(f"  - Overall Accuracy: {summary['llm_overall_accuracy']:.1%}\n\n")
        
        f.write("Constraint-Based Performance:\n")
        f.write(f"  - Relevant Results: {summary['constraint_total_relevant']}\n")
        f.write(f"  - Overall Accuracy: {summary['constraint_overall_accuracy']:.1%}\n\n")
        
        f.write("Agreement Analysis:\n")
        f.write(f"  - Agreements: {summary['total_agreements']}/{summary['total_results_evaluated']}\n")
        f.write(f"  - Disagreements: {summary['total_disagreements']}\n")
        f.write(f"  - Agreement Rate: {summary['overall_agreement_rate']:.1%}\n\n")
        
        # Per-Query Results
        f.write("\n" + "="*80 + "\n")
        f.write("PER-QUERY DETAILED RESULTS\n")
        f.write("="*80 + "\n\n")
        
        for query_data in results['queries']:
            f.write(f"\n{'='*80}\n")
            f.write(f"QUERY #{query_data['query_id']}\n")
            f.write(f"{'='*80}\n")
            f.write(f"{query_data['query_text']}\n\n")
            
            # Metrics comparison
            llm_m = query_data['llm_metrics']
            const_m = query_data['constraint_metrics']
            comp = query_data['comparison']
            
            f.write("METRICS:\n")
            f.write(f"  LLM Judge:         {llm_m['relevant_count']}/{llm_m['total_results']} relevant ({llm_m['accuracy']:.1%})\n")
            f.write(f"  Constraint-Based:  {const_m['relevant_count']}/{const_m['total_results']} relevant ({const_m['accuracy']:.1%})\n")
            f.write(f"  Agreement Rate:    {comp['agreement_rate']:.1%} ({comp['agreements']}/{comp['total_comparisons']})\n")
            f.write(f"  Avg LLM Confidence: {llm_m['avg_confidence']:.2f}\n\n")
            
            # Individual judgments
            f.write("INDIVIDUAL RESULTS:\n")
            f.write("-" * 80 + "\n")
            
            for judgment in query_data['judgments']:
                result_num = judgment['result_num']
                llm_j = judgment['llm_judgment']
                const_e = judgment['constraint_evaluation']
                agree = judgment['agreement']
                
                f.write(f"\nResult #{result_num}:\n")
                f.write(f"  Title: {judgment['title'][:70]}...\n")
                f.write(f"  URL: {judgment['url']}\n\n")
                
                # LLM Judgment
                f.write(f"  LLM JUDGMENT: {'✓ RELEVANT' if llm_j['relevant'] else '✗ NOT RELEVANT'}\n")
                f.write(f"    Confidence: {llm_j['confidence']:.2f}\n")
                f.write(f"    Reasoning: {llm_j['reasoning']}\n")
                f.write(f"    Matched Aspects: {', '.join(llm_j['matched_aspects']) if llm_j['matched_aspects'] else 'None'}\n")
                f.write(f"    Missing Aspects: {', '.join(llm_j['missing_aspects']) if llm_j['missing_aspects'] else 'None'}\n\n")
                
                # Constraint Judgment
                f.write(f"  CONSTRAINT-BASED: {'✓ RELEVANT' if const_e['relevant'] else '✗ NOT RELEVANT'}\n")
                f.write(f"    Confidence: {const_e['confidence']:.2f}\n")
                matched_str = ', '.join([f"{k}:{v}" for k, v in const_e['matched'].items()])
                f.write(f"    Matched: {matched_str}\n\n")
                
                # Agreement status
                if agree:
                    f.write(f"  ✓ AGREEMENT\n")
                else:
                    f.write(f"  ⚠️  DISAGREEMENT\n")
                
                f.write("-" * 80 + "\n")
            
            f.write("\n")
        
        # Footer
        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")


# Example usage
if __name__ == '__main__':
    # Initialize judge with seed for reproducibility
    print("Initializing Gemini Judge...")
    judge = GeminiJudge(model_name="gemini-2.5-flash", seed=42)
    print(f"✓ Using model: {judge.model_name}")
    print(f"✓ Temperature: 0.2 (for reproducibility)\n")
    
    # Path to Ollama benchmark results (use the latest one)
    benchmark_json = '/Users/shreyasbachiraju/uni/circle_capstone/web_llm/ollama_benchmark_20251026_223136.json'
    
    # Run LLM judge evaluation on all benchmark results
    print("🚀 Starting LLM Judge evaluation on Ollama benchmark results...")
    print("This will take a few minutes...\n")
    
    import time
    start_time = time.time()
    
    results = evaluate_ollama_benchmark(benchmark_json, judge)
    
    elapsed = time.time() - start_time
    print(f"✅ Evaluation complete! Total time: {elapsed:.1f}s")
    print("Done! 🎉")
