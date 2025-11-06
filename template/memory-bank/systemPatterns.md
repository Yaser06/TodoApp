---
architecturalPrinciples:
  global: []
  stackSpecific: []
codingPatterns:
  global: []
  stackSpecific: []
operationalPatterns:
  global: []
  stackSpecific: []
securityPatterns:
  global: []
  stackSpecific: []
updatedAt: ""
updatedBy: ""
---

# System Patterns — Universal Template

> **AI instruction**: Treat the front matter as the single source for patterns; the Markdown body is informational only.

## Architectural Principles
- Global: `{{ architecturalPrinciples.global }}`
- Stack Specific: `{{ architecturalPrinciples.stackSpecific }}`

## Coding Patterns
- Global: `{{ codingPatterns.global }}`
- Stack Specific: `{{ codingPatterns.stackSpecific }}`

## Operational Patterns
- Global: `{{ operationalPatterns.global }}`
- Stack Specific: `{{ operationalPatterns.stackSpecific }}`

## Security Patterns
- Global: `{{ securityPatterns.global }}`
- Stack Specific: `{{ securityPatterns.stackSpecific }}`

## When To Update
- Yeni reusable çözüm, pattern veya anti-pattern bulunduğunda.
- Postmortem / retro çıktıları sonrası yeni dersler olduğunda.
- Stack klasörüne yeni içerik eklendiğinde.

Front matter’daki her değişiklikte `updatedAt` ve `updatedBy` alanlarını güncellemeyi unutmayın.
