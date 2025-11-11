"""
Run LLM Judge on Ollama Benchmark Results

Evaluates all search results from the Ollama benchmark using Gemini as a judge,
then compares LLM judgments with constraint-based evaluations.
"""

import json
import time
from typing import Dict, List, Any
from llm_judge import GeminiJudge, compare_with_constraint_based

def load_benchmark_results(json_path: str) -> Dict[str, Any]:
    """Load Ollama benchmark results from JSON file"""
    with open(json_path, 'r') as f:
        return json.load(f)

def run_llm_evaluation(benchmark_data: Dict[str, Any], judge: GeminiJudge) -> Dict[str, Any]:
    """
    Run LLM judge on all benchmark results
    
    Returns:
        Dict with per-query LLM judgments and comparison metrics
    """
    all_results = {
        'test_date': benchmark_data['test_date'],
        'llm_model': judge.model_name,
        'queries': []
    }
    
    total_llm_relevant = 0
    total_constraint_relevant = 0
    total_agreements = 0
    total_results_evaluated = 0
    
    for query_result in benchmark_data['results']:
        query_id = query_result['query_id']
        query_text = query_result['query_text']
        
        print(f"\n{'='*80}")
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
    
    # Calculate overall statistics
    all_results['overall_summary'] = {
        'total_queries': len(benchmark_data['results']),
        'total_results_evaluated': total_results_evaluated,
        'llm_total_relevant': total_llm_relevant,
        'constraint_total_relevant': total_constraint_relevant,
        'total_agreements': total_agreements,
        'total_disagreements': total_results_evaluated - total_agreements,
        'overall_agreement_rate': total_agreements / total_results_evaluated if total_results_evaluated > 0 else 0.0,
        'llm_overall_accuracy': total_llm_relevant / total_results_evaluated if total_results_evaluated > 0 else 0.0,
        'constraint_overall_accuracy': total_constraint_relevant / total_results_evaluated if total_results_evaluated > 0 else 0.0
    }
    
    return all_results

def save_results(results: Dict[str, Any], output_path: str):
    """Save LLM judge results to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {output_path}")

def print_final_summary(results: Dict[str, Any]):
    """Print final summary of LLM judge evaluation"""
    summary = results['overall_summary']
    
    print(f"\n{'='*80}")
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

if __name__ == '__main__':
    # Paths
    benchmark_json = '/Users/shreyasbachiraju/uni/circle_capstone/ollama_benchmark_20251030_015843.json'
    output_json = '/Users/shreyasbachiraju/uni/circle_capstone/ollama_benchmark_20251030_015843_llm_judge.json'
    
    # Initialize LLM judge
    print("Initializing Gemini Judge...")
    judge = GeminiJudge(model_name="gemini-2.5-flash", seed=42)
    print(f"✓ Using model: {judge.model_name}")
    print(f"✓ Temperature: 0.2 (for reproducibility)")
    
    # Load benchmark data
    print(f"\nLoading benchmark results from: {benchmark_json}")
    benchmark_data = load_benchmark_results(benchmark_json)
    print(f"✓ Loaded {len(benchmark_data['results'])} queries with {sum(r['total_results'] for r in benchmark_data['results'])} total results")
    
    # Run LLM evaluation
    print("\n🚀 Starting LLM Judge evaluation...")
    print("This will take a few minutes...")
    
    start_time = time.time()
    results = run_llm_evaluation(benchmark_data, judge)
    elapsed = time.time() - start_time
    
    print(f"\n✅ Evaluation complete! ({elapsed:.1f}s)")
    
    # Print final summary
    print_final_summary(results)
    
    # Save results
    save_results(results, output_json)
    
    print("Done! 🎉")
