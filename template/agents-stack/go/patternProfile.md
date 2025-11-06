---
architectureStyle: "Clean Architecture"
layering: "handler → service → repository → domain"
errorStrategy: "explicit with wrapped errors"
testingApproach: "table-driven, parallel execution"
observability: "OpenTelemetry + structured logging"
---

# Pattern Profile — Go

## Architecture Pattern: Clean Architecture

```
┌─────────────────────────────────────┐
│          HTTP Handler Layer         │  ← Handles requests/responses
│  (Routing, validation, serialization)│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Service Layer               │  ← Business logic
│  (Use cases, orchestration)         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Repository Layer             │  ← Data access
│  (SQL queries, caching)             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Domain Layer               │  ← Business entities
│  (Structs, validation)              │
└─────────────────────────────────────┘
```

## Dependency Injection Pattern

**Interface-Based DI:**

```go
// Define interfaces in consumer packages
package service

type UserRepository interface {
    FindByID(ctx context.Context, id int) (*User, error)
    Create(ctx context.Context, user *User) error
}

type UserService struct {
    repo UserRepository  // Depends on interface
}

// Implementation in repository package
package repository

type PostgresUserRepository struct {
    db *sql.DB
}

func (r *PostgresUserRepository) FindByID(ctx context.Context, id int) (*User, error) {
    // implementation
}
```

## Error Handling Pattern

**Explicit Error Propagation:**

```go
// Wrap errors with context
func (s *UserService) GetUser(ctx context.Context, id int) (*User, error) {
    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, ErrUserNotFound
        }
        return nil, fmt.Errorf("service: failed to get user %d: %w", id, err)
    }
    return user, nil
}

// HTTP handler translates errors to status codes
func (h *UserHandler) GetUser(w http.ResponseWriter, r *http.Request) {
    user, err := h.service.GetUser(r.Context(), id)
    if err != nil {
        if errors.Is(err, ErrUserNotFound) {
            http.Error(w, "User not found", http.StatusNotFound)
            return
        }
        http.Error(w, "Internal error", http.StatusInternalServerError)
        return
    }
    json.NewEncoder(w).Encode(user)
}
```

## Testing Patterns

**1. Table-Driven Tests:**

```go
func TestValidateEmail(t *testing.T) {
    tests := []struct {
        name    string
        email   string
        wantErr bool
    }{
        {"valid", "user@example.com", false},
        {"empty", "", true},
        {"no @", "userexample.com", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            err := ValidateEmail(tt.email)
            if (err != nil) != tt.wantErr {
                t.Errorf("got error = %v, wantErr = %v", err, tt.wantErr)
            }
        })
    }
}
```

**2. Mock Interfaces:**

```go
// Mock repository for testing
type MockUserRepository struct {
    FindByIDFunc func(ctx context.Context, id int) (*User, error)
}

func (m *MockUserRepository) FindByID(ctx context.Context, id int) (*User, error) {
    return m.FindByIDFunc(ctx, id)
}

// Use in tests
func TestUserService_GetUser(t *testing.T) {
    mockRepo := &MockUserRepository{
        FindByIDFunc: func(ctx context.Context, id int) (*User, error) {
            return &User{ID: id, Email: "test@example.com"}, nil
        },
    }

    service := NewUserService(mockRepo)
    user, err := service.GetUser(context.Background(), 1)
    // assertions
}
```

## Middleware Pattern

**Chain Middleware Functions:**

```go
type Middleware func(http.Handler) http.Handler

// Logging middleware
func LoggingMiddleware(logger *slog.Logger) Middleware {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            next.ServeHTTP(w, r)
            logger.Info("request",
                "method", r.Method,
                "path", r.URL.Path,
                "duration", time.Since(start),
            )
        })
    }
}

// Chain middlewares
func Chain(h http.Handler, middlewares ...Middleware) http.Handler {
    for i := len(middlewares) - 1; i >= 0; i-- {
        h = middlewares[i](h)
    }
    return h
}

// Usage
mux := http.NewServeMux()
handler := Chain(mux, LoggingMiddleware(logger), AuthMiddleware())
```

## Observability Pattern

**OpenTelemetry Integration:**

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/trace"
)

func (s *UserService) GetUser(ctx context.Context, id int) (*User, error) {
    tracer := otel.Tracer("user-service")
    ctx, span := tracer.Start(ctx, "GetUser")
    defer span.End()

    span.SetAttributes(attribute.Int("user.id", id))

    user, err := s.repo.FindByID(ctx, id)
    if err != nil {
        span.RecordError(err)
        return nil, err
    }

    return user, nil
}
```

## Configuration Pattern

**Environment-Based Config:**

```go
type Config struct {
    Port         string
    DatabaseURL  string
    LogLevel     string
    Environment  string
}

func LoadConfig() (*Config, error) {
    return &Config{
        Port:        getEnv("PORT", "8080"),
        DatabaseURL: getEnv("DATABASE_URL", ""),
        LogLevel:    getEnv("LOG_LEVEL", "info"),
        Environment: getEnv("ENVIRONMENT", "development"),
    }, nil
}

func getEnv(key, defaultValue string) string {
    if value := os.Getenv(key); value != "" {
        return value
    }
    return defaultValue
}
```

## Anti-Patterns to Avoid

❌ **Global Variables**: Use DI instead
❌ **Panic in Libraries**: Return errors instead
❌ **Ignoring Errors**: Always check `err != nil`
❌ **Naked Returns**: Explicit returns preferred
❌ **Interface{} Abuse**: Use generics or concrete types
❌ **Context.Value Overuse**: Use for request-scoped data only
