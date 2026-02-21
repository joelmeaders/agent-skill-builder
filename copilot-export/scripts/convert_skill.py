#!/usr/bin/env python3
"""
Copilot Export: Skill Converter

Converts Agent Zero SKILL.md files to GitHub Copilot formats.

Usage:
    python scripts/convert_skill.py --skill-path /path/to/skill [--output-dir .github]

Requirements:
    - PyYAML
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


# Tool mapping from Agent Zero to GitHub Copilot
TOOL_MAPPING = {
    # Direct mappings
    "code_execution_tool": "execute",
    "document_query": "read",
    "search_engine": "web",
    "call_subordinate": "agent",
    
    # Tools requiring MCP
    "browser_agent": None,  # Requires MCP
    "memory_save": None,   # Requires MCP
    "memory_load": None,   # Requires MCP
    "memory_delete": None, # Requires MCP
    "memory_forget": None, # Requires MCP
    
    # Prompt-based tools (not actual tools)
    "response": None,
    "notify_user": None,
    
    # Scheduler tools
    "scheduler:create_scheduled_task": None,
    "scheduler:create_adhoc_task": None,
    "scheduler:create_planned_task": None,
    "scheduler:run_task": None,
    "scheduler:list_tasks": None,
    "scheduler:find_task_by_name": None,
    "scheduler:show_task": None,
    "scheduler:delete_task": None,
    "scheduler:wait_for_task": None,
}

# MCP server recommendations
MCP_RECOMMENDATIONS = {
    "browser_agent": {
        "name": "puppeteer-mcp",
        "description": "Browser automation for web scraping and testing",
        "install": "npx @puppeteer/mcp-server"
    },
    "memory_save": {
        "name": "memory-mcp",
        "description": "Persistent memory for AI agents",
        "install": "npx @memory/mcp-server"
    },
    "memory_load": {
        "name": "memory-mcp",
        "description": "Persistent memory for AI agents",
        "install": "npx @memory/mcp-server"
    },
    "memory_delete": {
        "name": "memory-mcp",
        "description": "Persistent memory for AI agents",
        "install": "npx @memory/mcp-server"
    },
    "memory_forget": {
        "name": "memory-mcp",
        "description": "Persistent memory for AI agents",
        "install": "npx @memory/mcp-server"
    },
    "scheduler:*": {
        "name": "scheduler-mcp",
        "description": "Task scheduling and cron execution",
        "install": "Custom implementation required"
    }
}


def parse_skill_md(skill_path: str) -> dict[str, Any]:
    """Parse a SKILL.md file and extract YAML frontmatter and content."""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split YAML frontmatter and content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return {"frontmatter": frontmatter, "body": body}
    
    return {"frontmatter": {}, "body": content}


def map_tools(allowed_tools: list[str]) -> tuple[list[str], dict, list[str]]:
    """
    Map Agent Zero tools to Copilot aliases.
    
    Returns:
        - mapped_tools: List of Copilot tool aliases
        - mcp_servers: Dict of MCP server configurations
        - skipped_tools: List of tools that couldn't be mapped
    """
    mapped_tools = []
    mcp_servers = {}
    skipped_tools = []
    used_mcp_servers = set()
    
    for tool in allowed_tools or []:
        if tool in TOOL_MAPPING:
            mapped = TOOL_MAPPING[tool]
            if mapped:
                mapped_tools.append(mapped)
            else:
                skipped_tools.append(tool)
                # Add MCP recommendation
                if tool in MCP_RECOMMENDATIONS:
                    mcp_info = MCP_RECOMMENDATIONS[tool]
                    if mcp_info["name"] not in used_mcp_servers:
                        mcp_servers[mcp_info["name"]] = {
                            "type": "local",
                            "command": "npx",
                            "args": [mcp_info["install"]],
                            "description": mcp_info["description"]
                        }
                        used_mcp_servers.add(mcp_info["name"])
        else:
            skipped_tools.append(tool)
    
    # Add MCP wildcard for tools requiring MCP
    if mcp_servers:
        for server_name in mcp_servers:
            mapped_tools.append(f"{server_name}/*")
    
    return mapped_tools, mcp_servers, skipped_tools


def extract_build_test_info(body: str) -> dict[str, list[str]]:
    """Extract build steps, testing info, and conventions from skill body.
    
    Only extracts from EXACT section headers to avoid false matches.
    """
    result = {
        "build_steps": [],
        "testing": [],
        "conventions": []
    }
    
    # Build section - EXACT match for "## Build" or "## Build Steps" etc.
    build_match = re.search(
        r'(?i)^##\s+(build|installation|setup|prerequisites)\s*$\n(.*?)(?=^##\s+|\Z)',
        body, re.DOTALL | re.MULTILINE
    )
    if build_match:
        for line in build_match.group(2).split('\n'):
            line = line.strip()
            if line and line.startswith(('- ', '* ')) and '```' not in line:
                result["build_steps"].append(line[2:].strip())
    
    # Testing section - EXACT match for "## Testing" or "## Tests" etc.
    test_match = re.search(
        r'(?i)^##\s+(testing|tests|validation)\s*$\n(.*?)(?=^##\s+|\Z)',
        body, re.DOTALL | re.MULTILINE
    )
    if test_match:
        for line in test_match.group(2).split('\n'):
            line = line.strip()
            if line and line.startswith(('- ', '* ')) and '```' not in line:
                result["testing"].append(line[2:].strip())
    
    # Conventions section - EXACT match
    conv_match = re.search(
        r'(?i)^##\s+(conventions?|coding standards?|style guide)\s*$\n(.*?)(?=^##\s+|\Z)',
        body, re.DOTALL | re.MULTILINE
    )
    if conv_match:
        for line in conv_match.group(2).split('\n'):
            line = line.strip()
            if line and line.startswith(('- ', '* ')) and '```' not in line:
                result["conventions"].append(line[2:].strip())
    
    return result


def generate_agent_profile(skill_data: dict, output_dir: str) -> tuple[str, list[str], dict]:
    """Generate GitHub Copilot custom agent profile."""
    fm = skill_data.get("frontmatter", {})
    body = skill_data.get("body", "")
    
    name = fm.get("name", "unnamed-agent")
    description = fm.get("description", "")
    allowed_tools = fm.get("allowed-tools", [])
    
    mapped_tools, mcp_servers, skipped = map_tools(allowed_tools)
    
    # Build YAML frontmatter
    agent_yaml = {"name": name, "description": description}
    
    if mapped_tools:
        agent_yaml["tools"] = mapped_tools
    else:
        # Default Copilot tools
        agent_yaml["tools"] = ["read", "edit", "execute", "search"]
    
    if mcp_servers:
        agent_yaml["mcp-servers"] = mcp_servers
    
    # Build agent prompt from body - use first 800 chars of content after first header
    paragraphs = body.split('\n\n')
    agent_prompt = "\n\n".join(paragraphs[:3]) if paragraphs else "# Agent prompt to be defined"
    
    # Convert to YAML string
    yaml_str = yaml.dump(agent_yaml, default_flow_style=False, sort_keys=False)
    
    output = f"""---
{yaml_str}---

