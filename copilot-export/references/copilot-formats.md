# GitHub Copilot Format Reference

## File Formats Overview

This guide documents the various file formats used by GitHub Copilot for custom instructions and agent configurations.

---

## 1. Custom Agent Profile (.agent.md)

### YAML Frontmatter Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Display name for the custom agent |
| `description` | string | Agent's purpose and capabilities (required) |
| `target` | string | Target environment: `vscode` or `github-copilot` |
| `tools` | array | List of tool names or aliases |
| `mcp-servers` | object | MCP server configurations |

### Example

```yaml
---
name: security-reviewer
description: Specialized agent for security code reviews
target: vscode
tools: ['read', 'edit', 'execute', 'search', 'web']
mcp-servers:
  security-tools:
    type: 'local'
    command: 'npx'
    args: ['@security/mcp-server']
---

# Agent Instructions
You are a security expert that reviews code for vulnerabilities...
```

---

## 2. AGENTS.md (Open Standard)

A project-level file for agent instructions, conventions, and build steps.

### Sections

- **Overview**: Project description
- **Build Steps**: How to build the project
- **Testing**: How to run tests
- **Conventions**: Coding standards and style

### Example

```markdown
# Agent Instructions for MyProject

## Overview
A modern web application built with React and Node.js.

## Build Steps
1. npm install
2. npm run build

## Testing
npm test

## Conventions
- Use TypeScript
- Follow ESLint rules
- Write unit tests for new features
```

---

## 3. .github/copilot-instructions.md

General project-wide instructions for Copilot.

### Example

```markdown
# Copilot Instructions

## Project Context
This is a Python Django project...

## Code Style
- Follow PEP 8
- Use Black for formatting
- Type hints required
```

---

## 4. .instructions.md (Agent-Specific)

Task-specific or agent-specific instructions using YAML frontmatter.

### Frontmatter Properties

| Property | Type | Description |
|----------|------|-------------|
| `applyTo` | string | Glob pattern for files |
| `excludeAgent` | string | Agent to exclude (e.g., `"code-review"`) |

### Example

```yaml
---
applyTo: "**"
excludeAgent: "code-review"
---

# Instructions for coding agent
Always write tests before implementing features...
```

---

## 5. MCP Server Configuration

### JSON Format

```json
{
  "mcpServers": {
    "server-name": {
      "type": "local",
      "command": "npx",
      "args": ["@package/mcp-server"],
      "description": "Server description",
      "env": {
        "ENV_VAR": "$SECRET_NAME"
      }
    }
  }
}
```

### Types

- `local`: Runs locally via command
- `stdio`: Standard input/output communication
- `sse`: Server-Sent Events

---

*Reference created: 2026-02-20*
