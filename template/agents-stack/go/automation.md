---
init:
  commands:
    - "go mod init <module-name>"
    - "go mod tidy"
  description: "Initialize Go module and install dependencies"

dev:
  commands:
    - "go run cmd/api/main.go"
  description: "Start development server"
  notes: "Use air or reflex for hot reload in development"

test:
  commands:
    - "go test ./... -v -race -cover"
  description: "Run all tests with race detector and coverage"
  coverage: "go test ./... -coverprofile=coverage.out && go tool cover -html=coverage.out"

build:
  commands:
    - "go build -o bin/api cmd/api/main.go"
  description: "Build production binary"
  optimized: "CGO_ENABLED=0 go build -ldflags='-s -w' -o bin/api cmd/api/main.go"

lint:
  commands:
    - "golangci-lint run ./..."
  description: "Run linter checks"
  install: "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"

format:
  commands:
    - "go fmt ./..."
    - "goimports -w ."
  description: "Format code with go fmt and goimports"

migrate:
  up: "migrate -path ./migrations -database $DATABASE_URL up"
  down: "migrate -path ./migrations -database $DATABASE_URL down"
  create: "migrate create -ext sql -dir ./migrations -seq <migration_name>"

docker:
  build: "docker build -t api:latest ."
  run: "docker run -p 8080:8080 --env-file .env api:latest"

deploy:
  commands:
    - "# Build and deploy to production"
  description: "Deployment steps (customize based on platform)"

monitoring:
  metrics: "http://localhost:8080/metrics"
  health: "http://localhost:8080/health"
  ready: "http://localhost:8080/ready"
---

# Automation Profile — Go

## Development Workflow

### 1. Initial Setup

```bash
# Create new project
go mod init github.com/username/project

# Install dependencies
go mod tidy

# Install development tools
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install github.com/golang-migrate/migrate/v4/cmd/migrate@latest
```

### 2. Development Server

```bash
# Run directly
go run cmd/api/main.go

# With hot reload (install air first: go install github.com/cosmtrek/air@latest)
air

# With environment variables
PORT=8080 DATABASE_URL=postgres://... go run cmd/api/main.go
```

### 3. Testing

```bash
# Run all tests
go test ./...

# With verbose output
go test ./... -v

# With race detector
go test ./... -race

# With coverage
go test ./... -cover

# Generate coverage report
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out

# Run specific package tests
go test ./internal/service/...

# Run specific test
go test ./internal/service -run TestUserService_Create
```

### 4. Linting & Formatting

```bash
# Format code
go fmt ./...

# Run linter
golangci-lint run ./...

# Auto-fix issues
golangci-lint run --fix ./...

# Organize imports (install: go install golang.org/x/tools/cmd/goimports@latest)
goimports -w .
```

### 5. Building

```bash
# Development build
go build -o bin/api cmd/api/main.go

# Production build (smaller binary, no debug info)
CGO_ENABLED=0 go build -ldflags='-s -w' -o bin/api cmd/api/main.go

# Cross-compile for Linux (from macOS/Windows)
GOOS=linux GOARCH=amd64 go build -o bin/api-linux cmd/api/main.go

# Run built binary
./bin/api
```

### 6. Database Migrations

```bash
# Install migrate tool
go install github.com/golang-migrate/migrate/v4/cmd/migrate@latest

# Create new migration
migrate create -ext sql -dir ./migrations -seq create_users_table

# Run migrations
migrate -path ./migrations -database "postgres://user:pass@localhost:5432/dbname?sslmode=disable" up

# Rollback last migration
migrate -path ./migrations -database $DATABASE_URL down 1

# Check migration status
migrate -path ./migrations -database $DATABASE_URL version
```

### 7. Docker

```dockerfile
# Example Dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags='-s -w' -o /api cmd/api/main.go

FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=builder /api /api
EXPOSE 8080
CMD ["/api"]
```

```bash
# Build image
docker build -t api:latest .

# Run container
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e DATABASE_URL=postgres://... \
  api:latest

# Docker Compose
docker-compose up --build
```

### 8. Monitoring & Debugging

```bash
# Check health
curl http://localhost:8080/health

# Check readiness
curl http://localhost:8080/ready

# View metrics (Prometheus format)
curl http://localhost:8080/metrics

# Profile CPU
go test -cpuprofile=cpu.prof ./...
go tool pprof cpu.prof

# Profile memory
go test -memprofile=mem.prof ./...
go tool pprof mem.prof

# Race condition detection
go test -race ./...
```

## CI/CD Pipeline Example

```yaml
# .github/workflows/go.yml
name: Go CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.22'

      - name: Install dependencies
        run: go mod download

      - name: Run tests
        run: go test -v -race -coverprofile=coverage.out ./...

      - name: Run linter
        uses: golangci/golangci-lint-action@v3

      - name: Build
        run: go build -v ./...
```

## Quality Gates

- ✅ All tests pass (`go test ./...`)
- ✅ No race conditions (`go test -race ./...`)
- ✅ Code coverage ≥ 80% (`go test -cover ./...`)
- ✅ Linter passes (`golangci-lint run`)
- ✅ Code formatted (`go fmt ./...`)
- ✅ No security vulnerabilities (`govulncheck ./...`)

## Environment Variables

```bash
# .env.example
PORT=8080
DATABASE_URL=postgres://user:pass@localhost:5432/dbname?sslmode=disable
LOG_LEVEL=info
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
API_TIMEOUT=30s
```

## Useful Commands

```bash
# Download dependencies
go mod download

# Update dependencies
go get -u ./...
go mod tidy

# List dependencies
go list -m all

# Check for vulnerabilities
go install golang.org/x/vuln/cmd/govulncheck@latest
govulncheck ./...

# Generate code (if using //go:generate)
go generate ./...

# View dependency graph
go mod graph

# Clean build cache
go clean -cache
```
