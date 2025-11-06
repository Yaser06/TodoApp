---
snapshot:
  projectName: ""
  stack: ""
  domain: ""
  elevatorPitch: ""
  primaryPersonas: []
  stakeholders: []
missionOutcomes:
  northStar: ""
  successMetrics: []
  keyMilestones: ""
scopeGuardrails:
  mvp: []
  niceToHave: []
  outOfScope: []
  assumptions: []
  risks: []
operatingModel:
  interfaces: []
  availabilityTarget: ""
  complianceNotes: ""
  operationalExpectations: ""
stackSummary: ""
updatedAt: ""
updatedBy: ""
---

# Project Brief — Universal Template

> **AI instruction**: Populate the front matter fields; the Markdown body is for human reference and does not require modification.

## Snapshot (özet)
- **Project Name**: `{{ snapshot.projectName }}`
- **Stack**: `{{ snapshot.stack }}`
- **Domain / Problem Space**: `{{ snapshot.domain }}`
- **Elevator Pitch**: `{{ snapshot.elevatorPitch }}`
- **Primary Personas**: `{{ snapshot.primaryPersonas }}`
- **Stakeholders**: `{{ snapshot.stakeholders }}`

## Mission & Outcomes
- **North Star Objective**: `{{ missionOutcomes.northStar }}`
- **Success Metrics**: `{{ missionOutcomes.successMetrics }}`
- **Key Milestones**: `{{ missionOutcomes.keyMilestones }}`

## Scope Guardrails
- **MVP / Must Have**: `{{ scopeGuardrails.mvp }}`
- **Nice to Have**: `{{ scopeGuardrails.niceToHave }}`
- **Out of Scope**: `{{ scopeGuardrails.outOfScope }}`
- **Assumptions**: `{{ scopeGuardrails.assumptions }}`
- **Risks / Unknowns**: `{{ scopeGuardrails.risks }}`

## Operating Model
- **Supported Interfaces**: `{{ operatingModel.interfaces }}`
- **Availability Target**: `{{ operatingModel.availabilityTarget }}`
- **Compliance / Policy Notes**: `{{ operatingModel.complianceNotes }}`
- **Operational Expectations**: `{{ operatingModel.operationalExpectations }}`

## Stack Summary
- `{{ stackSummary }}`

Bu dosya projenin “neden” ve “ne” sorularını yanıtlar. Büyük karar veya yön değişikliklerinde front matter’ı güncelleyin; `updatedAt` + `updatedBy` alanlarını doldurun.
