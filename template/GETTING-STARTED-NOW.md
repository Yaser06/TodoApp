# 🚀 Şimdi Başla - Step by Step Guide

## Prerequisites Check

```bash
# 1. Docker çalışıyor mu?
docker --version
# Docker version 20.x.x veya üstü olmalı

# 2. Docker Desktop çalışıyor mu?
docker info
# Hata vermemeli

# 3. Python 3 var mı?
python3 --version
# Python 3.8+ olmalı

# 4. Git var mı?
git --version
```

---

## 🎯 Senaryo 1: Single Agent Test (En Basit)

### Adım 1: Infrastructure Başlat
```bash
cd /Users/yaseraktas/dev/Projects/YapayZekaRules/ai-project-starter-kit/template

# Orchestrator'ı başlat
./orchestrate.sh
```

**Ne Olacak**:
```
🔍 Checking infrastructure...
⚠️  Orchestrator not running
📦 Starting infrastructure...
   Starting Redis and Orchestrator API...
⏳ Waiting for services to be ready...
✅ Infrastructure ready!

📊 Orchestrator Status:
   Agents: 0 active, 0 total
   Tasks: 0/5 completed
   Phase: 1

🔌 Connecting to orchestrator...
✅ Agent registered: agent-1

🎯 Claiming task...
✅ Claimed task: T001 - Setup project structure
🌿 Creating branch: agent-1/T001
💻 Preparing workspace for T001...
   ✓ Created: CURRENT_TASK.md
   ✓ Created: .ai-context/task-T001.json

============================================================
🎯 READY TO IMPLEMENT
============================================================
Task: Setup project structure
Type: setup

📋 What to do:
   1. Read: CURRENT_TASK.md (workspace context)
   2. Implement the feature (use your AI tool)
   3. Write tests
   4. Commit changes: git add . && git commit -m 'Implement T001'

💡 The agent will automatically detect your commit and continue...
============================================================

⏳ Waiting for implementation...
   Monitoring branch: agent-1/T001
   (Checking for commits every 10 seconds)

```

**Agent şimdi BEKLIYOR!** ⏸️

### Adım 2: Task Context'i Gör

