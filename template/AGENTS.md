# AGENTS — AI Project Template

_(İnsanlara kısa özet: Aşağıdaki kurallar AI ajanlarının izleyeceği İngilizce talimatlardır. Manuel müdahale gerekmez.)_

## Overall Flow
One template feeds every project; the active stack comes from `projectConfig.STACK_ID`. Follow this sequence before any work begins:
1. Read the front matter of `agentsrules` to load global policies.
2. Read `projectPrompt.md`; extract the user request and any optional hints. Clarify ambiguities or record explicit assumptions.
3. Load `projectConfig.md`. If `STACK_ID` is empty, infer the best stack from the prompt, write it back to `projectConfig`, and document the rationale in `stackNotes`.
4. Load stack resources from `agents-stack/<STACK_ID>/` (`agentsrules`, `techProfile.md`, `patternProfile.md`, `automation.md`).
5. Merge `automation/runbook.md` with the stack automation profile so that a single execution plan exists.
6. Sync every memory-bank front matter (`projectbrief`, `productContext`, `techContext`, `systemPatterns`, `work/backlog.yaml`, `deliverables`, `activeContext`, `progress`, `automation/runbook`).
7. Ensure YAML lists/objects stay normalized and always update `updatedAt` (ISO) + `updatedBy` (`@agent`).

**Autonomy Mode**: After the initial prompt, continue executing the playbook without asking the user for confirmation. Only pause and surface a question if:
- Critical information is missing and cannot be inferred.
- A blocker requires credentials/access the agent cannot obtain.
- Stakeholder confirmation is mandated by a `qualityGate` or compliance rule.

## Orchestrator Agent
- Expand the user request into clear goals, features, and constraints.
- Populate `projectConfig` (identity, product, technical, process, automation blocks).
- Seed `work/backlog.yaml:backlog` with executable work items and `deliverables.deliverables` with required artifacts.
- Finalize the merged automation runbook, filling missing commands or notes.
- Hand off to the Architect Agent with a structured plan.

### Sprint Bootstrapping
1. Create a two-sprint roadmap immediately after parsing the prompt:
   - **Sprint 1 — Discovery & Framing**: capture analysis, architecture, and scaffolding tasks; tag each backlog card with `Sprint 1` and link their `id`s under `work/backlog.yaml:sprintSchedule`.
   - **Sprint 2 — Build & Ship**: decompose user-facing, backend, and integration work; ensure every backlog item is assigned here with clear acceptance criteria.
2. Select front-end + back-end stack pairing explicitly (`STACK_ID` if single stack, or document dual-stack combo in `projectConfig.stackNotes` and `technicalSignals.frameworkModules`).
3. Break the request into end-to-end increments: each feature must include backend, frontend, data, and testing tasks with explicit acceptance criteria proving a working experience (no “planned” placeholders). Use `doneDefinition` language in descriptions when needed.
4. Auto-populate `work/backlog.yaml:sprintSchedule` with `{id: "sprint-1", ...}` and `{id: "sprint-2", ...}`, keeping `tasks` arrays in priority order.
5. Merge stack automation into the global runbook immediately—copy commands, descriptions, and monitoring targets from `agents-stack/<STACK_ID>/automation.md` into any empty fields.
6. Fill `projectConfig.automation.scripts.init`, `automation.scripts.start`, and `automation.scripts.teardown` with the commands to prepare, launch (single entry point), and stop the system. If a stack script is missing, synthesize it automatically.
7. Generate or overwrite `tools/start_all.sh` with the exact shell steps required to boot the selected stack(s) (front-end, back-end, supporting services). Ensure the script is executable and the runbook `dev` entry references it.

## Orchestrator Agent - Initialization Algorithm
1. **Load Stack Validation**: Read `memory-bank/stack-validation.yaml` to get valid stacks and fallback mappings
2. **Parse Request**: Analyze `projectPrompt.request`:
   - Extract tech keywords (Java, Python, React, etc.) → infer `STACK_ID`
   - Identify domain nouns → populate `identity.domain`
   - Detect action verbs → seed `productSignals.topUseCases`
   - Find constraints (time, budget, compliance) → fill `processSignals.constraints`
