#!/usr/bin/env python3
"""
Display query results in readable format
"""

import csv
import os

def show_query_results():
    csv_dir = "outputs/csv"
    files = [f for f in os.listdir(csv_dir) if f.startswith("query_results_") and f.endswith(".csv")]
    if not files:
        print("❌ No query results CSV found")
        return
    
    latest_file = sorted(files)[-1]
    file_path = os.path.join(csv_dir, latest_file)
    
    print(f"📂 Reading from: {latest_file}")
    print("="*80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            if i > 3:  # Show only first 3 queries
                break
                
            print(f"\n🔍 QUERY {row['query_number']}: {row['query_text']}")
            print("🎯 Top Results:")
            print(row['top_results'])
            print("-" * 80)

if __name__ == "__main__":
    show_query_results()
