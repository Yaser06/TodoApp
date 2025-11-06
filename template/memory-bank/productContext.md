---
personas:
  primary: []
  secondary: []
  offlineNeeds: ""
journeys:
  topJourneys: []
  edgeScenarios: []
experiencePillars:
  principles: []
  designReferences: ""
  navigationNotes: ""
businessRules:
  domainRules: []
  metrics: []
  monetization: ""
  compliance: ""
releaseStrategy:
  mvpScope: []
  rolloutStrategy: ""
  analyticsPlan: ""
  qaPlan: ""
collaboration:
  dependencies: []
  approvalGates: []
  cadence: ""
updatedAt: ""
updatedBy: ""
---

# Product Context — Universal Template

> **AI instruction**: Maintain the front matter; the Markdown body targets human readers and can stay untouched by automation.

## Personas & Journeys
- **Primary Personas**: `{{ personas.primary }}`
- **Secondary Personas / Internal Teams**: `{{ personas.secondary }}`
- **Top Journeys**: `{{ journeys.topJourneys }}`
- **Offline / Edge Needs**: `{{ personas.offlineNeeds }}`

## Experience Pillars
- **Design Principles**: `{{ experiencePillars.principles }}`
- **Design System / References**: `{{ experiencePillars.designReferences }}`
- **Navigation / Flow Notes**: `{{ experiencePillars.navigationNotes }}`

## Business Rules
- **Domain Rules**: `{{ businessRules.domainRules }}`
- **KPIs / Success Metrics**: `{{ businessRules.metrics }}`
- **Monetization / Pricing**: `{{ businessRules.monetization }}`
- **Compliance & Policy**: `{{ businessRules.compliance }}`

## Release & Experimentation
- **MVP Scope**: `{{ releaseStrategy.mvpScope }}`
- **Feature Flag / Rollout Strategy**: `{{ releaseStrategy.rolloutStrategy }}`
- **Analytics / Telemetry**: `{{ releaseStrategy.analyticsPlan }}`
- **QA / Device or Environment Coverage**: `{{ releaseStrategy.qaPlan }}`

## Collaboration & Dependencies
- **Team / Vendor Dependencies**: `{{ collaboration.dependencies }}`
- **Approval Gates**: `{{ collaboration.approvalGates }}`
- **Cadence / Rituals**: `{{ collaboration.cadence }}`

Sprint veya milestone sonunda front matter alanlarını güncelleyip `updatedAt` / `updatedBy` değerlerini işleyin.
