#!/usr/bin/env python3
"""Quick script to generate text summary from LLM judge JSON results"""

import json
import sys

def generate_text_summary(json_path: str, txt_path: str):
    # Load JSON
    with open(json_path, 'r') as f:
        results = json.load(f)
    
    with open(txt_path, 'w') as f:
        # Header
        f.write("="*80 + "\n")
        f.write("LLM JUDGE EVALUATION SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(f"Model: {results['llm_model']}\n")
        f.write(f"Temperature: 0.2\n")
        f.write(f"Test Date: {results['test_date']}\n")
        f.write("\n" + "="*80 + "\n")
        f.write("OVERALL SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        summary = results['overall_summary']
        f.write(f"Total Queries: {summary['total_queries']}\n")
        f.write(f"Total Results Evaluated: {summary['total_results_evaluated']}\n\n")
        
        f.write("LLM Judge Performance:\n")
        f.write(f"  - Relevant Results: {summary['llm_total_relevant']}\n")
        f.write(f"  - Overall Accuracy: {summary['llm_overall_accuracy']*100:.1f}%\n\n")
        
        f.write("Constraint-Based Performance:\n")
        f.write(f"  - Relevant Results: {summary['constraint_total_relevant']}\n")
        f.write(f"  - Overall Accuracy: {summary['constraint_overall_accuracy']*100:.1f}%\n\n")
        
        f.write("Agreement Analysis:\n")
        f.write(f"  - Agreements: {summary['total_agreements']}/{summary['total_results_evaluated']}\n")
        f.write(f"  - Disagreements: {summary['total_disagreements']}\n")
        f.write(f"  - Agreement Rate: {summary['overall_agreement_rate']*100:.1f}%\n\n")
        
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
            f.write(f"  LLM Judge:         {llm_m['relevant_count']}/{llm_m['total_results']} relevant ({llm_m['accuracy']*100:.1f}%)\n")
            f.write(f"  Constraint-Based:  {const_m['relevant_count']}/{const_m['total_results']} relevant ({const_m['accuracy']*100:.1f}%)\n")
            f.write(f"  Agreement Rate:    {comp['agreement_rate']*100:.1f}% ({comp['agreements']}/{comp['total_comparisons']})\n")
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
    
    print(f"✅ Text summary saved to: {txt_path}")

if __name__ == "__main__":
    json_file = "ollama_benchmark_20251030_015843_llm_judge.json"
    txt_file = "ollama_benchmark_20251030_015843_llm_judge.txt"
    
    generate_text_summary(json_file, txt_file)
