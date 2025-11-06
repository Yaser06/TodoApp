# 🚀 Multi-Agent Orchestration - Quick Start Guide

Get started with multi-agent orchestration in **2-5 minutes**!

---

## Choose Your Mode

### 🏠 **Local Mode** (Recommended for Testing)
- ⏱️ **2 minutes** setup
- ✅ No GitHub account needed
- ✅ No repo creation needed
- ✅ Just test the orchestrator

### 🌿 **Git Mode** (For Real Projects)
- ⏱️ **5 minutes** setup
- ✅ Full Git workflow
- ✅ PR creation & review
- ✅ Team collaboration

---

## 🏠 Quick Start: Local Mode (No GitHub)

### Prerequisites

- ✅ **Docker Desktop** installed and running
- ✅ **Python 3.8+** installed
- That's it!

### Step 1: Initialize Local Git

```bash
git init
git add .
git commit -m "Initial commit"
```

### Step 2: Configure Local Mode

Edit `orchestrator-config.yaml`:

```yaml
git:
  use_branches: true      # ← REQUIRED for multi-agent
  push_to_remote: false   # ← Don't push to GitHub
```

### Step 3: Prepare Backlog

Edit `memory-bank/work/backlog.yaml` with your tasks (example already included).

### Step 4: Start Agents

**Terminal 1:**
```bash
./orchestrate.sh
```

**Terminal 2:**
```bash
./orchestrate.sh
```

**Done!** Each agent works in its own branch. No conflicts, no GitHub needed.

---

## 🌿 Full Setup: Git Mode (With GitHub)

### Prerequisites

- ✅ **Docker Desktop** installed and running
- ✅ **Python 3.8+** installed
- ✅ **Git** configured
- ✅ **GitHub CLI** (`gh`) installed and authenticated

### Install GitHub CLI

```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

---

## Step 1: Setup Git Repository

```bash
# If not already initialized
git init
git remote add origin git@github.com:your-username/your-repo.git

# Create initial commit
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## Step 2: Configure Orchestrator

Edit `orchestrator-config.yaml`:

```yaml
agent_assignment:
  setup:
    enabled: true
  development:
    enabled: true
  testing:
    enabled: true
  review:
    enabled: false  # ← Manual PR reviews

git:
  use_branches: true      # ← REQUIRED for multi-agent
  push_to_remote: true    # ← Push to GitHub
  main_branch: "main"
  auto_pr: true           # ← Auto-create PRs
```

---

## Step 3: Prepare Your Backlog

Edit `memory-bank/work/backlog.yaml` with your tasks.

**Important**: Each task must have:
- `id`: Unique task ID (T001, T002, etc.)
- `title`: Task name
- `type`: Task type (`setup`, `development`, `testing`, `security`, `documentation`, `review`)
- `dependencies`: Array of task IDs this task depends on

**Example**:

```yaml
backlog:
  # Phase 1: Setup tasks (no dependencies, run in parallel)
  - id: "T001"
    title: "Setup database"
    type: "setup"
    pri: "H"
    description: "Configure PostgreSQL database"
    acceptanceCriteria: "Database running|Schema created|Migrations setup"
    dependencies: []

  - id: "T002"
    title: "Setup authentication service"
    type: "setup"
    pri: "H"
    description: "Configure JWT authentication"
    dependencies: []

  # Phase 2: Development (depends on setup)
  - id: "T003"
    title: "User registration API"
    type: "development"
    pri: "H"
    description: "Implement user registration endpoint"
    dependencies: ["T001", "T002"]  # ← Needs setup to be done first

  - id: "T004"
    title: "User login API"
    type: "development"
    pri: "H"
    description: "Implement login endpoint"
    dependencies: ["T001", "T002"]

  # Phase 3: Testing (depends on development)
  - id: "T005"
    title: "Integration tests"
    type: "testing"
    pri: "M"
    description: "Write integration tests for auth flow"
    dependencies: ["T003", "T004"]  # ← Needs dev tasks done first
```

**Orchestrator will automatically**:
- Calculate Phase 1: [T001, T002] (parallel)
- Calculate Phase 2: [T003, T004] (parallel, after Phase 1 complete)
- Calculate Phase 3: [T005] (after Phase 2 complete)

