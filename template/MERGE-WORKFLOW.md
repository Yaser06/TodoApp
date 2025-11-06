# 🔀 Merge Coordinator - Complete Workflow Guide

This document explains the **production-ready auto-merge system** that ensures conflict-free multi-agent collaboration.

---

## Table of Contents

1. [Overview](#overview)
2. [Task Status Lifecycle](#task-status-lifecycle)
3. [Merge Queue Architecture](#merge-queue-architecture)
4. [6-Step Merge Process](#6-step-merge-process)
5. [Conflict Resolution](#conflict-resolution)
6. [Test Failure Handling](#test-failure-handling)
7. [Agent Notification System](#agent-notification-system)
8. [Phase Advancement](#phase-advancement)
9. [Configuration Options](#configuration-options)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### Why Do We Need This?

**Problem**: Multiple agents working in parallel can create conflicts when merging to main:
- Agent 1 merges → main updated
- Agent 2's PR now has conflicts
- Agent 3's tests fail on outdated main
- System breaks down

**Solution**: Sequential merge coordinator that:
- ✅ Merges PRs one at a time (prevents race conditions)
- ✅ Detects conflicts before merging
- ✅ Runs tests before merging
- ✅ Notifies agents of issues
- ✅ Retries failed merges
- ✅ Only advances phases after successful merges

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Merge Coordinator                        │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Merge Queue │───▶│ Worker Thread│───▶│  Git Workflow│ │
│  │   (Redis)    │    │  (Sequential)│    │  (Isolated)  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Process: Update main → Check conflicts → Run tests   │  │
│  │          → Merge PR → Cleanup → Advance phase        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Task Status Lifecycle

Tasks go through these states:

```
pending ──▶ in_progress ──▶ done ──▶ [MERGE QUEUE] ──▶ merged
                              │
                              ├──▶ conflict ──▶ done ──▶ [RETRY]
                              │
                              ├──▶ test_failed ──▶ done ──▶ [RETRY]
                              │
                              └──▶ merge_failed ──▶ [RETRY 3x] ──▶ failed
```

### Status Definitions

| Status | Meaning | Agent State | Next Step |
|--------|---------|-------------|-----------|
| `pending` | Task not started | Available to claim | Agent claims task |
| `in_progress` | Agent working on task | Working | Agent completes & creates PR |
| `done` | PR created, awaiting merge | Idle | Enters merge queue |
| `conflict` | Merge conflict detected | Notified | Agent fixes conflict, re-pushes |
| `test_failed` | Tests failed on branch | Notified | Agent fixes tests, re-pushes |
| `merge_failed` | Merge failed (3x retry) | Notified | Manual intervention needed |
| `merged` | Successfully merged to main | - | Phase may advance |
| `failed` | Permanently failed | - | Skip in phase calculation |

### Key Points

- **Phase advancement** only happens when tasks reach `merged` or `failed` status
- `done` ≠ `merged` - Task in `done` is waiting in merge queue
- Conflicts and test failures are **temporary states** - agent gets notified to fix

---

## Merge Queue Architecture

### How It Works

1. **Agent completes task** → Creates PR → Calls `/task/complete`
2. **Orchestrator queues merge** → Adds to Redis queue: `orchestrator:merge_queue`
3. **Background worker** → Processes queue **sequentially** (one at a time)
4. **After merge** → Checks if phase is complete, advances if needed

### Why Sequential?

**Parallel merging causes race conditions**:

```
❌ Parallel (BROKEN):
T1: Update main (commit A) → Merge T1 (commit B)
T2: Update main (commit A) → Merge T2 (commit C)  ← CONFLICT! T1's commit B not included
```

```
✅ Sequential (CORRECT):
T1: Update main (commit A) → Merge T1 (commit B)
T2: Update main (commit B) → Merge T2 (commit C)  ← Safe! Includes T1's changes
```

### Queue Implementation

```python
# Redis-backed FIFO queue
merge_queue_key = "orchestrator:merge_queue"

# Agent completes task
merge_request = {
    "task_id": "T001",
    "pr_url": "https://github.com/user/repo/pull/1",
    "branch_name": "ai-agent-1/task-T001",
    "agent_id": "ai-agent-1",
    "queued_at": "2025-11-01T10:30:00",
    "retry_count": 0
}

# Add to queue (FIFO)
redis.rpush(merge_queue_key, json.dumps(merge_request))

# Worker processes (blocking pop with 5s timeout)
result = redis.blpop(merge_queue_key, timeout=5)
```

---

## 6-Step Merge Process

When a merge request is dequeued, the coordinator executes these steps:

### Step 1: Update Main Branch

```python
def _update_main_branch(self):
    # Checkout main
    subprocess.run(["git", "checkout", "main"])

    # Pull latest (if remote exists)
    if push_to_remote:
        subprocess.run(["git", "pull", "--rebase"])
```

**Purpose**: Ensure we're merging into the latest main branch.

---

### Step 2: Check for Conflicts

```python
def _check_conflicts(self, branch_name):
    # Dry-run merge (don't actually commit)
    result = subprocess.run([
        "git", "merge", "--no-commit", "--no-ff", branch_name
    ])

    # Abort the merge
    subprocess.run(["git", "merge", "--abort"])

    # Check if conflict occurred
    return "CONFLICT" in result.stdout
```

**Purpose**: Detect conflicts **before** attempting actual merge.

**If conflict detected**:
1. Task status → `conflict`
2. Agent notified via Redis pub/sub
3. Agent fixes conflict, re-pushes
4. New PR triggers new merge request

---

### Step 3: Run Tests

```python
def _run_tests(self, branch_name):
    # Checkout branch
    subprocess.run(["git", "checkout", branch_name])

    # Run quality checks from config
    for check in config['quality_gates']['checks']:
        if check['required']:
            subprocess.run(check['command'].split(), check=True)

    # Go back to main
    subprocess.run(["git", "checkout", "main"])
```

**Purpose**: Ensure tests pass on branch before merging.

**If tests fail**:
1. Task status → `test_failed`
2. Agent notified
3. Agent fixes tests, re-pushes
4. New merge request created

---

### Step 4: Merge PR

Two modes depending on configuration:

#### Remote Mode (`push_to_remote: true`)

```python
# Extract PR number from URL
pr_number = pr_url.split('/')[-1]

# Merge using GitHub CLI (squash merge)
subprocess.run([
    "gh", "pr", "merge", pr_number,
    "--squash",
    "--delete-branch"
])
```

#### Local Mode (`push_to_remote: false`)

```python
# Merge branch to main (squash)
subprocess.run(["git", "merge", "--squash", branch_name])

# Commit
subprocess.run(["git", "commit", "-m", f"Merge {branch_name}"])
```

**Purpose**: Actually merge the code into main branch.

---

### Step 5: Cleanup Branch

```python
def _cleanup_branch(self, branch_name):
    # Delete local branch
    subprocess.run(["git", "branch", "-D", branch_name])

    # Delete remote branch (if exists)
    if push_to_remote:
        subprocess.run(["git", "push", "origin", "--delete", branch_name])
```

**Purpose**: Keep repository clean, prevent branch clutter.

---

### Step 6: Update Task Status & Check Phase

```python
def _mark_task_merged(self, task_id):
    task['status'] = 'merged'
    task['merged_at'] = datetime.now().isoformat()
    redis.hset("orchestrator:tasks", task_id, json.dumps(task))

# Check if phase complete
def _check_phase_advancement(self):
    # If all tasks in phase are 'merged' or 'failed'
    if all_complete:
        # Mark phase complete
        # Start next phase
        # Log advancement
```

**Purpose**: Mark task complete, advance phase if ready.

---

## Conflict Resolution

### Conflict Detection

Conflicts are detected using a **dry-run merge**:

```bash
# Try to merge (but don't commit)
git merge --no-commit --no-ff ai-agent-1/task-T001

# Check output for "CONFLICT"
# Then abort
git merge --abort
```

### Conflict Workflow

```
┌────────────┐
│ Merge Queue│
└─────┬──────┘
      │
      ▼
┌────────────────────┐
│ Dry-run Merge Test │
└─────┬──────────────┘
      │
      ├─[NO CONFLICT]──▶ Continue to Step 3 (Tests)
      │
      └─[CONFLICT]──▶ Handle Conflict
                      │
                      ├─1. Mark task status: 'conflict'
                      │
                      ├─2. Notify agent via Redis pub/sub
                      │   Channel: agent:{agent_id}:notifications
                      │   Message: {
                      │     "event_type": "conflict_detected",
                      │     "branch": "ai-agent-1/task-T001",
                      │     "action_required": "resolve_conflict"
                      │   }
                      │
                      └─3. Agent resolves conflict
                          │
                          ├─ Agent pulls latest main
                          ├─ Agent rebases branch
                          ├─ Agent fixes conflicts
                          ├─ Agent pushes updated branch
                          │
                          └─ New merge request queued
```

### Agent-Side Conflict Resolution (To Be Implemented)

```python
# Agent receives notification
notification = redis.subscribe(f"agent:{agent_id}:notifications")

if notification['event_type'] == 'conflict_detected':
    branch_name = notification['branch']

    # Checkout branch
    git_checkout(branch_name)

    # Pull latest main and rebase
    subprocess.run(["git", "pull", "origin", "main", "--rebase"])

    # Use Claude Code to resolve conflicts
    # (Read conflicted files, ask Claude to resolve)

    # Push fixed branch
    subprocess.run(["git", "push", "--force-with-lease"])

    # Re-trigger merge (automatic when PR updated)
```

---

## Test Failure Handling

### Test Execution

Tests run on the branch **before merging**:

```python
# Checkout branch (not main!)
git checkout ai-agent-1/task-T001

# Run all required checks
npm test
npm run lint
npm run build

# Only merge if all pass
```

### Test Failure Workflow

```
┌────────────┐
│ Run Tests  │
└─────┬──────┘
      │
      ├─[PASS]──▶ Continue to Step 4 (Merge)
      │
      └─[FAIL]──▶ Handle Test Failure
                  │
                  ├─1. Mark task status: 'test_failed'
                  │
                  ├─2. Notify agent via Redis pub/sub
                  │   Message: {
                  │     "event_type": "tests_failed",
                  │     "task_id": "T001",
                  │     "action_required": "fix_tests"
                  │   }
                  │
                  └─3. Agent fixes tests
                      │
                      ├─ Agent checks test logs
                      ├─ Agent fixes failing tests
                      ├─ Agent pushes updated branch
                      │
                      └─ New merge request queued
```

### Common Test Failures

| Failure Type | Cause | Solution |
|--------------|-------|----------|
| **Unit tests fail** | Code logic error | Debug and fix implementation |
| **Integration tests fail** | Dependency not updated | Update dependencies or mocks |
| **Lint errors** | Code style issues | Run linter and fix warnings |
| **Build errors** | Syntax or type errors | Fix compilation errors |
| **Timeout** | Tests taking >5min | Optimize or increase timeout |

---

## Agent Notification System

### Architecture

```
┌─────────────────────┐
│ Merge Coordinator   │
└──────────┬──────────┘
           │
           │ (Publishes notification)
           │
           ▼
┌─────────────────────┐
│ Redis Pub/Sub       │
│ Channel: agent:{id}:│
│         notifications│
└──────────┬──────────┘
           │
           │ (Subscribes to channel)
           │
           ▼
┌─────────────────────┐
│ Agent Client        │
│ (Receives & Acts)   │
└─────────────────────┘
```

### Notification Types

#### 1. Conflict Detected

```json
{
  "agent_id": "ai-agent-1",
  "task_id": "T001",
  "event_type": "conflict_detected",
  "data": {
    "message": "Merge conflict detected in ai-agent-1/task-T001",
    "branch": "ai-agent-1/task-T001",
    "action_required": "resolve_conflict"
  },
  "timestamp": "2025-11-01T10:35:00"
}
```

**Agent Action**: Rebase branch on latest main, resolve conflicts, re-push.

---

#### 2. Tests Failed

```json
{
  "agent_id": "ai-agent-1",
  "task_id": "T001",
  "event_type": "tests_failed",
  "data": {
    "message": "Tests failed for T001",
    "action_required": "fix_tests"
  },
  "timestamp": "2025-11-01T10:36:00"
}
```

**Agent Action**: Check test logs, fix failing tests, re-push.

---

#### 3. Merge Failed

```json
{
  "agent_id": "ai-agent-1",
  "task_id": "T001",
  "event_type": "merge_failed",
  "data": {
    "message": "Merge failed after 3 retries for T001",
    "action_required": "manual_intervention"
  },
  "timestamp": "2025-11-01T10:37:00"
}
```

**Agent Action**: Alert user, requires manual investigation.

---

#### 4. Merge Success

```json
{
  "agent_id": "ai-agent-1",
  "task_id": "T001",
  "event_type": "merge_success",
  "data": {
    "message": "Task T001 successfully merged to main"
  },
  "timestamp": "2025-11-01T10:38:00"
}
```

**Agent Action**: Log success, claim next task.

---

### Notification Storage

Notifications are also stored in Redis for retrieval:

```python
# Publish to channel (real-time)
redis.publish(f"agent:{agent_id}:notifications", json.dumps(notification))

# Store for later retrieval (persistent)
redis.rpush(f"agent:{agent_id}:notifications:pending", json.dumps(notification))

# Agent retrieves pending notifications
pending = redis.lrange(f"agent:{agent_id}:notifications:pending", 0, -1)
```

---

## Phase Advancement

### Phase Completion Criteria

A phase is **complete** when **all tasks** in the phase are in one of these states:
- ✅ `merged` - Successfully merged to main
- ❌ `failed` - Permanently failed (3x retry limit)

**Important**: `done` (PR created) is **NOT** considered complete. Code must be merged into main.

### Advancement Logic

```python
def _check_phase_advancement(self):
    # Get current phase
    phase = get_current_phase()

    # Check all tasks in phase
    all_complete = True
    for task_id in phase['tasks']:
        task = get_task(task_id)

        # Task must be merged or failed
        if task['status'] not in ['merged', 'failed']:
            all_complete = False
            break

    if all_complete:
        # Mark phase complete
        phase['status'] = 'completed'
        phase['completed_at'] = datetime.now().isoformat()

        # Start next phase
        next_phase = get_next_phase()
        if next_phase:
            next_phase['status'] = 'active'
            next_phase['started_at'] = datetime.now().isoformat()

            logger.info(f"📍 Starting Phase {next_phase['id']} ({next_phase['name']})")
        else:
            logger.info("🎉 All phases complete!")
```

### Why This Matters

**Without proper advancement**:

```
❌ BROKEN:
Phase 1: [T001: done, T002: done] → Advance to Phase 2
Phase 2: T003 depends on T001, T002
         But T001, T002 not merged yet!
         T003 fails because code not in main
```

**With merge coordinator**:

```
✅ CORRECT:
Phase 1: [T001: done, T002: done] → Wait for merge
         [T001: merged, T002: merged] → Advance to Phase 2
Phase 2: T003 depends on T001, T002
         Code is in main, T003 succeeds
```

---

## Configuration Options

### Enable/Disable Auto-Merge

```yaml
# orchestrator-config.yaml
git:
  auto_merge:
    enabled: true  # Set to false for manual PR merging
```

**When disabled**:
- PRs created but not merged
- You merge manually: `gh pr merge 1`
- Phase advancement waits for you to merge

---

### Require Manual Review

```yaml
git:
  auto_merge:
    enabled: true
    require_review: true  # Agent assigned to review task must approve
```

**When enabled**:
- Merge waits for review task completion
- Review agent checks code, approves PR
- Then merge coordinator merges

---

### Test Requirements

```yaml
git:
  auto_merge:
    require_tests_pass: true  # Always run tests before merge

quality_gates:
  checks:
    - name: "Tests Pass"
      command: "npm test"
      required: true  # Blocks merge if fails

    - name: "Build Success"
      command: "npm run build"
      required: false  # Warning only, doesn't block
```

---

### Retry Settings

```yaml
advanced:
  retry_failed_tasks: true
  max_retries: 3  # Retry merge up to 3 times before marking failed
```

---

## Troubleshooting

### Issue: Merges Not Happening

**Symptoms**:
- Tasks stuck in `done` status
- Phase not advancing

**Diagnosis**:

```bash
# Check if merge coordinator running
./orchestrate.sh status
# Look for: "Merge coordinator initialized (auto-merge enabled)"

# Check merge queue
docker exec -it orchestrator-redis redis-cli
> LLEN orchestrator:merge_queue
> LRANGE orchestrator:merge_queue 0 -1

# Check orchestrator logs
docker-compose logs orchestrator-api
```

**Solutions**:

1. **Auto-merge disabled in config**:
   ```yaml
   # orchestrator-config.yaml
   git:
     auto_merge:
       enabled: true  # Make sure this is true
   ```

2. **Merge coordinator crashed**:
   ```bash
   # Restart orchestrator
   ./orchestrate.sh stop
   ./orchestrate.sh
   ```

3. **Redis connection issue**:
   ```bash
   # Check Redis health
   docker-compose ps
   # If unhealthy, restart
   docker-compose restart redis
   ```

---

### Issue: Conflicts Not Getting Resolved

**Symptoms**:
- Tasks stuck in `conflict` status
- Agents not fixing conflicts

**Diagnosis**:

```bash
# Check task status
./orchestrate.sh status | grep conflict

# Check if agent received notification
docker exec -it orchestrator-redis redis-cli
> LRANGE agent:ai-agent-1:notifications:pending 0 -1
```

**Solutions**:

1. **Agent not listening to notifications** (not yet implemented):
   - Agent notification listener needs to be implemented
   - For now, agent should periodically check for notifications

2. **Manual conflict resolution**:
   ```bash
   # Checkout the conflicted branch
   git checkout ai-agent-1/task-T001

   # Pull and rebase on main
   git pull origin main --rebase

   # Resolve conflicts manually
   # Edit conflicted files
   git add .
   git rebase --continue

   # Force push (safe with --force-with-lease)
   git push --force-with-lease
   ```

3. **Skip task** (if unresolvable):
   ```bash
   # Mark task as failed
   # Edit task status in Redis or via API
   ```

---

### Issue: Tests Keep Failing

**Symptoms**:
- Task in `test_failed` status
- Merge queue not progressing

**Diagnosis**:

```bash
# Check which tests failed
docker-compose logs orchestrator-api | grep "test"

# Run tests locally on branch
git checkout ai-agent-1/task-T001
npm test
```

**Solutions**:

1. **Fix tests in branch**:
   ```bash
   git checkout ai-agent-1/task-T001
   # Fix failing tests
   git add .
   git commit -m "Fix tests"
   git push
   ```

2. **Update test configuration**:
   ```yaml
   # orchestrator-config.yaml
   quality_gates:
     checks:
       - name: "Tests Pass"
         command: "npm test"
         required: false  # Make non-blocking temporarily
   ```

3. **Skip quality gates** (not recommended):
   ```yaml
   git:
     auto_merge:
       require_tests_pass: false  # ⚠️ Dangerous!
   ```

---

### Issue: Merge Queue Stuck

**Symptoms**:
- Queue has items but nothing processing
- Worker thread not running

**Diagnosis**:

```bash
# Check queue length
docker exec -it orchestrator-redis redis-cli LLEN orchestrator:merge_queue

# Check active merges
docker exec -it orchestrator-redis redis-cli HGETALL orchestrator:active_merges

# Check logs for worker thread
docker-compose logs orchestrator-api | grep "merge worker"
```

**Solutions**:

1. **Worker thread crashed**:
   ```bash
   # Restart orchestrator
   docker-compose restart orchestrator-api
   ```

2. **Task stuck in active_merges**:
   ```bash
   # Clear active merges (will retry)
   docker exec -it orchestrator-redis redis-cli DEL orchestrator:active_merges
   ```

3. **Clear entire queue** (nuclear option):
   ```bash
   # ⚠️ WARNING: This loses all pending merges
   docker exec -it orchestrator-redis redis-cli DEL orchestrator:merge_queue
   ```

---

### Issue: Phase Not Advancing

**Symptoms**:
- All tasks merged but phase not advancing
- Agents waiting for next phase

**Diagnosis**:

```bash
# Check current phase
./orchestrate.sh status

# Check all task statuses
docker exec -it orchestrator-redis redis-cli HGETALL orchestrator:tasks | grep status
```

**Solutions**:

1. **Task not marked as merged**:
   ```python
   # Check if merge coordinator called _mark_task_merged()
   # Manually update if needed:
   task['status'] = 'merged'
   task['merged_at'] = datetime.now().isoformat()
   ```

2. **Phase advancement check not triggered**:
   ```python
   # After each merge, _check_phase_advancement() should be called
   # If not, manually trigger:
   curl -X POST http://localhost:8765/phase/advance
   ```

3. **Dependency issue**:
   ```bash
   # Check if a task in phase failed
   # Failed tasks block phase advancement
   # Mark failed tasks appropriately
   ```

---

## Summary: What Makes This Production-Ready?

✅ **Sequential merge queue** - Prevents race conditions

✅ **Conflict detection** - Finds conflicts before breaking main

✅ **Test execution** - Ensures quality before merge

✅ **Agent notifications** - Real-time feedback for issues

✅ **Retry mechanism** - Handles transient failures

✅ **Proper phase advancement** - Only advances after code merged

✅ **Branch cleanup** - Keeps repository clean

✅ **Configurable** - Enable/disable features as needed

✅ **Local & remote support** - Works with or without GitHub

---

## Next Steps

1. **Implement agent notification listener** - Agent-side code to handle notifications
2. **Add conflict resolution workflow** - Automated conflict resolution in agent
3. **Monitoring dashboard** - Real-time view of merge queue status
4. **Metrics collection** - Track merge success rate, conflict frequency, etc.

---

**For more information, see**:
- [Quick Start Guide](ORCHESTRATOR-QUICKSTART.md)
- [Setup Modes](SETUP-MODES.md)
- [Full Documentation](tools/orchestrator/README.md)
