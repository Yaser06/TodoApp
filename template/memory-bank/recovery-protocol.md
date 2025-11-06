---
version: "1.0"
enabled: true
checkpointTriggers:
  tokenWarning: true
  tokenCritical: true
  sessionEnd: true
  taskCompletion: false
  manual: true
autoResume: true
recoveryMode: "minimal"
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Recovery Protocol — Checkpoint & Resume

> **AI instruction**: Follow this protocol when token limits approached or session interrupted. Always create checkpoints proactively.

## When to Create Checkpoint

### Automatic Triggers
1. **Token Warning (75%)**
   - Save current state to `checkpoints/latest.json`
   - Create timestamped backup
   - Switch to minimal context mode
   - Continue current task

2. **Token Critical (90%)**
   - Emergency save to `checkpoints/emergency-{timestamp}.json`
   - Decompose current task if incomplete
   - Halt execution after current operation
   - Provide resume instructions to user

3. **Session End**
   - Save if any work in progress
   - Include next steps and context

### Manual Trigger
User command: `"Create checkpoint"` or `"Save progress"`

## Checkpoint Creation Protocol

```yaml
# 1. Collect current state
state:
  completedTasks: [taskBoard.done task IDs]
  inProgress: [taskBoard.inProgress task IDs]
  backlogSnapshot: [next 5 backlog tasks]
  currentPhase: "bootstrap | development | testing | release"

# 2. Capture context
context:
  STACK_ID: [from projectConfig]
  currentSprint: [from taskBoard.sprintSchedule active]
  activeObjective: [from activeContext.currentObjective.summary]

# 3. Flush delta changes
deltaChanges: [copy from progress-delta.json]

# 4. Generate next steps
nextSteps:
  - "Complete current task T###"
  - "Run quality gates"
  - "Update progress metrics"

# 5. Write checkpoint
write: checkpoints/latest.json
backup: checkpoints/checkpoint-{timestamp}.json
```

## Resume Protocol

### On Session Start

```
1. Check for active checkpoint:
   - Read checkpoints/latest.json
   - If timestamp empty → no checkpoint, normal bootstrap
   - If timestamp present → checkpoint exists

2. Validate checkpoint:
   - Check timestamp < 24h old
   - Verify STACK_ID matches projectConfig
   - Confirm tasks still exist in taskBoard

3. Load minimal recovery context (max 2K tokens):
   - context-strategy.md (recovery mode)
   - projectConfig.md:STACK_ID
   - activeContext.md (from checkpoint)
   - Current task details only

4. Resume execution:
   - Apply delta changes from checkpoint
   - Continue with inProgress task
   - Use recovery mode (no stack profiles yet)

5. Complete current task:
   - Finish implementation
   - Run tests
   - Update progress

6. Full sync:
   - Flush all changes
   - Load standard context
   - Delete checkpoint
   - Return to normal mode
```

### Resume Command Format

When providing checkpoint to user:
```
Session interrupted at T004. To resume:

1. Start new session
2. Agent will auto-detect checkpoint
3. Or manually: "Resume from last checkpoint"
4. System loads minimal context and continues
```

## Recovery Mode Context Loading

In recovery mode, load only:
```yaml
required:
  - context-strategy.md
  - token-monitoring.md
  - projectConfig.md:STACK_ID
  - activeContext.md
  - Current task from checkpoints/latest.json

deferred:
  - Stack profiles (load when coding resumes)
  - techContext.md (load if needed)
  - systemPatterns.md (load if needed)
  - deliverables.md (skip unless release task)

estimated: 2,000 tokens max
```

## Error Recovery

If checkpoint resume fails:
1. Log error to progress.md:log
2. Fall back to normal bootstrap
3. Prompt user for manual intervention
4. Preserve checkpoint for debugging

## Checkpoint Maintenance

### Auto-Cleanup Rules
- Delete checkpoints > 7 days old
- Keep only latest + 5 timestamped backups
- Remove checkpoint on successful resume
- Archive emergency checkpoints separately

### Cleanup Script
```bash
# Run weekly or on session start
find checkpoints/ -name "checkpoint-*.json" -mtime +7 -delete
ls -t checkpoints/checkpoint-*.json | tail -n +6 | xargs rm -f
```

## Example Checkpoint

```json
{
  "version": "1.0",
  "timestamp": "2025-10-30T15:30:00Z",
  "reason": "token_critical",
  "tokenUsage": {
    "total": 182000,
    "percentage": 91,
    "mode": "recovery"
  },
  "state": {
    "completedTasks": ["T001", "T002", "T003", "T004"],
    "inProgress": "T005",
    "backlogSnapshot": [
      {"id": "T006", "title": "Add rate limiting"},
      {"id": "T007", "title": "Implement caching"},
      {"id": "T008", "title": "Setup monitoring"}
    ],
    "currentPhase": "development"
  },
  "context": {
    "STACK_ID": "fastapi",
    "currentSprint": "sprint-2",
    "activeObjective": "Complete authentication system"
  },
  "nextSteps": [
    "Finish T005: JWT refresh token logic",
    "Write unit tests for refresh endpoint",
    "Run pytest suite",
    "Update progress metrics",
    "Move T005 to done"
  ],
  "deltaChanges": [
    {"file": "taskBoard", "operation": "move", "taskId": "T005", "from": "backlog", "to": "inProgress"},
    {"file": "progress", "operation": "update", "field": "metrics.currentSprint.completed", "value": 4}
  ],
  "resumeInstructions": "Load recovery context, complete T005 JWT refresh implementation, run tests, then full sync and return to standard mode."
}
```

## Token Budget for Recovery

```
Checkpoint creation: ~500 tokens
Checkpoint load: ~300 tokens
Recovery context: ~2,000 tokens
Task completion: ~15,000 tokens
Full sync: ~1,000 tokens
-----------------------------------
Total recovery cycle: ~19,000 tokens

Safe to resume even at 90% token usage.
```
