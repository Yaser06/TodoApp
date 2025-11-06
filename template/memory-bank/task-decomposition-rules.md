---
version: "1.0"
enabled: true
triggers:
  tokenCritical: true
  estimateThreshold: "30min"
  complexityHigh: true
autoDecompose: true
targetSubtasks: 5
maxDepth: 2
preserveAcceptanceCriteria: true
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Task Decomposition Rules — Auto-Splitting

> **AI instruction**: When token usage > critical AND task estimate > 30min, automatically decompose task into subtasks. This prevents token exhaustion mid-implementation.

## Decomposition Triggers

### Primary Trigger
```yaml
condition: |
  tokenUsage > criticalThreshold (90%)
  AND currentTask.estimate > "30min"
  AND currentTask.status == "inProgress"
action: "auto-decompose"
```

### Secondary Triggers
```yaml
- condition: "Task has > 5 acceptance criteria"
  action: "suggest decomposition"

- condition: "Task involves multiple stack layers (FE + BE + DB)"
  action: "decompose by layer"

- condition: "Estimate > 8h"
  action: "mandatory decomposition"
```

## Decomposition Algorithm

### Step 1: Analyze Task
```python
# Identify decomposable dimensions:
dimensions = {
  "by_layer": ["backend", "frontend", "database", "tests"],
  "by_feature": ["create", "read", "update", "delete"],
  "by_component": ["model", "service", "controller", "view"],
  "by_phase": ["scaffold", "implement", "test", "document"]
}
```

### Step 2: Generate Subtasks
```yaml
# Original task
- id: "T042"
  title: "Implement user authentication"
  ac: "signup|login|logout|jwt|refresh|validation|tests"
  est: "8h"
  status: "inProgress"

# Decomposed (by feature + layer)
- id: "T042"
  title: "Implement user authentication"
  status: "decomposed"
  subtasks: ["T042-1", "T042-2", "T042-3", "T042-4", "T042-5"]

- id: "T042-1"
  title: "Auth models and DB schema"
  parent: "T042"
  ac: "User model|password hashing|migration"
  est: "1.5h"
  pri: "H"
  tags: "be,db"
  deps: []

- id: "T042-2"
  title: "Signup endpoint"
  parent: "T042"
  ac: "POST /signup|validation|201 response"
  est: "1.5h"
  pri: "H"
  tags: "be,api"
  deps: ["T042-1"]

- id: "T042-3"
  title: "Login & JWT generation"
  parent: "T042"
  ac: "POST /login|JWT token|refresh token"
  est: "2h"
  pri: "H"
  tags: "be,api,sec"
  deps: ["T042-1"]

- id: "T042-4"
  title: "JWT middleware"
  parent: "T042"
  ac: "validate token|protect routes|401 handling"
  est: "1.5h"
  pri: "H"
  tags: "be,sec"
  deps: ["T042-3"]

- id: "T042-5"
  title: "Auth tests"
  parent: "T042"
  ac: "unit tests|integration tests|coverage>90"
  est: "1.5h"
  pri: "H"
  tags: "be,test"
  deps: ["T042-2", "T042-3", "T042-4"]
```

### Step 3: Update Task Board
```json
// Append to progress-delta.json
{
  "timestamp": "2025-10-30T16:00:00Z",
  "file": "taskBoard",
  "operation": "decompose",
  "taskId": "T042",
  "subtasks": ["T042-1", "T042-2", "T042-3", "T042-4", "T042-5"],
  "reason": "token_critical + estimate_high"
}
```

### Step 4: Resume with First Subtask
```
1. Mark parent T042 as "decomposed"
2. Add subtasks to backlog (priority order)
3. Move T042-1 to inProgress
4. Create checkpoint
5. Continue in recovery mode
```

## Decomposition Strategies

### By Stack Layer
```
Full-stack task → Backend + Frontend + DB + Tests
Example: "User profile page"
→ T###-1: Backend API
→ T###-2: Frontend UI
→ T###-3: Database schema
→ T###-4: Integration tests
```

### By Feature Scope
```
Large feature → Individual CRUD operations
Example: "Product management"
→ T###-1: Create product
→ T###-2: List products
→ T###-3: Update product
→ T###-4: Delete product
```

### By Implementation Phase
```
Complex task → Sequential phases
Example: "Search functionality"
→ T###-1: Basic search (exact match)
→ T###-2: Fuzzy search
→ T###-3: Filters and sorting
→ T###-4: Pagination
→ T###-5: Search analytics
```

