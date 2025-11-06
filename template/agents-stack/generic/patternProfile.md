---
architectureStyle: "Layered Architecture"
layering: "Presentation → Business → Data Access → Data"
errorStrategy: "exceptions with structured error responses"
testingApproach: "unit + integration tests"
observability: "structured logging"
---

# Pattern Profile — Generic (Fallback)

## Architectural Patterns

### Layered Architecture

**Presentation Layer**
- Handles HTTP requests/responses
- Input validation
- Format conversion (JSON, XML, etc.)
- No business logic

**Business Logic Layer**
- Core application logic
- Business rules enforcement
- Orchestrates data access
- Independent of presentation

**Data Access Layer**
- Database queries
- External API calls
- Caching logic
- Returns domain objects

**Data Layer**
- Database
- File storage
- External services

### Dependency Flow

```
Presentation → Business → Data Access → Data
     ↑            ↑            ↑
     └────────────┴────────────┘
     Dependencies point inward
```

## Design Patterns

### Repository Pattern

```
// Interface
interface UserRepository:
    function find_by_id(id): User
    function save(user): void
    function delete(id): void

// Implementation
class DatabaseUserRepository implements UserRepository:
    constructor(database):
        this.db = database

    function find_by_id(id):
        return this.db.query("SELECT * FROM users WHERE id = ?", id)
```

### Service Pattern

```
class UserService:
    constructor(user_repository, email_service):
        this.users = user_repository
        this.email = email_service

    function register(email, password):
        # Validate
        if not valid_email(email):
            throw ValidationError()

        # Business logic
        user = User(email, hash(password))
        this.users.save(user)

        # Side effects
        this.email.send_welcome(email)

        return user
```

### Factory Pattern

```
class ServiceFactory:
    function create_user_service():
        db = DatabaseConnection()
        repo = UserRepository(db)
        email = EmailService()
        return UserService(repo, email)

# Usage
factory = ServiceFactory()
service = factory.create_user_service()
```

### Strategy Pattern

```
// Different implementations of same interface
interface AuthenticationStrategy:
    function authenticate(credentials): User

class JWTAuthentication implements AuthenticationStrategy:
    function authenticate(token):
        # JWT logic
        pass

class BasicAuthentication implements AuthenticationStrategy:
    function authenticate(credentials):
        # Basic auth logic
        pass

# Usage
auth = select_strategy(config.auth_type)
user = auth.authenticate(request.credentials)
```

## Error Handling Patterns

### Try-Catch Hierarchy

```
try:
    result = business_operation()
    return success_response(result)
catch ValidationError as e:
    # 400 Bad Request
    return client_error_response(e)
catch NotFoundError as e:
    # 404 Not Found
    return not_found_response(e)
catch AuthorizationError as e:
    # 403 Forbidden
    return forbidden_response(e)
catch Exception as e:
    # 500 Internal Server Error
    log_error(e)
    return server_error_response()
```

### Early Returns (Guard Clauses)

```
// ✅ Good: Early returns
function process_payment(user, amount):
    if not user.is_active:
        throw InactiveUserError()

    if amount <= 0:
        throw InvalidAmountError()

    if user.balance < amount:
        throw InsufficientFundsError()

    # Happy path
    user.balance -= amount
    save(user)

// ❌ Bad: Nested conditions
function process_payment(user, amount):
    if user.is_active:
        if amount > 0:
            if user.balance >= amount:
                user.balance -= amount
                save(user)
            else:
                throw InsufficientFundsError()
        else:
            throw InvalidAmountError()
    else:
        throw InactiveUserError()
```

## Testing Patterns

### Arrange-Act-Assert (AAA)

```
function test_user_registration():
    # Arrange
    email = "test@example.com"
    password = "secure123"
    service = create_user_service()

    # Act
    user = service.register(email, password)

    # Assert
    assert user.email == email
    assert user.password != password  # Should be hashed
    assert user.is_active == false
```

### Mock Dependencies

```
function test_user_service_sends_email():
    # Arrange
    mock_email = MockEmailService()
    service = UserService(repo, mock_email)

    # Act
    service.register("test@example.com", "pass")

    # Assert
    assert mock_email.send_welcome.called == true
    assert mock_email.send_welcome.call_args[0] == "test@example.com"
```

## Logging Patterns

### Structured Logging

```
// ✅ Good: Structured
logger.info("User registered", {
    user_id: 123,
    email: "user@example.com",
    timestamp: now(),
    ip_address: request.ip
})

// ❌ Bad: Unstructured
logger.info("User user@example.com registered with id 123")
```

### Log Levels

```
logger.debug("Query executed", query=sql, duration=0.05)  # Development
logger.info("User logged in", user_id=123)                # Important events
logger.warning("Rate limit approaching", user_id=123)      # Potential issues
logger.error("Database timeout", error=e, query=sql)      # Errors
logger.critical("Service unavailable", service="payment") # Critical failures
```

## Anti-Patterns to Avoid

❌ **God Objects**: Classes that do everything
❌ **Global State**: Mutable global variables
❌ **Tight Coupling**: Classes depend on concrete implementations
❌ **Magic Numbers**: Hardcoded values without context
❌ **Premature Optimization**: Optimizing before measuring
❌ **Copy-Paste Programming**: Duplicated code blocks
❌ **Long Methods**: Functions > 50 lines
❌ **Deep Nesting**: More than 3 levels of indentation
❌ **Obscure Names**: Variables like `data`, `temp`, `x`
❌ **Missing Error Handling**: Assuming operations always succeed

## Best Practices

✅ **Single Responsibility**: One class, one purpose
✅ **Open/Closed**: Open for extension, closed for modification
✅ **Dependency Inversion**: Depend on abstractions, not concretions
✅ **Explicit Better Than Implicit**: Clear over clever
✅ **Fail Fast**: Validate early, error immediately
✅ **Composition Over Inheritance**: Prefer has-a over is-a
✅ **Immutability**: Prefer immutable data structures
✅ **Small Functions**: Functions do one thing well