---

## Step 4: Start First Agent

Open **Terminal 1**:

```bash
cd template/
./orchestrate.sh
```

You should see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AI Multi-Agent Orchestration System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Starting infrastructure...
   Starting Redis and Orchestrator API...
⏳ Waiting for services to be ready...
✅ Infrastructure ready!

📊 Orchestrator Status:
   Agents: 0 active, 0 total
   Tasks: 0/5 completed
   Phase: 1

🔌 Connecting to orchestrator...

✅ Registered as: ai-agent-1
📋 Claiming task...
🎯 Claimed: T001 (Setup database)
   Role: setup-specialist

🔄 Switching to main branch...
⬇️  Pulling latest changes...
🌿 Creating branch: ai-agent-1/task-T001
💻 Working on T001...
```

The agent is now working on task T001!

---

## Step 5: Start More Agents (Parallel Work)

While Agent 1 is working, open **Terminal 2**:

```bash
cd template/
./orchestrate.sh
```

You should see:

```
✅ Orchestrator is running
📊 Orchestrator Status:
   Agents: 1 active, 1 total
   Tasks: 0/5 completed
   Phase: 1

✅ Registered as: ai-agent-2
🎯 Claimed: T002 (Setup authentication service)
   Role: setup-specialist
```

Agent 2 is now working on T002 **in parallel** with Agent 1!

---

## Step 6: Add Even More Agents (Optional)

Open **Terminal 3**:

```bash
./orchestrate.sh
```

If all Phase 1 tasks are claimed, it will wait:

```
✅ Registered as: ai-agent-3
⏸️  No tasks available (no_tasks_available), waiting...
```

Once Agent 1 or 2 completes their task and Phase 1 is done, Agent 3 will automatically claim a Phase 2 task!

---

## Step 7: Monitor Progress

In another terminal:

```bash
# Check status
./orchestrate.sh status

# View live logs
./orchestrate.sh logs

# Open task board (if enabled)
open http://localhost:9090
```

---

## Step 8: Review PRs

As agents complete tasks, they create PRs. You can:

**Option A: Manual Review** (recommended)
```bash
# View PRs
gh pr list

# Review and merge
gh pr view 1
gh pr merge 1
```

**Option B: Auto-Review** (if `review.enabled: true`)
- Orchestrator automatically reviews and merges PRs
- ⚠️ Use with caution!

---

## Step 9: Stop When Done

When all tasks are complete:

```bash
# Stop infrastructure
./orchestrate.sh stop

# Or just Ctrl+C in each terminal
```

---

## Troubleshooting

### "Docker is not running!"

```bash
# macOS: Start Docker Desktop
open -a Docker

# Linux: Start Docker service
sudo systemctl start docker
```

### "Orchestrator failed to start"

```bash
# Check logs
docker-compose logs orchestrator-api

# Common issue: Port 8765 already in use
lsof -i :8765
# Kill the process using that port

# Restart
./orchestrate.sh stop
./orchestrate.sh
```

### "No tasks available"

```bash
# Check backlog
cat memory-bank/work/backlog.yaml

# Verify tasks have correct dependencies
# Ensure current phase has available tasks
./orchestrate.sh status
```

### "Git push failed"

```bash
# Ensure SSH key is configured
ssh -T git@github.com

# Re-authenticate GitHub CLI
gh auth login

# Check remote
git remote -v
```

---

## Next Steps

- 📖 Read full documentation: [tools/orchestrator/README.md](tools/orchestrator/README.md)
- ⚙️ Customize configuration: `orchestrator-config.yaml`
- 🎯 Add your own tasks to `memory-bank/work/backlog.yaml`
- 🔧 Integrate with your existing project

---

## Tips

1. **Start small**: Test with 2-3 simple tasks first
2. **Use dependencies**: Properly define task dependencies for correct phasing
3. **Monitor logs**: Keep one terminal showing logs (`./orchestrate.sh logs`)
4. **Manual reviews**: Disable auto-review initially, review PRs manually
5. **Git hygiene**: Ensure main branch is clean before starting

---

**Happy multi-agent coding!** 🚀
