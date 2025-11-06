# 🤖 AI Multi-Agent Orchestrator

**Coordinate multiple AI agents (Claude Code instances) to work in parallel on a single project.**

Each terminal runs a separate Claude Code instance that connects to a central orchestrator, claims tasks, implements them with full Git workflow, and creates PRs automatically.

---

## ✨ Features

- 🔄 **Multi-Agent Coordination**: Run multiple AI agents in parallel across different terminals
- 🧠 **Intelligent Task Distribution**: Automatic phase calculation based on dependencies
- 🎯 **Dynamic Role Assignment**: Agents switch roles (developer/tester/security) based on task type
- 🌿 **Full Git Workflow**: Automatic branching, commits, pushes, and PR creation
- ⚙️ **Configurable**: Control which task types are auto-assigned
- 🔒 **Atomic Operations**: Redis-backed state prevents race conditions
- 📊 **Real-time Monitoring**: Track all agents and tasks in real-time

---

## 🚀 Quick Start

### 1. Prerequisites

**Required for all modes:**
- Docker Desktop
- Python 3.8+

**Required only for Git mode:**
- Git
- GitHub CLI (gh)
- GitHub repository

### 2. Choose Your Mode

**🏠 Local Mode** (No GitHub needed)
- Fastest setup (2 minutes)
- No Git, no PRs
- Perfect for testing

**🌿 Git Mode** (Full workflow)
- Complete Git workflow
- PR creation & review
- Team collaboration

### 3. Setup

**For Local Mode:**

```bash
# Edit config
echo "git:
  enabled: false" >> orchestrator-config.yaml

# Done! Skip to step 4.
```

**For Git Mode:**

```bash
# Install GitHub CLI
# macOS:
brew install gh

# Linux:
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Setup Git Repository
git init
git remote add origin git@github.com:your-username/your-repo.git

# Authenticate GitHub CLI
gh auth login

# Edit config
echo "git:
  enabled: true" >> orchestrator-config.yaml
```

### 3. Configure Orchestrator

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
    enabled: false  # ← Disable auto-review if you want manual PR reviews
```

### 4. Prepare Backlog

Edit `memory-bank/work/backlog.yaml` with your tasks:

```yaml
backlog:
  - id: "T001"
    title: "Setup database"
    type: "setup"
    pri: "H"
    description: "Configure PostgreSQL database"
    dependencies: []

  - id: "T002"
    title: "User authentication API"
    type: "development"
    pri: "H"
    description: "Implement JWT auth"
    dependencies: ["T001"]  # ← Depends on T001
```

### 5. Start AI Agents

**Terminal 1:**
```bash
./orchestrate.sh
```

**Terminal 2:**
```bash
./orchestrate.sh
```

**Terminal 3:**
```bash
./orchestrate.sh
```

Each terminal becomes an AI agent that:
1. Connects to orchestrator
2. Claims next available task
3. Creates git branch
4. Implements the task
5. Commits & pushes
6. Creates PR
7. Repeats

---

## 📁 Architecture

```
┌─────────────────────────────────────────┐
│         Redis (State Store)             │
│  - Task Queue                           │
│  - Agent Registry                       │
│  - Phase Management                     │
│  - Locks                                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│    Orchestrator API (Port 8765)         │
│  - Task Distribution                    │
│  - Phase Calculation                    │
│  - Agent Coordination                   │
└────┬───────┬───────┬────────────────────┘
     │       │       │
  ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
  │Agent│ │Agent│ │Agent│
  │  1  │ │  2  │ │  3  │
  └──┬──┘ └──┬──┘ └──┬──┘
     │       │       │
  ┌──▼───────▼───────▼──┐
  │   Git Repository    │
  │  (main + branches)  │
  └─────────────────────┘
```

---

## 🎯 How It Works

### Phase Calculation

The orchestrator analyzes task dependencies and calculates execution phases:

```yaml
# Input:
backlog:
  - id: T001, deps: []
  - id: T002, deps: []
  - id: T003, deps: [T001, T002]
  - id: T004, deps: [T003]

# Output:
Phase 1: [T001, T002]  # Parallel
Phase 2: [T003]
Phase 3: [T004]
```

### Agent Task Loop

```
1. Agent claims task from current phase
2. Checks task type (setup/development/testing)
3. Switches role if needed
4. Creates git branch: {agent-id}/task-{task-id}
5. Implements task
6. Runs quality gates (tests, linter)
7. Commits: "feat: {task-title} ({task-id})"
8. Pushes to remote
9. Creates PR
10. Marks task complete
11. Orchestrator checks if phase complete
12. If complete, advances to next phase
13. Agent claims next task...
```

### Git Workflow

```
main (protected)
├── ai-agent-1/task-T001
│   └── PR #1 → merged
├── ai-agent-2/task-T002
│   └── PR #2 → merged
├── ai-agent-1/task-T003  (agent-1 working on new task)
│   └── PR #3 → open
└── ai-agent-3/task-T004
    └── PR #4 → open
