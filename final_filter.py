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

# Patterns to blacklist
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
    
    # Game-specific pattern in URL paths
    r"\w+/TFT$",
    r"Category:Wild_Rift",
    r"Category:Teamfight_Tactics",
    r"Category:TFT",
    r"Category:Legends_of_Runeterra",
    
    # Valorant content
    r"/Valorant",
    r"Category:Valorant",
]

# Whitelist patterns - these should be kept even if they match a blacklist pattern
WHITELIST = [
    # Core League content
    r"/wiki/League_of_Legends$",
    r"/wiki/Champion$",
    r"/wiki/Runeterra$",  # Keep main Runeterra lore page
]

def parse_sitemap_index(file_path):
    """Parse the sitemap index XML file and return all sitemap URLs."""
    try:
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()
        
        # Handle XML namespaces
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        sitemap_urls = []
        for sitemap in root.xpath('.//sm:sitemap/sm:loc', namespaces=ns):
            sitemap_urls.append(sitemap.text)
            
        if not sitemap_urls:
            return parse_sitemap_index_bs4(file_path)
            
        return sitemap_urls
    except Exception as e:
        print(f"Error parsing with lxml: {e}")
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
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to download {url}: Status code {response.status_code}")
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
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def parse_urls_from_sitemap(file_path):
    """Parse URLs from a sitemap XML file."""
    try:
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

def filter_urls(urls, blacklist_patterns, whitelist_patterns=None):
    """Filter URLs based on blacklist patterns with whitelist override."""
    filtered_urls = []
    blacklisted_urls = []
    
    # Compile patterns
    compiled_blacklist = [re.compile(pattern, re.IGNORECASE) for pattern in blacklist_patterns]
    compiled_whitelist = [re.compile(pattern, re.IGNORECASE) for pattern in whitelist_patterns] if whitelist_patterns else []
    
    for url in urls:
        # Check if URL matches any whitelist pattern
        is_whitelisted = any(pattern.search(url) for pattern in compiled_whitelist) if compiled_whitelist else False
        
        # If whitelisted, include regardless of blacklist
        if is_whitelisted:
            filtered_urls.append(url)
            continue
            
        # Otherwise, check blacklist
        is_blacklisted = any(pattern.search(url) for pattern in compiled_blacklist)
        if is_blacklisted:
            blacklisted_urls.append(url)
        else:
            filtered_urls.append(url)
    
    return filtered_urls, blacklisted_urls

def analyze_urls_by_path(urls):
    """Analyze URL structure by path components to identify patterns."""
    # Group URLs by their path structure
    path_patterns = Counter()
    
    for url in urls:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        # Create a generalized pattern
        if len(path_parts) > 1:
            if path_parts[0] == 'wiki':
                # Handle common URL patterns
                if len(path_parts) == 2:
                    # Simple wiki page
                    path_patterns[f"wiki/{path_parts[1]}"] += 1
                elif len(path_parts) == 3:
                    # Pattern like /wiki/Champion/LoL
                    path_patterns[f"wiki/{path_parts[1]}/{path_parts[2]}"] += 1
    
    return path_patterns

