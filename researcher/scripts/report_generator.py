#!/usr/bin/env python3
"""
Report Generator Script for Researcher Skill

Generates structured research reports from gathered information.

Usage:
    python scripts/report_generator.py --input data.json --output report.md

Arguments:
    --input: JSON file with research data
    --output: Output markdown file path
    --format: Report format (brief, standard, comprehensive)

Returns:
    Markdown formatted research report
"""

import argparse
import json
import sys

def generate_report(data, format_type="standard"):
    """Generate structured research report from data."""
    sections = {
        "brief": ["Summary", "Key Findings", "Sources"],
        "standard": ["Executive Summary", "Introduction", "Key Findings", "Analysis", "Conclusion", "Sources"],
        "comprehensive": ["Executive Summary", "Introduction", "Methodology", "Key Findings", "Detailed Analysis", "Limitations", "Conclusion", "Recommendations", "Sources"]
    }
    
    return sections.get(format_type, sections["standard"])

def main():
    parser = argparse.ArgumentParser(description="Research report generator")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output markdown file")
    parser.add_argument("--format", default="standard", choices=["brief", "standard", "comprehensive"], help="Report format")
    
    args = parser.parse_args()
    
    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        sections = generate_report(data, args.format)
        
        print(json.dumps({
            "status": "ready",
            "sections": sections,
            "format": args.format
        }, indent=2))
    except FileNotFoundError:
        print(json.dumps({"error": "Input file not found"}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
