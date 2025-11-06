# 📊 Task Board - Real-Time Monitoring

Modern, lightweight task board for monitoring AI agent progress in real-time.

## ✨ Features

- ✅ **Real-time updates** - SSE (Server-Sent Events) for instant task updates
- ✅ **Auto-start** - Agent automatically starts task board when working
- ✅ **Smart port detection** - Finds available port (9090-9099)
- ✅ **No database** - Uses backlog.yaml directly (file-based)
- ✅ **Docker-based** - Clean, isolated environment
- ✅ **Modern UI** - Tailwind CSS, responsive Kanban board
- ✅ **Concurrent safe** - File locking prevents conflicts

## 🚀 Quick Start

### Automatic (via Agent)

Agent automatically starts task board when you begin work:

```bash
claude "Load memory-bank/core/project.yaml and start"
# → Agent will start task board automatically
# → Browser opens at http://localhost:9090 (or next available port)
```

### Manual Start

```bash
cd tools/task-board
./start.sh
# → Opens at http://localhost:9090
```

Or with Docker Compose:

```bash
cd tools/task-board
docker-compose up -d
```

## 📋 UI Overview

```
┌──────────────────────────────────────────────────────────┐
│  Task Board                              Agent: Working   │
├──────────────────────────────────────────────────────────┤
│  [+ New Task]                                             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  BACKLOG   │  │ IN PROGRESS│  │    DONE     │        │
│  │    (5)     │  │    (1)     │  │    (3)      │        │
│  ├────────────┤  ├────────────┤  ├────────────┤        │
│  │ T001 🤖    │  │ T003 🤖    │  │ T002 ✓     │        │
│  │ Setup DB   │  │ Auth API   │  │ Models     │        │
│  │ High       │  │ ⚙️  Now    │  │            │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│                                                           │
└──────────────────────────────────────────────────────────┘

Legend:
🤖 = AI-generated task
👤 = User-created task
⚙️ = Currently executing
✓ = Completed
```

## 🎯 User Actions

| Action | When Allowed | Effect |
|--------|--------------|--------|
| **Add Task** | Anytime | Creates new task in backlog with title, description, AC, and priority |
| **Edit Task** | Backlog or Done (not AI InProgress) | Update task details (title, description, AC, priority) |
| **Edit Done Task** | Done tasks only | Updates task AND moves it back to Backlog (AI re-processes) |
| **View Status** | Anytime | Real-time task progress with live updates |

**Task Fields:**
- **Title**: Task name (required)
- **Description**: Optional task details
- **AC (Acceptance Criteria)**: Pipe-separated checklist (e.g., "Login|Logout|Reset Password")
- **Priority**: H (High), M (Medium), L (Low)

**Important Rules:**
- ✅ **Backlog tasks**: Can be edited anytime
- ✅ **Done tasks**: Can be edited (moves to Backlog for AI to re-process)
- ❌ **InProgress AI tasks**: Cannot be edited (no edit button shown)

## 🔧 Architecture

```
Browser (User)
    ↓ SSE (real-time)
Flask Backend (Port 9090-9099)
    ↓ File lock
backlog.yaml (memory-bank/work/)
    ↓ File lock
AI Agent (Read/Write)
```

### Key Components

- **Backend**: Flask + SSE + Watchdog
- **Frontend**: React (inline) + Tailwind CSS
- **Storage**: backlog.yaml (no database!)
- **Concurrency**: File locking (fcntl)
- **Real-time**: Server-Sent Events (SSE)

## 🐳 Docker Details

### Port Auto-Detection

```yaml
ports:
  - "9090-9099:9090"  # Tries 9090, if busy → 9091, 9092, etc.
```

### Volume Mount

```yaml
volumes:
  - ../../memory-bank/work:/app/data  # Shares backlog.yaml
```

### Health Check

```bash
curl http://localhost:9090/health
# → {"status": "healthy", "service": "task-board"}
```

## 🛠️ API Endpoints

```
GET    /health              # Health check
GET    /api/tasks           # Get all tasks
POST   /api/tasks           # Create task (user) - auto-generates unique ID
PUT    /api/tasks/:id       # Update task (blocks InProgress AI tasks)
                            # - If task is Done → moves to Backlog
                            # - If task is InProgress AI → returns 403 error
PATCH  /api/tasks/:id/priority  # Change priority
GET    /stream              # SSE endpoint (real-time updates)
```

