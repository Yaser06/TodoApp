---
init:
  commands:
    - "npx nuxi@latest init <project-name>"
    - "pnpm install"
  description: "Initialize Nuxt 3 project"

dev:
  commands:
    - "pnpm dev"
  description: "Start development server on http://localhost:3000"

test:
  commands:
    - "pnpm test"
    - "pnpm test:e2e"
  description: "Run unit and e2e tests"

build:
  commands:
    - "pnpm build"
  description: "Build for production"

preview:
  commands:
    - "pnpm preview"
  description: "Preview production build locally"

lint:
  commands:
    - "pnpm lint"
    - "pnpm lint:fix"
  description: "Run ESLint"

format:
  commands:
    - "pnpm format"
  description: "Format with Prettier"

generate:
  commands:
    - "pnpm generate"
  description: "Generate static site"

deploy:
  commands:
    - "# Deploy to Vercel, Netlify, or Cloudflare Pages"
  description: "Deployment (platform-specific)"
---

# Automation Profile — Vue3/Nuxt

## Development Workflow

### Initial Setup
```bash
npx nuxi@latest init my-app
cd my-app
pnpm install  # or npm install

# Add modules
pnpm add @nuxt/ui @pinia/nuxt @vueuse/nuxt
```

### Development
```bash
pnpm dev        # Start dev server
pnpm build      # Build for production
pnpm preview    # Preview production build
pnpm generate   # Static site generation
```

### Testing
```bash
pnpm test              # Vitest
pnpm test:ui           # Vitest UI
pnpm test:e2e          # Playwright
pnpm test:e2e:ui       # Playwright UI
```

### Linting
```bash
pnpm lint              # Run ESLint
pnpm lint:fix          # Fix issues
pnpm format            # Prettier
```

## Quality Gates
- ✅ All tests pass
- ✅ No TypeScript errors
- ✅ ESLint passes
- ✅ Build succeeds
- ✅ Lighthouse score ≥ 90
