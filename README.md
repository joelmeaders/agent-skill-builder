# Agent Skill Builder

A framework for creating AI agent skills using the SKILL.md standard from agentskills.io.

## Overview

This project provides a structured framework for building, testing, and maintaining AI agent capabilities using the SKILL.md specification from [agentskills.io](https://agentskills.io/).

## Features

- **SKILL.md Standard**: Define agent capabilities using YAML frontmatter and markdown content
- **Modular Structure**: Organize skills with scripts, references, and assets
- **Agent Discovery**: Keywords in descriptions enable intelligent skill activation
- **Version Control**: Track changes to your skills with git

## Included Skills

| Skill | Description |
|-------|-------------|
| `researcher` | Comprehensive research assistant for gathering and analyzing information |
| `prompt-engineering-patterns` | Advanced techniques for maximizing LLM performance |
| `copilot-export` | Convert Agent Zero skills to GitHub Copilot format |

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/joelmeaders/agent-skill-builder.git
   cd agent-skill-builder
   ```

2. **Explore the skills**
   ```bash
   ls -la */
   ```

3. **Create a new skill**
   See the [SKILL.md Specification](#skillmd-specification) below.

## Project Structure

```
agent-skill-builder/
├── researcher/              # Research assistant skill
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
├── prompt-engineering-patterns/  # Prompt engineering skill
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
├── copilot-export/          # Export skill
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
└── README.md
```

## SKILL.md Specification

Skills are defined using YAML frontmatter followed by markdown content.

```yaml
---
name: skill-name
description: >
  A clear description of what the skill does and when to use it.
  Include keywords for agent discovery. (1-1024 characters)
metadata:
  author: your-name
  version: "1.0"
allowed-tools:
  - tool_name_1
  - tool_name_2
---

# Skill Instructions
Your skill content here...
```

### Required Fields

| Field | Rules |
|-------|-------|
| `name` | 1-64 chars, lowercase a-z + hyphens only |
| `description` | 1-1024 chars, non-empty, descriptive |

### Optional Fields

| Field | Description |
|-------|-------------|
| `license` | License name (e.g., MIT, Apache-2.0) |
| `compatibility` | Version requirements |
| `metadata` | Key-value pairs (author, version, etc.) |
| `allowed-tools` | List of tool names the skill can use |

## Resources

- [agentskills.io](https://agentskills.io/) - Official specification
- [SKILL.md Specification](https://agentskills.io/specification)
- [Agent Zero Framework](https://github.com/joelmeaders/agent-zero)

## License

MIT License - See individual skill directories for specific licenses.

---

*Project created: 2026-02-20*