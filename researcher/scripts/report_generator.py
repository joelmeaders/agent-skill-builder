#!/usr/bin/env python3
"""
Report Generator Script for Researcher Skill

Generates structured research reports from gathered information.

Usage:
    python scripts/report_generator.py --input data.json --format type

Arguments:
    --input: JSON file with research data
    --format: Output format (brief, standard, comprehensive)
    --output: Output file path

Returns:
    Formatted research report
"""

import argparse
import json
import sys
from datetime import datetime

def generate_executive_summary(findings):
    """Generate executive summary from key findings."""
    summary = "## Executive Summary\n\n"
    
    if isinstance(findings, list) and len(findings) > 0:
        summary += f"This research covers {len(findings)} key areas. "
        
        # Extract main themes
        themes = set()
        for f in findings:
            if isinstance(f, dict) and "theme" in f:
                themes.add(f["theme"])
        
        if themes:
            summary += f"Main themes identified: {', '.join(themes)}. "
    
    summary += "See below for detailed findings and analysis."
    return summary

def format_citations(sources):
    """Format sources into proper citations."""
    if not sources:
        return "*No sources cited*"
    
    formatted = "## Sources\n\n"
    
    for i, source in enumerate(sources, 1):
        if isinstance(source, dict):
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            date = source.get("date", "n.d.")
            
            formatted += f"{i}. {title} ({date}). "
            if url:
                formatted += f"Retrieved from {url}\n"
            else:
                formatted += "\n"
        else:
            formatted += f"{i}. {source}\n"
    
    return formatted

def generate_report(data, format_type="standard"):
    """Generate complete research report."""
    report = []
    
    # Header
    report.append(f"# Research Report\n")
    report.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n")
    
    # Topic
    if "topic" in data:
        report.append(f"## Topic: {data['topic']}\n")
    
    # Executive Summary
    findings = data.get("findings", [])
    report.append(generate_executive_summary(findings))
    report.append("")
    
    # Findings section
    report.append("## Key Findings\n")
    
    if isinstance(findings, list):
        for i, finding in enumerate(findings, 1):
            if isinstance(finding, dict):
                title = finding.get("title", f"Finding {i}")
                content = finding.get("content", "")
                report.append(f"### {i}. {title}\n")
                report.append(f"{content}\n")
            else:
                report.append(f"### {i}. {finding}\n")
    
    report.append("")
    
    # Citations
    sources = data.get("sources", [])
    report.append(format_citations(sources))
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Research report generator")
    parser.add_argument("--input", help="Input JSON file with research data")
    parser.add_argument("--format", default="standard",
                        choices=["brief", "standard", "comprehensive"],
                        help="Report format")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Load data
    if args.input:
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(json.dumps({"error": "Input file not found"}, indent=2))
            sys.exit(1)
    else:
        data = {"findings": [], "sources": []}
    
    # Generate report
    report = generate_report(data, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(json.dumps({"status": "success", "output": args.output}, indent=2))
    else:
        print(report)

if __name__ == "__main__":
    main()
