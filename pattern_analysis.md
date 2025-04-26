# League of Legends Pattern Matching Analysis

This analysis provides insight into how our whitelist and blacklist patterns interact with the League of Legends wiki sitemap.

## URL Pattern Coverage

| Category | Count | Percentage |
|----------|-------|------------|
| Total URLs | 16,594 | 100.00% |
| Whitelist Only | 628 | 3.78% |
| Blacklist Only | 4,334 | 26.12% |
| Both Whitelist & Blacklist | 72 | 0.43% |
| Neither Pattern | 11,560 | 69.66% |

## Whitelist-Only Content

When using only the whitelist (without a blacklist), we get:
- 700 URLs (4.22% of total content)

The difference between the whitelist-only count (700) and the whitelist-only when using both lists (628) is due to the 72 URLs that match both patterns.

## Pattern Effectiveness

The current filtering approach (using both whitelist and blacklist) keeps URLs that:
1. Match the whitelist (and are prioritized over blacklist matches)
2. Don't match any pattern but aren't explicitly blacklisted

This approach preserves:
- 628 (whitelist only) + 11,560 (neither pattern) = 12,188 URLs (73.45%)

Our actual final filtered content count is slightly lower (11,970 URLs or 72.13%) due to implementation details in the filter logic.

## Top Matching Patterns

### Most Effective Whitelist Patterns

| Pattern | Match Count |
|---------|-------------|
| /wiki/[\w%']+/LoL$ | 176 |
| /wiki/[\w%']+/Development | 170 |
| /wiki/[\w%']+/Trivia | 168 |
| /wiki/Category:Lore | 24 |
| /wiki/Void | 16 |

### Most Effective Blacklist Patterns

| Pattern | Match Count |
|---------|-------------|
| \(Legends_of_Runeterra\) | 2,179 |
| \(Teamfight_Tactics\) | 1,063 |
| /wiki/V\d+\.\d+ | 679 |
| \(Wild_Rift\) | 349 |
| /wiki/List_of_ | 93 |

## Observations

1. Only a small portion (4.22%) of content is explicitly matched by our whitelist patterns
2. The vast majority (69.66%) of kept content is due to it not matching any pattern
3. Our blacklist is more comprehensive than our whitelist (207 vs. 54 patterns)
4. A relatively small number of URLs (72) match both whitelist and blacklist patterns

## Recommendations

1. **Expand the whitelist** to explicitly match more of the "neither" category content
2. **Create more specific whitelists** for narrative-relevant content categories
3. **Consider a whitelist-only approach** if we want to be stricter about exactly what content to include
4. **Review overlap patterns** to ensure important content isn't being caught in both lists