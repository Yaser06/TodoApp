# Work — Active Task Tracking

This directory contains **warm data** related to ongoing work. Loaded on demand when tasks are being executed.

## Files

- `backlog.yaml` - Task queue in compact format
- `progress-delta.json` - Incremental change tracker
- `sprint-metrics.yaml` - Current sprint statistics

## Characteristics

- **Load timing**: When starting task execution
- **Token cost**: ~2-3K tokens
- **Update frequency**: On task completion, batch writes
- **Cache strategy**: Unload after task completion

## Purpose

Tracks:
- Pending tasks
- Work in flight
- Progress metrics
- Quality trends

## Loading Triggers

- User requests task list
- Agent selects next task
- Progress report needed
- Sprint planning

## What NOT to Put Here

- Project identity (→ core/)
- Stack configuration (→ reference/)
- Architecture patterns (→ reference/)
- Old completed tasks (archive after sprint)
