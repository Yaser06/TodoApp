# 🎯 Orchestrator Setup Modes

The orchestrator supports **two modes**: Local-only and Git workflow.

**IMPORTANT:** Git branches are **ALWAYS used** for multi-agent isolation (prevents conflicts). The difference is whether you push to GitHub or stay local.

---

## 🏠 Mode 1: Local-Only (No GitHub Required)

**Use when:**
- You just want to test the orchestrator
- You don't need PR reviews
- Working on a local project without remote
- No GitHub account

### Setup

1. **Initialize local Git repo:**

```bash
git init
git add .
git commit -m "Initial commit"
```

2. Edit `orchestrator-config.yaml`:

```yaml
git:
  use_branches: true      # ← REQUIRED for multi-agent
  push_to_remote: false   # ← No GitHub push
```

3. Start agents:

```bash
./orchestrate.sh
```

**What happens:**
- ✅ Agents work on tasks
- ✅ Each agent creates a branch (isolation!)
- ✅ Code is committed to branch
- ✅ Tests run
- ❌ No push to remote
- ❌ No PRs

**Requirements:**
- Docker Desktop
- Python 3.8+
- Git (local only, no GitHub)

**Benefit:** Each agent works in its own branch → **no conflicts!**

---

## 🌿 Mode 2: Git Workflow (Full CI/CD)

**Use when:**
- You want proper Git workflow with PRs
- You want PR reviews
- Working with a team
- Need remote backup

### Setup

1. **Create GitHub Repository:**

```bash
# Create repo on GitHub (via web or CLI)
gh repo create my-project --public

# Or if repo already exists
git init
git remote add origin git@github.com:username/my-project.git
```

2. **Authenticate GitHub CLI:**

```bash
gh auth login
```

3. **Configure orchestrator:**

Edit `orchestrator-config.yaml`:

```yaml
git:
  use_branches: true      # ← REQUIRED for multi-agent
  push_to_remote: true    # ← Push to GitHub
  main_branch: "main"
  auto_pr: true
```

4. **Initial commit:**

```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

5. **Start agents:**

```bash
./orchestrate.sh
```

**What happens:**
- ✅ Agents work on tasks
- ✅ Each agent creates a branch (isolation!)
- ✅ Code is committed to branch
- ✅ Branch is pushed to GitHub
- ✅ PR is created automatically
- ✅ Tests run
- ✅ (Optional) PR auto-merged

**Requirements:**
- Docker Desktop
- Python 3.8+
- Git configured
- GitHub CLI (`gh`)
- GitHub repository

---

## 🔄 Switching Between Modes

You can switch modes anytime by editing `orchestrator-config.yaml`:

### Local → GitHub:

1. Set `git.push_to_remote: true`
2. Create GitHub repo
3. Run `gh auth login`
4. Add remote: `git remote add origin <url>`
5. Continue with agents

### GitHub → Local:

1. Set `git.push_to_remote: false`
2. Continue with agents
3. (Existing branches remain, new branches won't push)

---

## 📊 Comparison

| Feature | Local Mode | Git Mode |
|---------|-----------|----------|
| **GitHub repo required** | ❌ No | ✅ Yes |
| **GitHub CLI required** | ❌ No | ✅ Yes |
| **Git branches** | ✅ Yes (local) | ✅ Yes (pushed) |
| **Git commits** | ✅ Yes (local) | ✅ Yes (pushed) |
| **Agent isolation** | ✅ Yes | ✅ Yes |
| **Push to remote** | ❌ No | ✅ Yes |
| **PRs created** | ❌ No | ✅ Yes |
| **Code written** | ✅ Yes | ✅ Yes |
| **Tests run** | ✅ Yes | ✅ Yes |
| **Multi-agent coordination** | ✅ Yes | ✅ Yes |
| **Conflict prevention** | ✅ Yes (branches) | ✅ Yes (branches) |
| **Setup time** | 🟢 2 min | 🟡 5 min |
| **Best for** | Testing, solo | Teams, production |

---

## 💡 Recommendations

### For Testing
```yaml
git:
  use_branches: true
  push_to_remote: false  # No GitHub needed
```
Test orchestrator locally without GitHub setup.

### For Solo Projects
```yaml
git:
  use_branches: true
  push_to_remote: true   # Keep remote backup
  auto_pr: false          # No need for PRs
```

### For Team Projects
```yaml
git:
  use_branches: true
  push_to_remote: true
  auto_pr: true
  auto_merge:
    enabled: false  # Manual review
    require_review: true
```

---

## 🚀 Quick Start Examples

### Example 1: Test Orchestrator (No GitHub)

```bash
# 1. Init local git
git init
git add .
git commit -m "Initial commit"

# 2. Edit config
cat > orchestrator-config.yaml << EOF
git:
  use_branches: true
  push_to_remote: false
EOF

# 3. Start agents
./orchestrate.sh  # Terminal 1
./orchestrate.sh  # Terminal 2

# Each agent works in its own branch!
# No GitHub needed, no conflicts!
```

### Example 2: Full Git Workflow

```bash
# 1. Init git and create GitHub repo
git init
gh repo create my-project --public
git remote add origin git@github.com:username/my-project.git

# 2. Authenticate
gh auth login

# 3. Initial commit
git add .
git commit -m "Initial commit"
git push -u origin main

# 4. Configure
cat > orchestrator-config.yaml << EOF
git:
  use_branches: true
  push_to_remote: true
  auto_pr: true
EOF

# 5. Start agents
./orchestrate.sh  # Terminal 1
./orchestrate.sh  # Terminal 2

# PRs will be created automatically!
```

---

## ❓ FAQ

**Q: Why are branches required even in local mode?**

A: **Agent isolation!** Without branches, multiple agents would edit the same files simultaneously → conflicts. Each agent needs its own branch.

**Q: Can I use Git without PRs?**

A: Yes! Set `push_to_remote: true` but `auto_pr: false`. This commits and pushes to branches but doesn't create PRs.

```yaml
git:
  use_branches: true
  push_to_remote: true
  auto_pr: false  # ← No PRs
```

**Q: Can I work completely offline?**

A: Yes! Set `push_to_remote: false`. Git branches are created locally, commits are local, nothing is pushed.

```yaml
git:
  use_branches: true
  push_to_remote: false  # ← Offline mode
```

**Q: What if I don't have a GitHub repo yet?**

A: Use local mode (`push_to_remote: false`) until you're ready to create the repo.

**Q: Can I switch modes mid-project?**

A: Yes! Just edit the config and restart agents. Existing branches remain intact.

**Q: Will agents conflict in local mode?**

A: **No!** Each agent creates its own branch (e.g., `ai-agent-1/task-T001`). Branches prevent conflicts.

---

**Choose your mode and start orchestrating!** 🚀
