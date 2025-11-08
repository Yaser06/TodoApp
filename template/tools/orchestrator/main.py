#!/usr/bin/env python3
"""
AI Multi-Agent Orchestrator API

Manages coordination between multiple AI agents via Redis.
Handles task distribution, phase management, and Git workflow.
"""

import os
import sys
import json
import yaml
import redis
import logging
import time
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify
from pathlib import Path
from redis.exceptions import ConnectionError as RedisConnectionError, TimeoutError as RedisTimeoutError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
CONFIG_PATH = os.getenv('CONFIG_PATH', '/app/orchestrator-config.yaml')
with open(CONFIG_PATH, 'r') as f:
    CONFIG = yaml.safe_load(f)


# Fix #10: Redis connection with retry logic
def create_redis_connection(max_retries=5):
    """Create Redis connection with retry logic"""
    redis_host = os.getenv('REDIS_HOST', CONFIG['redis']['host'])
    redis_port = int(os.getenv('REDIS_PORT', CONFIG['redis']['port']))
    redis_db = CONFIG['redis']['db']

    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            r.ping()
            logger.info(f"✅ Connected to Redis at {redis_host}:{redis_port}")
            return r
        except (RedisConnectionError, RedisTimeoutError) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(
                    f"⚠️  Redis connection failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s... Error: {e}"
                )
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Redis connection failed after {max_retries} attempts")
                raise

    raise RedisConnectionError("Failed to connect to Redis")


# Redis connection
r = create_redis_connection()

