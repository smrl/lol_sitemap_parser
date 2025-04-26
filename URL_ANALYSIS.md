# League of Legends URL Analysis

This document provides insights into the structure and organization of the League of Legends wiki URLs to help with further filtering and categorization.

## URL Structure Patterns

The main URL format is: `https://leagueoflegends.fandom.com/wiki/[Page_Name]`

### Champion URLs

Champions have several URL patterns:
- Champion main page: `/wiki/[Champion_Name]`
- Champion LoL-specific page: `/wiki/[Champion_Name]/LoL`
- Champion background: `/wiki/[Champion_Name]/Background`
- Champion history: `/wiki/[Champion_Name]/History`
- Champion quotes: `/wiki/[Champion_Name]/Quotes`
- Champion development: `/wiki/[Champion_Name]/Development`

### World and Region URLs

Locations in the world of Runeterra:
- Main world page: `/wiki/Runeterra`
- World map: `/wiki/Runeterra/Map`
- Regions: `/wiki/[Region_Name]` (e.g., `/wiki/Demacia`, `/wiki/Noxus`)
- Region detailed pages: `/wiki/[Region_Name]/[Subpage]`

### Narrative Content

Story-specific content:
- Short stories: `/wiki/[Story_Title]`
- Comics: `/wiki/[Comic_Name]` 
- Narrative event: `/wiki/[Event_Name]`
- Universe entries: `/wiki/Universe`

### Category Pages

Wiki categories:
- Category listings: `/wiki/Category:[Category_Name]`
- Places: `/wiki/Category:Places`
- Factions: `/wiki/Category:Factions`
- Species: `/wiki/Category:Species`
- Characters: `/wiki/Category:Characters`

## Continuing Filtering Suggestions

To further refine the filtered content, consider:

1. **Create specialized filters for specific narratives**:
   - Create filters for specific storylines (e.g., Spirit Blossom, Star Guardian)
   - Filter by timeline periods or key historical events

2. **Focus on relationship content**:
   - Identify pages that describe relationships between champions
   - Find content that connects regions and factions
   - Look for lore that connects champions to specific regions

3. **Extract structured data**:
   - Generate a character relationship graph
   - Map champions to their home regions
   - Create faction alliance/opposition networks

4. **Additional blacklist suggestions**:
   - Remove template and administrative pages
   - Filter out image galleries that don't add narrative content
   - Consider removing disambiguations and redirect pages

## Categories Worth Further Exploration

These categories may contain valuable narrative content that could be further filtered:

1. `/wiki/Category:Short_stories` - Pure narrative content
2. `/wiki/Category:Videos` - May contain cinematics with lore significance
3. `/wiki/Category:Places` - World-building content
4. `/wiki/Category:Characters` - Characters beyond the playable champions
5. `/wiki/Category:Timeline` - History and chronology of the world

## Next Steps for Analysis

1. Sample the uncategorized URLs to identify additional patterns
2. Create more specific subcategories for different types of narrative content
3. Generate a visualization of the narrative connections between URLs
4. Consider developing an auto-categorization system based on URL patterns and content