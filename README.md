# League of Legends Narrative Sitemap Filter

This tool filters League of Legends wiki content to create a narrative-focused dataset, excluding gameplay mechanics, other Riot Games, and technical details while preserving lore, characters, and world-building content.

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests lxml beautifulsoup4
```

## Usage

### Narrative-Focused Filtering

```bash
# Run with narrative-focused blacklist and whitelist
python final_filter.py sitemap-newsitemapxml-index.xml --output-dir lol_narrative \
  --blacklist-file enhanced_blacklist.txt \
  --whitelist-file enhanced_whitelist.txt \
  --url-categories
```

### Analysis Mode

```bash
# Analyze URLs without filtering to discover patterns
python analyze_sitemap.py sitemap-newsitemapxml-index.xml --analyze-only
```

### Search Mode

```bash
# Search for specific terms in URLs
python analyze_sitemap.py sitemap-newsitemapxml-index.xml --search-term "Runeterra"
```

## Key Features

1. **Narrative-focused filtering**: Preserves story content while excluding gameplay mechanics
2. **URL categorization**: Organizes content by champions, maps, regions, and stories
3. **Whitelist/blacklist system**: Fine-grained control over included/excluded content
4. **Incremental refinement**: Supports iterative filtering for content optimization

## Output Files

The script generates several output files:

- `filtered_urls.txt`: Narrative-focused League of Legends URLs
- `blacklisted_urls.txt`: Excluded gameplay and non-narrative URLs
- `{category}_urls.txt`: Categorized content (champions, regions, etc.)
- `path_patterns.json`: Analysis of URL structure patterns
- `uncategorized_urls.txt`: URLs that didn't match specific categories

## Filtering Results

Through multiple iterations of filtering, we've achieved:

- Total URLs processed: 16,594
- URLs kept (final narrative version): 6,413 (38.7%)
- URLs excluded: 10,181 (61.3%)

## Documentation

- `filtering_summary.md`: Detailed analysis of what was kept/filtered
- `URL_ANALYSIS.md`: Insights into URL structures and patterns
- `enhanced_blacklist.txt`: Rules for excluding gameplay content
- `enhanced_whitelist.txt`: Rules for preserving narrative content

## What's Included

✅ Champion lore and backgrounds
✅ World regions and geography
✅ Faction histories and relationships
✅ Character stories and development
✅ Cinematics and media with narrative value

## What's Excluded

❌ Game mechanics and abilities
❌ Items and equipment
❌ Patch notes and updates
❌ Gameplay statistics
❌ Other Riot games content