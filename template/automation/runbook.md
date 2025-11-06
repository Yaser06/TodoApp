---
executionPolicy:
  retryOnFailure: 3
  retryDelay: "5s"
  stopOnError: true
  captureOutput: true
  logFailures: "progress.md"
setup:
  - name: "Install dependencies"
    description: "Install project dependencies for the selected stack"
    command: ""
  - name: "Bootstrap environment"
    description: "Prepare environment variables, secrets, and tooling"
    command: ""
dev:
  - name: "Start full platform (single command)"
    command: "./tools/start_all.sh"
  - name: "Start development server"
    command: ""
  - name: "Run watcher tests"
    command: ""
test:
  - name: "Unit tests"
    command: ""
  - name: "Integration tests"
    command: ""
  - name: "Static analysis"
    command: ""
build:
  - name: "Build artifacts"
    command: ""
  - name: "Package application"
    command: ""
deploy:
  - name: "Deploy to staging"
    command: ""
  - name: "Deploy to production"
    command: ""
qualityGates:
  testCoverageTarget: 80
  lintRequired: true
  securityScan: true
  additionalChecks: []
monitoring:
  - metric: "uptime"
    target: "99.9%"
  - metric: "error_rate"
    target: "< 1%"
autoTasks:
  - trigger: "post-commit"
    actions:
      - "run tests"
      - "update progress log"
updatedAt: "2025-10-30"
updatedBy: "@agent"
---

# Automation Runbook — Command Execution

> **AI instruction**: Merge with stack automation. Empty commands auto-filled from stack profile. Execute sequentially: setup → dev → test → build → deploy.
