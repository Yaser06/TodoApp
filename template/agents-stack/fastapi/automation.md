---
setup:
  - name: "Install dependencies"
    command: ["poetry", "install"]
  - name: "Start services"
    command: ["docker-compose", "up", "-d", "db", "redis"]
dev:
  - name: "Run app (reload)"
    command: ["poetry", "run", "uvicorn", "app.main:app", "--reload"]
  - name: "Run background worker"
    command: ["poetry", "run", "celery", "-A", "app.worker", "worker", "--loglevel=info"]
test:
  - name: "Unit tests"
    command: ["poetry", "run", "pytest", "tests/unit"]
  - name: "Integration tests"
    command: ["poetry", "run", "pytest", "tests/integration"]
  - name: "Static analysis"
    command: ["poetry", "run", "ruff", "check", "."]
build:
  - name: "Build docker image"
    command: ["docker", "build", "-t", "fastapi-app:latest", "."]
deploy:
  - name: "Deploy to staging"
    command: ["bash", "-lc", "helm upgrade --install api charts/api -f charts/api/values-staging.yaml"]
  - name: "Deploy to production"
    command: ["bash", "-lc", "helm upgrade --install api charts/api -f charts/api/values-prod.yaml"]
qualityGates:
  testCoverageTarget: 85
  lintRequired: true
  securityScan: true
  additionalChecks:
    - "poetry run mypy app"
    - "poetry run bandit -r app"
monitoring:
  - metric: "latency_p95"
    target: "< 150ms"
  - metric: "error_rate"
    target: "< 0.3%"
autoTasks:
  - trigger: "pre-merge"
    actions:
      - "poetry run pytest"
      - "poetry run ruff check ."
updatedAt: ""
updatedBy: ""
---

# Automation Profile — FastAPI

Front matter FastAPI projeleri için varsayılan otomasyon komutlarını sağlar. Global runbook ile birleşerek ajanın tam uçtan uca akışlar çalıştırmasına yardımcı olur.