# Redis keys
AGENTS_KEY = "orchestrator:agents"
TASKS_KEY = "orchestrator:tasks"
PHASE_KEY = "orchestrator:current_phase"
PHASES_KEY = "orchestrator:phases"
CONFIG_KEY = "orchestrator:config"
STATS_KEY = "orchestrator:stats"


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        r.ping()
        return jsonify({
            "status": "healthy",
            "redis": "connected",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/cleanup', methods=['POST'])
def cleanup_stuck_tasks():
    """
    Cleanup stuck tasks (Fix #23)

    Recovers tasks that are:
    - In-progress but agent is dead
    - Failed but retry is enabled

    Response:
        {
            "recovered": 2,
            "failed_reset": 1,
            "message": "Cleanup completed"
        }
    """
    try:
        from init import recover_stuck_tasks

        logger.info("🧹 Manual cleanup requested via API")
        recovered_count = recover_stuck_tasks(r, CONFIG)

        return jsonify({
            "recovered": recovered_count,
            "message": "Cleanup completed successfully"
        })
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return jsonify({
            "error": str(e),
            "message": "Cleanup failed"
        }), 500


@app.route('/agent/register', methods=['POST'])
def register_agent():
    """
    Register a new AI agent

    Request:
        {
            "session_id": "12345"
        }

    Response:
        {
            "agent_id": "ai-agent-1",
            "config": {...}
        }
    """
    data = request.json
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    # Generate unique agent ID
    agent_count = r.hlen(AGENTS_KEY)
    agent_id = f"ai-agent-{agent_count + 1}"

    # Store agent info
    agent_info = {
        "agent_id": agent_id,
        "session_id": session_id,
        "status": "idle",
        "current_task": None,
        "current_role": None,
        "registered_at": datetime.now().isoformat(),
        "last_heartbeat": datetime.now().isoformat(),
        "tasks_completed": 0,
        "tasks_failed": 0
    }

    r.hset(AGENTS_KEY, agent_id, json.dumps(agent_info))

    logger.info(f"✅ Agent registered: {agent_id} (session: {session_id})")

    # Return agent config
    return jsonify({
        "agent_id": agent_id,
        "config": CONFIG
    })


@app.route('/task/claim', methods=['POST'])
def claim_task():
    """
    Agent claims next available task (atomic operation)

    Request:
        {
            "agent_id": "ai-agent-1"
        }

    Response:
        {
            "task": {
                "id": "T001",
                "title": "Setup DB",
                "type": "setup",
                ...
            }
        }

        or

        {
            "task": null,
            "reason": "no_tasks_available"
        }
    """
    data = request.json
    agent_id = data.get('agent_id')

    if not agent_id:
        return jsonify({"error": "agent_id required"}), 400

    # Check if agent exists
    agent_json = r.hget(AGENTS_KEY, agent_id)
    if not agent_json:
        return jsonify({"error": "Agent not registered"}), 404

    # Use Redis transaction for atomic claim
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            # Get current phase
            current_phase = get_current_phase()

            if not current_phase:
                return jsonify({
                    "task": None,
                    "reason": "no_active_phase"
                })

            # Find next available task in current phase
            task = find_next_available_task(current_phase, agent_id)

            if not task:
                return jsonify({
                    "task": None,
                    "reason": "no_tasks_available",
                    "phase": current_phase['id']
                })

            # Atomic claim using Redis SET NX (set if not exists)
            task_lock_key = f"task_lock:{task['id']}"
            lock_acquired = r.set(
                task_lock_key,
                agent_id,
                nx=True,
                ex=CONFIG['redis']['task_lock_ttl']
            )

            if not lock_acquired:
                # Another agent claimed this task, retry
                continue

            # Update task status
            task['status'] = 'in_progress'
            task['assigned_to'] = agent_id
            task['started_at'] = datetime.now().isoformat()
            r.hset(TASKS_KEY, task['id'], json.dumps(task))

            # Determine role for this task
            role = determine_role(task['type'])

            # Update agent status
            agent_info = json.loads(agent_json)
            agent_info['status'] = 'working'
            agent_info['current_task'] = task['id']
            agent_info['current_role'] = role
            r.hset(AGENTS_KEY, agent_id, json.dumps(agent_info))

            logger.info(f"🎯 Task {task['id']} claimed by {agent_id} (role: {role})")

            return jsonify({"task": task, "role": role})

        except Exception as e:
            logger.error(f"Error claiming task: {e}")
            if attempt == max_attempts - 1:
                return jsonify({"error": str(e)}), 500
            continue

    # Failed to claim after max attempts
    return jsonify({
        "task": None,
        "reason": "claim_failed_max_attempts"
    })


@app.route('/task/complete', methods=['POST'])
def complete_task():
    """
    Mark task as complete

    Request:
        {
            "agent_id": "ai-agent-1",
            "task_id": "T001",
            "success": true,
            "pr_url": "https://github.com/...",
            "branch_name": "ai-agent-1/task-T001"
        }
    """
    data = request.json
    agent_id = data.get('agent_id')
    task_id = data.get('task_id')
    success = data.get('success', True)
    pr_url = data.get('pr_url')
    branch_name = data.get('branch_name')

    if not agent_id or not task_id:
        return jsonify({"error": "agent_id and task_id required"}), 400

    # Update task
    task_json = r.hget(TASKS_KEY, task_id)
    if not task_json:
        return jsonify({"error": "Task not found"}), 404

    task = json.loads(task_json)
    task['status'] = 'done' if success else 'failed'
    task['completed_at'] = datetime.now().isoformat()
    if pr_url:
        task['pr_url'] = pr_url
    if branch_name:
        task['branch_name'] = branch_name
    r.hset(TASKS_KEY, task_id, json.dumps(task))

    # Release task lock
    r.delete(f"task_lock:{task_id}")

    # Update agent
    agent_json = r.hget(AGENTS_KEY, agent_id)
    if agent_json:
        agent_info = json.loads(agent_json)
        agent_info['status'] = 'idle'
        agent_info['current_task'] = None
        agent_info['current_role'] = None
        if success:
            agent_info['tasks_completed'] = agent_info.get('tasks_completed', 0) + 1
        else:
            agent_info['tasks_failed'] = agent_info.get('tasks_failed', 0) + 1
        r.hset(AGENTS_KEY, agent_id, json.dumps(agent_info))

    status_icon = "✅" if success else "❌"
    logger.info(f"{status_icon} Task {task_id} completed by {agent_id} (success: {success})")

    # Queue for merge (if auto-merge enabled and PR was created)
    merge_coordinator = app.config.get('MERGE_COORDINATOR')
    if merge_coordinator and success and pr_url and branch_name:
        queue_pos = merge_coordinator.queue_merge(task_id, pr_url, branch_name, agent_id)
        logger.info(f"🔀 Task {task_id} queued for merge (position: {queue_pos})")

    # Note: Phase advancement happens after successful merge, not here

    return jsonify({"success": True})


@app.route('/agent/heartbeat', methods=['POST'])
def heartbeat():
    """
    Agent heartbeat to indicate it's still alive

    Request:
        {
            "agent_id": "ai-agent-1"
        }
    """
    data = request.json
    agent_id = data.get('agent_id')

    if not agent_id:
        return jsonify({"error": "agent_id required"}), 400

    agent_json = r.hget(AGENTS_KEY, agent_id)
    if not agent_json:
        return jsonify({"error": "Agent not found"}), 404

    agent_info = json.loads(agent_json)
    agent_info['last_heartbeat'] = datetime.now().isoformat()
    r.hset(AGENTS_KEY, agent_id, json.dumps(agent_info))

    return jsonify({"success": True})


@app.route('/agent/unregister', methods=['POST'])
def unregister_agent():
    """Unregister agent when shutting down"""
    data = request.json
    agent_id = data.get('agent_id')

    if not agent_id:
        return jsonify({"error": "agent_id required"}), 400

    # Release any locked tasks
    agent_json = r.hget(AGENTS_KEY, agent_id)
    if agent_json:
        agent_info = json.loads(agent_json)
        if agent_info.get('current_task'):
            task_lock_key = f"task_lock:{agent_info['current_task']}"
            r.delete(task_lock_key)

            # Reset task status
            task_json = r.hget(TASKS_KEY, agent_info['current_task'])
            if task_json:
                task = json.loads(task_json)
                task['status'] = 'pending'
                task['assigned_to'] = None
                r.hset(TASKS_KEY, agent_info['current_task'], json.dumps(task))

    # Remove agent
    r.hdel(AGENTS_KEY, agent_id)

    logger.info(f"👋 Agent unregistered: {agent_id}")

    return jsonify({"success": True})


@app.route('/status', methods=['GET'])
def get_status():
    """Get orchestrator status"""
    # Get all agents
    agents = {}
    for agent_id, agent_json in r.hgetall(AGENTS_KEY).items():
        agents[agent_id] = json.loads(agent_json)

    # Get all tasks
    tasks = {}
    for task_id, task_json in r.hgetall(TASKS_KEY).items():
        tasks[task_id] = json.loads(task_json)

    # Get current phase
    current_phase = get_current_phase()

    # Get all phases
    phases_json = r.get(PHASES_KEY)
    phases = json.loads(phases_json) if phases_json else []

    # Calculate stats
    stats = {
        "total_agents": len(agents),
        "active_agents": len([a for a in agents.values() if a['status'] == 'working']),
        "idle_agents": len([a for a in agents.values() if a['status'] == 'idle']),
        "total_tasks": len(tasks),
        "pending_tasks": len([t for t in tasks.values() if t['status'] == 'pending']),
        "in_progress_tasks": len([t for t in tasks.values() if t['status'] == 'in_progress']),
        "completed_tasks": len([t for t in tasks.values() if t['status'] == 'done']),
        "failed_tasks": len([t for t in tasks.values() if t['status'] == 'failed']),
        "current_phase": current_phase['id'] if current_phase else None,
        "total_phases": len(phases)
    }

    return jsonify({
        "agents": agents,
        "tasks": tasks,
        "phases": phases,
        "current_phase": current_phase,
        "stats": stats,
        "config": CONFIG
    })


# Helper functions

def get_current_phase():
    """Get current active phase"""
    phase_json = r.get(PHASE_KEY)
    if phase_json:
        return json.loads(phase_json)
    return None


def find_next_available_task(phase, agent_id):
    """
    Find next available task in current phase for agent

    Fix #17: Skip tasks that are blocked due to failed dependencies
    """
    for task_id in phase['tasks']:
        task_json = r.hget(TASKS_KEY, task_id)
        if not task_json:
            continue

        task = json.loads(task_json)

        # Check if task is available
        # Fix #17: Skip blocked tasks
        if task['status'] not in ['pending']:
            continue

        # Check if task type is enabled in config
        task_type = task.get('type', 'development')
        if not CONFIG['agent_assignment'].get(task_type, {}).get('enabled', True):
            continue

        # Check dependencies (this may mark task as 'blocked')
        if not all_dependencies_complete(task):
            continue

        return task

    return None


def all_dependencies_complete(task):
    """
    Check if all task dependencies are complete (Fix #17)

    A dependency is complete if:
    - 'merged': Successfully merged to main ✓
    - 'failed': Failed permanently (blocks dependent tasks) ❌

    If any dependency failed, mark this task as 'blocked'
    """
    task_id = task['id']

    for dep_id in task.get('dependencies', []):
        dep_json = r.hget(TASKS_KEY, dep_id)
        if not dep_json:
            # Dependency doesn't exist
            logger.warning(f"Task {task_id}: Dependency {dep_id} not found")
            return False

        dep = json.loads(dep_json)
        dep_status = dep['status']

        if dep_status == 'merged':
            # Dependency successful, continue
            continue

        elif dep_status == 'failed':
            # Dependency failed - block this task
            logger.warning(
                f"Task {task_id}: Dependency {dep_id} failed, "
                f"marking as blocked"
            )

            # Mark task as blocked
            task['status'] = 'blocked'
            task['blocked_reason'] = f"Dependency {dep_id} failed"
            task['blocked_at'] = datetime.now().isoformat()
            r.hset(TASKS_KEY, task_id, json.dumps(task))

            return False

        else:
            # Dependency still in progress (pending, in_progress, done, etc.)
            return False

    return True


def determine_role(task_type):
    """Determine agent role based on task type"""
    role_mapping = {
        'setup': 'setup-specialist',
        'development': 'developer',
        'testing': 'tester',
        'security': 'security-auditor',
        'documentation': 'technical-writer',
        'review': 'code-reviewer'
    }
    return role_mapping.get(task_type, 'developer')


# Fix #6: Removed duplicate check_and_advance_phase() function
# Phase advancement is handled by merge_coordinator._check_phase_advancement()
# This avoids code duplication and ensures single source of truth


# Fix #16: Dead Agent Lock Cleanup Service
def dead_agent_cleanup_service():
    """
    Background service that cleans up task locks from dead agents

    Runs every 60 seconds and checks for agents that haven't sent
    heartbeat in agent_timeout seconds. Releases their task locks.
    """
    logger.info("🧹 Dead agent cleanup service started")

    agent_timeout = CONFIG['redis']['agent_timeout']
    cleanup_interval = 60  # Check every minute

    while True:
        try:
            time.sleep(cleanup_interval)

            # Get all agents
            agents = r.hgetall(AGENTS_KEY)
            if not agents:
                continue

            current_time = datetime.now()
            cleaned_count = 0

            for agent_id, agent_json in agents.items():
                try:
                    agent = json.loads(agent_json)

                    # Check last heartbeat
                    last_heartbeat_str = agent.get('last_heartbeat')
                    if not last_heartbeat_str:
                        continue

                    last_heartbeat = datetime.fromisoformat(last_heartbeat_str)
                    time_since_heartbeat = (current_time - last_heartbeat).total_seconds()

                    # Agent is dead if no heartbeat for agent_timeout seconds
                    if time_since_heartbeat > agent_timeout:
                        logger.warning(
                            f"🪦 Agent {agent_id} is dead "
                            f"(no heartbeat for {int(time_since_heartbeat)}s)"
                        )

                        # Get current task
                        current_task = agent.get('current_task')
                        if current_task:
                            # Release task lock
                            lock_key = f"task_lock:{current_task}"
                            lock_deleted = r.delete(lock_key)

                            if lock_deleted:
                                logger.info(f"   🔓 Released lock for task {current_task}")

                                # Reset task status to pending
                                task_json = r.hget(TASKS_KEY, current_task)
                                if task_json:
                                    task = json.loads(task_json)
                                    task['status'] = 'pending'
                                    task['assigned_to'] = None
                                    r.hset(TASKS_KEY, current_task, json.dumps(task))
                                    logger.info(f"   ♻️  Reset task {current_task} to pending")
                                    cleaned_count += 1

                        # Remove dead agent from registry
                        r.hdel(AGENTS_KEY, agent_id)
                        logger.info(f"   🗑️  Removed dead agent {agent_id} from registry")

                except Exception as e:
                    logger.error(f"Error processing agent {agent_id}: {e}")
                    continue

            if cleaned_count > 0:
                logger.info(f"✅ Cleanup cycle complete: {cleaned_count} tasks released")

        except Exception as e:
            logger.error(f"❌ Cleanup service error: {e}")
            time.sleep(5)  # Short sleep before retry


if __name__ == "__main__":
    logger.info("🚀 Starting AI Multi-Agent Orchestrator API...")
    logger.info(f"📋 Configuration loaded from: {CONFIG_PATH}")

    # Initialize orchestrator (load backlog, calculate phases)
    from init import initialize_orchestrator
    try:
        initialize_orchestrator(r, CONFIG)
        logger.info("✅ Orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
        sys.exit(1)

    # Initialize merge coordinator (if auto-merge enabled)
    merge_coordinator = None
    if CONFIG['git'].get('auto_merge', {}).get('enabled', False):
        from merge_coordinator import MergeCoordinator
        merge_coordinator = MergeCoordinator(r, CONFIG)
        logger.info("✅ Merge coordinator initialized (auto-merge enabled)")
    else:
        logger.info("⚠️  Auto-merge disabled in config")

    # Store merge coordinator in app context for access in routes
    app.config['MERGE_COORDINATOR'] = merge_coordinator

    # Fix #16: Start dead agent cleanup service
    cleanup_thread = Thread(target=dead_agent_cleanup_service, daemon=True)
    cleanup_thread.start()
    logger.info("✅ Dead agent cleanup service started")

    # Start API server
    port = 8765
    logger.info(f"🌐 API server listening on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
