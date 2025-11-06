---
architecturalPrinciples:
  - "Katmanlı yapı: Router → Service/Domain → Repository/Adapter"
  - "Async-first tasarım; blocking I/O (sync DB driver, `requests`) yasak"
  - "Pydantic modelleri dış kontrat, domain modelleri ayrı tutulur"
  - "Konfigürasyon pydantic-settings ile tipli ve environment tabanlı yönetilir"
codingPatterns:
  - "Dependency Injection: Depends + context managers (DB session)"
  - "Error handling: merkezi exception handler + problem detail response (HTTPException sadece delegasyon için)"
  - "Background işler: Celery task'leri, APScheduler/Celery beat planı belgelenir"
  - "Request/response şemaları versionlanmalı, validation strict tutulmalı"
operationalPatterns:
  - "Health endpoints (`/health`, `/ready`) DB/queue kontrolleri ile zenginleştirilir"
  - "Rate limiting middleware (SlowAPI) veya API gateway konfigürasyonu"
  - "Structured logging + correlation IDs (`X-Request-ID`)"
  - "Blue/green veya canary deployment stratejisi tanımlı"
securityPatterns:
  - "OAuth2/JWT + refresh token flow, scope bazlı yetkilendirme"
  - "Input boyut limitleri, payload sanitization, güvenlik header'ları (`X-Content-Type-Options` vb.)"
  - "Secrets runtime’da yüklenir, global mutable state'ten kaçınılır"
  - "Audit log: kritik aksiyonlarda zorunlu"
updatedAt: ""
updatedBy: ""
---

# Pattern Profile — Python FastAPI

Front matter FastAPI projelerinde kullanılacak pattern özetlerini içerir; `systemPatterns.md` bu verileri stack-specific alanlara aktarır. Markdown bölümü açıklama eklemek için kullanılabilir.
