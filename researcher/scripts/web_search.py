#!/usr/bin/env python3
"""
Web Search Script for Researcher Skill

Provides advanced web search functionality with filtering and result parsing.

Usage:
    python scripts/web_search.py "search query" [--num N] [--type type]

Arguments:
    query: Search query string
    --num: Number of results (default: 10)
    --type: Result type filter (news, general, images)

Returns:
    JSON formatted search results with titles, URLs, descriptions
"""

import argparse
import json
import sys

def format_search_results(results, query):
    """Format search results into structured output."""
    formatted = {
        "query": query,
        "total_results": len(results),
        "results": []
    }
    
    for i, result in enumerate(results, 1):
        formatted["results"].append({
            "rank": i,
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "description": result.get("description", ""),
            "source": extract_domain(result.get("url", ""))
        })
    
    return formatted

def extract_domain(url):
    """Extract domain from URL for source identification."""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return "unknown"

def main():
    parser = argparse.ArgumentParser(description="Web search tool for research")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--num", type=int, default=10, help="Number of results")
    parser.add_argument("--type", default="general", help="Search type")
    
    args = parser.parse_args()
    
    # Note: Actual search is handled by search_engine tool
    # This script provides formatting and filtering utilities
    
    print(json.dumps({
        "status": "ready",
        "message": "Use search_engine tool for actual web searches",
        "query": args.query,
        "filters": {
            "num_results": args.num,
            "search_type": args.type
        }
    }, indent=2))

if __name__ == "__main__":
    main()
