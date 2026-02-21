#!/usr/bin/env python3
"""
Document Analyzer Script for Researcher Skill

Analyzes documents to extract key information, statistics, and insights.

Usage:
    python scripts/document_analyzer.py <document_url> [--extract type]

Arguments:
    document: URL or path to document
    --extract: Type of extraction (summary, key_points, stats, all)

Returns:
    Extracted information in structured format
"""

import argparse
import json
import re

def extract_statistics(text):
    """Extract numerical statistics from text."""
    patterns = [
        r'(\d+\.?\d*%)\s+',  # Percentages
        r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s+(?:million|billion|trillion)',  # Large numbers
        r'\$\s*(\d+\.?\d*)\s+(?:billion|million|thousand)',  # Currency
    ]
    
    stats = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        stats.extend(matches)
    
    return stats[:10]  # Limit to top 10

def extract_key_points(text, num_points=5):
    """Extract key points from document text."""
    sentences = re.split(r'[.!?]+', text)
    
    # Simple heuristic: prefer sentences with numbers or key terms
    scored = []
    key_terms = ['important', 'significant', 'key', 'major', 'critical', 'essential']
    
    for sent in sentences:
        if len(sent.strip()) < 20:
            continue
        score = 0
        sent_lower = sent.lower()
        if any(term in sent_lower for term in key_terms):
            score += 2
        if any(c.isdigit() for c in sent):
            score += 1
        if score > 0:
            scored.append((score, sent.strip()))
    
    scored.sort(reverse=True)
    return [s[1] for s in scored[:num_points]]

def generate_summary(text, max_length=500):
    """Generate a brief summary of the document."""
    # Simple extractive summarization
    sentences = re.split(r'[.!?]+', text)
    summary = ""
    
    for sent in sentences:
        if len(summary) + len(sent) > max_length:
            break
        summary += sent + "."
    
    return summary.strip() if summary else text[:max_length]

def main():
    parser = argparse.ArgumentParser(description="Document analysis tool")
    parser.add_argument("document", help="Document URL or path")
    parser.add_argument("--extract", default="all", 
                        choices=["summary", "key_points", "stats", "all"],
                        help="Type of extraction")
    
    args = parser.parse_args()
    
    # Note: Actual document analysis is handled by document_query tool
    # This script provides post-processing utilities
    
    print(json.dumps({
        "status": "ready",
        "message": "Use document_query tool for actual document analysis",
        "document": args.document,
        "extraction_type": args.extract
    }, indent=2))

if __name__ == "__main__":
    main()
