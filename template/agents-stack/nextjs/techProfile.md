---
stackDefaults:
  language: "TypeScript ≥ 5.x"
  framework: "Next.js (App Router, server + client components)"
  styling: "Tailwind CSS + shadcn/ui; design tokens CSS variables ile yönetilir"
  componentLibrary: "Radix primitives + shadcn/ui bileşenleri"
  stateManagement: "React Query (server data) + Zustand (local state)"
  forms: "React Hook Form + Zod resolver; tüm validation mesajları görünür"
  dataAccess: "REST veya tRPC client; API katmanı `lib/api` altında"
  auth: "NextAuth (veya proje gereksinimine göre custom provider)"
  testing: "Vitest + Testing Library; Playwright ile smoke E2E"
toolingWorkflow:
  packageManager: "pnpm; lock dosyası zorunlu"
  lintFormat:
    - "ESLint (next/core-web-vitals)"
    - "Prettier"
    - "Stylelint (Tailwind plugin)"
  testingStack:
    - "Vitest"
    - "Playwright smoke suite"
    - "Chromatic/Storybook (opsiyonel görsel regresyon)"
  automation: "Husky + lint-staged; CI pipeline `pnpm lint && pnpm test && pnpm typecheck && pnpm build`"
  localDev: "`pnpm dev`, `.env.local` örneği, `pnpm storybook`"
updatedAt: ""
updatedBy: ""
---

# Tech Profile — Next.js Web

Bu profil, Next.js tabanlı web projeleri için varsayılan teknik tercihleri listeler; `techContext.md` bu değerlerden beslenir ve ajanların modern UI/UX standartlarını korumasını sağlar.
