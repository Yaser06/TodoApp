---
init:
  commands: []
  description: "Project initialization (language-specific)"

dev:
  commands: []
  description: "Start development server (language-specific)"

test:
  commands: []
  description: "Run tests (language-specific)"

build:
  commands: []
  description: "Build for production (language-specific)"

lint:
  commands: []
  description: "Run linter (language-specific)"

format:
  commands: []
  description: "Format code (language-specific)"

deploy:
  commands: []
  description: "Deploy to production (platform-specific)"
---

# Automation Profile — Generic (Fallback)

**⚠️ This profile provides generic automation guidance. Adapt to your specific stack.**

## Generic Development Workflow

### 1. Project Initialization

```bash
# Language-specific examples:

# Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js
npm install
# or
pnpm install

# Go
go mod init project-name
go mod tidy

# Java
mvn clean install
# or
gradle build

# Rust
cargo new project-name
cargo build
```

### 2. Development Server

```bash
# Run development environment

# Python
python main.py
# or
uvicorn main:app --reload

# Node.js
npm run dev
# or
node --watch server.js

# Go
go run main.go
# or
air  # with hot reload

# Java
mvn spring-boot:run
# or
gradle bootRun
```

### 3. Testing

```bash
# Run tests

# Python
pytest
pytest --cov=src

# Node.js
npm test
npm run test:coverage

# Go
go test ./...
go test -cover ./...

# Java
mvn test
gradle test

# Rust
cargo test
```

### 4. Linting & Formatting

```bash
# Code quality

# Python
ruff check .
black .
mypy src/

# Node.js
eslint .
prettier --write .

# Go
golangci-lint run
go fmt ./...

# Java
mvn checkstyle:check
gradle check

# Rust
cargo clippy
cargo fmt
```

### 5. Building

```bash
# Production build

# Python
pip install --no-dev
python -m compileall src/

# Node.js
npm run build

# Go
go build -o bin/app cmd/main.go

# Java
mvn package
gradle bootJar

# Rust
cargo build --release
```

### 6. Running Production

```bash
# Start production server

# Python
gunicorn app:app --workers 4

# Node.js
NODE_ENV=production node dist/server.js

# Go
./bin/app

# Java
java -jar target/app.jar

# Rust
./target/release/app
```

## Docker Generic Pattern

```dockerfile
# Multi-stage build example
FROM <base-image> AS builder

WORKDIR /app

# Copy dependency files
COPY <dependency-files> .

# Install dependencies
RUN <install-command>

# Copy source code
COPY . .

# Build
RUN <build-command>

# Production image
FROM <runtime-image>

WORKDIR /app

# Copy built artifacts
COPY --from=builder /app/<artifacts> .

# Expose port
EXPOSE <port>

# Run
CMD ["<run-command>"]
```

## Environment Variables Pattern

```bash
# .env file structure
ENVIRONMENT=production
PORT=8080
DATABASE_URL=<connection-string>
API_KEY=<secret-key>
LOG_LEVEL=info
```

## CI/CD Generic Pipeline

```yaml
# Generic CI pipeline (adapt to GitHub Actions, GitLab CI, etc.)

stages:
  - lint
  - test
  - build
  - deploy

lint:
  script:
    - <lint-command>

test:
  script:
    - <test-command>
  coverage: <coverage-report>

build:
  script:
    - <build-command>
  artifacts:
    - <build-output>

deploy:
  script:
    - <deploy-command>
  only:
    - main
```

## Quality Gates

- ✅ All tests pass
- ✅ Code coverage ≥ 80%
- ✅ Linter passes with no errors
- ✅ Security scan (no critical vulnerabilities)
- ✅ Build succeeds
- ✅ Documentation updated

## Monitoring & Observability

```bash
# Health checks
curl http://localhost:PORT/health

# Metrics (if available)
curl http://localhost:PORT/metrics

# Logs
tail -f logs/application.log

# Performance profiling (language-specific)
# Python: py-spy, cProfile
# Node.js: clinic, 0x
# Go: pprof
# Java: VisualVM, JProfiler
```

## Common Commands Reference

### Package Management
```bash
# Install dependencies
<package-manager> install

# Add new package
<package-manager> add <package-name>

# Remove package
<package-manager> remove <package-name>

# Update dependencies
<package-manager> update
```

### Database Migrations
```bash
# Create migration
<migration-tool> create <migration-name>

# Run migrations
<migration-tool> migrate

# Rollback
<migration-tool> rollback
```

### Process Management
```bash
# Production process managers:
# - PM2 (Node.js)
# - Supervisor (Python)
# - systemd (Linux)

# Example: PM2
pm2 start app.js
pm2 list
pm2 logs
pm2 restart app
```

## Recommendation

This generic automation profile provides basic guidance. For optimal developer experience, create a dedicated stack profile with:

1. Exact commands for your stack
2. Tool versions and configuration
3. Development scripts
4. Deployment instructions
5. Troubleshooting guide

Refer to `agents-stack/fastapi/automation.md` or similar for examples.
