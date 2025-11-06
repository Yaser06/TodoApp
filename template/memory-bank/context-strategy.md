---
version: "1.0"
strategy: "incremental"
tokenBudget:
  total: 200000
  reserved: 50000  # For responses and code generation
  warningThreshold: 150000  # 75%
  criticalThreshold: 180000  # 90%
loadingPolicy:
  initial:
    priority: "high"
    files:
      - "core/project.yaml"
      - "core/active.yaml"
      - "context-strategy.md"
      - "token-monitoring.md"
    estimatedTokens: 3000
    lazyLoad: true
  onDemand:
    priority: "medium"
    triggers:
      - condition: "task selection"
        load: ["work/backlog.yaml", "work/sprint-metrics.yaml"]
        estimatedTokens: 1500
      - condition: "task involves coding (tags: be,fe,api,db)"
        load: ["reference/tech-stack.yaml", "agents-stack/{STACK_ID}/agentsrules"]
        estimatedTokens: 4000
      - condition: "architectural decision needed"
        load: ["reference/patterns.yaml"]
        estimatedTokens: 2000
      - condition: "release preparation"
        load: ["reference/delivery.yaml"]
        estimatedTokens: 2000
      - condition: "running tests"
        load: ["reference/delivery.yaml:qualityGates"]
        estimatedTokens: 500
  cached:
    priority: "low"
    files:
      - "reference/history.yaml"
      - "reference/delivery.yaml:releaseChecklist"
      - "reference/patterns.yaml"
    loadOnlyIf: "explicitly requested"
    unloadImmediately: true
dataClassification:
  hot:
    description: "Always loaded, never unloaded"
    ttl: "session"
    directory: "core/"
    files:
      - "core/project.yaml"
      - "core/active.yaml"
      - "context-strategy.md"
      - "token-monitoring.md"
  warm:
    description: "Loaded on task selection, unloaded after task"
    ttl: "task-duration"
    directory: "work/"
    files:
      - "work/backlog.yaml"
      - "work/sprint-metrics.yaml"
      - "progress-delta.json"
  cold:
    description: "Load on trigger, unload immediately after use"
    ttl: "immediate"
    directory: "reference/"
    files:
      - "reference/tech-stack.yaml"
      - "reference/patterns.yaml"
      - "reference/delivery.yaml"
      - "reference/history.yaml"
contextModes:
  full:
    description: "Load all memory bank files"
    useCase: "Initial setup, architecture planning"
    estimatedTokens: 18000
  standard:
    description: "Load hot + warm data"
    useCase: "Regular development tasks"
    estimatedTokens: 7000
  minimal:
    description: "Load only hot data + current task"
    useCase: "Token warning threshold reached"
    estimatedTokens: 3000
  recovery:
    description: "Load only checkpoint + current task"
    useCase: "Resume after token limit or error"
    estimatedTokens: 2000
compressionRules:
  taskFormat: "compact"  # Use abbreviated field names
  arrayLimit: 10  # Max items to load from arrays
  stringTruncate: 200  # Max chars for description fields
  omitEmpty: true  # Skip null/empty fields in YAML
  inlineRefs: false  # Don't expand {{references}}
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Context Strategy — Memory Optimization

> **AI instruction**: This file controls how you load and manage memory bank context to optimize token usage. Follow these rules strictly.

## Loading Sequence

1. **Bootstrap** (start of session):
   - Load only `initial.files` from `loadingPolicy`
   - Estimate total token usage
   - Select appropriate `contextMode` based on task complexity

2. **Execution** (during task processing):
   - Keep hot data in active context
   - Load warm data when needed (trigger-based)
   - Avoid loading cold data unless explicitly required

3. **Recovery** (on token warning):
   - Switch to `minimal` mode
   - Unload cold and warm data
   - Complete current task with hot data only
   - Full sync after task completion

## Token Monitoring

Check token usage after every operation:
- Read operation: Log estimated tokens
- Write operation: Log delta size
- Context switch: Recalculate total

If `warningThreshold` reached:
- Switch to minimal mode
- Consider task decomposition
- Create checkpoint

If `criticalThreshold` reached:
- Save state immediately
- Decompose current task
- Resume with recovery mode

## Compression Guidelines

Use compact formats:
- Task IDs: `T001` not `TASK-001`
- Acceptance criteria: Pipe-separated `ac: "201|validation|coverage>90"`
- Tags: Comma-separated `tags: "be,auth"`
- Dependencies: Array of IDs only `deps: ["T000"]`

## Example Token Budget

```
Initial load (minimal mode):     3,000 tokens
Average task context:            2,000 tokens
Code generation buffer:         10,000 tokens
Response generation:             5,000 tokens
Safety margin:                  30,000 tokens
-------------------------------------------
Total per task cycle:           50,000 tokens
Target: 4 tasks per 200K budget
```