# {name.title()} Agent

{agent_prompt}

---
*Converted from Agent Zero SKILL.md on {datetime.now().isoformat()}*
*Original version: {fm.get('metadata', {}).get('version', 'unknown')}*
"""
    
    output_path = os.path.join(output_dir, f"{name}.agent.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    return output_path, skipped, mcp_servers


def generate_agents_md(skill_data: dict, output_dir: str) -> str:
    """Generate AGENTS.md file."""
    fm = skill_data.get("frontmatter", {})
    body = skill_data.get("body", "")
    
    name = fm.get("name", "Unnamed Project")
    description = fm.get("description", "")
    
    info = extract_build_test_info(body)
    
    content = f"""# Agent Instructions for {name}

## Overview
{description}

"""
    
    # Only add sections that have content
    if info["build_steps"]:
        content += "## Build Steps\n\n"
        for step in info["build_steps"][:5]:
            content += f"- {step}\n"
        content += "\n"
    
    if info["testing"]:
        content += "## Testing\n\n"
        for test in info["testing"][:5]:
            content += f"- {test}\n"
        content += "\n"
    
    if info["conventions"]:
        content += "## Conventions\n\n"
        for conv in info["conventions"][:5]:
            content += f"- {conv}\n"
        content += "\n"
    
    # If no sections have content, add a note
    if not info["build_steps"] and not info["testing"] and not info["conventions"]:
        content += "## Additional Information\n\n"
        content += "This skill's detailed instructions are in the custom agent profile.\n"
        content += "Refer to the .agent.md file for complete usage guidelines.\n\n"
    
    content += f"""---