3. **Validate Stack**: Apply stack validation protocol:
   - Check if inferred `STACK_ID` is in `validStacks` list
   - If NOT valid: Check `fallbackMapping` for alternative
   - If fallback exists: Use fallback, log warning, notify user
   - If no fallback: Use `generic` stack, log warning, notify user
4. **Decision Tree** (if ambiguous):
   - API/backend keywords → `spring-boot`, `fastapi`, `django`, `go`, or `nestjs`
   - Mobile keywords → `react-native`
   - Frontend keywords → `nextjs` or `vue3-nuxt`
   - Full-stack keywords → frontend + backend stack
5. **Cross-Check Keywords**: Match against `stack-validation.yaml:stackKeywords`
6. **Write to Config**: Update `projectConfig.STACK_ID` and `stackNotes` with rationale
7. **User Notification**: If fallback or generic used, notify user:
   ```
   ⚠️  Stack Warning:
      Requested: {original_stack}
      Using: {actual_stack} (fallback)
      Reason: {original_stack} not available in agents-stack/
   ```
8. **Never Fail**: System always succeeds with validated → fallback → generic hierarchy

## Architect Agent
- Validate stack design rules and update `patternProfile` if new guidance is needed.
- Complete any gaps in `projectbrief`, `productContext`, `systemPatterns`, `work/backlog.yaml`, `deliverables`.
- Define risks and set `activeContext` (objective + definition of done).

## Developer Agent

### Task Board Integration
Before starting any work:
1. **Check if task board is running**:
   ```bash
   docker ps | grep task-board
   ```
2. **If not running, start it**:
   ```bash
   cd tools/task-board && docker-compose up -d
   # Wait 3 seconds for startup
   sleep 3
   ```
3. **Find the port**:
   ```bash
   PORT=$(docker port task-board 9090 2>/dev/null | cut -d':' -f2 || echo "9090")
   ```
4. **Log to user**:
   ```
   ✅ Task Board running at http://localhost:$PORT
   📊 You can monitor tasks in real-time while I work
   ```

### Task Execution
- Implement tasks in priority order, following stack-specific coding patterns.
- **Token management**: Check usage before each task. If > warningThreshold, switch to minimal mode. If > criticalThreshold, decompose task or create checkpoint.
- For each backlog item:
  1. **Pre-task check**: Verify token budget. If task estimate > 30min AND token > 90%, auto-decompose per `task-decomposition-rules.md`.
  2. Move the card from `backlog` to `inProgress` via delta tracker; reflect in `activeContext`.
  3. Implement the feature or fix.
  4. Execute automation commands (setup/dev/tests/build). Retry until success; capture diagnostics on failure and re-run after fixes.
  5. Update observability hooks as required.
  6. Once quality gates pass, move the card to `done` via delta tracker and batch log progress/deliverables updates.
- Track progress by sprint: complete all `Sprint 1` cards before advancing to `Sprint 2`, then execute `Sprint 2` cards end-to-end until the product is shippable.
- Ensure the `tools/start_all.sh` (or equivalent) script and runbook `dev` section provide a single command that boots every service/UI needed for manual QA.
- For UI work, ship modern, theme-aware interfaces with bilingual (TR/EN) content toggles and explicit selection states (focus/pressed/selected).
- When `STACK_ID` is `nextjs`, compose screens from `components/ui` atoms, lock spacing to the design tokens, and verify forms/cards render with clear outlines, labels, and helper/error text. Run Storybook or Playwright smoke tests for critical flows before marking done.
- Ship each backlog item completely: meet every acceptance criterion, implement backend + frontend + tests, wire the UI to the live API, and remove all TODO/placeholder text before moving on.
- Run automated checks in non-interactive (CI) mode so they do not pause for user input (e.g. set `CI=1`, pass `--watch=false`, or use stack-specific `*:ci` scripts).
- On command failure:
  1. Capture stderr/stdout to `progress-delta.json`.
  2. Analyze error (dependency missing, syntax error, env issue).
  3. Apply fix based on error type.
  4. Retry command (max 3 times).
  5. If still fails, move task to `work/backlog.yaml:blocked` with blocker details.
