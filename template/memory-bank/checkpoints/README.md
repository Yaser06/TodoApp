# Checkpoints Directory

This directory stores checkpoint files that allow the AI agent to resume work after interruptions (token limits, errors, session ends).

## File Naming Convention

- `latest.json` - Most recent checkpoint (always overwritten)
- `checkpoint-{timestamp}.json` - Timestamped backups
- `emergency-{timestamp}.json` - Created on critical token threshold

## Checkpoint Structure

```json
{
  "version": "1.0",
  "timestamp": "2025-10-30T10:45:00Z",
  "reason": "token_warning | token_critical | session_end | manual",
  "tokenUsage": {
    "total": 152000,
    "percentage": 76,
    "mode": "minimal"
  },
  "state": {
    "completedTasks": ["T001", "T002", "T003"],
    "inProgress": "T004",
    "backlogSnapshot": [...],
    "currentPhase": "development | testing | release"
  },
  "context": {
    "STACK_ID": "fastapi",
    "currentSprint": "sprint-1",
    "activeObjective": "Implement authentication"
  },
  "nextSteps": [
    "Complete T004: JWT middleware",
    "Run test suite",
    "Update progress metrics"
  ],
  "resumeInstructions": "Load minimal context, continue with T004 in recovery mode"
}
```

## Usage

### Creating a Checkpoint (Agent)

When token usage > warningThreshold:
```
1. Save current state to latest.json
2. Copy to timestamped backup
3. Continue in minimal mode
```

### Resuming from Checkpoint (Agent)

On session start, check for `latest.json`:
```
1. Load checkpoint data
2. Verify state matches memory-bank files
3. Resume with minimal context (2K tokens)
4. Complete interrupted task
5. Full sync after completion
6. Delete checkpoint
```

## Auto-Cleanup

- Keep only latest + last 5 timestamped checkpoints
- Delete checkpoints older than 7 days
- Remove checkpoint after successful resume
