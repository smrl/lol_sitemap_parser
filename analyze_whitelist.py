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
        loc_elements = root.xpath('.//sm:url/sm:loc', namespaces=ns)
        if not loc_elements:
            loc_elements = root.xpath('.//url/loc')
        
        for url_element in loc_elements:
            urls.append(url_element.text)
        
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
        
        for loc in soup.find_all('loc'):
            if loc.parent.name != 'sitemap':
                urls.append(loc.text)
        
        return urls
    except Exception as e:
        print(f"Error parsing {file_path} with BeautifulSoup: {e}")
        return []

def read_pattern_file(file_path):
    """Read patterns from a file and return them as a list."""
    patterns = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
        return patterns
    except Exception as e:
        print(f"Error reading pattern file {file_path}: {e}")
        return []

def analyze_patterns(urls, whitelist_patterns, blacklist_patterns=None):
    """Analyze how patterns match URLs."""
    compiled_whitelist = [re.compile(pattern, re.IGNORECASE) for pattern in whitelist_patterns]
    
    if blacklist_patterns:
        compiled_blacklist = [re.compile(pattern, re.IGNORECASE) for pattern in blacklist_patterns]
    else:
        compiled_blacklist = []
    
    # Match counts
    whitelist_matches = {}
    for pattern in whitelist_patterns:
        whitelist_matches[pattern] = 0
    
    blacklist_matches = {}
    for pattern in blacklist_patterns or []:
        blacklist_matches[pattern] = 0
    
    # URL categorization
    whitelist_only = []
    blacklist_only = []
    both_match = []
    neither_match = []
    
    for url in urls:
        w_match = any(re.search(pattern, url, re.IGNORECASE) for pattern in whitelist_patterns)
        b_match = blacklist_patterns and any(re.search(pattern, url, re.IGNORECASE) for pattern in blacklist_patterns)
        
        # Count individual pattern matches
        for i, pattern in enumerate(whitelist_patterns):
            if re.search(pattern, url, re.IGNORECASE):
                whitelist_matches[pattern] += 1
        
        if blacklist_patterns:
            for i, pattern in enumerate(blacklist_patterns):
                if re.search(pattern, url, re.IGNORECASE):
                    blacklist_matches[pattern] += 1
        
        # Categorize URL
        if w_match and not b_match:
            whitelist_only.append(url)
        elif b_match and not w_match:
            blacklist_only.append(url)
        elif w_match and b_match:
            both_match.append(url)
        else:
            neither_match.append(url)
    
    return {
        'whitelist_only': whitelist_only,
        'blacklist_only': blacklist_only,
        'both_match': both_match,
        'neither_match': neither_match,
        'whitelist_matches': whitelist_matches,
        'blacklist_matches': blacklist_matches
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze whitelist and blacklist pattern matching.')
    parser.add_argument('sitemap_index', help='Path to the sitemap index XML file')
    parser.add_argument('--output-dir', '-o', default='whitelist_analysis', 
                        help='Directory to save analysis results')
    parser.add_argument('--whitelist-file', '-w', required=True,
                        help='File containing whitelist patterns (one per line)')
    parser.add_argument('--blacklist-file', '-b', default=None,
                        help='File containing blacklist patterns (one per line)')
    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Load patterns
    whitelist_patterns = read_pattern_file(args.whitelist_file)
    print(f"Loaded {len(whitelist_patterns)} whitelist patterns")
    
    blacklist_patterns = None
    if args.blacklist_file:
        blacklist_patterns = read_pattern_file(args.blacklist_file)
        print(f"Loaded {len(blacklist_patterns)} blacklist patterns")
    
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
    
    # Analyze pattern matching
    analysis = analyze_patterns(all_urls, whitelist_patterns, blacklist_patterns)
    
    # Print summary
    print("\nPattern Matching Summary:")
    print(f"  URLs matching whitelist only: {len(analysis['whitelist_only'])} ({len(analysis['whitelist_only'])/len(all_urls)*100:.2f}%)")
    if blacklist_patterns:
        print(f"  URLs matching blacklist only: {len(analysis['blacklist_only'])} ({len(analysis['blacklist_only'])/len(all_urls)*100:.2f}%)")
        print(f"  URLs matching both whitelist and blacklist: {len(analysis['both_match'])} ({len(analysis['both_match'])/len(all_urls)*100:.2f}%)")
    print(f"  URLs matching neither: {len(analysis['neither_match'])} ({len(analysis['neither_match'])/len(all_urls)*100:.2f}%)")
    
    # Save results
    with open(output_dir / "whitelist_only.txt", 'w', encoding='utf-8') as f:
        for url in analysis['whitelist_only']:
            f.write(f"{url}\n")
    
    if blacklist_patterns:
        with open(output_dir / "blacklist_only.txt", 'w', encoding='utf-8') as f:
            for url in analysis['blacklist_only']:
                f.write(f"{url}\n")
        
        with open(output_dir / "both_match.txt", 'w', encoding='utf-8') as f:
            for url in analysis['both_match']:
                f.write(f"{url}\n")
    
    with open(output_dir / "neither_match.txt", 'w', encoding='utf-8') as f:
        for url in analysis['neither_match']:
            f.write(f"{url}\n")
    
    # Save pattern match counts
    whitelist_counts = [(pattern, count) for pattern, count in analysis['whitelist_matches'].items()]
    whitelist_counts.sort(key=lambda x: x[1], reverse=True)
    
    with open(output_dir / "whitelist_pattern_counts.txt", 'w', encoding='utf-8') as f:
        for pattern, count in whitelist_counts:
            f.write(f"{pattern}: {count} matches\n")
    
    if blacklist_patterns:
        blacklist_counts = [(pattern, count) for pattern, count in analysis['blacklist_matches'].items()]
        blacklist_counts.sort(key=lambda x: x[1], reverse=True)
        
        with open(output_dir / "blacklist_pattern_counts.txt", 'w', encoding='utf-8') as f:
            for pattern, count in blacklist_counts:
                f.write(f"{pattern}: {count} matches\n")
    
    # Print top matching patterns
    print("\nTop 10 whitelist patterns by match count:")
    for pattern, count in whitelist_counts[:10]:
        print(f"  {pattern}: {count} matches")
    
    if blacklist_patterns:
        print("\nTop 10 blacklist patterns by match count:")
        for pattern, count in blacklist_counts[:10]:
            print(f"  {pattern}: {count} matches")
    
    print(f"\nAnalysis complete. Results saved to {args.output_dir}/")

if __name__ == "__main__":
    main()