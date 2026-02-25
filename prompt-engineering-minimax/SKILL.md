---
name: prompt-engineering-minimax
description: Always-active skill that applies MiniMax M2.5 prompt engineering best practices. Automatically enriches prompts with additional context, asks for clarification when needed, and ensures clear instructions. Use when processing any user request to optimize prompt clarity and effectiveness.
license: MIT
compatibility:
  agent0: ">=1.0.0"
metadata:
  author: agent0
  version: 1.0.0
  tags:
    - prompt-engineering
    - mini-max
    - context
    - clarification
    - always-active
allowed-tools:
  - memory_load
  - memory_save
---

# Prompt Engineering - MiniMax Best Practices

This skill is **always active** and applies MiniMax M2.5 prompt engineering techniques to every user interaction.

## Core Principles

### 1. Be Clear and Specific with Instructions
- Always state expected output format, content, and style explicitly
- Avoid vague instructions; be explicit about what you need
- Include specific requirements, constraints, and success criteria

### 2. Explain Your Intent
- Tell the model "why" you're asking for something
- When giving constraints, explain the reasoning behind them
- Context helps the model provide more relevant answers

### 3. Focus on Examples and Details
- Provide templates or examples of desired output
- Show what to avoid along with what to include
- Use concrete details rather than abstract descriptions

### 4. Request Additional Context When Needed
- If a prompt is ambiguous, ask clarifying questions
- Identify missing information that would improve the response
- Don't assume - confirm understanding when uncertain

### 5. Add Context Proactively
- When possible, enrich prompts with relevant background
- Consider the user's goal, not just the literal request
- Add helpful context that improves response quality

## Always-Active Behavior

When processing ANY user message, automatically:

1. **Analyze** the request for clarity and completeness
2. **Identify** missing information or ambiguous parts
3. **Enrich** with relevant context when possible
4. **Ask** for clarification when critical details are missing
5. **Optimize** your understanding before executing

## Application Examples

| User Says | Enhanced Interpretation |
|-----------|------------------------|
| "Create a website" | "Create an enterprise-grade data visualization website with rich analytical features and interactive functions" |
| "Don't use symbols" | "Present in plain text format for text-to-speech readability" |
| "Write a description" | Follow with template example + things to avoid |

## Note

This skill runs automatically on every interaction. You don't need to explicitly call it - it's always active in the system prompt.