### By Component
```
Architectural task → Modular components
Example: "Payment integration"
→ T###-1: Payment models
→ T###-2: Stripe client wrapper
→ T###-3: Webhook handler
→ T###-4: Payment service
→ T###-5: API endpoints
```

## Acceptance Criteria Distribution

Distribute parent AC across subtasks:
```yaml
parent_ac: "signup|login|logout|jwt|refresh|password-reset|validation|tests|docs"

subtasks:
  - id: "T042-1"
    ac: "signup|validation"
  - id: "T042-2"
    ac: "login|jwt"
  - id: "T042-3"
    ac: "logout|refresh"
  - id: "T042-4"
    ac: "password-reset"
  - id: "T042-5"
    ac: "tests>90|docs"
```

## Dependency Management

Establish subtask dependencies:
```yaml
# Sequential dependencies
T042-1 (models) → T042-2 (endpoints) → T042-3 (tests)

# Parallel branches
T042-1 (models) → [T042-2 (signup), T042-3 (login)] → T042-4 (tests)

# Complex graph
T042-1 (models)
  → T042-2 (service layer)
    → [T042-3 (API), T042-4 (CLI)]
      → T042-5 (tests)
```

## Estimate Distribution

Target: Subtasks ≤ 2h each
```
Parent: 8h → 5 subtasks × 1.5-2h
Parent: 4h → 3 subtasks × 1-1.5h
Parent: 2h → No decomposition
```

## Priority Inheritance
```yaml
# Parent priority → All subtasks
parent_pri: "H"
subtasks_pri: "H" (inherit)

# Adjust based on dependencies
first_subtasks: "H"
dependent_subtasks: "H" (maintain)
test_subtasks: "M" (can be lower)
```

## Tags Composition
```yaml
# Parent tags + specific tags
parent_tags: "be,auth"

subtasks:
  - id: "T042-1"
    tags: "be,auth,db"  # + db
  - id: "T042-2"
    tags: "be,auth,api"  # + api
  - id: "T042-3"
    tags: "be,auth,sec"  # + sec
```

## Decomposition Limits

### Max Depth
```
- Depth 1: T042 → T042-1, T042-2, ...
- Depth 2: T042-1 → T042-1-A, T042-1-B, ... (if needed)
- Depth 3+: Not allowed (indicates task too complex)
```

### Max Subtasks
```
- Optimal: 3-5 subtasks
- Maximum: 8 subtasks
- If > 8: Consider deeper hierarchy or task is too large
```

## Special Cases

### Already Partially Complete
```yaml
# Parent T042 has some work done
- id: "T042"
  status: "decomposed"
  progress: "50%"
  notes: "Models and signup done, login pending"

# Only decompose remaining work
subtasks:
  - id: "T042-3"  # Skip T042-1, T042-2
    title: "Login endpoint"
  - id: "T042-4"
    title: "JWT middleware"
  - id: "T042-5"
    title: "Tests"
```

### Blocked Dependencies
```yaml
# Parent blocked on external dependency
- id: "T042"
  status: "blocked"
  blocker: "Waiting for API keys"

# Don't decompose, mark subtasks as blocked too
action: "skip decomposition, wait for unblock"
```

### Low Token Budget
```yaml
# Token > 95%, can't afford decomposition analysis
- condition: "tokenUsage > 95%"
  action: "emergency checkpoint, defer decomposition to resume"
```

## Decomposition Prompt Template

When auto-decomposing, agent uses:
```
Task T### estimate indicates >30min work and token usage is at 92%.
Decomposing into subtasks to prevent token exhaustion.

Analyzing task: "{title}"
Acceptance criteria: {ac}
Estimate: {est}

Decomposition strategy: {strategy} (by_layer | by_feature | by_phase)
Target: {count} subtasks of ~{target_est} each

Generated subtasks:
- T###-1: {title} [est: {est}, deps: {deps}]
- T###-2: {title} [est: {est}, deps: {deps}]
...

Adding to backlog, starting with T###-1.
Creating checkpoint before proceeding.
```

## Success Metrics

Track decomposition effectiveness:
```yaml
metrics:
  decompositionsTriggered: 0
  avgSubtasks: 4.2
  avgSubtaskEstimate: "1.5h"
  completionRate: 0.95
  tokenSavings: "45000 tokens avg"
```

Log in `progress.md:lessons`:
```yaml
lessons:
  - insight: "Auto-decomposition at 90% token prevented 3 session restarts"
    action: "Keep trigger at 90%, works well"
```
