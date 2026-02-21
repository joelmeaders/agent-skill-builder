---
name: prompt-engineering-patterns
description: Master advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability in production. Use when optimizing prompts, improving LLM outputs, or designing production prompt templates.
---

# Prompt Engineering Patterns

Master advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability.

## When to Use This Skill

- Designing complex prompts for production LLM applications
- Optimizing prompt performance and consistency
- Implementing structured reasoning patterns (chain-of-thought, tree-of-thought)
- Building few-shot learning systems with dynamic example selection
- Creating reusable prompt templates with variable interpolation
- Debugging and refining prompts that produce inconsistent outputs
- Implementing system prompts for specialized AI assistants
- Using structured outputs (JSON mode) for reliable parsing

## Core Capabilities

### 1. Few-Shot Learning
- Example selection strategies (semantic similarity, diversity sampling)
- Balancing example count with context window constraints
- Constructing effective demonstrations with input-output pairs

### 2. Chain-of-Thought Prompting
- Step-by-step reasoning elicitation
- Zero-shot CoT with "Let's think step by step"
- Few-shot CoT with reasoning traces
- Self-consistency techniques

### 3. Structured Outputs
- JSON mode for reliable parsing
- Pydantic schema enforcement
- Type-safe response handling

### 4. Prompt Optimization
- Iterative refinement workflows
- A/B testing prompt variations
- Measuring prompt performance metrics

### 5. Template Systems
- Variable interpolation and formatting
- Conditional prompt sections
- Multi-turn conversation templates

### 6. System Prompt Design
- Setting model behavior and constraints
- Defining output formats and structure
- Establishing role and expertise

## Best Practices

1. **Be Specific**: Vague prompts produce inconsistent results
2. **Show, Don't Tell**: Examples are more effective than descriptions
3. **Use Structured Outputs**: Enforce schemas with Pydantic for reliability
4. **Test Extensively**: Evaluate on diverse, representative inputs
5. **Iterate Rapidly**: Small changes can have large impacts
6. **Monitor Performance**: Track metrics in production

## Common Pitfalls

- Over-engineering: Starting with complex prompts before trying simple ones
- Example pollution: Using examples that don't match the target task
- Ambiguous instructions: Leaving room for multiple interpretations
- No error handling: Assuming outputs will always be well-formed

## Resources

- Anthropic Prompt Engineering Guide
- OpenAI Prompt Engineering
- LangChain Prompts
