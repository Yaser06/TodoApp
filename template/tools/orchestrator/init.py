#!/usr/bin/env python3
"""
Orchestrator Initialization

Loads backlog, calculates phases, initializes Redis state.
"""

import yaml
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def detect_project_type(project_root="/app"):
    """
    Detect project type based on files in project root (Fix #8)

    Returns: Project type string (nodejs/python/golang/rust/java/generic)
    """
    project_path = Path(project_root)

    # Check for Node.js
    if (project_path / "package.json").exists():
        return "nodejs"

    # Check for Python
    if (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
        return "python"

    # Check for Go
    if (project_path / "go.mod").exists():
        return "golang"

    # Check for Rust
    if (project_path / "Cargo.toml").exists():
        return "rust"

    # Check for Java/Maven
    if (project_path / "pom.xml").exists():
        return "java-maven"

    # Check for Java/Gradle
    if (project_path / "build.gradle").exists() or (project_path / "build.gradle.kts").exists():
        return "java-gradle"

    # Default to generic
    return "generic"


def get_test_commands_for_project(project_type):
    """
    Get test commands based on project type (Fix #8)

    Returns: List of check configurations
    """
    test_commands = {
        "nodejs": [
            {"name": "Tests Pass", "command": "npm test", "required": True},
            {"name": "Linter Pass", "command": "npm run lint", "required": True},
            {"name": "Build Success", "command": "npm run build", "required": False},
        ],
        "python": [
            {"name": "Tests Pass", "command": "pytest", "required": True},
            {"name": "Linter Pass", "command": "flake8 .", "required": False},
            {"name": "Type Check", "command": "mypy .", "required": False},
        ],
        "golang": [
            {"name": "Tests Pass", "command": "go test ./...", "required": True},
            {"name": "Vet Check", "command": "go vet ./...", "required": True},
            {"name": "Build Success", "command": "go build ./...", "required": False},
        ],
        "rust": [
            {"name": "Tests Pass", "command": "cargo test", "required": True},
            {"name": "Clippy Check", "command": "cargo clippy", "required": True},
            {"name": "Build Success", "command": "cargo build", "required": False},
        ],
        "java-maven": [
            {"name": "Tests Pass", "command": "mvn test", "required": True},
            {"name": "Build Success", "command": "mvn package", "required": False},
        ],
        "java-gradle": [
            {"name": "Tests Pass", "command": "gradle test", "required": True},
            {"name": "Build Success", "command": "gradle build", "required": False},
        ],
        "generic": [
            {"name": "Tests Pass", "command": "echo 'No test command configured'", "required": False},
        ],
    }

    return test_commands.get(project_type, test_commands["generic"])


def validate_backlog_tasks(tasks):
    """
    Validate task format (Fix #11)

    Ensures all tasks have required fields and valid values
    """
    required_fields = ['id', 'title', 'type']
    valid_types = ['setup', 'development', 'testing', 'security', 'documentation', 'review']

    task_ids = set()

    for idx, task in enumerate(tasks, 1):
        # Check required fields
        for field in required_fields:
            if field not in task or not task[field]:
                raise ValueError(
                    f"Task #{idx}: Missing required field '{field}'\n"
                    f"Task data: {task}"
                )

        # Check duplicate IDs
        task_id = task['id']
        if task_id in task_ids:
            raise ValueError(f"Duplicate task ID found: {task_id}")
        task_ids.add(task_id)

        # Validate type
        task_type = task['type']
        if task_type not in valid_types:
            raise ValueError(
                f"Task {task_id}: Invalid type '{task_type}'\n"
                f"Valid types: {', '.join(valid_types)}"
            )

        # Ensure dependencies is a list
        if 'dependencies' not in task:
            task['dependencies'] = []
        elif not isinstance(task['dependencies'], list):
            raise ValueError(
                f"Task {task_id}: 'dependencies' must be a list\n"
                f"Got: {type(task['dependencies']).__name__}"
            )

        # Check if dependencies exist
        for dep_id in task['dependencies']:
            if dep_id not in task_ids and dep_id not in [t['id'] for t in tasks]:
                logger.warning(
                    f"Task {task_id}: Dependency '{dep_id}' not found in backlog"
                )

    logger.info(f"✅ Backlog validation passed ({len(tasks)} tasks)")


def initialize_orchestrator(redis_client, config):
    """
    Initialize orchestrator state

    1. Load backlog from memory-bank/work/backlog.yaml
    2. Calculate dependency graph
    3. Determine execution phases
    4. Store in Redis
    """
    logger.info("📋 Initializing orchestrator...")

    # Fix #8: Detect project type and update config with appropriate test commands
    project_type = detect_project_type("/app")
    logger.info(f"🔍 Detected project type: {project_type}")

    # Override quality_gates checks with project-specific commands
    test_commands = get_test_commands_for_project(project_type)
    config['quality_gates']['checks'] = test_commands
    config['project_type'] = project_type

    logger.info(f"✅ Configured {len(test_commands)} quality checks for {project_type}")

    # Load backlog
    backlog_path = Path("/app/memory-bank/work/backlog.yaml")
    if not backlog_path.exists():
        raise FileNotFoundError(f"Backlog not found: {backlog_path}")

    with open(backlog_path, 'r') as f:
        backlog_data = yaml.safe_load(f)

    tasks = backlog_data.get('backlog', [])
    if not tasks:
        raise ValueError("No tasks found in backlog")

    # Fix #11: Validate task format
    validate_backlog_tasks(tasks)

    logger.info(f"📦 Loaded {len(tasks)} tasks from backlog")

    # Calculate phases
    phases = calculate_phases(tasks)
    logger.info(f"📊 Calculated {len(phases)} execution phases")

    # Store tasks in Redis
    for task in tasks:
        task['status'] = 'pending'
        task['assigned_to'] = None
        redis_client.hset(
            "orchestrator:tasks",
            task['id'],
            json.dumps(task)
        )

    # Store phases in Redis
    redis_client.set("orchestrator:phases", json.dumps(phases))

    # Set first phase as active
    if phases:
        first_phase = phases[0]
        first_phase['status'] = 'active'
        first_phase['started_at'] = datetime.now().isoformat()
        redis_client.set("orchestrator:current_phase", json.dumps(first_phase))
        logger.info(f"📍 Starting Phase 1: {first_phase['name']}")

    # Store config
    redis_client.set("orchestrator:config", json.dumps(config))

    logger.info("✅ Orchestrator initialization complete")


def calculate_phases(tasks):
    """
    Calculate execution phases using dependency graph

    Uses topological sort (Kahn's algorithm) to determine
    which tasks can run in parallel.

    Returns: List of phases, each containing task IDs that can run in parallel
    """
    # Build dependency graph
    graph = DependencyGraph(tasks)

    # Perform topological sort
    phases = graph.topological_sort()

    # Format phases
    formatted_phases = []
    for phase_idx, phase_tasks in enumerate(phases, 1):
        # Determine phase name based on task types
        task_types = list(set(t['type'] for t in phase_tasks))
        if len(task_types) == 1:
            phase_name = task_types[0].capitalize()
        else:
            phase_name = f"Phase {phase_idx}"

        formatted_phases.append({
            'id': phase_idx,
            'name': phase_name,
            'tasks': [t['id'] for t in phase_tasks],
            'status': 'pending',
            'started_at': None,
            'completed_at': None
        })

    return formatted_phases


class DependencyGraph:
    """Dependency graph for task scheduling"""

    def __init__(self, tasks):
        self.tasks = {t['id']: t for t in tasks}
        self.graph = self.build_graph()

    def build_graph(self):
        """Build adjacency list: task_id -> [dependent_task_ids]"""
        graph = {task_id: [] for task_id in self.tasks}

        for task_id, task in self.tasks.items():
            for dep_id in task.get('dependencies', []):
                if dep_id in graph:
                    graph[dep_id].append(task_id)

        return graph

    def topological_sort(self):
        """
        Kahn's algorithm for topological sort

        Returns: List of phases (each phase is a list of tasks that can run in parallel)
        """
        # Calculate in-degree for each task
        in_degree = {tid: 0 for tid in self.tasks}

        for task_id, task in self.tasks.items():
            for dep_id in task.get('dependencies', []):
                if dep_id in in_degree:
                    in_degree[task_id] += 1

        # Phase 0: tasks with no dependencies
        phases = []
        current_phase = [self.tasks[tid] for tid, deg in in_degree.items() if deg == 0]

        while current_phase:
            phases.append(current_phase)

            # Find next phase
            next_phase = []
            for task in current_phase:
                task_id = task['id']
                for dependent_id in self.graph[task_id]:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        next_phase.append(self.tasks[dependent_id])

            current_phase = next_phase

        # Check for cycles (Fix #12: Better error message)
        if sum(in_degree.values()) > 0:
            # Find tasks that are part of cycle
            cycle_tasks = [tid for tid, deg in in_degree.items() if deg > 0]
            cycle_tasks_str = ", ".join(cycle_tasks)

            # Build dependency info for cycle tasks
            cycle_info = []
            for tid in cycle_tasks:
                deps = self.tasks[tid].get('dependencies', [])
                cycle_info.append(f"  - {tid} depends on: {deps}")

            raise ValueError(
                f"Dependency cycle detected in backlog!\n"
                f"Tasks involved in cycle: {cycle_tasks_str}\n"
                f"Dependency chain:\n" + "\n".join(cycle_info) + "\n"
                f"Fix: Remove circular dependencies between these tasks."
            )

        return phases
