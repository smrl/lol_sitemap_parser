#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from lxml import etree
from bs4 import BeautifulSoup
import requests
import argparse
from urllib.parse import urlparse
import re
import sys
from pathlib import Path
import json
from collections import Counter
import os

# Predefined blacklist patterns
DEFAULT_BLACKLIST = [
    # Game-specific markers in titles
    r"\(Wild_Rift\)",
    r"\(Legends_of_Runeterra\)",
    r"\(Teamfight_Tactics\)",
    r"\(TFT\)",
    
    # Game-specific paths
    r"/Wild_Rift/",
    r"/Legends_of_Runeterra/",
    r"/Teamfight_Tactics/",
    r"/TFT/",
]

def parse_sitemap_index(file_path):
    """Parse the sitemap index XML file and return all sitemap URLs."""
    try:
        # Try with lxml for better performance and error handling
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        
        # Handle XML namespaces
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        sitemap_urls = []
        for sitemap in root.xpath('.//sm:sitemap/sm:loc', namespaces=ns):
            sitemap_urls.append(sitemap.text)
            
        # If no URLs found, try alternative approach with BeautifulSoup
        if not sitemap_urls:
            return parse_sitemap_index_bs4(file_path)
            
        return sitemap_urls
    except Exception as e:
        print(f"Error parsing with lxml: {e}")
        # Fallback to BeautifulSoup
        return parse_sitemap_index_bs4(file_path)
        
def parse_sitemap_index_bs4(file_path):
    """Parse sitemap index using BeautifulSoup as fallback."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'xml')
    sitemap_urls = []
    
    for loc in soup.find_all('loc'):
        sitemap_urls.append(loc.text)
        
    return sitemap_urls

def download_sitemap(url, output_dir):
    """Download a sitemap from a URL and save it to the output directory."""
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to download {url}")
        return None
    
    # Create a filename based on the URL
    parsed_url = urlparse(url)
    filename = Path(parsed_url.path).name
    if not filename:
        filename = f"sitemap-{hash(url)}.xml"
    
    output_path = Path(output_dir) / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return output_path

def parse_urls_from_sitemap(file_path):
    """Parse URLs from a sitemap XML file."""
    try:
        # Try with lxml for better performance and error handling
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        
        # Handle XML namespaces
        ns = {
            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'news': 'http://www.google.com/schemas/sitemap-news/0.9',
            'n': 'http://www.google.com/schemas/sitemap-news/0.9'
        }
        
        urls = []
        # Try different XML structures that might be present
        loc_elements = root.xpath('.//sm:url/sm:loc', namespaces=ns)
        if not loc_elements:
            # Try without namespace
            loc_elements = root.xpath('.//url/loc')
        
        for url_element in loc_elements:
            urls.append(url_element.text)
        
        # If still no URLs found, try with BeautifulSoup
        if not urls:
            return parse_urls_from_sitemap_bs4(file_path)
        
        return urls
    except Exception as e:
        print(f"Error parsing {file_path} with lxml: {e}")
        return parse_urls_from_sitemap_bs4(file_path)

def parse_urls_from_sitemap_bs4(file_path):
    """Parse URLs from sitemap using BeautifulSoup as fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'xml')
        urls = []
        
        # Try to find all loc elements (could be under url or directly)
        for loc in soup.find_all('loc'):
            # Check if this is part of a sitemap index
            if loc.parent.name != 'sitemap':
                urls.append(loc.text)
        
        return urls
    except Exception as e:
        print(f"Error parsing {file_path} with BeautifulSoup: {e}")
        return []

def filter_urls(urls, blacklist_patterns):
    """Filter URLs based on blacklist patterns."""
    filtered_urls = []
    blacklisted_urls = []
    
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in blacklist_patterns]
    
    for url in urls:
        is_blacklisted = any(pattern.search(url) for pattern in compiled_patterns)
        if is_blacklisted:
            blacklisted_urls.append(url)
        else:
            filtered_urls.append(url)
    
    return filtered_urls, blacklisted_urls

