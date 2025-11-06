---
stackDefaults:
  language: "TypeScript ≥ 5.x, React Native ≥ 0.7x"
  navigation: "React Navigation (stack/tab), deeplink + universal link konfigürasyonu"
  stateManagement: "Redux Toolkit veya Zustand — seçim projectConfig’de belirtilmeli"
  networking: "React Query/Axios wrapper; caching ve retry stratejisi tanımlı"
  styling: "Tailwind (NativeWind) veya Styled Components; design tokens merkezi yönetilir"
  nativeModules: "Kamera, ödeme, sensör SDK’ları için platform notları (Info.plist / AndroidManifest)"
  buildRelease: "Expo EAS veya bare workflow + fastlane/gradle; CI pipeline otomatik build"
  security: "Secure storage (Keychain/Keystore), TLS pinning opsiyonu, gizli config environment değişkenlerinde"
  observability: "Sentry/Firebase Crashlytics, React Native Performance izleme, analytics SDK (Segment/Amplitude)"
toolingWorkflow:
  packageManager: "Yarn Berry veya PNPM (lock dosyası zorunlu)"
  lintFormat:
    - "ESLint (project config)"
    - "Prettier"
    - "TypeScript `--noEmit`"
  testingStack:
    - "Jest"
    - "React Native Testing Library"
    - "Detox veya Maestro (E2E)"
    - "Storybook (opsiyonel)"
  automation: "Husky + lint-staged, app.json/eas.json profilleri, OTA stratejisi dokümante"
  localDev: ".env.example, simulator/emulator listesi, Makefile veya task runner komutları"
updatedAt: ""
updatedBy: ""
---

# Tech Profile — React Native

Front matter, React Native projeleri için standart teknik tercihleri içerir ve `techContext.md` tarafından tüketilir. Markdown bölümü, ihtiyaç duyulduğunda açıklama eklemeniz için ayrılmıştır.
