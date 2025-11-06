# Reference — Rarely-Loaded Documentation

This directory contains **cold data** that is only loaded when explicitly needed for specific decisions.

## Files

- `tech-stack.yaml` - Full technical context and stack details
- `patterns.yaml` - Architectural patterns and best practices
- `delivery.yaml` - Deliverables, quality gates, release checklist
- `history.yaml` - Completed work, lessons learned

## Characteristics

- **Load timing**: On explicit need (architecture decision, release prep)
- **Token cost**: ~5-8K tokens (full load)
- **Update frequency**: Rare (end of sprint, major decisions)
- **Cache strategy**: Load → use → unload immediately

## Purpose

Provides deep context for:
- Architectural decisions
- Stack-specific coding patterns
- Quality gate definitions
- Release preparation
- Historical reference

## Loading Triggers

- `"Review architecture"` command
- Quality gate enforcement
- Release checklist execution
- Pattern lookup
- Lessons learned review

## Optimization

Load selectively:
- `tech-stack.yaml:frameworkModules` (not full file)
- `patterns.yaml:stackSpecific` (only relevant stack)
- `delivery.yaml:qualityGates` (only when testing)

## What NOT to Put Here

- Current task (→ core/active.yaml)
- Active backlog (→ work/backlog.yaml)
- Token rules (→ core/context-strategy.yaml)