def analyze_urls(urls, top_n=20):
    """Analyze URLs to find common patterns."""
    analysis = {
        "total_urls": len(urls),
        "domains": Counter(),
        "path_components": Counter(),
        "file_extensions": Counter(),
        "common_path_prefixes": Counter(),
        "common_patterns": [],
    }
    
    # Analyze each URL
    for url in urls:
        # Parse URL
        parsed = urlparse(url)
        
        # Count domains
        analysis["domains"][parsed.netloc] += 1
        
        # Count path components
        path_parts = [p for p in parsed.path.split('/') if p]
        for part in path_parts:
            analysis["path_components"][part] += 1
        
        # Count file extensions
        if '.' in path_parts[-1] if path_parts else '':
            ext = path_parts[-1].split('.')[-1]
            analysis["file_extensions"][ext] += 1
        
        # Count common path prefixes (first 1-3 components)
        for i in range(1, min(4, len(path_parts) + 1)):
            prefix = '/'.join(path_parts[:i])
            analysis["common_path_prefixes"][prefix] += 1
    
    # Find potential patterns for filtering
    for component, count in analysis["path_components"].most_common(top_n):
        if count > 10 and any(c.isalpha() for c in component):
            # Check if this is a game-specific component that appears in multiple URLs
            if any(game_name.lower() in component.lower() for game_name in 
                   ["wild rift", "legends of runeterra", "teamfight tactics", "tft"]):
                pattern = re.escape(component)
                analysis["common_patterns"].append({
                    "pattern": pattern,
                    "count": count,
                    "percent": count / len(urls) * 100
                })
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description='Analyze and filter League of Legends sitemaps.')
    parser.add_argument('sitemap_index', help='Path to the sitemap index XML file')
    parser.add_argument('--output-dir', '-o', default='filtered_sitemaps', 
                        help='Directory to save downloaded sitemaps and results')
    parser.add_argument('--blacklist', '-b', action='append', default=None,
                        help='Additional regex patterns to blacklist URLs (can be used multiple times)')
    parser.add_argument('--blacklist-file', type=str, default=None,
                        help='File containing blacklist patterns (one per line)')
    parser.add_argument('--analyze-only', action='store_true',
                        help='Only analyze URLs without filtering')
    parser.add_argument('--no-default-blacklist', action='store_true',
                        help='Do not use the default blacklist patterns')
    parser.add_argument('--search-term', type=str, default=None,
                        help='Search for URLs containing this term and show examples')
    args = parser.parse_args()

    # Set up blacklist patterns
    blacklist_patterns = []
    if not args.no_default_blacklist:
        blacklist_patterns.extend(DEFAULT_BLACKLIST)
    if args.blacklist:
        blacklist_patterns.extend(args.blacklist)
    if args.blacklist_file:
        try:
            with open(args.blacklist_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        blacklist_patterns.append(line)
            print(f"Loaded {len(blacklist_patterns) - len(DEFAULT_BLACKLIST) - (len(args.blacklist) if args.blacklist else 0)} patterns from {args.blacklist_file}")
        except Exception as e:
            print(f"Error loading blacklist file: {e}")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Parse sitemap index
    print(f"Parsing sitemap index: {args.sitemap_index}")
    sitemap_urls = parse_sitemap_index(args.sitemap_index)
    print(f"Found {len(sitemap_urls)} sitemaps in the index")
    
    # Download and parse all sitemaps
    all_urls = []
    for i, sitemap_url in enumerate(sitemap_urls):
        print(f"Downloading sitemap [{i+1}/{len(sitemap_urls)}]: {sitemap_url}")
        sitemap_file = download_sitemap(sitemap_url, output_dir)
        if sitemap_file:
            urls = parse_urls_from_sitemap(sitemap_file)
            print(f"  Found {len(urls)} URLs in sitemap")
            all_urls.extend(urls)
    
    print(f"\nTotal URLs found: {len(all_urls)}")
    
    # Write out all URLs for reference
    all_urls_file = output_dir / "all_urls.txt"
    with open(all_urls_file, 'w', encoding='utf-8') as f:
        for url in all_urls:
            f.write(f"{url}\n")
    
    # Search for specific term if requested
    if args.search_term:
        matching_urls = [url for url in all_urls if args.search_term.lower() in url.lower()]
        print(f"\nFound {len(matching_urls)} URLs containing '{args.search_term}'")
        
        if matching_urls:
            display_count = min(20, len(matching_urls))
            print(f"\nShowing {display_count} examples:")
            for i, url in enumerate(matching_urls[:display_count]):
                print(f"  {i+1}. {url}")
            
            search_results_file = output_dir / f"search_results_{args.search_term}.txt"
            with open(search_results_file, 'w', encoding='utf-8') as f:
                for url in matching_urls:
                    f.write(f"{url}\n")
            print(f"\nSaved search results to: {search_results_file}")
    
    # Analyze URL patterns
    print("\nAnalyzing URL patterns...")
    analysis = analyze_urls(all_urls)
    
    # Save analysis
    analysis_file = output_dir / "url_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2)
    
    # Print summary of analysis
    print(f"\nURL Analysis Summary:")
    print(f"  Total URLs: {analysis['total_urls']}")
    print(f"  Domains: {len(analysis['domains'])}")
    
    print("\nTop path components (might indicate content categories):")
    for component, count in list(analysis["path_components"].items())[:20]:
        if count > 100:  # Only show components that appear frequently
            print(f"  {component}: {count} ({count/analysis['total_urls']*100:.2f}%)")
    
    print("\nPotential patterns for blacklisting:")
    for pattern_info in analysis["common_patterns"]:
        print(f"  {pattern_info['pattern']}: {pattern_info['count']} matches ({pattern_info['percent']:.2f}%)")
    
    # If we're only analyzing, stop here
    if args.analyze_only:
        print(f"\nAnalysis complete. Results saved to {analysis_file}")
        return
    
    # Filter URLs
    filtered_urls, blacklisted_urls = filter_urls(all_urls, blacklist_patterns)
    
    # Save results
    output_file = output_dir / "filtered_urls.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in filtered_urls:
            f.write(f"{url}\n")
    
    blacklist_output = output_dir / "blacklisted_urls.txt"
    with open(blacklist_output, 'w', encoding='utf-8') as f:
        for url in blacklisted_urls:
            f.write(f"{url}\n")
    
    patterns_output = output_dir / "blacklist_patterns.txt"
    with open(patterns_output, 'w', encoding='utf-8') as f:
        for pattern in blacklist_patterns:
            f.write(f"{pattern}\n")
    
    print(f"\nFiltering Results:")
    print(f"  Total URLs: {len(all_urls)}")
    print(f"  Filtered URLs (kept): {len(filtered_urls)} ({len(filtered_urls)/len(all_urls)*100:.2f}%)")
    print(f"  Blacklisted URLs: {len(blacklisted_urls)} ({len(blacklisted_urls)/len(all_urls)*100:.2f}%)")
    print(f"\nSaved filtered URLs to: {output_file}")
    print(f"Saved blacklisted URLs to: {blacklist_output}")
    print(f"Saved blacklist patterns to: {patterns_output}")
    
    # Sample of filtered URLs
    print("\nSample of filtered (kept) URLs:")
    sample_size = min(5, len(filtered_urls))
    for i, url in enumerate(filtered_urls[:sample_size]):
        print(f"  {i+1}. {url}")
    
    # Sample of blacklisted URLs
    print("\nSample of blacklisted URLs:")
    sample_size = min(5, len(blacklisted_urls))
    for i, url in enumerate(blacklisted_urls[:sample_size]):
        print(f"  {i+1}. {url}")

if __name__ == "__main__":
    main()