# League of Legends Content Filtering Findings

Our comprehensive filtering process has yielded several important insights about the structure and content of the League of Legends wiki.

## Content Distribution

The original wiki content (16,594 URLs) can be broken down as follows:

| Content Type | Approximate Count | Percentage |
|--------------|-------------------|------------|
| Core narrative content | 7,799 | 47.0% |
| Organizational pages | 4,171 | 25.1% |
| Game mechanics | 2,500 | 15.1% |
| Other games content | 1,450 | 8.7% |
| Cosmetics/skins | 674 | 4.1% |

## Content Patterns

Our analysis revealed several interesting patterns:

1. **Discussion pages**: 2,754 URLs (16.6% of all content) were discussion-related pages that added little narrative value
2. **Category pages**: 2,859 category pages (17.2%) were primarily for wiki organization
3. **Path of Champions**: 356 pages (2.1%) were related to the Path of Champions game mode
4. **Other games content**: Over 3,000 pages combined were for non-core League of Legends content

## Filtering Effectiveness

Our iterative filtering approach progressed through several stages:

1. **Basic filtering** (removed other games): 78.3% kept
2. **Mechanics filtering** (removed items, abilities): 73.6% kept
3. **Cosmetics filtering** (removed skins): 72.1% kept 
4. **Organizational filtering** (removed meta pages): 47.0% kept

The most dramatic improvement came from filtering organizational content, which removed over 4,100 URLs that didn't contain substantial lore.

## Remaining Content Quality

The remaining 7,799 URLs contain:

1. **Champion lore**: 176 champion pages with their background, history, and development
2. **World geography**: 33 map pages and 6 Runeterra region pages
3. **Narrative elements**: Stories, comics, and lore events
4. **Character relationships**: Development of connections between champions and regions

## Key Learnings

1. **Wiki structure** is heavily oriented toward gameplay, with lore being a secondary focus
2. **Organizational overhead** in wikis is substantial, with nearly 25% of pages dedicated to organization
3. **Game-specific content** often crowds out narrative elements
4. **Whitelist approach** is less effective than a comprehensive blacklist with good categorization

## Recommendations for Narrative Extraction

1. Focus on the `/wiki/[Champion]/Background` and `/wiki/[Champion]/Development` pages for character lore
2. Prioritize region pages and character relationship pages for world-building
3. Look for short stories and narrative-specific content rather than game implementation details
4. Exclude discussions, organizational pages, and template-based content