**Task ID Generation:**
- Auto-generated as `T001`, `T002`, etc.
- Scans ALL columns (backlog, inProgress, done) to find max ID
- Always generates unique, sequential IDs

## 📁 File Structure

```
task-board/
├── Dockerfile               # Container image
├── docker-compose.yml       # Orchestration
├── requirements.txt         # Python deps
├── start.sh                 # Quick start script
├── README.md               # This file
│
├── backend/
│   ├── app.py              # Flask server + port detection
│   ├── file_manager.py     # YAML with file locking
│   ├── sse.py              # Server-Sent Events
│   └── watcher.py          # File change monitor
│
└── frontend/
    ├── index.html          # Single-file React app
    └── dist/
        └── index.html      # Production build
```

## 🔒 Concurrency Safety

### File Locking Strategy

```python
# Read (shared lock - multiple readers OK)
fcntl.flock(file, fcntl.LOCK_SH)

# Write (exclusive lock - single writer, blocks readers)
fcntl.flock(file, fcntl.LOCK_EX)
```

### Scenario: User + AI write simultaneously

```
Time    User Action           AI Agent Action
0ms     Click "Add Task"      -
1ms     Acquire lock ✅       -
2ms     Read backlog.yaml     Try acquire lock ⏳
3ms     Add new task          Waiting...
4ms     Write backlog.yaml    Waiting...
5ms     Release lock          Acquire lock ✅
6ms     -                     Read (now includes user's task)
7ms     -                     Move task to inProgress
8ms     -                     Write backlog.yaml
9ms     -                     Release lock
```

**Result**: Both operations succeed, no data loss!

## 🚦 Troubleshooting

### Port already in use

**Problem**: Port 9090-9099 all busy

**Solution**:
```bash
# Stop existing task board
docker-compose down

# Or kill process on port
lsof -ti:9090 | xargs kill
```

### Task board not starting

**Problem**: Docker not running

**Solution**:
```bash
# Check Docker status
docker info

# Start Docker Desktop (macOS/Windows)
open -a Docker
```

### Tasks not updating in UI

**Problem**: SSE connection lost

**Solution**:
- Refresh browser (auto-reconnects after 3s)
- Check backend logs: `docker logs task-board`

### File permission errors

**Problem**: backlog.yaml not writable

**Solution**:
```bash
# Fix permissions
chmod 666 memory-bank/work/backlog.yaml
```

## 💡 Tips

1. **Leave it running** - Task board uses minimal resources (~50MB RAM)
2. **Open in second monitor** - Watch tasks while coding
3. **Refresh safe** - Page reload reconnects SSE automatically
4. **Port flexible** - If 9090 busy, tries 9091, 9092, etc.

## 🎯 Design Decisions

### Why SSE instead of WebSocket?

- ✅ Simpler (one-way communication sufficient)
- ✅ Auto-reconnect built-in
- ✅ Less overhead

### Why file-based instead of database?

- ✅ No extra dependency
- ✅ Agent already uses backlog.yaml
- ✅ Simpler architecture
- ✅ Easy backup/versioning

### Why Docker?

- ✅ Isolated environment
- ✅ Consistent across machines
- ✅ Easy port management
- ✅ No Python version conflicts

### Why single-file frontend?

- ✅ No build step needed
- ✅ CDN-based (React, Tailwind)
- ✅ Instant deployment
- ✅ Easy to customize

## 📝 Future Enhancements

Potential features (not implemented yet):

- [ ] Drag & drop between columns
- [ ] Task filtering (AI/Manual, Priority)
- [ ] Export tasks to PDF/CSV
- [ ] Dark mode toggle
- [ ] Mobile responsive improvements
- [ ] Task notes/comments
- [ ] Time tracking per task

## 🤝 Contributing

To modify the UI:

1. Edit `frontend/index.html`
2. Copy to `frontend/dist/`
3. Rebuild Docker: `docker-compose build`
4. Restart: `docker-compose up -d`

## 📄 License

Part of AI Project Starter Kit - MIT License
