---
version: "1.0"
enabled: true
strategy: "load-on-trigger"
cacheEnabled: true
cacheTTL: "1 hour"
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Lazy Loading Protocol — On-Demand Context

> **AI instruction**: Do not load all memory bank files upfront. Load incrementally based on task requirements. This is critical for token efficiency.

## Loading Phases

### Phase 1: Bootstrap (Immediate)
```yaml
# Load within first 3 seconds
files:
  - core/context-strategy.yaml
  - core/project.yaml
  - core/active.yaml
  - token-monitoring.md

estimatedTokens: 3000
timing: "session start"
cache: "keep in memory (hot)"
```

### Phase 2: Task Selection (On Demand)
```yaml
# Load when user/agent selects next task
files:
  - work/backlog.yaml
  - work/sprint-metrics.yaml (optional)

trigger: "task selection | backlog review"
estimatedTokens: 1500
timing: "before task execution"
cache: "keep for session (warm)"
unloadAfter: "task completion"
```

### Phase 3: Implementation (Conditional)
```yaml
# Load stack details ONLY when coding begins
files:
  - reference/tech-stack.yaml (if coding task)
  - agents-stack/{STACK_ID}/agentsrules (if coding task)
  - reference/patterns.yaml (if architectural decision)

triggers:
  - "task tags include: be, fe, db, api"
  - "acceptance criteria mention: implement, create, build"
  - "user requests: architecture review"

estimatedTokens: 4000
timing: "just before implementation"
cache: "unload after task done (cold)"
```

### Phase 4: Quality & Release (Very Conditional)
```yaml
# Load ONLY during testing or release prep
files:
  - reference/delivery.yaml:qualityGates (if running tests)
  - reference/delivery.yaml:releaseChecklist (if release task)
  - automation/runbook.md (if executing commands)

triggers:
  - "running test suite"
  - "release preparation"
  - "quality gate enforcement"

estimatedTokens: 2000
timing: "just before tests/release"
cache: "unload immediately (cold)"
```

### Phase 5: Reference (Explicit Only)
```yaml
# Load ONLY on explicit request
files:
  - reference/history.yaml
  - reference/patterns.yaml
  - systemPatterns.md
  - productContext.md

triggers:
  - user: "show lessons learned"
  - user: "review architecture"
  - user: "what patterns do we use?"

estimatedTokens: 3000
timing: "explicit command"
cache: "unload immediately"
```

## Loading Decision Tree

```
Session Start
└─> Load Phase 1 (core/) ~3K tokens
    └─> User selects task?
        ├─> No → Wait
        └─> Yes → Load Phase 2 (work/backlog) ~1.5K tokens
            └─> Task type?
                ├─> Coding/Implementation
                │   └─> Load Phase 3 (stack + tech) ~4K tokens
                │       └─> Execute task
                │           └─> Run tests?
                │               ├─> Yes → Load Phase 4 (quality gates) ~2K tokens
                │               └─> No → Complete task
                │                   └─> Unload Phase 3 & 4
                │                       └─> Update work/backlog (delta)
                │
                ├─> Planning/Documentation
                │   └─> Load reference/patterns ~3K tokens
                │       └─> Execute task
                │           └─> Unload patterns
                │
                └─> Testing/Release
                    └─> Load Phase 4 (delivery) ~2K tokens
                        └─> Execute
                            └─> Unload Phase 4
```

## Trigger-Based Loading Rules

### Rule 1: Stack Profiles
```yaml
trigger:
  condition: "task.tags contains coding tag (be, fe, db, api)"
  OR: "task.ac contains implement keyword"

action:
  load: "agents-stack/{STACK_ID}/agentsrules"
  load: "reference/tech-stack.yaml:frameworkModules"
  cache: "until task done"

example:
  task: "T042: Implement user login"
  tags: "be,api,auth"
  → Load fastapi agentsrules + tech-stack
```

### Rule 2: Architecture Patterns
```yaml
trigger:
  condition: "task involves design decision"
  OR: "user asks about patterns"
  OR: "new component being created"

action:
  load: "reference/patterns.yaml"
  cache: "until decision made"

example:
  task: "T015: Design caching layer"
  → Load patterns.yaml:cachingStrategy
```

### Rule 3: Quality Gates
```yaml
trigger:
  condition: "executing test command"
  OR: "task.ac contains 'cov>' keyword"

action:
  load: "reference/delivery.yaml:qualityGates"
  cache: "until tests complete"

example:
  task: "T042-5: Auth tests"
  ac: "unit|integration|cov>90"
  → Load quality gates before running pytest
```

### Rule 4: Historical Data
```yaml
trigger:
  condition: "explicit user request"
  keywords: ["lessons", "history", "what did we learn"]

action:
  load: "reference/history.yaml"
  cache: "unload after response"

example:
  user: "What issues did we face last sprint?"
  → Load history.yaml:lessons
  → Respond
  → Unload immediately
```

## Incremental Loading

