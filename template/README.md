# 🚀 AI Project Starter Kit - Template

Modern, production-ready template for AI-powered projects with multi-stack support and real-time task tracking.

## 📦 What's Included

This template provides:

- ✅ **Multi-Stack Support** - Django, FastAPI, Go, NestJS, Vue3/Nuxt
- ✅ **Memory Bank System** - Persistent AI context and knowledge
- ✅ **Task Board** - Real-time task monitoring with visual Kanban board
- ✅ **Stack Validation** - Automatic stack detection with intelligent fallbacks
- ✅ **Agent System** - Pre-configured AI agents for different tasks

## 📁 Project Structure

```
template/
├── memory-bank/              # AI memory and context
│   ├── core/                 # Project configuration
│   │   └── project.yaml      # Main project settings
│   └── work/                 # Active work items
│       └── backlog.yaml      # Task backlog (empty by default)
│
├── agents-stack/             # Stack-specific agent configurations
│   ├── django/              # Django stack
│   ├── fastapi/             # FastAPI stack
│   ├── go/                  # Go stack
│   ├── nestjs/              # NestJS stack
│   └── vue3-nuxt/           # Vue3/Nuxt stack
│
└── tools/                    # Development tools
    ├── context_builder.py   # Context generation tool
    └── task-board/          # Real-time task monitoring
        ├── backend/         # Flask API + SSE
        ├── frontend/        # React UI
        └── docker-compose.yml

```

## 🚀 Quick Start

### 1. Choose Your Stack

Copy this template to your project:

```bash
cp -r template/ my-new-project/
cd my-new-project/
```

### 2. Configure Project

Edit `memory-bank/core/project.yaml`:

```yaml
stack: django  # or: fastapi, go, nestjs, vue3-nuxt
projectName: "My Awesome Project"
description: "Project description here"
```

### 3. Start Task Board (Optional)

```bash
cd tools/task-board
docker-compose up -d
# Opens at http://localhost:9090 (or 9091, 9092... if 9090 is busy)
```

### 4. Start Development

The AI agent will automatically:
- Detect your stack
- Load appropriate configurations
- Start processing tasks from `backlog.yaml`

## 🎯 Key Features

### Memory Bank System

**Purpose**: Persistent AI context across sessions

**Structure**:
- `memory-bank/core/` - Project-wide configuration
- `memory-bank/work/` - Active tasks and backlog

**Benefits**:
- AI remembers project context
- Consistent behavior across sessions
- Shared knowledge between stack types

### Task Board

**Purpose**: Visual, real-time task monitoring

**Features**:
- Real-time updates via SSE
- Kanban board (Backlog → In Progress → Done)
- Edit tasks (with smart AI protection)
- Auto-generated unique task IDs
- Acceptance Criteria support

**Access**: `http://localhost:9090` (auto-detects available port)

**Details**: See [tools/task-board/README.md](tools/task-board/README.md)

### Multi-Stack Support

**Supported Stacks**:

| Stack | Framework | Language | Use Case |
|-------|-----------|----------|----------|
| **Django** | Django 4.x | Python | Full-stack web apps |
| **FastAPI** | FastAPI | Python | Modern APIs, async |
| **Go** | Gin/Echo | Go | High-performance services |
| **NestJS** | NestJS | TypeScript | Enterprise Node.js apps |
| **Vue3/Nuxt** | Nuxt 3 | TypeScript | Modern SPA/SSR |

**Stack Detection**:
1. Checks `memory-bank/core/project.yaml`
2. Falls back to file detection (requirements.txt, go.mod, etc.)
3. Uses generic fallback if nothing detected

## 📋 Task Management

### Creating Tasks

**Via Task Board UI**:
1. Click "+ New Task"
2. Fill in:
   - Title (required)
   - Description (optional)
   - Acceptance Criteria (pipe-separated: `Login|Logout|Reset`)
   - Priority (H/M/L)

**Via YAML** (manual):
```yaml
backlog:
  - id: "T001"
    title: "Setup authentication"
    ac: "Login endpoint|JWT tokens|Password reset"
    pri: "H"
    source: "manual"
```

### Task Lifecycle

```
┌─────────────┐
│   BACKLOG   │  User adds task / AI creates task
└──────┬──────┘
       │
       ↓ AI picks up task
┌─────────────┐
│ IN PROGRESS │  AI is working (LOCKED - cannot edit)
└──────┬──────┘
       │
       ↓ AI completes
┌─────────────┐
│    DONE     │  Can edit (moves back to Backlog for re-work)
└─────────────┘
```

