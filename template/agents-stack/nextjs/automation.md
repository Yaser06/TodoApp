---
setup:
  - name: "Install dependencies"
    command: ["pnpm", "install"]
  - name: "Prepare environment"
    command: ["bash", "-lc", "cp .env.example .env.local || true"]
dev:
  - name: "Start web app"
    command: ["pnpm", "dev"]
  - name: "Start Storybook"
    command: ["pnpm", "storybook"]
test:
  - name: "Unit tests"
    command: ["bash", "-lc", "CI=1 pnpm test -- --watch=false"]
  - name: "Lint"
    command: ["pnpm", "lint"]
  - name: "Type check"
    command: ["pnpm", "typecheck"]
  - name: "Playwright smoke"
    command: ["pnpm", "test:e2e"]
build:
  - name: "Build production bundle"
    command: ["pnpm", "build"]
  - name: "Export static assets"
    command: ["pnpm", "export"]
deploy:
  - name: "Deploy to staging"
    command: ["bash", "-lc", "vercel deploy --prebuilt --env staging --token $VERCEL_TOKEN"]
  - name: "Deploy to production"
    command: ["bash", "-lc", "vercel deploy --prebuilt --prod --token $VERCEL_TOKEN"]
qualityGates:
  testCoverageTarget: 85
  lintRequired: true
  securityScan: false
  additionalChecks:
    - "pnpm audit --prod"
monitoring:
  - metric: "core_web_vitals_lcp"
    target: "< 2.5s"
  - metric: "error_rate"
    target: "< 0.5%"
autoTasks:
  - trigger: "pre-commit"
    actions:
      - "pnpm lint"
      - "pnpm test --runInBand"
updatedAt: ""
updatedBy: ""
---

# Automation Profile — Next.js Web

Bu profil Next.js projelerinde çalıştırılacak komutları tanımlar; global runbook ile birleştiğinde tam otomatik build/test/deploy akışı sağlar. Ajanlar gerekli token/env ayarlarını `projectConfig.automation.environment` altında belgeler.