**Yeni bir terminal aç** (agent terminal'i açık bırak):
```bash
cd /Users/yaseraktas/dev/Projects/YapayZekaRules/ai-project-starter-kit/template

# CURRENT_TASK.md'yi oku
cat CURRENT_TASK.md
```

**Göreceğin**:
```markdown
# 🎯 Current Task: Setup project structure

**Task ID:** `T001`
**Type:** `setup`
**Priority:** `H`

## 📋 Description
Initialize project with basic folder structure and configuration

## ✅ Acceptance Criteria
- Folders created
- Config files added
- README updated

## 🚀 When Done:
git add .
git commit -m "feat: Setup project structure (T001)"
```

### Adım 3: Implementation (3 Seçenek)

#### Seçenek A: Claude Code ile (Önerilen)
```bash
# Eğer Claude Code kuruluysa:
claude code "read CURRENT_TASK.md and implement the task"

# Claude Code:
# 1. CURRENT_TASK.md'yi okur
# 2. Folder'ları oluşturur
# 3. Config file'ları ekler
# 4. README'yi update eder
# 5. Commit atar
```

#### Seçenek B: Manuel (Test için hızlı)
```bash
# Basit bir implementation (test için):
mkdir -p src tests docs
echo "# Project" > README.md
echo "node_modules/" > .gitignore

# Commit et
git add .
git commit -m "feat: Setup project structure (T001)"
```

#### Seçenek C: Cursor/Windsurf
```bash
# Cursor'da:
# 1. CURRENT_TASK.md'yi aç
# 2. Cursor AI'a "implement this task" de
# 3. Commit et
```

### Adım 4: Agent Otomatik Devam Eder

**İlk terminal'de göreceğin** (commit attıktan sonra):
```
✅ Implementation committed!
   Commit: feat: Setup project structure (T001)
   ✓ Cleaned up: CURRENT_TASK.md

🧪 Running tests...
   Running: Tests Pass...
   ✅ Tests Pass passed (or skipped if no tests yet)

✅ Changes committed to local branch: agent-1/T001
💡 To push later: git push origin agent-1/T001

✅ Task T001 completed successfully!

🎯 Claiming next task...
✅ Claimed task: T002 - Setup database
...
```

**Agent otomatik next task'a geçer!** 🎉

---

## 🎯 Senaryo 2: Multi-Agent Test (2-3 Terminal)

### Adım 1: İlk Agent'ı Başlat
```bash
# Terminal 1
cd /Users/yaseraktas/dev/Projects/YapayZekaRules/ai-project-starter-kit/template
./orchestrate.sh
```

**Sonuç**: Agent-1 T001'i claim eder, READY TO IMPLEMENT der

### Adım 2: İkinci Agent'ı Başlat

**Yeni terminal aç**:
```bash
# Terminal 2
cd /Users/yaseraktas/dev/Projects/YapayZekaRules/ai-project-starter-kit/template
./orchestrate.sh
```

**Sonuç**:
- Agent-2 register olur
- T001 zaten claimed (agent-1'de)
- Agent-2 T002'yi claim eder
- READY TO IMPLEMENT (farklı task!)

### Adım 3: Üçüncü Agent (Optional)

**Yeni terminal aç**:
```bash
# Terminal 3
cd /Users/yaseraktas/dev/Projects/YapayZekaRules/ai-project-starter-kit/template
./orchestrate.sh
```

**Sonuç**:
- Agent-3 register olur
- T001 ve T002 zaten claimed
- T003'ün dependencies var (T001, T002)
- Agent-3 bekler veya "No tasks available" der

### Adım 4: İmplement Parallel

**Her terminal için ayrı ayrı** (paralel çalışabilirsiniz):

```bash
# Terminal 1'de: T001 implement et
git add .
git commit -m "feat: T001 implementation"

# Terminal 2'de: T002 implement et
git add .
git commit -m "feat: T002 implementation"
```

**Her agent kendi branch'inde çalışır**:
- Terminal 1: `agent-1/T001`
- Terminal 2: `agent-2/T002`
- Terminal 3: (T003 için T001, T002 merge olmasını bekliyor)

### Adım 5: Merge ve Phase Advancement

**T001 merge olduktan sonra**:
- Merge coordinator (background) PR'ı detect eder
- Sequential merge başlar
- T001 → main'e merge
- T002 sırada bekler

**T001 ve T002 merge olunca**:
- Phase 2 başlar
- Agent-3 artık T003'ü implement edebilir

---

## 🧪 Test Scenarios

### Test 1: Happy Path (Her Şey Başarılı)
```bash
# 1. Agent başlat
./orchestrate.sh

# 2. Simple implementation
mkdir src
echo "console.log('hello')" > src/index.js
git add .
git commit -m "feat: T001 implementation"

# 3. Agent auto-continues
# ✅ Tests pass
# ✅ Commit already done
# ✅ Task complete
# ✅ Next task claimed
```

### Test 2: Test Failure (Auto-Fix)
```bash
# 1. Agent başlat, task claim
./orchestrate.sh

# 2. Broken implementation
mkdir src
echo "console.log('broken" > src/index.js  # Syntax error!
git add .
git commit -m "feat: T001 broken"

# 3. Tests fail!
# Agent creates FIX_TASK.md
# Agent waits for fix

# 4. Read FIX_TASK.md
cat FIX_TASK.md
# Shows: syntax error, test output

# 5. Fix it
echo "console.log('fixed')" > src/index.js
git add .
git commit -m "fix: T001 syntax error"

# 6. Agent detects fix
# ✅ Re-tests
# ✅ Re-pushes
# ✅ Success!
```

### Test 3: Timeout
```bash
# 1. Agent başlat
./orchestrate.sh

# 2. Don't commit anything
# Wait 60 minutes...

# 3. Agent timeout
# ⚠️  Timeout: No commit detected after 60 minutes
# Task marked as failed
```

---

## 📊 Monitor System

### Terminal'de:
```bash
# Status check
./orchestrate.sh status
```

**Output**:
```
📊 Orchestrator Status:
   Agents: 2 active, 3 total
   Tasks: 2/5 completed
   Phase: 2
```

### Task Board UI (Optional):
```bash
# Start task board
docker-compose --profile dev up -d task-board

# Open browser
open http://localhost:9090
```

**Göreceğin**:
- Backlog tasks
- In Progress tasks (hangi agent)
- Done tasks
- Current phase

### Logs:
```bash
# Orchestrator logs
./orchestrate.sh logs

# Agent logs
# Her terminal'de zaten görüyorsun
```

---

## 🛑 Stop Everything

```bash
# Ctrl+C in each agent terminal

# Stop infrastructure
./orchestrate.sh stop
```

---

## 🔧 Troubleshooting

### "Docker is not running"
```bash
# Start Docker Desktop
# Then retry: ./orchestrate.sh
```

### "Orchestrator failed to start"
```bash
# Check logs
docker-compose logs orchestrator-api

# Common issue: Port 8765 already in use
# Solution: Kill process using port 8765
lsof -ti:8765 | xargs kill -9
```

### "No tasks available"
```bash
# Check if tasks have dependencies
cat memory-bank/work/backlog.yaml

# Example: T003 depends on T001, T002
# Solution: Wait for T001, T002 to be merged
```

### Agent stuck on "Waiting for implementation"
```bash
# Check if you're on the right branch
git branch --show-current
# Should be: agent-X/TXXX

# Check if you committed
git log -1

# If yes, agent should detect it within 10 seconds
# If not, commit now:
git add .
git commit -m "feat: implementation"
```

### "Git remote not configured"
```bash
# Option 1: Add remote
git remote add origin <your-repo-url>

# Option 2: Use local mode
# Edit orchestrator-config.yaml:
#   push_to_remote: false
#   auto_pr: false
```

---

## 🎯 Quick Start Summary

**Tek Agent**:
```bash
# 1. Start
./orchestrate.sh

# 2. Wait for "READY TO IMPLEMENT"

# 3. Implement (new terminal or same)
cat CURRENT_TASK.md  # Read task
# ... implement ...
git add . && git commit -m "feat: implementation"

# 4. Agent auto-continues!
```

**Multi Agent**:
```bash
# Terminal 1, 2, 3:
./orchestrate.sh

# Each claims different task
# Implement in parallel
# System handles merge sequentially
```

---

## 📚 Useful Commands

```bash
# Status
./orchestrate.sh status

# Logs
./orchestrate.sh logs

# Stop
./orchestrate.sh stop

# Reset (start fresh)
./orchestrate.sh reset

# Help
./orchestrate.sh help

# Test workflows
./orchestrate.sh test-persistence
./orchestrate.sh test-workflow
```

---

## 🎉 Ready!

**En basit test**:
```bash
# Single command
./orchestrate.sh
```

**Sonra ne olacak**:
1. ✅ Infrastructure starts
2. ✅ Agent registers
3. ✅ Task claimed
4. ✅ READY TO IMPLEMENT
5. 👉 **Sen implement et**
6. ✅ Auto-continues!

**Başla!** 🚀