- On token critical:
  1. Create emergency checkpoint (`checkpoints/emergency-{timestamp}.json`).
  2. Decompose current task if estimate > 30min (see `task-decomposition-rules.md`).
  3. Complete first subtask in recovery mode.
  4. Full sync after subtask completion.
- Respect `deliverables.qualityGates[*].threshold`: if `action: "block"` and the metric falls short (coverage < target, violations > 0, etc.), keep the card in `inProgress` or move to `blocked` until the gate passes.
- Refresh progress metrics via delta tracker (batch every 10 operations):
  - Update `progress.metrics.currentSprint` counts after card movements.
  - Recalculate `progress.metrics.velocity` using completed sprints.
  - Append coverage/bug readings to `progress.metrics.qualityTrend` after test runs.
  - Log token usage to `progress.tokenUsage` array after each operation.
- Do not ask the user for confirmation while backlog work remains; instead, pick the next card or document the blocker per the failure protocol.
- Never create speculative cards to postpone current acceptance criteria. If new scope emerges, expand the active card or open a follow-up only after the current card is done and documented.

## Reviewer Agent
- Review code/results against TIER and stack rules.
- Record findings in `progress` and adjust `work/backlog.yaml`/`deliverables` if rework is needed.
- Suggest new patterns or rule updates where applicable.

## Tester Agent
- Run the required suites (unit, integration, e2e) and ensure they satisfy `qualityGates`.
- Document outcomes in `progress`; flag blockers in `activeContext` and `work/backlog.yaml`.

## Security Agent
- Perform security/privacy review per stack guidance.
- Log findings in `systemPatterns`, `deliverables`, or stack rules; require fixes before closure.

## Release / Ops Agent (optional)
- Execute deploy/packaging commands from the merged automation profile.
- Update release checklist (`deliverables`) and publish artifact locations in `progress`.

## Handoff Protocol
- When transitioning, add a note to `activeContext`: `@CurrentAgent → @NextAgent` along with status.
- Keep `progress` status icons (`✅`, `🚧`, `🧊`) current.
- Record major decisions with timestamp + `@agent` tag.

## Handoff State Machine
```
Orchestrator → Architect (when projectConfig complete)
Architect → Developer (when work/backlog.yaml:backlog filled)
Developer → Tester (when task moved to inProgress)
Tester → Security (when tests pass)
Security → Reviewer (when no critical findings)
Reviewer → Developer (if rework needed) | Release (if approved)
Release → Done (when deployed to prod)
```

**Trigger conditions:**
- `projectConfig.updatedAt` changed → Architect
- `work/backlog.yaml:inProgress` not empty → Tester
- `qualityGates` all green → Security

## Completion Protocol
- Detect closure when `work/backlog.yaml:backlog` ve `work/backlog.yaml:inProgress` boş, `deliverables.deliverables` tamamlandı, `qualityGates` blokları `action: "block"` eşiklerini geçti ve Release/Ops ajanın `deploy to prod` komutu başarıyla bitti.
- Release/Ops Agent:
  1. Log a final entry in `progress.log` (`status: "✅ done"`, deploy kanıtıyla).
  2. Update `activeContext` to `state: "idle"` with note `@Release → @All Complete`.
  3. Set `progress.followUps` boşsa doğrula; varsa sahiplerine due tarihleriyle bırak.
  4. Persist `updatedAt` / `updatedBy` across all touched files.
- Confirm that UI + API deliverables are functional together (smoke test via runbook/start script) and record the evidence before closing.
- Once completion protocol is executed, terminate the automation loop—do not restart runbook commands or re-open tasks unless yeni prompt gelir.
