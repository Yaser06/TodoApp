---
stackDefaults:
  language: "Python 3.11+ (async-first)"
  framework: "FastAPI + Starlette, Pydantic v2 modeller ve Settings"
  asgiServer: "Uvicorn (uvloop+httptools) veya Hypercorn — prod için worker/loop değerleri belirlenmeli"
  database: "PostgreSQL 14+ + SQLModel/SQLAlchemy 2.x (async), migrations Alembic"
  backgroundProcessing: "Celery (Redis/RabbitMQ) veya Dramatiq; queue ve retry politikaları belgelenmeli"
  caching: "Redis (async client) + key namespace stratejisi"
  infrastructure: "Docker compose (local), Kubernetes (prod) + readiness/liveness probe'ları"
  security: "OAuth2/JWT, passlib hashing, secrets manager (AWS SSM/Vault); CORS ayarları sıkı"
  observability: "Structlog/Loguru JSON logging, Prometheus FastAPI Instrumentator, OpenTelemetry traces"
toolingWorkflow:
  dependencyManagement: "Poetry veya PDM (lock dosyası commit edilmeli)"
  formattingLinting:
    - "Ruff (lint + format)"
    - "Black (opsiyonel)"
    - "isort"
    - "MyPy (strict optional)"
  testingStack:
    - "Pytest"
    - "pytest-asyncio"
    - "HTTPX AsyncClient"
    - "Testcontainers (DB/message broker)"
  securityScans:
    - "Bandit"
    - "safety veya pip-audit"
  cicd: "Lint → Type-check → Unit/Integration Tests → Security Scan → Deploy"
  localDev: "`make`/`taskipy` komutları, .env.example, docker-compose ile destek servisleri"
updatedAt: ""
updatedBy: ""
---

# Tech Profile — Python FastAPI

Front matter, FastAPI stack’i için varsayılan teknik tercihleri tutar. `techContext.md` bu değerlerden yararlanır.

## Notlar
- Dependency yönetiminde lock dosyasının commit edilmesi kritik.
- Async zincirde blocking I/O tespit edildiğinde ilgili servis refactor edilmelidir.
