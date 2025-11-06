---
stackDefaults:
  language: "Java 17+"
  framework: "Spring Boot 3.x (Web, Validation, Data JPA, Actuator)"
  buildTool: "Maven Wrapper 3.9.x veya Gradle Wrapper 8.x — seçim projectConfig’de belirtilmeli"
  persistence: "PostgreSQL 14+ veya MySQL 8, Hibernate, Flyway/Liquibase migrations"
  messaging: "Kafka (Spring Cloud Stream) veya RabbitMQ; retry + DLQ politikaları zorunlu"
  caching: "Redis (Spring Data Redis) veya Caffeine; TTL/eviction stratejisi dokümante edilmeli"
  infrastructure: "Docker Compose (local), Kubernetes (prod); health checkler Actuator ile beslenir"
  security: "Spring Security + JWT/OAuth2; secrets environment/secrets manager üzerinden"
  observability: "Micrometer + Prometheus/Grafana, OpenTelemetry tracing, JSON structured logging"
toolingWorkflow:
  staticAnalysis:
    - "SpotBugs"
    - "Checkstyle veya PMD"
    - "SonarQube"
  testingStack:
    - "JUnit 5"
    - "Mockito"
    - "Testcontainers"
    - "WireMock"
  formatting: "Spotless plugin + Google Java Format"
  cicd: "Build → Unit Test → Integration Test → Static Analysis → Security Scan → Deploy"
  localDev: "docker-compose profilleri, Testcontainers destek profili, Makefile veya task runner komutları"
updatedAt: ""
updatedBy: ""
---

# Tech Profile — Spring Boot

Yukarıdaki YAML front matter, Spring Boot stack’i için varsayılan teknik tercihleri ve araç zincirini içerir. `techContext.md` bu değerleri kullanarak doldurulur.

## Notlar
- `buildTool` seçiminde Maven/Gradle ayrımını proje özelinde kesinleştirin.
- Messaging ve caching tercihleri production ortamında gözden geçirilmeli; fallback stratejisi tanımlı olmalı.
- Observability kısmı, log formatı ve trace kimliklendirmesini zorunlu kılar (MDC `correlation-id`).
