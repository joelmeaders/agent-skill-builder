---
name: copilot-export
description: >
  A meta-skill that converts Agent Zero skills, agents, and prompts into GitHub Copilot compatible formats. Use when: exporting skills for Copilot use, creating Copilot custom agents from Agent Zero, converting prompts between systems, generating MCP server configurations. This skill enables interoperability between Agent Zero and GitHub Copilot.
metadata:
  author: Agent Zero
  version: "1.0"
  created: "2026-02-20"
allowed-tools:
  - code_execution_tool
  - document_query
  - search_engine
---

# Copilot Export Skill

## Overview

This meta-skill converts Agent Zero artifacts (skills, agents, prompts) into GitHub Copilot compatible formats. It ensures seamless interoperability between the Agent Zero framework and GitHub Copilot by generating proper configuration files, agent profiles, and instruction documents.

## When to Use

Activate this skill when:
- Converting existing SKILL.md files to GitHub Copilot custom agents
- Exporting Agent Zero skills for use with Copilot
- Creating dual-compatible skills that work in both systems
- Generating MCP server configurations for tools not native to Copilot
- Building a skill library that bridges Agent Zero and GitHub Copilot

## Capabilities

1. **SKILL.md to Copilot Agent Profile Conversion**
   - Parse SKILL.md YAML frontmatter and content
   - Generate `.agent.md` custom agent profile
   - Map `allowed-tools` to Copilot tool aliases

2. **AGENTS.md Generation**
   - Extract build steps, testing, and conventions from skill content
   - Generate `AGENTS.md` following the open standard
   - Only creates sections if content exists in source

3. **Tool Mapping**
   - Convert Agent Zero tools to Copilot aliases
   - Identify tools requiring MCP servers
   - Generate MCP server configurations

4. **Agent Profile Generation**
   - Create custom agent profiles from Agent Zero skill definitions
   - Support for tool lists and MCP server configuration
   - Preserve original skill metadata

5. **Conditional Output Generation**
   - Only create files when source artifacts exist
   - Skip missing components gracefully
   - Report what was and wasn't converted

## Output Files

The skill generates the following files in the `.github/{skillname}/` directory:

| File | Description |
|------|-------------|
| `{skill-name}.agent.md` | Custom agent profile with YAML frontmatter |
| `AGENTS.md` | Build/test/conventions (only if sections exist in source) |
| `SKILL.md` | Copy of the original skill file |
| `mcp-servers.json` | MCP configuration for tools requiring external servers |

## Step-by-Step Instructions

### Phase 1: Analyze Source Artifact

1. **Identify the source type**:
   - Skill: Look for `SKILL.md` file

2. **Check if source exists**:
   ```bash
   ls -la /path/to/skill/SKILL.md
   ```

3. **Parse YAML frontmatter** if present (SKILL.md)
4. **Extract key content** (description, instructions, tool lists)

### Phase 2: Tool Mapping

1. **Map Agent Zero tools to Copilot aliases**:

   | Agent Zero Tool | Copilot Alias | Requires MCP? |
   |-----------------|---------------|---------------|
   | `code_execution_tool` | `execute` | No |
   | `document_query` | `read` | No |
   | `search_engine` | `web` | No |
   | `browser_agent` | N/A | Yes (Puppeteer MCP) |
   | `memory_save` | N/A | Yes (Memory MCP) |
   | `memory_load` | N/A | Yes (Memory MCP) |
   | `call_subordinate` | `agent` | No |

2. **For tools requiring MCP**:
   - Generate MCP server configuration
   - Document limitation in output

### Phase 3: Generate Copilot Files

1. **Create `.github/{skillname}/` directory structure**:
   ```bash
   mkdir -p /path/to/export/.github
   ```

2. **Generate custom agent profile** (`.agent.md`):
   ```yaml
   ---
   name: {skill-name}
   description: {description from SKILL.md}
   tools: [{mapped-tools}]
   mcp-servers:
     {server-config-if-needed}
   ---
   
   {agent-prompt-from-skill-content}
   ```

3. **Generate AGENTS.md** (if build/test info exists):
   - Only includes ## Build Steps, ## Testing, ## Conventions if content is present
   - Otherwise shows ## Additional Information pointing to .agent.md

4. **Copy original SKILL.md** to preserve the source

5. **Generate `mcp-servers.json`** for tools needing MCP

## Edge Cases

1. **No SKILL.md found**
   - Report error: "Skill file not found"
   - No output files created

2. **No allowed-tools specified**
   - Use default Copilot tools (`read`, `edit`, `execute`, `search`)
   - Warn: "No allowed-tools specified, using defaults"

3. **Unknown tool names**
   - Skip unknown tools
   - Report: "Unknown tool: {tool-name}, skipping"
   - Add to recommendations list

4. **Empty skill content**
   - Still create agent profile with frontmatter only
   - Add placeholder: "# Agent prompt to be defined"

5. **No Build/Testing/Conventions sections**
   - Skip these sections in AGENTS.md
   - Add note pointing to .agent.md for full details

## Tool Alias Reference

### Copilot Built-in Tool Aliases
- `execute` - Run terminal commands
- `read` - Read file contents
- `edit` - Edit/apply changes to files
- `search` - Search files or text
- `agent` - Invoke another custom agent
- `web` - Fetch URL content or search web

### MCP Tool Prefix
- Format: `{mcp-server-name}/{tool-name}`
- Wildcard: `{mcp-server-name}/*` (all tools from server)

## Notes

- This is a meta-skill that operates on other skills
- Always check if source artifact exists before conversion
- Generated files are placed in `.github/{skillname}/` directory
- Tool mapping is one-way (Agent Zero → Copilot)
- MCP configurations are templates; users must have MCP servers running
- Use `document_query` to read source files before conversion
- Use `code_execution_tool` to write generated files

---
*Skill Version: 1.0 | Author: Agent Zero | Based on agentskills.io specification*
*Converts: SKILL.md → GitHub Copilot formats*
