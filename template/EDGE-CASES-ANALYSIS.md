# 🔍 Edge Case Analizi - Farklı Senaryolar

Bu dokümanda sistemin farklı kullanım senaryolarında nasıl davrandığını analiz ediyoruz.

---

## 📋 İçindekiler

1. [Tek Agent Senaryosu](#1-tek-agent-senaryosu)
2. [Git Remote Olmadan](#2-git-remote-olmadan)
3. [GitHub Authentication Olmadan](#3-github-authentication-olmadan)
4. [Agent Mid-Task Crash](#4-agent-mid-task-crash)
5. [Redis/Orchestrator Crash](#5-redisorchestrator-crash)
6. [Tüm Task'lar Fail Ederse](#6-tüm-tasklar-fail-ederse)
7. [Boş Backlog](#7-boş-backlog)
8. [Network Issues](#8-network-issues)

---

## 1. Tek Agent Senaryosu

### Soru: 1 tane AI çalıştırırsam sistem ne olur?

### ✅ Çalışır! İşte nasıl:

```
Timeline:
═════════════════════════════════════════════════════════

10:00  Agent-1 Start
       └─ Register → ai-agent-1

10:01  Phase 1: [T001, T002]
       Agent-1 → Claims T001
       └─ T002 remains pending

10:05  Agent-1 → Completes T001
       └─ PR #1 created
       └─ Enters merge queue

10:06  Merge Coordinator → Processing PR #1
       └─ Update main
       └─ Check conflicts
       └─ Run tests
       └─ Merge PR #1
       └─ T001: merged ✓

10:07  Agent-1 → Claims T002 (no competition!)
       └─ T002: in_progress

10:12  Agent-1 → Completes T002
       └─ PR #2 created

10:13  Merge Coordinator → Processing PR #2
       └─ Merge PR #2
       └─ T002: merged ✓

10:14  Phase 1 Complete!
       Phase 2 Starts...
       Agent-1 → Claims T003

... continues
```

### Sonuç:

**✅ Sorunsuz Çalışır**
- Sequential task execution (parallellik olmaz ama o kadar)
- Merge queue tek item alır (zaten tek agent var)
- Phase advancement normal çalışır
- **Tek fark**: Yavaş (parallellik yok)

### Avantajları:
- 🟢 Conflict riski çok az (tek agent, sequential work)
- 🟢 Debug kolay (tek agent log)
- 🟢 Test için ideal

### Dezavantajları:
- 🔴 Yavaş (parallellik yok)
- 🔴 Agent crash olursa tüm sistem durur

---

## 2. Git Remote Olmadan

### Soru: Git bağlantısı kurmazsam ne olur?

### Senaryo 1: Config Doğru (`push_to_remote: false`)

```yaml
# orchestrator-config.yaml
git:
  use_branches: true      # ✓ Branch isolation
  push_to_remote: false   # ✓ No remote needed
  auto_pr: false          # ✓ Can't create PR without remote
  auto_merge:
    enabled: true
```

**✅ Çalışır!**

```
Agent Flow:
├─ Claim task
├─ Create local branch
├─ Implement code
├─ Commit to local branch
├─ Complete task (no PR created, pr_url=None)
├─ Merge coordinator:
│  ├─ Skip PR merge (no PR URL)
│  ├─ Do local merge: git merge --squash branch
│  └─ Mark task as merged ✓
└─ Phase advances
```

**Sonuç**: ✅ Sorunsuz local-only workflow

---

### Senaryo 2: Config Yanlış (`push_to_remote: true` ama remote yok)

```yaml
git:
  use_branches: true
  push_to_remote: true   # ❌ Problem! Remote yok
```

**❌ Fail Eder!**

```
Agent Flow:
├─ Claim task
├─ Create local branch
├─ Implement code
├─ git push origin branch
│  └─ Error: fatal: 'origin' does not appear to be a git repository
└─ Task fails ❌
```

**Çözüm**:
```bash
# Option 1: Fix config
push_to_remote: false

# Option 2: Add remote
git remote add origin git@github.com:user/repo.git
```

---

### Senaryo 3: Remote var ama SSH key yok

```yaml
git:
  push_to_remote: true
```

Remote: `git@github.com:user/repo.git` (SSH)
SSH key: ❌ Yok veya mount edilmemiş

**❌ Fail Eder!**

```
git push origin branch
└─ Error: Permission denied (publickey)
```

**Çözüm**:
```yaml
# docker-compose.yml
volumes:
  - ~/.ssh:/root/.ssh:ro  # SSH key mount et
```

Ya da HTTPS kullan:
```bash
git remote set-url origin https://github.com/user/repo.git
# GitHub token gerekir
```

---

### 🚨 YENİ SORUN TESPİT EDİLDİ: Remote Check Eksik!

**Problem**: `push_to_remote: true` olduğunda agent remote'un varlığını kontrol etmiyor!

```python
# agent_client.py:179 - git push yapıyor
# Ama önce remote var mı diye bakmıyor!
```

**Çözüm Gerekli**:
```python
def check_git_remote(self):
    """Check if git remote exists"""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=self.project_root,
        capture_output=True
    )
    return result.returncode == 0

def execute_task(self, task, role):
    # ...
    if push_to_remote:
        # Check remote exists
        if not self.check_git_remote():
            print(f"❌ Git remote 'origin' not configured!")
            print(f"   Either:")
            print(f"   1. Add remote: git remote add origin <url>")
            print(f"   2. Set push_to_remote: false in config")
            return False, None, branch_name
    # ... continue
```

---

## 3. GitHub Authentication Olmadan

### Senaryo: `gh` CLI configured değil

```yaml
git:
  push_to_remote: true
  auto_pr: true  # ❌ Problem! gh CLI auth gerekli
```

**Test Edelim**:

```bash
gh pr create
└─ Error: authentication token not found
```

**Ne Olur?**

```python
# agent_client.py:189
result = subprocess.run(
    ["gh", "pr", "create", "--title", title, "--body", body],
    check=True  # ❌ Raise exception!
)
```

**Sonuç**: ❌ Task fail eder

**Çözüm 1**: Mount GitHub config
```yaml
volumes:
  - ~/.config/gh:/root/.config/gh:ro
```

**Çözüm 2**: Set token
```yaml
environment:
  - GH_TOKEN=${GH_TOKEN}
```

**Çözüm 3**: Disable auto-PR
```yaml
git:
  auto_pr: false  # Agent PR oluşturmaz, sen manuel yaparsın
```

---

### 🚨 YENİ SORUN: gh CLI Check Eksik!

**Problem**: `auto_pr: true` olduğunda `gh` CLI varlığı kontrol edilmiyor!

```python
# agent_client.py:189
subprocess.run(["gh", "pr", "create", ...])
# Ama gh yüklü mü/auth mu diye bakmıyor!
```

**Çözüm Gerekli**:
```python
def check_gh_cli(self):
    """Check if gh CLI is available and authenticated"""
    # Check if gh exists
    result = subprocess.run(
        ["which", "gh"],
        capture_output=True
    )
    if result.returncode != 0:
        return False, "gh CLI not installed"

    # Check if authenticated
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True
    )
    if result.returncode != 0:
        return False, "gh CLI not authenticated"

    return True, None

def create_pull_request(self, task_id, branch, task):
    # Check gh CLI
    gh_ok, error = self.check_gh_cli()
    if not gh_ok:
        print(f"⚠️  Cannot create PR: {error}")
        print(f"   Skipping PR creation")
        return None  # Continue without PR
```

---

## 4. Agent Mid-Task Crash

### Senaryo: Agent task ortasında crash oldu

```
10:00  Agent-1 claims T001
       └─ T001: in_progress
       └─ Task lock: ai-agent-1 (TTL: 600s)

10:05  Agent-1 implementing...
       💥 CRASH! (Python error, Ctrl+C, etc.)

10:06  Agent-1 offline
       ├─ No heartbeat sent
       ├─ Task lock still active (TTL: 594s remaining)
       ├─ T001: in_progress (orphaned!)
       └─ Other agents can't claim T001

10:15  Heartbeat timeout (300s passed)
       └─ Agent considered dead
       └─ But task lock still active! (294s remaining)

10:16  Task lock expires (600s passed)
       └─ T001 unlocked
       └─ Other agents can claim

10:17  Agent-2 claims T001
       └─ Starts fresh
```

### Sonuç:

**⚠️ Kısmen Çalışır**
- Task lock TTL sayesinde eventually recover eder
- Ama 10 dakika beklemek gerekir (task_lock_ttl: 600)

### Sorun:

Agent timeout (5 min) ile task lock TTL (10 min) arasında 5 dakika gap var.
- Agent dead olduğu detect edilir (5 dk)
- Ama task lock hala aktif (10 dk)
- 5 dakika idle time

### Çözüm 1: Task Lock Cleanup Service

```python
# orchestrator/cleanup_service.py
def cleanup_dead_agent_locks():
    """Cleanup locks from dead agents"""
    while True:
        time.sleep(60)  # Check every minute

        # Get all agents
        agents = redis.hgetall("orchestrator:agents")

        for agent_id, agent_json in agents.items():
            agent = json.loads(agent_json)

            # Check if agent is dead (no heartbeat in 5 min)
            last_heartbeat = datetime.fromisoformat(agent['last_heartbeat'])
            if (datetime.now() - last_heartbeat).seconds > 300:
                # Agent is dead
                print(f"⚠️  Agent {agent_id} is dead (no heartbeat)")

                # Release task lock
                current_task = agent.get('current_task')
                if current_task:
                    redis.delete(f"task_lock:{current_task}")
                    print(f"   Released lock for task {current_task}")

                    # Reset task status
                    task_json = redis.hget("orchestrator:tasks", current_task)
                    if task_json:
                        task = json.loads(task_json)
                        task['status'] = 'pending'
                        task['assigned_to'] = None
                        redis.hset("orchestrator:tasks", current_task, json.dumps(task))
                        print(f"   Reset task {current_task} to pending")
```

**Bu servisi main.py'a eklemek gerekiyor!**

---

## 5. Redis/Orchestrator Crash

### Senaryo 1: Redis Crash

```
10:00  System running
       ├─ Redis: ✓
       ├─ Orchestrator: ✓
       └─ 3 Agents: ✓

10:05  Redis crashes 💥
       └─ Container stopped

10:06  Orchestrator tries Redis operation
       ├─ RedisConnectionError
       ├─ Retry logic (Fix #10)
       ├─ Attempt 1: fail (2s wait)
       ├─ Attempt 2: fail (4s wait)
       └─ Crash after 5 attempts

10:07  Agents try to claim tasks
       └─ HTTP request to orchestrator
       └─ Connection refused (orchestrator down)

10:08  Redis restarts (docker restart)
       └─ Data lost! (if not persisted)

10:09  Orchestrator needs manual restart
       docker-compose restart orchestrator-api
```

### Sorun:

**🚨 Redis persistence configuration eksik!**

```yaml
# docker-compose.yml:12
command: redis-server --appendonly yes --appendfilename "orchestrator.aof"
```

✓ AOF enabled
✗ Volume mapping var ama...

**Test edelim**:
```bash
docker-compose down
docker-compose up -d
# Redis datası var mı?
```

**Eğer data kaybolursa**:
- Orchestrator initialization re-runs
- Fresh state
- ✗ In-progress task'lar lost

---

### Senaryo 2: Orchestrator Crash

```
10:00  System running
       └─ Orchestrator crashes 💥

10:01  Agents can't claim tasks
       └─ HTTP connection refused

10:02  Merge coordinator stopped
       └─ Merge queue stops processing

10:03  Manual restart needed
       docker-compose restart orchestrator-api

10:04  Orchestrator restarts
       ├─ Reads Redis state
       ├─ Agents reconnect
       └─ Merge coordinator resumes
```

### Sonuç:

**✅ Redis ile state preserved**
- Task status korunur
- Merge queue korunur
- Phase info korunur

**❌ In-flight merges lost**
- Merge coordinator thread'i crash olur
- Active merge retry gerekir

---

## 6. Tüm Task'lar Fail Ederse

### Senaryo: Phase 1'deki tüm task'lar fail ediyor

```yaml
backlog:
  # Phase 1
  - id: "T001"
    # Implementation fails (bug, wrong approach, etc.)

  - id: "T002"
    # Tests fail

  # Phase 2 (depends on Phase 1)
  - id: "T003"
    dependencies: ["T001", "T002"]
```

**Ne Olur?**

```
10:00  Agent-1 → T001
       └─ Implementation error
       └─ complete_task(success=False)
       └─ T001: failed

10:05  Agent-2 → T002
       └─ Tests fail after 3 retries
       └─ T002: failed

10:10  Phase 1 Status:
       ├─ T001: failed
       └─ T002: failed

10:11  Phase advancement check:
       └─ All tasks 'failed' or 'merged'?
       └─ ✓ Yes (all failed)
       └─ Phase 1: completed
       └─ Start Phase 2

10:12  Agent-1 tries to claim T003
       └─ Dependency check:
           ├─ T001: failed ❌
           └─ T002: failed ❌
       └─ Can't claim! (dependencies not met)

10:13  All agents stuck
       └─ ⏸️ No tasks available
       └─ Phase 2 can't start
       └─ System deadlocked!
```

### 🚨 SORUN: Dependency Check Sadece 'done' Bakıyor!

```python
# main.py:433
def all_dependencies_complete(task):
    for dep_id in task.get('dependencies', []):
        dep = get_task(dep_id)
        if dep['status'] != 'done':  # ❌ Sadece 'done' check ediyor!
            return False
    return True
```

**Failed task'lar 'done' değil, 'failed'!**

**Çözüm Gerekli**:
```python
def all_dependencies_complete(task):
    """
    Check if all dependencies are complete

    A dependency is complete if it's 'merged' (success) or 'failed' (skip).
    If dependency failed, dependent task should also be marked as blocked/failed.
    """
    for dep_id in task.get('dependencies', []):
        dep_json = r.hget(TASKS_KEY, dep_id)
        if not dep_json:
            return False

        dep = json.loads(dep_json)
        status = dep['status']

        # Check if dependency is complete (merged or failed)
        if status == 'merged':
            continue  # ✓ Success
        elif status == 'failed':
            # Dependency failed - mark this task as blocked
            task['status'] = 'blocked'
            task['blocked_reason'] = f"Dependency {dep_id} failed"
            r.hset(TASKS_KEY, task['id'], json.dumps(task))
            return False
        else:
            # Dependency still in progress
            return False

    return True
```

**Yeni Task Status Eklemek Gerekiyor**: `blocked`

---

## 7. Boş Backlog

### Senaryo: `backlog.yaml` boş

```yaml
backlog: []
```

**Ne Olur?**

```python
# init.py:180
tasks = backlog_data.get('backlog', [])
if not tasks:
    raise ValueError("No tasks found in backlog")  # ✓ Caught!
```

**Sonuç**: ✅ Orchestrator başlamaz, clear error

---

## 8. Network Issues

### Senaryo 1: Agent → Orchestrator bağlantısı kesildi

```
10:00  Agent working on task
10:05  Network loss
       └─ Can't send heartbeat
       └─ Can't complete task
10:10  Agent timeout (5 min)
       └─ Orchestrator marks agent as dead
10:11  Task lock cleanup (if service added)
       └─ Task released
```

### Senaryo 2: Orchestrator → Redis bağlantısı kesildi

```
10:00  Network loss
       └─ Orchestrator can't read/write Redis
10:01  Retry logic (Fix #10)
       └─ 5 retries with backoff
10:02  Still failing
       └─ Orchestrator crashes
```

---

## 📊 Tespit Edilen Yeni Sorunlar

Yukarıdaki analiz sonucunda **5 yeni sorun** tespit edildi:

### 🚨 #14: Git Remote Existence Check Yok
**Dosya**: `agent_client.py:179`
**Sorun**: `push_to_remote: true` ama remote yoksa crash
**Çözüm**: Remote check ekle, graceful fail

### 🚨 #15: GitHub CLI Check Yok
**Dosya**: `agent_client.py:189`
**Sorun**: `auto_pr: true` ama `gh` yoksa crash
**Çözüm**: `gh` availability check, graceful skip

### 🚨 #16: Dead Agent Lock Cleanup Yok
**Dosya**: `main.py` (yeni service gerekli)
**Sorun**: Agent crash olunca task lock 10 dk bekliyor
**Çözüm**: Cleanup service - dead agent'ların lock'larını temizle

### 🚨 #17: Failed Dependencies Block System
**Dosya**: `main.py:433`
**Sorun**: Dependency fail edince dependent task deadlock
**Çözüm**:
- Failed dependency → mark dependent as `blocked`
- New status: `blocked`
- Phase can advance even with blocked tasks

### 🚨 #18: Redis Data Persistence Test Yok
**Dosya**: `docker-compose.yml`
**Sorun**: Redis restart olunca data kaybolabilir
**Çözüm**: Test persistence, verify AOF working

---

## ✅ Çalışan Senaryolar

1. **Tek agent** → ✅ Çalışır (yavaş ama sorunsuz)
2. **Local mode** (config doğruysa) → ✅ Çalışır
3. **Redis restart** (persistence varsa) → ✅ Recover eder
4. **Orchestrator restart** → ✅ State korunur
5. **Empty backlog** → ✅ Clear error

## ❌ Sorunlu Senaryolar

1. **Remote yok ama `push_to_remote: true`** → ❌ Crash (#14)
2. **gh CLI yok ama `auto_pr: true`** → ❌ Crash (#15)
3. **Agent crash** → ⚠️ 10 dk bekler (#16)
4. **Dependencies fail** → ❌ Deadlock (#17)
5. **Redis data loss** → ⚠️ State lost (#18)

---

## 🎯 Önerilen Düzeltme Öncelikleri

### Critical (Sistem crash eder):
1. **#14**: Git remote check
2. **#15**: GitHub CLI check
3. **#17**: Failed dependency handling

### High (UX kötü):
4. **#16**: Dead agent cleanup service

### Medium (Edge case):
5. **#18**: Redis persistence test

---

## 📝 Sonraki Adımlar

Bu 5 yeni sorunu da düzeltmek ister misin?

Ya da önce mevcut sistemi test edip, hangilerinin priority olduğuna karar verebiliriz.
