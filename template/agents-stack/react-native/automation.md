---
setup:
  - name: "Install dependencies"
    command: ["yarn", "install"]
  - name: "Set up environment files"
    command: ["bash", "-lc", "cp .env.example .env.local || true"]
dev:
  - name: "Start Metro bundler"
    command: ["yarn", "start"]
  - name: "Start iOS simulator"
    command: ["yarn", "ios"]
  - name: "Start Android emulator"
    command: ["yarn", "android"]
test:
  - name: "Unit tests"
    command: ["yarn", "test", "--watchAll=false"]
  - name: "Lint"
    command: ["yarn", "lint"]
  - name: "Type check"
    command: ["yarn", "tsc", "--noEmit"]
  - name: "E2E tests"
    command: ["yarn", "detox", "test", "--configuration", "ios.sim.debug"]
build:
  - name: "Build iOS app"
    command: ["yarn", "build:ios"]
  - name: "Build Android app"
    command: ["yarn", "build:android"]
  - name: "Publish OTA update"
    command: ["yarn", "eas", "update", "--branch", "main"]
deploy:
  - name: "Submit to TestFlight"
    command: ["yarn", "eas", "submit", "--platform", "ios"]
  - name: "Submit to Play Console"
    command: ["yarn", "eas", "submit", "--platform", "android"]
qualityGates:
  testCoverageTarget: 80
  lintRequired: true
  securityScan: false
  additionalChecks:
    - "yarn audit --groups dependencies"
monitoring:
  - metric: "crash_free_users"
    target: "> 99%"
  - metric: "startup_time"
    target: "< 2s"
autoTasks:
  - trigger: "pre-release"
    actions:
      - "Run detox smoke suite"
      - "Update release notes in progress log"
updatedAt: ""
updatedBy: ""
---

# Automation Profile — React Native

Front matter React Native projeleri için otomasyon komutlarını tanımlar. Global runbook ile birlikte ajanların build/test/deploy döngülerini tam otomatik çalıştırmasını sağlar.
