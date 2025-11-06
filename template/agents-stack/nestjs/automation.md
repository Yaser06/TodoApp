---
init:
  commands:
    - "npm i -g @nestjs/cli"
    - "nest new project-name"
  description: "Initialize NestJS project"

dev:
  commands:
    - "npm run start:dev"
  description: "Start dev server with hot reload"

test:
  commands:
    - "npm run test"
    - "npm run test:e2e"
  description: "Run unit and e2e tests"

build:
  commands:
    - "npm run build"
  description: "Build for production"

lint:
  commands:
    - "npm run lint"
  description: "Run ESLint"

format:
  commands:
    - "npm run format"
  description: "Format with Prettier"

deploy:
  commands:
    - "node dist/main"
  description: "Run production build"

monitoring:
  api: "http://localhost:3000"
  docs: "http://localhost:3000/api/docs"
---

# Automation Profile — NestJS

## Development Workflow

### Initial Setup
```bash
npm i -g @nestjs/cli
nest new my-app
cd my-app
npm install
```

### Development
```bash
npm run start:dev      # Hot reload
npm run start:debug    # Debug mode
npm run build          # Build
npm run start:prod     # Production
```

### Testing
```bash
npm run test           # Unit tests
npm run test:watch     # Watch mode
npm run test:cov       # Coverage
npm run test:e2e       # E2E tests
```

### Code Quality
```bash
npm run lint           # ESLint
npm run format         # Prettier
```

## Quality Gates
- ✅ All tests pass
- ✅ No TypeScript errors
- ✅ ESLint passes
- ✅ Test coverage ≥ 80%
- ✅ Swagger docs generated
