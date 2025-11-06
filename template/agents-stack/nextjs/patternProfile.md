---
architecture:
  layers:
    - name: "app/"
      description: "Route segmentleri, layout’lar, server actions"
    - name: "components/ui"
      description: "Design system atomları (button, card, input, form primitives)"
    - name: "components/features"
      description: "Özelleşmiş ekran/flow bileşenleri, reusable section’lar"
    - name: "lib/"
      description: "API client, utilities, design tokens, config"
    - name: "stories/"
      description: "Storybook senaryoları"
  dataFlow: "React Query kullanarak server’dan gelen veriler cache’lenir; optimistic updates + error toasts"
  errorHandling: "Error boundary + toast notifications; form errorları alan altında gösterilir"
  accessibility: "Radix primitives ile ARIA uyumlu bileşenler; keyboard navigation zorunlu"
patterns:
  ui:
    - "Card/grid layout’larında `gap-6` ve `max-w-` kısıtlarıyla okunabilirlik sağla"
    - "Form input’ları `FormField` wrapper’ı ile label, description, error metni içerir"
    - "Primary/secondary button stilleri design tokens (`btn-primary`, `btn-ghost`) üzerinden gelir"
  state:
    - "Global UI state (theme, toasts) için Zustand store; data fetch React Query"
    - "Server actions ile mutate; optimistic UI + rollback strateji dokümante"
  testing:
    - "Vitest için `__tests__` dizinleri; Testing Library ile kullanıcı odaklı test"
    - "Playwright smoke: todo CRUD, auth flow, navigation"
updatedAt: ""
updatedBy: ""
---

# Pattern Profile — Next.js Web

Modern web arayüzleri için layout, erişilebilirlik ve test pratiklerini standartlaştırır. Ajanlar yeni öğrenimleri buraya ekleyerek tasarım sistemini geliştirir.
