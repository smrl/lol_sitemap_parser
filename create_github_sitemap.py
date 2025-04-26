#!/usr/bin/env python3
import xml.dom.minidom as md
import xml.etree.ElementTree as ET
from datetime import datetime
import os

def create_github_sitemap_index(repo_owner, repo_name, branch, output_file, sitemap_count=3):
    """Create a sitemap index XML file with GitHub raw content URLs."""
    # Create root element
    root = ET.Element("sitemapindex")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Add sitemaps
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    base_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/lol_narrative_sitemaps"
    
    for i in range(1, sitemap_count + 1):
        sitemap_element = ET.SubElement(root, "sitemap")
        loc = ET.SubElement(sitemap_element, "loc")
        loc.text = f"{base_url}/sitemap-{i}.xml"
        lastmod = ET.SubElement(sitemap_element, "lastmod")
        lastmod.text = now
    
    # Convert to pretty-printed XML
    xmlstr = ET.tostring(root, encoding='utf-8')
    dom = md.parseString(xmlstr)
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"GitHub sitemap index created successfully: {output_file}")
    print(f"Base URL: {base_url}")
    for i in range(1, sitemap_count + 1):
        print(f"  Sitemap {i}: {base_url}/sitemap-{i}.xml")

def update_readme_for_github(input_file, output_file, repo_owner, repo_name, branch):
    """Update README with GitHub URLs."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace references to local files with GitHub URLs
    base_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}"
    github_content = content.replace(
        "- **Full sitemap**: `lol_narrative_sitemap.xml` (874 KB)",
        f"- **Full sitemap**: [{base_url}/lol_narrative_sitemap.xml]({base_url}/lol_narrative_sitemap.xml) (874 KB)"
    )
    
    github_content = github_content.replace(
        "  - `lol_narrative_sitemaps/sitemap-1.xml` (2,500 URLs)",
        f"  - [{base_url}/lol_narrative_sitemaps/sitemap-1.xml]({base_url}/lol_narrative_sitemaps/sitemap-1.xml) (2,500 URLs)"
    )
    
    github_content = github_content.replace(
        "  - `lol_narrative_sitemaps/sitemap-2.xml` (2,500 URLs)",
        f"  - [{base_url}/lol_narrative_sitemaps/sitemap-2.xml]({base_url}/lol_narrative_sitemaps/sitemap-2.xml) (2,500 URLs)"
    )
    
    github_content = github_content.replace(
        "  - `lol_narrative_sitemaps/sitemap-3.xml` (1,413 URLs)",
        f"  - [{base_url}/lol_narrative_sitemaps/sitemap-3.xml]({base_url}/lol_narrative_sitemaps/sitemap-3.xml) (1,413 URLs)"
    )
    
    github_content = github_content.replace(
        "  - `lol_narrative_sitemaps/sitemap-index.xml` (Index file)",
        f"  - [{base_url}/lol_narrative_sitemaps/sitemap-index.xml]({base_url}/lol_narrative_sitemaps/sitemap-index.xml) (Index file)"
    )
    
    # Write updated README
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(github_content)
    
    print(f"Updated README with GitHub URLs: {output_file}")

if __name__ == "__main__":
    # Configuration
    repo_owner = "smrl"
    repo_name = "lol_sitemap_parser"
    branch = "master"  # or "main" depending on your branch name
    
    # Create sitemap index with GitHub URLs
    create_github_sitemap_index(
        repo_owner, 
        repo_name, 
        branch, 
        "/home/user/audio_ai/lol_scraper2/lol_narrative_sitemaps/sitemap-index.xml",
        sitemap_count=3
    )
    
    # Update README with GitHub URLs
    update_readme_for_github(
        "/home/user/audio_ai/lol_scraper2/README_SITEMAP.md",
        "/home/user/audio_ai/lol_scraper2/README_SITEMAP.md",
        repo_owner,
        repo_name,
        branch
    )