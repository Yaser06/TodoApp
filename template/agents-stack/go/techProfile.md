---
language: "Go"
version: "1.22+"
runtime: "Go runtime"
packageManager: "go modules"
keyLibraries:
  - "net/http (standard library)"
  - "database/sql + driver (pgx for PostgreSQL)"
  - "encoding/json (standard library)"
  - "github.com/google/uuid"
  - "github.com/golang-migrate/migrate (migrations)"
architecture: "Clean Architecture with DI"
testFramework: "testing (standard library) + testify/assert"
buildTool: "go build"
linting: "golangci-lint"
---

# Tech Profile — Go

## Core Stack

**Language**: Go 1.22+
**HTTP Server**: Standard library `net/http` with new ServeMux
**Database**: `database/sql` + driver (pgx, mysql, sqlite3)
**Validation**: Custom validators or `go-playground/validator`
**Serialization**: `encoding/json` (standard library)

## Project Structure

```
project/
├── cmd/
│   └── api/
│       └── main.go           # Application entry point
├── internal/
│   ├── domain/               # Business entities
│   ├── handler/              # HTTP handlers (controllers)
│   ├── service/              # Business logic
│   ├── repository/           # Data access
│   └── middleware/           # HTTP middleware
├── pkg/                      # Public libraries (if any)
├── migrations/               # Database migrations
├── go.mod
└── go.sum
```

## Dependency Injection

```go
// Constructor-based DI
type Server struct {
    userService UserService
    logger      Logger
}

func NewServer(userSvc UserService, log Logger) *Server {
    return &Server{
        userService: userSvc,
        logger:      log,
    }
}
```

## HTTP Patterns

```go
// Go 1.22+ ServeMux with method routing
mux := http.NewServeMux()
mux.HandleFunc("GET /api/v1/users/{id}", handler.GetUser)
mux.HandleFunc("POST /api/v1/users", handler.CreateUser)
mux.HandleFunc("DELETE /api/v1/users/{id}", handler.DeleteUser)
```

## Error Handling

```go
// Wrapped errors for traceability
if err != nil {
    return fmt.Errorf("failed to fetch user %d: %w", userID, err)
}

// Custom error types
type AppError struct {
    Code    string
    Message string
    Err     error
}
```

## Testing

```go
// Table-driven tests
func TestUserService_Create(t *testing.T) {
    tests := []struct {
        name    string
        input   CreateUserInput
        wantErr bool
    }{
        {"valid user", CreateUserInput{Email: "test@example.com"}, false},
        {"empty email", CreateUserInput{Email: ""}, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            // test logic
        })
    }
}
```

## Production Considerations

- **Graceful Shutdown**: Handle OS signals (SIGTERM, SIGINT)
- **Health Checks**: `/health` (liveness), `/ready` (readiness)
- **Metrics**: Prometheus `/metrics` endpoint
- **Tracing**: OpenTelemetry integration
- **Configuration**: Environment variables with defaults
