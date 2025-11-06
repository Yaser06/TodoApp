---
stackOverview:
  stackName: ""
  runtimeLanguage: ""
  frameworkModules: []
  buildTooling: ""
  stackDefaults: ""
dataIntegration:
  dataLayer: ""
  asyncComponents: ""
  cachingStrategy: ""
  externalIntegrations: []
  internalContracts: []
  secretsManagement: ""
qualityObservability:
  testingStack: []
  staticAnalysis: []
  loggingMetrics: ""
  tracing: ""
  sloNotes: ""
workflowTooling:
  formattingStandards: []
  localTooling: []
  cicdPipeline: ""
  deploymentWorkflow: ""
updatedAt: ""
updatedBy: ""
---

# Tech Context — Universal Template

> **AI instruction**: Update the front matter only; the Markdown body serves as human-readable reference.

## Stack Overview
- **Stack Name**: `{{ stackOverview.stackName }}`
- **Runtime & Language**: `{{ stackOverview.runtimeLanguage }}`
- **Framework / Platform Modules**: `{{ stackOverview.frameworkModules }}`
- **Build Tooling**: `{{ stackOverview.buildTooling }}`
- **Stack Defaults**: `{{ stackOverview.stackDefaults }}`

## Data & Integration
- **Data Layer (DB, ORM, migrations)**: `{{ dataIntegration.dataLayer }}`
- **Messaging / Async Components**: `{{ dataIntegration.asyncComponents }}`
- **Caching Strategy**: `{{ dataIntegration.cachingStrategy }}`
- **External Integrations**: `{{ dataIntegration.externalIntegrations }}`
- **Internal Contracts**: `{{ dataIntegration.internalContracts }}`
- **Secrets Management**: `{{ dataIntegration.secretsManagement }}`

## Quality & Observability
- **Testing Stack**: `{{ qualityObservability.testingStack }}`
- **Static Analysis / Security Tooling**: `{{ qualityObservability.staticAnalysis }}`
- **Logging & Metrics**: `{{ qualityObservability.loggingMetrics }}`
- **Tracing / APM**: `{{ qualityObservability.tracing }}`
- **SLO / SLA Notes**: `{{ qualityObservability.sloNotes }}`

## Workflow & Tooling
- **Formatting & Linting Standards**: `{{ workflowTooling.formattingStandards }}`
- **Local Dev Tooling / Scripts**: `{{ workflowTooling.localTooling }}`
- **CI/CD Pipeline & Required Checks**: `{{ workflowTooling.cicdPipeline }}`
- **Deployment Workflow**: `{{ workflowTooling.deploymentWorkflow }}`

Yeni bağımlılık veya süreç kararı sonrası front matter alanlarını güncellemeyi ve `updatedAt` / `updatedBy` değerlerini güncel tutmayı unutmayın.