def main():
    parser = argparse.ArgumentParser(description='Filter League of Legends content from sitemaps.')
    parser.add_argument('sitemap_index', help='Path to the sitemap index XML file')
    parser.add_argument('--output-dir', '-o', default='filtered_lol', 
                        help='Directory to save downloaded sitemaps and results')
    parser.add_argument('--blacklist-file', type=str, default=None,
                        help='File containing additional blacklist patterns (one per line)')
    parser.add_argument('--whitelist-file', type=str, default=None,
                        help='File containing whitelist patterns (one per line)')
    parser.add_argument('--analyze-only', action='store_true',
                        help='Only analyze URLs without filtering')
    parser.add_argument('--url-categories', action='store_true',
                        help='Group URLs by categories and save to separate files')
    parser.add_argument('--no-default-blacklist', action='store_true',
                        help='Do not use the default blacklist patterns')
    args = parser.parse_args()

    # Set up blacklist patterns
    blacklist_patterns = []
    if not args.no_default_blacklist:
        blacklist_patterns.extend(DEFAULT_BLACKLIST)
    
    # Load additional blacklist patterns
    if args.blacklist_file:
        try:
            with open(args.blacklist_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        blacklist_patterns.append(line)
            print(f"Loaded {len(blacklist_patterns) - len(DEFAULT_BLACKLIST)} additional blacklist patterns")
        except Exception as e:
            print(f"Error loading blacklist file: {e}")
    
    # Set up whitelist patterns
    whitelist_patterns = WHITELIST.copy()
    
    # Load additional whitelist patterns
    if args.whitelist_file:
        try:
            with open(args.whitelist_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        whitelist_patterns.append(line)
            print(f"Loaded {len(whitelist_patterns) - len(WHITELIST)} additional whitelist patterns")
        except Exception as e:
            print(f"Error loading whitelist file: {e}")

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
        print(f"Processing sitemap [{i+1}/{len(sitemap_urls)}]: {sitemap_url}")
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
    
    # Filter URLs
    filtered_urls, blacklisted_urls = filter_urls(all_urls, blacklist_patterns, whitelist_patterns)
    
    # Save blacklist and whitelist patterns
    with open(output_dir / "blacklist_patterns.txt", 'w', encoding='utf-8') as f:
        for pattern in blacklist_patterns:
            f.write(f"{pattern}\n")
    
    with open(output_dir / "whitelist_patterns.txt", 'w', encoding='utf-8') as f:
        for pattern in whitelist_patterns:
            f.write(f"{pattern}\n")
    
    # Analyze URL patterns by path
    print("\nAnalyzing URL patterns by path structure...")
    path_patterns = analyze_urls_by_path(filtered_urls)
    
    # Save path pattern analysis
    with open(output_dir / "path_patterns.json", 'w', encoding='utf-8') as f:
        # Convert Counter to dict for JSON serialization
        json.dump({"path_patterns": {k: v for k, v in path_patterns.most_common()}}, f, indent=2)
    
    # Print top path patterns
    print("\nTop URL path patterns (after filtering):")
    for pattern, count in path_patterns.most_common(10):
        print(f"  {pattern}: {count} URLs")
    
    # Group URLs by categories if requested
    if args.url_categories:
        # Define categories by regex patterns
        categories = {
            "champions": r"/wiki/[\w%']+/LoL$",
            "items": r"/wiki/[\w%']+_(item)$|/wiki/Item:",
            "runes": r"/wiki/Rune",
            "summoner_spells": r"/wiki/Summoner",
            "maps": r"/wiki/Map",
            "lore": r"/wiki/Runeterra|/wiki/Universe",
            "game_modes": r"/wiki/Game_modes|/wiki/Clash|/wiki/ARAM|/wiki/URF",
        }
        
        # Group URLs
        categorized_urls = {category: [] for category in categories}
        uncategorized = []
        
        for url in filtered_urls:
            categorized = False
            for category, pattern in categories.items():
                if re.search(pattern, url, re.IGNORECASE):
                    categorized_urls[category].append(url)
                    categorized = True
                    break
            
            if not categorized:
                uncategorized.append(url)
        
        # Save categorized URLs
        for category, urls in categorized_urls.items():
            with open(output_dir / f"{category}_urls.txt", 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(f"{url}\n")
            print(f"  {category}: {len(urls)} URLs")
        
        # Save uncategorized URLs
        with open(output_dir / "uncategorized_urls.txt", 'w', encoding='utf-8') as f:
            for url in uncategorized:
                f.write(f"{url}\n")
        print(f"  uncategorized: {len(uncategorized)} URLs")
    
    # Save filtered and blacklisted URLs
    output_file = output_dir / "filtered_urls.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in filtered_urls:
            f.write(f"{url}\n")
    
    blacklist_output = output_dir / "blacklisted_urls.txt"
    with open(blacklist_output, 'w', encoding='utf-8') as f:
        for url in blacklisted_urls:
            f.write(f"{url}\n")
    
    print(f"\nFiltering Results:")
    print(f"  Total URLs: {len(all_urls)}")
    print(f"  Filtered URLs (kept): {len(filtered_urls)} ({len(filtered_urls)/len(all_urls)*100:.2f}%)")
    print(f"  Blacklisted URLs: {len(blacklisted_urls)} ({len(blacklisted_urls)/len(all_urls)*100:.2f}%)")
    print(f"\nSaved filtered URLs to: {output_file}")
    print(f"Saved blacklisted URLs to: {blacklist_output}")
    
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