#!/usr/bin/env python3
import re
import argparse
import urllib.parse
from collections import Counter
from pathlib import Path

def analyze_urls(urls_file, output_dir=None):
    """Analyze URLs to identify patterns of organizational pages."""
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Analyzing {len(urls)} URLs...")
    
    # Extract patterns
    patterns = {
        'disambiguation': [],
        'list_pages': [],
        'index_pages': [],
        'category_pages': [],
        'collection_pages': [],
        'admin_pages': [],
        'stub_pages': [],
        'template_pages': [],
        'portal_pages': [],
        'organizational': [],
    }
    
    # General patterns
    for url in urls:
        path = urllib.parse.urlparse(url).path
        page_name = path.split('/')[-1]
        
        # Disambiguation pages
        if '(disambiguation)' in page_name or '_disambiguation' in page_name:
            patterns['disambiguation'].append(url)
        
        # List pages
        if page_name.startswith('List_of_') or '_list' in page_name.lower() or '/List_' in path:
            patterns['list_pages'].append(url)
        
        # Index pages
        if page_name.endswith('_index') or page_name.startswith('Index_of_') or '_index_' in page_name:
            patterns['index_pages'].append(url)
        
        # Category pages (beyond /wiki/Category: which should already be filtered)
        if page_name.startswith('Category:') or '_category' in page_name.lower() or '_categories' in page_name.lower():
            patterns['category_pages'].append(url)
        
        # Collection/grouping pages
        if any(term in page_name.lower() for term in ['collection', 'group', 'series', 'set', 'related', 'overview']):
            patterns['collection_pages'].append(url)
        
        # Administrative/meta pages
        if any(term in page_name.lower() for term in ['admin', 'policy', 'guideline', 'rules', 'help', 'sandbox']):
            patterns['admin_pages'].append(url)
        
        # Stub pages
        if '_stub' in page_name.lower() or 'stub_' in page_name.lower():
            patterns['stub_pages'].append(url)
        
        # Template pages
        if page_name.startswith('Template:') or '_template' in page_name.lower():
            patterns['template_pages'].append(url)
        
        # Portal pages
        if page_name.startswith('Portal:') or 'portal_' in page_name.lower() or '_portal' in page_name.lower():
            patterns['portal_pages'].append(url)
        
        # General organizational indicators
        if any(term in page_name.lower() for term in [
            'navigation', 'redirect', 'table_of_contents', 'toc', 'sitemap', 'contents',
            'directory', 'glossary', 'terminology', 'classifications', 'catalog'
        ]):
            patterns['organizational'].append(url)
    
    # URL structure analysis
    path_components = Counter()
    for url in urls:
        path = urllib.parse.urlparse(url).path
        parts = path.strip('/').split('/')
        if len(parts) > 2:  # more than /wiki/PageName
            for i in range(2, len(parts)):
                path_pattern = '/'.join(parts[:i+1])
                path_components[path_pattern] += 1
    
    # Report findings
    print("\nPotential organizational page patterns found:")
    all_organizational = set()
    
    for pattern_type, urls_list in patterns.items():
        if urls_list:
            print(f"  {pattern_type}: {len(urls_list)} URLs")
            all_organizational.update(urls_list)
    
    print(f"\nTotal unique organizational URLs identified: {len(all_organizational)}")
    
    # Identify frequent URL path patterns
    print("\nCommon URL path patterns (excluding /wiki/PageName):")
    for pattern, count in path_components.most_common(20):
        if count > 5:  # Show only patterns that appear multiple times
            print(f"  {pattern}: {count} occurrences")
    
    # Suggest regex patterns for blacklisting
    print("\nSuggested regex patterns for blacklisting:")
    
    blacklist_suggestions = [
        r'/wiki/.*\(disambiguation\)',
        r'/wiki/List_of_',
        r'/wiki/.*_index',
        r'/wiki/.*_list',
        r'/wiki/.*_collection',
        r'/wiki/.*_overview',
        r'/wiki/.*_catalog',
        r'/wiki/.*_directory',
        r'/wiki/.*_glossary',
    ]
    
    for suggestion in blacklist_suggestions:
        print(f"  {suggestion}")
    
    # Save results if output_dir is provided
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for pattern_type, urls_list in patterns.items():
            if urls_list:
                with open(output_path / f"{pattern_type}_urls.txt", 'w', encoding='utf-8') as f:
                    for url in urls_list:
                        f.write(f"{url}\n")
        
        # Save all organizational URLs in one file
        with open(output_path / "all_organizational_urls.txt", 'w', encoding='utf-8') as f:
            for url in sorted(all_organizational):
                f.write(f"{url}\n")
        
        # Save suggested blacklist patterns
        with open(output_path / "suggested_blacklist_patterns.txt", 'w', encoding='utf-8') as f:
            for pattern in blacklist_suggestions:
                f.write(f"{pattern}\n")
        
        print(f"\nResults saved to {output_dir}/")
    
    return all_organizational

def main():
    parser = argparse.ArgumentParser(description='Find organizational pages in a URL list')
    parser.add_argument('urls_file', help='Path to file containing URLs to analyze')
    parser.add_argument('--output-dir', '-o', default=None, help='Directory to save categorized URLs')
    
    args = parser.parse_args()
    analyze_urls(args.urls_file, args.output_dir)

if __name__ == "__main__":
    main()