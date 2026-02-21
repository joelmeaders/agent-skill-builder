# Tool Mapping Reference Guide

## Agent Zero to GitHub Copilot Tool Conversion

This reference documents the mapping between Agent Zero native tools and GitHub Copilot equivalents.

---

## Direct Mappings

These tools have direct equivalents in GitHub Copilot:

| Agent Zero Tool | Copilot Alias | Description |
|-----------------|---------------|-------------|
| `code_execution_tool` | `execute` | Execute terminal commands |
| `document_query` | `read` | Read file contents |
| `search_engine` | `web` | Web search capability |
| `call_subordinate` | `agent` | Invoke other agents |

---

## Tools Requiring MCP

These tools are not natively available in GitHub Copilot and require MCP server configuration:

| Agent Zero Tool | MCP Server | Install Command |
|-----------------|-------------|------------------|
| `browser_agent` | Puppeteer MCP | `npx @puppeteer/mcp-server` |
| `memory_save` | Memory MCP | `npx @memory/mcp-server` |
| `memory_load` | Memory MCP | `npx @memory/mcp-server` |
| `memory_delete` | Memory MCP | `npx @memory/mcp-server` |
| `memory_forget` | Memory MCP | `npx @memory/mcp-server` |
| `scheduler:*` | Custom | Implementation required |

---

## Prompt-Based Tools

These are not actual tools but output/communication patterns:

| Agent Zero Tool | Copilot Handling |
|-----------------|------------------|
| `response` | Use prompt instructions |
| `notify_user` | Use prompt instructions |

---

## GitHub Copilot Built-in Tool Aliases

Reference for Copilot tool aliases:

| Alias | Purpose | Example |
|-------|---------|---------|
| `execute` | Run terminal commands | `execute: npm install` |
| `read` | Read file contents | `read: path/to/file` |
| `edit` | Apply changes to files | `edit: replace X with Y` |
| `search` | Search files or text | `search: function definitions` |
| `agent` | Invoke custom agents | `agent: security-reviewer` |
| `web` | Fetch URL or search | `web: https://example.com` |

---

## MCP Tool Naming

MCP tools follow the pattern: `{server-name}/{tool-name}`

Examples:
- `github-mcp/search-repositories`
- `puppeteer-mcp/navigate`
- `filesystem-mcp/read-file`

Wildcard: `{server-name}/*` enables all tools from a server.

---

*Generated: 2026-02-20*
