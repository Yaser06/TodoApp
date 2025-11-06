---
setup:
  - name: "Install dependencies"
    command: ["./mvnw", "clean", "install", "-DskipTests"]
  - name: "Bootstrap database"
    command: ["docker-compose", "up", "-d", "db"]
dev:
  - name: "Start application"
    command: ["./mvnw", "spring-boot:run"]
  - name: "Run watcher tests"
    command: ["./mvnw", "test", "-Plive-reload"]
test:
  - name: "Unit tests"
    command: ["./mvnw", "test"]
  - name: "Integration tests"
    command: ["./mvnw", "verify", "-Pintegration"]
  - name: "Static analysis"
    command: ["./mvnw", "spotless:check", "checkstyle:check"]
build:
  - name: "Build jar"
    command: ["./mvnw", "clean", "package", "-DskipTests=false"]
  - name: "Docker image"
    command: ["docker", "build", "-t", "app:latest", "."]
deploy:
  - name: "Deploy to staging"
    command: ["bash", "-lc", "kubectl apply -f k8s/staging"]
  - name: "Deploy to production"
    command: ["bash", "-lc", "kubectl apply -f k8s/prod"]
qualityGates:
  testCoverageTarget: 85
  lintRequired: true
  securityScan: true
  additionalChecks:
    - "Dependency check (`./mvnw org.owasp:dependency-check-maven:aggregate`)"
monitoring:
  - metric: "latency_p95"
    target: "< 200ms"
  - metric: "error_rate"
    target: "< 0.5%"
autoTasks:
  - trigger: "post-merge"
    actions:
      - "run ./mvnw test"
      - "update progress log with results"
updatedAt: ""
updatedBy: ""
---

# Automation Profile — Spring Boot

Bu dosya Spring Boot projelerinde kullanılacak varsayılan komutları ve kalite kapılarını içerir. Global runbook ile birleşerek emergent tarzı otomasyon akışını tamamlar.
