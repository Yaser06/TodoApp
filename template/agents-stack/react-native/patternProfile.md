---
architecturalPrinciples:
  - "Feature-based dizin yapısı (`features/<name>`), ortak bileşenler `shared/`"
  - "Presentational vs container ayrımı; hooks ile veri erişimi soyutlanır"
  - "Offline-first yaklaşım: optimistic updates, queue cache sistemi"
  - "Navigation olayları merkezi orchestrator (deeplink, analytics)"
codingPatterns:
  - "TypeScript strict mode zorunlu; `any` yalnızca gerekçeyle"
  - "Reusable UI bileşenleri accessibility etiketi (`accessible`, `accessibilityLabel`) içerir"
  - "Network çağrıları merkezi client üzerinden; error normalization + retry/backoff"
  - "Error boundaries ve fallback UI akışları tanımlı"
operationalPatterns:
  - "Feature flag / remote config ile kademeli yayın"
  - "Crash & performance metric takibi her release’te kontrol edilir"
  - "OTA (Expo Updates/CodePush) + store release planı dokümante"
  - "Versioning: semantic version + build numarası politikası"
securityPatterns:
  - "Sensitive veri secure storage; AsyncStorage’da PII saklanmaz"
  - "Permission prompt metinleri Info.plist/AndroidManifest üzerinde güncel"
  - "Logging: PII maskelenir, debug logları prod’da devre dışı"
  - "Clipboard, screenshot, screen recording için koruma stratejisi belirlenir"
updatedAt: ""
updatedBy: ""
---

# Pattern Profile — React Native

Front matter, React Native projeleri için önerilen desenleri sağlar; `systemPatterns.md` stack-specific alanlarda bu değerleri kullanır. Markdown bölümü açıklama veya örnek eklemek için ayrılmıştır.
