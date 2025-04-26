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

# Predefined blacklist patterns - be careful with shared lore terms
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
    
    # Avoid filtering shared lore terms like "Runeterra" which is the world all games are set in
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

def interactive_blacklist_builder(urls, initial_blacklist=None):
    """Interactively build a blacklist by examining sample URLs."""
    if initial_blacklist is None:
        blacklist = []
    else:
        blacklist = list(initial_blacklist)
    
    compiled_blacklist = [re.compile(pattern, re.IGNORECASE) for pattern in blacklist]
    
    # Show existing patterns first
    if blacklist:
        print("\nExisting blacklist patterns:")
        for i, pattern in enumerate(blacklist):
            print(f"  {i+1}. {pattern}")

    # Sample a subset of URLs for examination
    print("\nHow many sample URLs would you like to examine? (default: 20)")
    try:
        user_sample_size = input("> ")
        sample_size = int(user_sample_size) if user_sample_size.strip() else 20
    except ValueError:
        sample_size = 20
    
    sample_size = min(sample_size, len(urls))
    import random
    sample_urls = random.sample(urls, sample_size)
    
    # Option to search for specific terms in URLs
    print("\nWould you like to search for specific terms in the URLs? (y/n)")
    if input("> ").lower() == 'y':
        while True:
            term = input("Enter term to search (or 'q' to quit search mode): ")
            if term.lower() == 'q':
                break
            
            matching_urls = [url for url in urls if term.lower() in url.lower()]
            print(f"Found {len(matching_urls)} URLs containing '{term}'")
            
            if matching_urls:
                display_count = min(5, len(matching_urls))
                print(f"\nShowing {display_count} examples:")
                for i, url in enumerate(matching_urls[:display_count]):
                    print(f"  {i+1}. {url}")
                
                print(f"\nWould you like to add a blacklist pattern for '{term}'? (y/n)")
                if input("> ").lower() == 'y':
                    pattern = input(f"Enter regex pattern [default: {re.escape(term)}]: ")
                    if not pattern:
                        pattern = re.escape(term)
                    
                    try:
                        re.compile(pattern)
                        blacklist.append(pattern)
                        compiled_blacklist.append(re.compile(pattern, re.IGNORECASE))
                        print(f"Added pattern: {pattern}")
                    except re.error:
                        print("Invalid regex pattern.")
    
    # Continue with random sampling
    print(f"\nExamining {sample_size} sample URLs to build blacklist patterns:")
    for i, url in enumerate(sample_urls):
        print(f"\n[{i+1}/{sample_size}] {url}")
        
        # Check if already matched by existing patterns
        matches = [pattern.pattern for pattern in compiled_blacklist if pattern.search(url)]
        if matches:
            print(f"  Already matched by patterns: {', '.join(matches)}")
            continue
        
        # Show URL parts to help with pattern creation
        parsed = urlparse(url)
        path_parts = parsed.path.split('/')
        print(f"  Domain: {parsed.netloc}")
        print(f"  Path: {parsed.path}")
        if path_parts:
            print(f"  Last path component: {path_parts[-1] if path_parts[-1] else path_parts[-2] if len(path_parts) > 1 else ''}")
        
        response = input("Blacklist this URL? [y/n/p/s/q] (p=add pattern, s=skip rest, q=quit): ").lower()
        
        if response == 'y':
            # Extract a reasonable pattern from the URL
            suggestion = path_parts[-1] if path_parts[-1] else path_parts[-2] if len(path_parts) > 1 else ""
            
            pattern = input(f"Enter regex pattern to match this URL [default: {suggestion}]: ")
            if not pattern and suggestion:
                pattern = re.escape(suggestion)
            
            if pattern:
                try:
                    # Test if it's a valid regex
                    re.compile(pattern)
                    blacklist.append(pattern)
                    compiled_blacklist.append(re.compile(pattern, re.IGNORECASE))
                    print(f"Added pattern: {pattern}")
                    
                    # Show how many URLs this would match
                    matches = sum(1 for url in urls if re.search(pattern, url, re.IGNORECASE))
                    print(f"This pattern would match {matches} URLs ({matches/len(urls)*100:.2f}% of total)")
                except re.error:
                    print("Invalid regex pattern.")
        elif response == 'p':
            pattern = input("Enter regex pattern to add to blacklist: ")
            if pattern:
                try:
                    re.compile(pattern)
                    blacklist.append(pattern)
                    compiled_blacklist.append(re.compile(pattern, re.IGNORECASE))
                    print(f"Added pattern: {pattern}")
                    
                    # Show how many URLs this would match
                    matches = sum(1 for url in urls if re.search(pattern, url, re.IGNORECASE))
                    print(f"This pattern would match {matches} URLs ({matches/len(urls)*100:.2f}% of total)")
                except re.error:
                    print("Invalid regex pattern.")
        elif response == 's':
            print("Skipping remaining URLs...")
            break
        elif response == 'q':
            break
    
    return blacklist

def main():
    parser = argparse.ArgumentParser(description='Filter League of Legends sitemaps.')
    parser.add_argument('sitemap_index', help='Path to the sitemap index XML file')
    parser.add_argument('--output-dir', '-o', default='filtered_sitemaps', 
                        help='Directory to save downloaded sitemaps and results')
    parser.add_argument('--blacklist', '-b', action='append', default=None,
                        help='Additional regex patterns to blacklist URLs (can be used multiple times)')
    parser.add_argument('--blacklist-file', type=str, default=None,
                        help='File containing blacklist patterns (one per line)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Enter interactive mode to build blacklist patterns')
    parser.add_argument('--no-default-blacklist', action='store_true',
                        help='Do not use the default blacklist patterns')
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
    for sitemap_url in sitemap_urls:
        print(f"Downloading sitemap: {sitemap_url}")
        sitemap_file = download_sitemap(sitemap_url, output_dir)
        if sitemap_file:
            urls = parse_urls_from_sitemap(sitemap_file)
            print(f"  Found {len(urls)} URLs in sitemap")
            all_urls.extend(urls)
    
    print(f"Total URLs found: {len(all_urls)}")
    
    # Interactive blacklist building
    if args.interactive:
        blacklist_patterns = interactive_blacklist_builder(all_urls, blacklist_patterns)
        print("\nFinal blacklist patterns:")
        for pattern in blacklist_patterns:
            print(f"  {pattern}")
    
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
    
    print(f"\nResults:")
    print(f"  Total URLs: {len(all_urls)}")
    print(f"  Filtered URLs: {len(filtered_urls)}")
    print(f"  Blacklisted URLs: {len(blacklisted_urls)}")
    print(f"\nSaved filtered URLs to: {output_file}")
    print(f"Saved blacklisted URLs to: {blacklist_output}")
    print(f"Saved blacklist patterns to: {patterns_output}")

if __name__ == "__main__":
    main()