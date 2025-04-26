#!/usr/bin/env python3
import re
import argparse
import urllib.parse
from collections import Counter
from pathlib import Path

def analyze_path_structure(urls_file, output_dir):
    """Analyze URL path structure to identify common patterns."""
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Analyzing path structure of {len(urls)} URLs...")
    
    # Extract path components
    page_names = []
    path_structures = Counter()
    path_prefixes = Counter()
    path_components = Counter()
    
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path
        
        # Get the page name (last part of path)
        page_name = path.split('/')[-1]
        page_names.append(page_name)
        
        # Analyze path structure
        parts = path.strip('/').split('/')
        
        # Count overall path structures
        path_structure = '/'.join([f"{i}:{part}" for i, part in enumerate(parts)])
        path_structures[path_structure] += 1
        
        # Count path prefixes (e.g., /wiki/Champion/, /wiki/Item/)
        if len(parts) >= 2:
            prefix = '/'.join(parts[:2])
            path_prefixes[prefix] += 1
            
            # If there's a deeper structure, count that too
            if len(parts) > 2:
                deeper_prefix = '/'.join(parts[:3])
                path_prefixes[deeper_prefix] += 1
        
        # Count individual path components
        for part in parts:
            path_components[part] += 1
    
    # Analyze page names for patterns
    page_name_patterns = Counter()
    
    for name in page_names:
        # Check for parentheses patterns like "X_(Y)"
        if '(' in name and ')' in name:
            pattern = name.split('(')[0] + '(*)'
            page_name_patterns[pattern] += 1
            
            # Extract what's in the parentheses
            try:
                in_parens = re.search(r'\((.*?)\)', name).group(1)
                parens_pattern = f"*({in_parens})"
                page_name_patterns[parens_pattern] += 1
            except:
                pass
        
        # Check for underscore patterns
        if '_' in name:
            parts = name.split('_')
            if len(parts) > 2:
                prefix_pattern = f"{parts[0]}_*"
                page_name_patterns[prefix_pattern] += 1
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Save frequent path structures
    with open(output_path / "path_structures.txt", 'w', encoding='utf-8') as f:
        f.write(f"Common URL path structures (frequency):\\n\\n")
        for structure, count in path_structures.most_common(30):
            f.write(f"{structure}: {count}\\n")
    
    # Save frequent path prefixes
    with open(output_path / "path_prefixes.txt", 'w', encoding='utf-8') as f:
        f.write(f"Common URL path prefixes (frequency):\\n\\n")
        for prefix, count in path_prefixes.most_common(50):
            if count > 5:  # Only include prefixes that appear multiple times
                f.write(f"{prefix}: {count}\\n")
    
    # Save frequent page name patterns
    with open(output_path / "page_name_patterns.txt", 'w', encoding='utf-8') as f:
        f.write(f"Common page name patterns (frequency):\\n\\n")
        for pattern, count in page_name_patterns.most_common(50):
            if count > 5:  # Only include patterns that appear multiple times
                f.write(f"{pattern}: {count}\\n")
    
    # Generate blacklist suggestions
    with open(output_path / "blacklist_suggestions.txt", 'w', encoding='utf-8') as f:
        f.write("# Suggested blacklist patterns based on path analysis:\\n\\n")
        
        # Add suggestions based on path prefixes
        f.write("# Common path prefixes to consider blacklisting:\\n")
        for prefix, count in path_prefixes.most_common(30):
            if count > 20 and 'Category' not in prefix and 'champion' not in prefix.lower():
                f.write(f"/wiki/{prefix.split('/')[-1]}/  # {count} URLs\\n")
        
        # Add suggestions based on page name patterns
        f.write("\\n# Common page name patterns to consider blacklisting:\\n")
        for pattern, count in page_name_patterns.most_common(30):
            if count > 20 and '(*)' in pattern:
                base = pattern.split('(')[0]
                if base and len(base) > 2:
                    f.write(f"/wiki/{base}\\(.*\\)  # {count} URLs\\n")
            elif count > 20 and '_*' in pattern:
                base = pattern.split('_')[0]
                if base and len(base) > 2:
                    f.write(f"/wiki/{base}_  # {count} URLs\\n")
    
    # Print summary
    print("\nPath structure analysis complete. Results saved to:")
    print(f"  {output_path}/path_structures.txt")
    print(f"  {output_path}/path_prefixes.txt")
    print(f"  {output_path}/page_name_patterns.txt")
    print(f"  {output_path}/blacklist_suggestions.txt")
    
    # Print top path prefixes
    print("\nTop path prefixes (potential patterns to blacklist):")
    for prefix, count in path_prefixes.most_common(10):
        if count > 50:
            print(f"  {prefix}: {count} occurrences")
    
    # Print top page name patterns
    print("\nTop page name patterns (potential patterns to blacklist):")
    for pattern, count in page_name_patterns.most_common(10):
        if count > 50:
            print(f"  {pattern}: {count} occurrences")

def main():
    parser = argparse.ArgumentParser(description='Analyze URL path structure for pattern recognition')
    parser.add_argument('urls_file', help='Path to file containing URLs to analyze')
    parser.add_argument('--output-dir', '-o', default='path_analysis', 
                        help='Directory to save analysis results')
    
    args = parser.parse_args()
    analyze_path_structure(args.urls_file, args.output_dir)

if __name__ == "__main__":
    main()