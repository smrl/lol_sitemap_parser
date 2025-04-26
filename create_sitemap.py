#!/usr/bin/env python3
import argparse
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
from datetime import datetime
import os

def create_sitemap(input_file, output_file):
    """Create a sitemap XML file from a list of URLs."""
    # Read URLs from input file
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Creating sitemap with {len(urls)} URLs...")
    
    # Create root element
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Add URLs
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    for url in urls:
        url_element = ET.SubElement(root, "url")
        loc = ET.SubElement(url_element, "loc")
        loc.text = url
        lastmod = ET.SubElement(url_element, "lastmod")
        lastmod.text = now
    
    # Create XML tree
    tree = ET.ElementTree(root)
    
    # Convert to pretty-printed XML
    xmlstr = ET.tostring(root, encoding='utf-8')
    dom = md.parseString(xmlstr)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"Sitemap created successfully: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")

def create_sitemap_index(sitemap_files, output_file):
    """Create a sitemap index XML file pointing to multiple sitemaps."""
    # Create root element
    root = ET.Element("sitemapindex")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Add sitemaps
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    for sitemap_file in sitemap_files:
        sitemap_element = ET.SubElement(root, "sitemap")
        loc = ET.SubElement(sitemap_element, "loc")
        loc.text = sitemap_file
        lastmod = ET.SubElement(sitemap_element, "lastmod")
        lastmod.text = now
    
    # Create XML tree
    tree = ET.ElementTree(root)
    
    # Convert to pretty-printed XML
    xmlstr = ET.tostring(root, encoding='utf-8')
    dom = md.parseString(xmlstr)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"Sitemap index created successfully: {output_file}")
    print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")

def split_sitemap(input_file, output_dir, url_per_file=5000):
    """Split a large list of URLs into multiple sitemap files."""
    # Read URLs from input file
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Split URLs into chunks
    chunks = [urls[i:i + url_per_file] for i in range(0, len(urls), url_per_file)]
    
    sitemap_files = []
    for i, chunk in enumerate(chunks):
        output_file = os.path.join(output_dir, f"sitemap-{i+1}.xml")
        
        # Create sitemap for this chunk
        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        # Add URLs
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
        for url in chunk:
            url_element = ET.SubElement(root, "url")
            loc = ET.SubElement(url_element, "loc")
            loc.text = url
            lastmod = ET.SubElement(url_element, "lastmod")
            lastmod.text = now
        
        # Convert to pretty-printed XML
        xmlstr = ET.tostring(root, encoding='utf-8')
        dom = md.parseString(xmlstr)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(pretty_xml)
        
        sitemap_files.append(output_file)
        print(f"Created sitemap part {i+1}: {output_file} with {len(chunk)} URLs")
    
    # Create sitemap index if needed
    if len(chunks) > 1:
        index_file = os.path.join(output_dir, "sitemap-index.xml")
        
        # For the index, we need full URLs (assuming these are relative paths)
        sitemap_urls = []
        for file in sitemap_files:
            # Convert relative path to URL (user would need to replace this with actual domain)
            filename = os.path.basename(file)
            sitemap_urls.append(f"https://leagueoflegends.fandom.com/{filename}")
        
        create_sitemap_index(sitemap_urls, index_file)
    
    print(f"Split {len(urls)} URLs into {len(chunks)} sitemap files")

def main():
    parser = argparse.ArgumentParser(description='Create sitemap XML from a list of URLs')
    parser.add_argument('input_file', help='Text file containing URLs, one per line')
    parser.add_argument('--output', '-o', default='sitemap.xml', help='Output sitemap XML file')
    parser.add_argument('--split', '-s', action='store_true', help='Split large sitemap into multiple files')
    parser.add_argument('--output-dir', '-d', default='sitemaps', help='Output directory for split sitemaps')
    parser.add_argument('--urls-per-file', '-u', type=int, default=5000, help='Maximum URLs per sitemap file')
    
    args = parser.parse_args()
    
    if args.split:
        split_sitemap(args.input_file, args.output_dir, args.urls_per_file)
    else:
        create_sitemap(args.input_file, args.output)

if __name__ == "__main__":
    main()