### Edit Rules

- ✅ **Backlog**: Freely editable
- ✅ **Done**: Editable (moves to Backlog for AI to re-process)
- ❌ **InProgress (AI)**: Locked (no edit button)

## 🛠️ Tools

### Context Builder

Generate context for AI agents:

```bash
python tools/context_builder.py <stack>

# Examples:
python tools/context_builder.py django
python tools/context_builder.py go
```

**Output**: Formatted context for AI consumption

### Task Board

See [tools/task-board/README.md](tools/task-board/README.md) for:
- Full API documentation
- Architecture details
- Troubleshooting guide
- Development instructions

## 🏗️ Customization

### Adding New Stack

1. Create stack directory:
```bash
mkdir -p agents-stack/my-stack
```

2. Add configuration files:
```bash
agents-stack/my-stack/
├── agentsrules
├── commands/
└── prompts/
```

3. Update stack validation in `memory-bank/stack-validation.yaml`

### Customizing Task Board

1. Edit UI: `tools/task-board/frontend/dist/index.html`
2. Rebuild: `docker-compose build`
3. Restart: `docker-compose up -d`

## 🔒 File Safety

**Concurrent Access Protection**:
- File locking (fcntl) prevents data corruption
- Multiple readers allowed (shared lock)
- Single writer at a time (exclusive lock)
- Automatic retry with exponential backoff

**Example Scenario**:
```
User adds task → Acquires lock → Writes → Releases lock
    ↓ (1ms later)
AI processes → Waits for lock → Acquires → Reads (includes user's task)
```

## 📊 Best Practices

### Task Management

1. **Clear Titles**: Use descriptive task names
2. **Acceptance Criteria**: Break down requirements with `|` separator
3. **Priority Wisely**: Use H (High) sparingly
4. **Edit Done Tasks**: Update completed tasks if requirements change (auto-moves to Backlog)

### Project Organization

1. **Keep backlog.yaml clean**: Archive old tasks regularly
2. **Use descriptive IDs**: Auto-generated T001, T002... are sequential
3. **Monitor task board**: Keep it open while developing

### Stack Configuration

1. **Set stack explicitly**: In `project.yaml` for best performance
2. **Update configurations**: As project evolves
3. **Test fallbacks**: Ensure generic stack works as backup

## 🚦 Troubleshooting

### Task Board Won't Start

**Docker not running:**
```bash
docker info  # Check if Docker is running
open -a Docker  # Start Docker Desktop (macOS)
```

**Port busy:**
```bash
docker-compose down  # Stop existing instance
# Task board will auto-detect next available port (9091, 9092...)
```

### Tasks Not Showing in UI

**SSE connection lost:**
- Refresh browser (auto-reconnects)
- Check logs: `docker logs task-board`

**Empty backlog:**
- Verify `memory-bank/work/backlog.yaml` has tasks
- Check file permissions: `chmod 666 backlog.yaml`

### Stack Not Detected

**Manual override:**
```yaml
# memory-bank/core/project.yaml
stack: django  # Force specific stack
```

**Check validation:**
```bash
cat memory-bank/stack-validation.yaml
```

## 🎯 Common Workflows

### Starting New Project

1. Copy template
2. Set stack in `project.yaml`
3. Start task board: `cd tools/task-board && docker-compose up -d`
4. Add initial tasks via UI
5. Let AI process backlog

### Adding Feature

1. Open task board: `http://localhost:9090`
2. Click "+ New Task"
3. Add feature details:
   - Title: "Add user authentication"
   - AC: "Login page|JWT tokens|Logout|Password reset"
   - Priority: High
4. Watch AI process in real-time

### Re-working Completed Task

1. Find task in "Done" column
2. Click "✏️ Edit"
3. Update requirements
4. Save → Task automatically moves to Backlog
5. AI will re-process with new requirements

## 📚 Further Reading

- **Task Board**: [tools/task-board/README.md](tools/task-board/README.md)
- **Stack Guides**: Check `agents-stack/<stack>/README.md` for stack-specific docs

## 🤝 Contributing

This is a template - customize it for your needs!

Common customizations:
- Add new stacks
- Modify task board UI
- Create custom agent rules
- Add project-specific tools

## 📄 License

MIT License - Use freely in your projects!

---

**Ready to build something amazing?** 🚀

1. Configure your stack
2. Start task board
3. Add your first task
4. Watch the magic happen!