```

---

## ⚙️ Configuration Reference

### orchestrator-config.yaml

```yaml
# Agent Assignment
agent_assignment:
  setup:
    enabled: true  # Auto-assign setup tasks
  development:
    enabled: true  # Auto-assign dev tasks
  testing:
    enabled: true  # Auto-assign test tasks
  review:
    enabled: false  # Manual PR reviews

# Agent Pool
agent_pool:
  auto_calculate: true  # Auto-calculate optimal agent count
  min_agents: 2
  max_agents: 8
  target_utilization: 0.6  # 60% utilization target

# Git Settings
git:
  main_branch: "main"
  branch_pattern: "{agent_id}/task-{task_id}"
  auto_pr: true
  auto_merge:
    enabled: false  # Set to true for auto-merge
    require_review: true
    require_tests_pass: true

# Quality Gates
quality_gates:
  run_tests: true
  run_linter: true
  checks:
    - name: "Tests Pass"
      command: "npm test"
      required: true

# Phase Management
phases:
  auto_advance: true  # Auto-advance when phase complete
  advance_delay: 5  # Wait 5s before advancing
```

---

## 🛠️ Commands

```bash
# Start an agent
./orchestrate.sh

# Show status
./orchestrate.sh status

# View logs
./orchestrate.sh logs

# Stop infrastructure
./orchestrate.sh stop

# Reset state (clears Redis data)
./orchestrate.sh reset
```

---

## 📊 Monitoring

### Check Status

```bash
$ ./orchestrate.sh status

📊 Orchestrator Status:
   Agents: 3 active, 3 total
   Tasks: 2/5 completed
   Phase: 2
```

### View Logs

```bash
$ ./orchestrate.sh logs

orchestrator-api | 🎯 Task T003 claimed by ai-agent-1 (role: developer)
orchestrator-api | ✅ Task T001 completed by ai-agent-2 (success: True)
orchestrator-api | 📍 Starting Phase 2 (Development)
```

### API Endpoints

```bash
# Health check
curl http://localhost:8765/health

# Get full status
curl http://localhost:8765/status | jq .
```

---

## 🔧 Troubleshooting

### Infrastructure Won't Start

```bash
# Check Docker is running
docker info

# Check logs
docker-compose logs

# Restart infrastructure
./orchestrate.sh stop
./orchestrate.sh
```

### Agent Can't Connect

```bash
# Verify orchestrator is running
curl http://localhost:8765/health

# Check if port 8765 is in use
lsof -i :8765

# Restart orchestrator
docker-compose restart orchestrator-api
```

### Tasks Not Being Claimed

```bash
# Check orchestrator status
./orchestrate.sh status

# Verify backlog has tasks
cat memory-bank/work/backlog.yaml

# Check Redis
docker-compose exec redis redis-cli
> HGETALL orchestrator:tasks
```

### Git Push Fails

```bash
# Ensure SSH key is configured
ssh -T git@github.com

# Authenticate GitHub CLI
gh auth login

# Check git remote
git remote -v
```

---

## 🎓 Advanced Usage

### Custom Task Types

Add custom task types in `orchestrator-config.yaml`:

```yaml
agent_assignment:
  deployment:
    enabled: true
    description: "Deployment and release tasks"
```

Then use in backlog:

```yaml
backlog:
  - id: "T010"
    title: "Deploy to production"
    type: "deployment"  # ← Custom type
    pri: "H"
```

### Manual Task Distribution

Disable auto-assignment for specific task types:

```yaml
agent_assignment:
  review:
    enabled: false  # Manual PR reviews
  security:
    enabled: false  # Manual security audits
```

### Integration with Existing Projects

1. Copy orchestrator files to your project:
```bash
cp -r template/tools/orchestrator your-project/tools/
cp template/orchestrate.sh your-project/
cp template/orchestrator-config.yaml your-project/
cp template/docker-compose.yml your-project/
```

2. Update `backlog.yaml` with your tasks

3. Configure `orchestrator-config.yaml`

4. Run `./orchestrate.sh`

---

## 📚 API Reference

See [API.md](./API.md) for complete API documentation.

---

## 🤝 Contributing

Improvements welcome! Areas of interest:
- Better conflict resolution
- Advanced scheduling algorithms
- Multi-repository support
- Cloud deployment (AWS/GCP)

---

## 📄 License

MIT License - use freely in your projects
