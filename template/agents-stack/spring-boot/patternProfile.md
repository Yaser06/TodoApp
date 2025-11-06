---
architecturalPrinciples:
  - "Katmanlı mimari: Controller → Service → Repository/Port → Adapter"
  - "Domain sınırları paket yapısıyla ayrıştırılır; DTO ↔ Entity mapping MapStruct veya dedicated mapper sınıflarıyla yapılır"
  - "Idempotent ve transactional servisler; @Transactional yalnızca servis katmanında kullanılır"
  - "Spring profilleri (`dev`, `staging`, `prod`) konfigürasyon ayrımı için kullanılır"
codingPatterns:
  - "Validation: jakarta.validation anotasyonları + servis seviyesinde guardlar"
  - "Exception handling: merkezi @ControllerAdvice + problem detail yanıtları"
  - "Logging: SLF4J + MDC (correlation-id), güvenlik logları ayrı kanal"
  - "Configuration: application-*.yml; secrets environment/secrets manager üzerinden enjekte edilir"
operationalPatterns:
  - "Actuator health/info endpoints monitoringe bağlı"
  - "Feature toggles: Spring Cloud Config / Unleash / LaunchDarkly"
  - "Deployment: Rolling update veya blue/green; rollback planı dokümante"
securityPatterns:
  - "OAuth2 Resource Server veya custom JWT filter ile authz/authn"
  - "Input sanitization + output encoding; SQL injection’a karşı parametrik sorgu"
  - "Secrets manager (Vault, AWS Secrets Manager) kullanım kuralı"
  - "Audit logging: kritik işlemler için zorunlu"
updatedAt: ""
updatedBy: ""
---

# Pattern Profile — Spring Boot

Yukarıdaki front matter, Spring Boot projeleri için önerilen desenleri listeler. `systemPatterns.md` bu alanları stack-specific değerler olarak kullanır. Markdown bölümü, gerektiğinde açıklama veya örnek eklemek için boş bırakılmıştır.
