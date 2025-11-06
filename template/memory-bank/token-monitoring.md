---
enabled: true
logLevel: "info"  # debug | info | warn | error
logDestination: "progress.md:tokenUsage"
monitoringInterval: "after-each-operation"
thresholds:
  warning: 150000
  critical: 180000
  emergency: 195000
actions:
  onWarning:
    - action: "log-warning"
      message: "Token usage at 75%. Switching to minimal context mode."
    - action: "switch-context-mode"
      mode: "minimal"
    - action: "unload-cold-data"
    - action: "create-checkpoint"
  onCritical:
    - action: "log-critical"
      message: "Token usage at 90%. Initiating task decomposition."
    - action: "save-state"
    - action: "decompose-current-task"
      maxSubtasks: 5
    - action: "switch-context-mode"
      mode: "recovery"
  onEmergency:
    - action: "emergency-save"
    - action: "halt-execution"
    - action: "create-resume-checkpoint"
      includeInstructions: true
metrics:
  trackPerOperation: true
  estimateBeforeLoad: true
  compareActualVsEstimate: true
  reportSummary: "end-of-session"
optimizationHints:
  - "Batch read operations when possible"
  - "Use delta updates instead of full rewrites"
  - "Load stack profiles only when coding"
  - "Defer deliverables until release phase"
  - "Cache frequently accessed data in memory"
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Token Monitoring — Usage Guidelines

> **AI instruction**: Continuously monitor token usage and take proactive action before limits are reached.

## Monitoring Protocol

### After Every Operation

1. **Estimate tokens consumed**:
   - File read: ~(filesize / 4) tokens
   - YAML frontmatter: ~(linecount * 15) tokens
   - Task processing: ~2000 tokens

2. **Update running total**:
   ```
   totalUsed = previousTotal + currentOperation
   ```

3. **Check thresholds**:
   - If totalUsed > warning: Execute `onWarning` actions
   - If totalUsed > critical: Execute `onCritical` actions
   - If totalUsed > emergency: Execute `onEmergency` actions

4. **Log to progress**:
   ```yaml
   tokenUsage:
     - timestamp: "2025-10-30T10:15:00Z"
       operation: "Read taskBoard.md"
       estimated: 1200
       actual: 1350
       total: 45000
       percentUsed: 22.5
   ```

## Task Decomposition Protocol

When critical threshold reached and current task is incomplete:

1. **Analyze remaining work**:
   - Estimate time: < 30min → complete it
   - Estimate time: > 30min → decompose

2. **Decompose into subtasks**:
   ```yaml
   # Original task
   - id: "T005"
     title: "Implement user authentication"
     status: "in_progress"

   # Decomposed (add to backlog)
   - id: "T005-1"
     title: "Create auth models"
     parent: "T005"
     priority: "H"
   - id: "T005-2"
     title: "Implement login endpoint"
     parent: "T005"
     priority: "H"
   - id: "T005-3"
     title: "Add JWT middleware"
     parent: "T005"
     priority: "H"
   ```

3. **Mark parent as decomposed**:
   ```yaml
   - id: "T005"
     title: "Implement user authentication"
     status: "decomposed"
     subtasks: ["T005-1", "T005-2", "T005-3"]
   ```

4. **Continue with first subtask** in minimal mode

## Recovery Protocol

When resuming from checkpoint:

1. **Load checkpoint data**:
   - Read `checkpoints/latest.json`
   - Extract: completedTasks, inProgress, context snapshot

2. **Minimal context load**:
   - activeContext.md
   - Current task from backlog
   - Essential config only

3. **Resume execution**:
   - Pick up where left off
   - Use compact formats
   - Defer non-critical updates

4. **Full sync after completion**:
   - Update all files
   - Clear checkpoint
   - Return to standard mode

## Token Efficiency Best Practices

1. **Read Operations**:
   - ✅ Read only needed sections: `projectConfig.md:identity`
   - ✅ Use array slicing: `backlog[0:3]`
   - ❌ Don't read entire file if only need frontmatter

2. **Write Operations**:
   - ✅ Use delta tracker for progress updates
   - ✅ Batch multiple updates into single write
   - ❌ Don't rewrite entire file for single field change

3. **Context Management**:
   - ✅ Unload cold data after use
   - ✅ Cache hot data in session memory
   - ❌ Don't keep full memory bank loaded

4. **Task Processing**:
   - ✅ Complete small tasks in minimal mode
   - ✅ Decompose large tasks proactively
   - ❌ Don't attempt large tasks near token limit

## Example Session Log

```yaml
tokenUsage:
  - timestamp: "2025-10-30T10:00:00Z"
    operation: "Session start - load initial context"
    estimated: 4000
    actual: 3850
    total: 3850
    percentUsed: 1.9
    mode: "standard"

  - timestamp: "2025-10-30T10:05:00Z"
    operation: "Load techContext for Task T001"
    estimated: 2000
    actual: 2200
    total: 6050
    percentUsed: 3.0
    mode: "standard"

  - timestamp: "2025-10-30T10:45:00Z"
    operation: "Task T005 processing"
    estimated: 15000
    actual: 18000
    total: 152000
    percentUsed: 76.0
    mode: "standard"
    alert: "WARNING - switching to minimal mode"

  - timestamp: "2025-10-30T10:46:00Z"
    operation: "Switch to minimal context"
    estimated: -10000
    actual: -11000
    total: 141000
    percentUsed: 70.5
    mode: "minimal"

  - timestamp: "2025-10-30T11:15:00Z"
    operation: "Task T005 decomposition"
    estimated: 500
    actual: 450
    total: 179500
    percentUsed: 89.8
    mode: "recovery"
    alert: "CRITICAL - task decomposed into T005-1, T005-2, T005-3"
```
