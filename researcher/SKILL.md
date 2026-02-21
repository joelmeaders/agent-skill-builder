---
name: researcher
description: >
  A comprehensive research assistant skill that enables agents to gather,
  analyze, and synthesize information from multiple sources. Use when the
  user needs deep research, data analysis, fact-checking, competitive analysis,
  or comprehensive reports on any topic. Keywords: research, analysis,
  information gathering, fact-check, report, synthesis, investigation, study.
metadata:
  author: Agent Zero
  version: "1.1"
allowed-tools:
  - search_engine
  - document_query
  - code_execution_tool
  - memory_save
  - memory_load
  - call_subordinate
---

# Researcher Skill

## Overview
This skill enables AI agents to perform comprehensive research tasks by leveraging web search, document analysis, information synthesis, and subagent delegation capabilities. The researcher skill transforms raw information into structured, actionable insights with proper citations.

## When to Use
Activate this skill when the user needs:
- Deep research on any topic
- Fact-checking and verification of claims
- Comparative analysis between products, technologies, or approaches
- Competitive analysis and market research
- Literature reviews and academic research
- Data analysis and interpretation
- Comprehensive reports with sources

## Capabilities

1. **Web Search & Information Retrieval**
   - Search multiple sources simultaneously
   - Filter by recency, relevance, and source credibility
   - Extract key information from search results

2. **Document Analysis**
   - Parse and analyze web documents, PDFs, and text
   - Extract key findings, statistics, and insights
   - Identify patterns and trends across sources

3. **Information Synthesis**
   - Combine findings from multiple sources
   - Identify consensus and conflicting viewpoints
   - Create coherent narratives from disparate data

4. **Fact-Checking**
   - Verify claims against multiple reliable sources
   - Identify misinformation and biases
   - Provide confidence levels for claims

5. **Report Generation**
   - Structure findings into clear sections
   - Include proper citations and sources
   - Provide executive summaries and key takeaways

6. **Source Citation**
   - Format citations in standard styles (APA, MLA, Chicago)
   - Provide links to original sources
   - Assess source credibility and reliability

7. **Parallel Research with Subagents** (NEW in v1.1)
   - Delegate research subtasks to specialized subagents
   - Conduct parallel research on different aspects
   - Synthesize findings from multiple subagent results

## Step-by-Step Instructions

### Phase 1: Define Research Scope
1. Clarify the research question or topic with the user if unclear
2. Identify key aspects to investigate
3. Determine desired output format (brief summary, detailed report, comparison)
4. Establish depth requirements (surface-level, moderate, comprehensive)
5. **Determine if parallel research is beneficial**: For complex topics with multiple distinct subtopics, consider using subagents

### Phase 2: Information Gathering
1. Conduct initial web searches using `search_engine`
   - Use multiple search queries to cover different aspects
   - Include both broad and specific terms
2. Analyze top results using `document_query`
   - Extract relevant information from promising sources
   - Note source URLs and publication dates
3. Search for additional context if initial results are insufficient
4. Prioritize authoritative sources (academic, government, established publications)

### Phase 2b: Parallel Research with Subagents (Optional)
For complex research tasks, delegate subtasks to subagents:

```python
# Example: Researching a multi-faceted topic
# Split into parallel research streams

# Subagent 1: Academic sources
call_subordinate(
    profile="researcher",
    message="Research [TOPIC] focusing on academic papers and peer-reviewed sources. "
            "Provide key findings, authors, and citations.",
    reset=true
)

# Subagent 2: Industry sources
call_subordinate(
    profile="researcher",
    message="Research [TOPIC] from industry perspective. "
            "Look for company reports, market analysis, and practical applications.",
    reset=true
)

# Subagent 3: Recent developments
call_subordinate(
    profile="researcher",
    message="Research the latest news and developments about [TOPIC] "
            "from the past 6 months. Focus on recent announcements and trends.",
    reset=true
)
```

**When to Use Subagents:**
- Topic has multiple distinct aspects that can be researched independently
- Need diverse perspectives (academic, industry, news)
- Large research scope that would benefit from parallel processing
- Time-sensitive research requiring faster completion

**Best Practices for Subagent Delegation:**
1. **Clear Briefs**: Provide specific, focused research questions to each subagent
2. **Consistent Format**: Ask for similar output structures from all subagents
3. **Overlap Topics Slightly**: Allow subagents to cover overlapping areas for cross-verification
4. **Synthesize Results**: Always combine and synthesize subagent findings into coherent output
5. **Cite Sources**: Each subagent should provide sources; aggregate all citations

### Phase 3: Analysis & Synthesis
1. Review all gathered information (including subagent results)
2. Identify key themes, patterns, and trends
3. Note areas of consensus and conflict
4. Extract relevant statistics, quotes, and findings
5. Assess the reliability and credibility of each source

### Phase 4: Report Generation
1. Structure the report with clear sections:
   - Executive Summary
   - Introduction/Background
   - Key Findings (organized by theme)
   - Analysis
   - Conclusion
   - Sources/Citations