### Load Specific Fields Only
```python
# Bad: Load entire file
projectConfig = read("memory-bank/projectConfig.md")  # 2500 tokens

# Good: Load specific field
STACK_ID = read("memory-bank/core/project.yaml:STACK_ID")  # 50 tokens
identity = read("memory-bank/core/project.yaml:projectName,domain")  # 100 tokens
```

### Array Slicing
```python
# Bad: Load all backlog tasks
backlog = read("work/backlog.yaml:backlog")  # All tasks, 3000 tokens

# Good: Load next 3 tasks only
backlog = read("work/backlog.yaml:backlog[0:3]")  # 300 tokens
```

### Conditional Field Loading
```yaml
# Load config with conditional fields
if task.type == "backend":
  load: "reference/tech-stack.yaml:frameworkModules,dataLayer"
elif task.type == "frontend":
  load: "reference/tech-stack.yaml:frameworkModules"  # Skip dataLayer
elif task.type == "docs":
  skip: "reference/tech-stack.yaml"  # Don't load at all
```

## Cache Management

### Hot Data (Always in Memory)
```yaml
- core/project.yaml
- core/active.yaml
- context-strategy.yaml

ttl: "session"
eviction: "never"
```

### Warm Data (Session Cache)
```yaml
- work/backlog.yaml
- work/sprint-metrics.yaml

ttl: "1 hour"
eviction: "after task completion"
```

### Cold Data (No Cache)
```yaml
- reference/tech-stack.yaml
- reference/patterns.yaml
- reference/delivery.yaml
- reference/history.yaml

ttl: "immediate"
eviction: "after use"
```

## Token Savings Calculation

### Traditional Full Load
```
projectPrompt: 500
projectConfig: 2500
taskBoard: 1200
deliverables: 1000
progress: 800
activeContext: 700
techContext: 3000
systemPatterns: 2500
automation: 1500
agentsrules: 3000
AGENTS.md: 5000
Stack files: 4000
-------------------------
TOTAL: 25,700 tokens
```

### Lazy Load (Typical Task)
```
Phase 1 (bootstrap): 3000
Phase 2 (task select): 1500
Phase 3 (implementation): 4000
-------------------------
TOTAL: 8,500 tokens
SAVINGS: 17,200 tokens (67%)
```

### Lazy Load (Simple Task)
```
Phase 1 (bootstrap): 3000
Phase 2 (task select): 1500
(Skip Phase 3 - just docs update)
-------------------------
TOTAL: 4,500 tokens
SAVINGS: 21,200 tokens (82%)
```

## Implementation Example

```python
# Session start
load("core/context-strategy.yaml")  # 500 tokens
load("core/project.yaml")  # 1000 tokens
load("core/active.yaml")  # 800 tokens
load("token-monitoring.md")  # 700 tokens
# Bootstrap complete: 3000 tokens

# User: "Start next task"
load("work/backlog.yaml:backlog[0]")  # 150 tokens (first task only)
task = parse_task("T042")
# Task selection complete: 150 tokens

# Agent: Analyze task
if "be" in task.tags or "api" in task.tags:
    # Coding task detected
    load(f"agents-stack/{STACK_ID}/agentsrules")  # 2000 tokens
    load("reference/tech-stack.yaml:frameworkModules,testingStack")  # 1500 tokens
    # Implementation context loaded: 3500 tokens

# Agent: Implement task
# ... coding work ...

# Agent: Run tests
if task.ac contains "cov>":
    load("reference/delivery.yaml:qualityGates.tests")  # 500 tokens
    run_tests()
    unload("reference/delivery.yaml")
    # Tests complete, unloaded

# Agent: Complete task
unload("reference/tech-stack.yaml")
unload("agents-stack/{STACK_ID}/agentsrules")
update_delta("work/backlog.yaml", move_task(T042, "done"))
# Task complete, cold data unloaded

# Total session: 3000 + 150 + 3500 + 500 = 7150 tokens
# vs Traditional: 25,700 tokens
# Savings: 18,550 tokens (72%)
```

## Best Practices

1. **Always start minimal**: Load only core/ at bootstrap
2. **Trigger-based loading**: Use task tags and keywords to decide what to load
3. **Unload aggressively**: Remove cold data immediately after use
4. **Cache hot data**: Keep core/ and work/ in session memory
5. **Field-level access**: Load specific YAML fields, not entire files
6. **Array slicing**: Load next 3-5 items, not full arrays
7. **Conditional branches**: Different task types = different context needs
8. **Monitor savings**: Log token usage with/without lazy loading

## Monitoring

Track lazy loading effectiveness:
```yaml
lazyLoadingMetrics:
  sessionsWithLazyLoad: 45
  avgTokensPerSession: 8200
  avgTokensSaved: 17500
  savingsPercentage: 68
  cachehitRate: 0.85
  unloadEvents: 120
```

Log in `progress.tokenUsage`:
```yaml
- ts: "2025-10-30T10:15:00Z"
  op: "lazy load: Phase 3 (stack context)"
  est: 4000
  act: 3800
  trigger: "task T042 tags: be,api"
  unloadedAt: "2025-10-30T10:45:00Z"
```