*Generated from Agent Zero SKILL.md on {datetime.now().isoformat()}*
*See {name}.agent.md for full agent configuration*
"""
    
    output_path = os.path.join(output_dir, "AGENTS.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


def generate_mcp_config(mcp_servers: dict, output_dir: str) -> str:
    """Generate MCP server configuration file."""
    config = {
        "mcpServers": mcp_servers
    }
    
    output_path = os.path.join(output_dir, "mcp-servers.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    return output_path


def convert_skill(skill_path: str, output_dir: str = ".github") -> dict:
    """Convert a SKILL.md file to GitHub Copilot formats."""
    
    # Check if skill exists
    if not os.path.exists(skill_path):
        return {"error": f"Skill file not found: {skill_path}"}
    
    # Parse skill file first to get skill name
    skill_data = parse_skill_md(skill_path)
    
    if not skill_data.get("frontmatter"):
        return {"error": "No valid YAML frontmatter found in SKILL.md"}
    
    # Get skill name for subdirectory
    fm = skill_data.get("frontmatter", {})
    skill_name = fm.get("name", "unnamed")
    
    # Create output directory with skill name subdirectory
    output_dir = os.path.join(output_dir, skill_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # skill_data already parsed above
    
    results = {
        "skill": skill_path,
        "skill_name": skill_name,
        "output_dir": output_dir,
        "files_created": [],
        "tools_skipped": [],
        "mcp_servers": {}
    }
    
    # Generate custom agent profile
    agent_path, skipped, mcp_servers = generate_agent_profile(skill_data, output_dir)
    results["files_created"].append(agent_path)
    results["tools_skipped"] = skipped
    results["mcp_servers"] = mcp_servers
    
    # Generate AGENTS.md
    agents_path = generate_agents_md(skill_data, output_dir)
    results["files_created"].append(agents_path)
    
    # Copy original SKILL.md to output directory
    import shutil
    skill_filename = os.path.basename(skill_path)
    skill_dest = os.path.join(output_dir, skill_filename)
    if skill_path != skill_dest:  # Only copy if different path
        shutil.copy2(skill_path, skill_dest)
        results["files_created"].append(skill_dest)
    
    # Generate MCP config if needed
    if mcp_servers:
        mcp_path = generate_mcp_config(mcp_servers, output_dir)
        results["files_created"].append(mcp_path)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert Agent Zero SKILL.md to GitHub Copilot formats"
    )
    parser.add_argument(
        "--skill-path", "-s",
        required=True,
        help="Path to SKILL.md file"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=".github",
        help="Output directory (default: .github)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    result = convert_skill(args.skill_path, args.output_dir)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print(f"\n✓ Conversion complete!")
    print(f"\nFiles created:")
    for f in result["files_created"]:
        print(f"  - {f}")
    
    if result["tools_skipped"]:
        print(f"\n⚠ Tools requiring MCP (not natively available):")
        for tool in result["tools_skipped"]:
            print(f"  - {tool}")
    
    if result["mcp_servers"]:
        print(f"\n📦 MCP servers configured:")
        for name, config in result["mcp_servers"].items():
            print(f"  - {name}: {config.get('description', 'N/A')}")
    
    return result


if __name__ == "__main__":
    main()
