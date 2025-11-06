# Core — Always-Loaded Context

This directory contains **hot data** that is always loaded at session start and kept in active context.

## Files

- `project.yaml` - Merged projectPrompt + projectConfig essentials
- `active.yaml` - Current task and immediate focus
- `context-strategy.yaml` - Loading rules and token budgets

## Characteristics

- **Load timing**: Session bootstrap (first 3 seconds)
- **Token cost**: ~3-4K tokens
- **Update frequency**: Every task switch
- **Cache strategy**: Keep in memory, never unload

## Purpose

Provides minimal essential context for:
- Task identification and selection
- Stack determination
- Current work status
- Token management rules

## What NOT to Put Here

- Full technical details (→ reference/)
- Historical progress logs (→ work/)
- Completed tasks (→ work/)
- Stack-specific patterns (→ reference/)
- Delivery artifacts (→ reference/)
