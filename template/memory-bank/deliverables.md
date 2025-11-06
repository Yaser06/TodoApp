---
deliverables:
  - id: ""
    name: ""
    type: ""
    owner: ""
    due: ""
    status: "planned"
    ac: ""
qualityGates:
  tests:
    - name: "Unit tests"
      cmd: "./mvnw test"
      thresh:
        cov: 85
        act: "block"
  lint:
    - name: "Checkstyle"
      cmd: "./mvnw checkstyle:check"
      thresh:
        viol: 0
        act: "block"
  security:
    - name: ""
      cmd: ""
releaseChecklist:
  - item: ""
    status: "pending"
    owner: ""
compactFormat: true
compressionRules:
  cmd: "command (abbreviated)"
  thresh: "threshold (abbreviated)"
  cov: "coverage"
  viol: "violations"
  act: "action"
  ac: "acceptanceCriteria (pipe-separated)"
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Deliverables & Quality Gates — Compact Format

> **AI instruction**: Load this file only during release preparation (cold data). Use abbreviated field names to reduce tokens.

## Compact Format
```yaml
deliverables:
  - id: "D001"
    name: "API Service"
    type: "service"
    owner: "@backend-team"
    due: "2025-11-15"
    status: "planned"
    ac: "deployed|tested|documented|monitored"
```

## Quality Gate Abbreviations
- `cmd`: command
- `thresh`: threshold
- `cov`: coverage
- `viol`: violations
- `act`: action (block/warn/ignore)

Load on demand when release tasks active.