2. Include proper citations using information from sources
3. Provide a balanced view, noting limitations and gaps
4. Highlight actionable insights when appropriate

### Phase 5: Review & Refine
1. Verify all claims have source support
2. Check citation accuracy
3. Ensure balanced presentation of viewpoints
4. Confirm the report addresses the original research question

## Example Use Cases

### Example 1: Topic Research with Parallel Subagents
- **Input**: "Research the impact of AI on healthcare diagnostics"
- **Approach**:
  - Use 3 subagents for: (1) Clinical applications, (2) Market trends, (3) Regulatory landscape
  - Synthesize results into comprehensive report
- **Output**:
  - Executive summary with key findings
  - Overview of AI diagnostic tools (imaging, pathology, predictive)
  - Statistics on accuracy improvements
  - Case studies from major healthcare systems
  - Ethical considerations and challenges
  - Future outlook
  - 10+ cited sources with links

### Example 2: Fact-Checking
- **Input**: "Verify if renewable energy is now cheaper than fossil fuels for electricity generation"
- **Output**:
  - Verified claim with confidence level
  - LCOE (Levelized Cost of Energy) comparison data
  - Regional variations and caveats
  - Source citations from IEA, IRENA, academic studies
  - Context on different metrics and methodologies

### Example 3: Comparative Analysis
- **Input**: "Compare TensorFlow, PyTorch, and JAX for production machine learning deployments"
- **Output**:
  - Side-by-side comparison table
  - Pros and cons for each framework
  - Use case recommendations
  - Performance benchmarks
  - Community support and ecosystem comparison
  - Migration considerations

### Example 4: Competitive Analysis
- **Input**: "Analyze the cloud computing market: AWS vs Azure vs Google Cloud"
- **Output**:
  - Market share breakdown
  - Service offerings comparison
  - Pricing models analysis
  - Strengths and weaknesses of each provider
  - Target use cases and customer segments
  - Recent innovations and announcements

### Example 5: Literature Review
- **Input**: "What are the latest developments in CRISPR gene editing therapy?"
- **Output**:
  - Summary of recent clinical trials
  - Breakthroughs in delivery mechanisms
  - Regulatory landscape updates
  - Ethical considerations
  - Key research papers and authors
  - Future therapeutic applications

## Edge Cases

1. **Limited Available Information**
   - If search results are sparse, note the information gap
   - Suggest alternative research angles
   - Provide what's available with appropriate caveats

2. **Conflicting Sources**
   - Present multiple viewpoints equally
   - Explain the nature of the disagreement
   - Provide context for why sources may differ
   - Suggest factors users should consider

3. **Outdated Information**
   - Note the publication date of sources
   - Indicate if newer information may exist
   - Flag any claims that may have changed

4. **Sensitive or Controversial Topics**
   - Present multiple perspectives fairly
   - Acknowledge limitations and Avoid taking partisan positions biases
   -
   - Cite diverse source types

5. **Technical or Specialized Topics**
   - Ensure accuracy of technical details
   - Explain jargon when necessary
   - Verify claims with authoritative technical sources

6. **Large Research Requests**
   - Break into manageable phases
   - Consider using subagents for parallel research
   - Provide interim summaries
   - Ask for clarification on priorities

7. **Subagent Results Conflicts**
   - If subagents provide conflicting information, note the conflict
   - Cross-verify with additional searches if needed
   - Present both viewpoints with context

## Best Practices

1. **Source Diversity**: Use multiple source types (academic, news, industry, government)
2. **Verification**: Cross-check critical claims across sources
3. **Transparency**: Clearly indicate confidence levels and uncertainties
4. **Balance**: Present balanced views, especially on controversial topics
5. **Actionability**: Include practical takeaways when relevant
6. **Citations**: Always provide source links for verifiable claims
7. **Currency**: Prefer recent sources; note when using older information
8. **Subagent Strategy**: Use parallel research wisely - for complex, multi-faceted topics

## Tools & Resources

### Required Tools
- `search_engine`: For web information retrieval
- `document_query`: For analyzing web documents and content
- `code_execution_tool`: For data processing and formatting

### Optional Tools
- `memory_save`: To store research findings for future reference
- `memory_load`: To recall previous research on related topics
- `call_subordinate`: To delegate research subtasks to parallel subagents

### Output Formats
The skill supports various output formats:
- Brief summary (250-500 words)
- Standard report (1000-2000 words)
- Comprehensive analysis (3000+ words)
- Comparison tables
- Fact-sheets with key points

## Notes

- Always prioritize accuracy over speed
- When in doubt, note limitations rather than overstate conclusions
- Ask for clarification if the research scope is unclear
- Save valuable research findings to memory for future reference
- Use the `code_execution_tool` to process and visualize data when helpful
- Consider using subagents for complex, multi-faceted research topics
- Use `§§include()` to incorporate subagent results directly into your report

---
*Skill Version: 1.1 | Author: Agent Zero | Based on agentskills.io specification*
*Added in v1.1: Subagent delegation support for parallel research*