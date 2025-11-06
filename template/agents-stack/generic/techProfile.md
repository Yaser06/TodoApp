---
language: "Generic"
version: "N/A"
framework: "Generic"
packageManager: "N/A"
keyLibraries: []
architecture: "Layered Architecture"
testFramework: "Language-specific"
buildTool: "Language-specific"
linting: "Language-specific"
---

# Tech Profile — Generic (Fallback)

**⚠️ This profile provides generic guidance applicable to any stack.**

## Universal Architecture

```
┌─────────────────────────────────────┐
│       Presentation Layer            │  ← HTTP/UI handling
│   (Controllers, Routes, Views)      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Business Logic Layer         │  ← Core application logic
│   (Services, Use Cases)             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Data Access Layer           │  ← Database/API access
│   (Repositories, DAOs)              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│          Data Layer                 │  ← Database/Storage
└─────────────────────────────────────┘
```

## Generic Patterns

### Input Validation

```
// Pseudocode
function createUser(input):
    if not validate_email(input.email):
        throw ValidationError("Invalid email")

    if len(input.password) < 8:
        throw ValidationError("Password too short")

    # Proceed with creation
```

### Error Handling

```
// Pseudocode
try:
    result = perform_operation()
    return success_response(result)
catch ValidationError as e:
    return error_response(400, e.message)
catch DatabaseError as e:
    log_error(e)
    return error_response(500, "Internal error")
```

### Dependency Injection

```
// Pseudocode
class UserService:
    constructor(database, logger):
        this.database = database
        this.logger = logger

    function create_user(data):
        this.logger.info("Creating user")
        return this.database.save(data)

# Usage
database = DatabaseConnection()
logger = Logger()
service = UserService(database, logger)
```

### Separation of Concerns

```
// ✅ Good: Layered
Controller → Service → Repository

// ❌ Bad: Mixed concerns
Controller does everything (DB access, business logic, formatting)
```

## Configuration Management

```
# Environment variables
DATABASE_URL=postgres://...
API_KEY=secret_key_here
LOG_LEVEL=info
ENVIRONMENT=production

# Load in code
config = load_from_environment()
database = connect(config.DATABASE_URL)
```

## Testing Structure

```
tests/
├── unit/              # Fast, isolated tests
│   ├── services/
│   └── utils/
├── integration/       # Database/API tests
│   └── repositories/
└── e2e/              # Full application tests
```

## Security Checklist

- ✅ Input validation on all user inputs
- ✅ Parameterized queries (no SQL injection)
- ✅ Password hashing (never store plaintext)
- ✅ HTTPS in production
- ✅ Rate limiting on public endpoints
- ✅ Authentication on protected routes
- ✅ Authorization checks (user permissions)
- ✅ Error messages don't leak sensitive info
- ✅ Secrets in environment variables
- ✅ Dependency updates for security patches

## Code Quality Checklist

- ✅ Functions < 50 lines
- ✅ Descriptive names (no `data`, `temp`, `foo`)
- ✅ DRY: No code duplication
- ✅ Comments only for complex logic
- ✅ Consistent formatting
- ✅ Type hints/annotations
- ✅ Error handling for failure cases
- ✅ Unit tests for business logic

## Logging Best Practices

```
# Good logging
log.info("User created", user_id=123, email="user@example.com")
log.error("Database connection failed", error=str(e), retry_count=3)

# Bad logging
log.info("Something happened")
log.error("Error!")
```

## API Response Format

```json
// Success
{
  "success": true,
  "data": {
    "id": 123,
    "name": "John"
  }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "field": "email"
  }
}
```
