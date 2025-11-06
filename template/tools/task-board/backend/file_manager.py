"""
File Manager - Safe YAML read/write with file locking
"""
import fcntl
import time
import yaml
from pathlib import Path


class TaskFileManager:
    """Manages backlog.yaml with file locking for concurrent access"""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.lock_file = self.file_path.with_suffix('.lock')

        # Ensure file exists
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize_file()

    def _initialize_file(self):
        """Initialize empty backlog.yaml"""
        initial_data = {
            'backlog': [],
            'inProgress': [],
            'blocked': [],
            'done': [],
            'flushThreshold': 10,
            'pendingChanges': 0,
            'updatedAt': time.strftime('%Y-%m-%d'),
            'updatedBy': '@agent'
        }
        self.file_path.write_text(yaml.dump(initial_data))

    def read_tasks(self):
        """Read tasks with shared lock (multiple readers OK)"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.lock_file.open('a') as lock:
                    # Shared lock - multiple readers allowed
                    fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
                    try:
                        text = self.file_path.read_text(encoding='utf-8')
                        data = yaml.safe_load(text) or {}
                        return data
                    finally:
                        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            except BlockingIOError:
                # Lock is held, wait and retry
                time.sleep(0.1 * (attempt + 1))
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1 * (attempt + 1))

        raise TimeoutError("Could not acquire read lock after retries")

    def write_tasks(self, data):
        """Write tasks with exclusive lock (single writer)"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with self.lock_file.open('a') as lock:
                    # Exclusive lock - only one writer, blocks readers
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                    try:
                        # Update timestamp
                        data['updatedAt'] = time.strftime('%Y-%m-%d %H:%M:%S')

                        # Write to temp file first (atomic write)
                        temp_file = self.file_path.with_suffix('.tmp')
                        yaml_content = yaml.dump(
                            data,
                            default_flow_style=False,
                            allow_unicode=True,
                            sort_keys=False,
                            encoding='utf-8'
                        ).decode('utf-8')
                        temp_file.write_text(yaml_content, encoding='utf-8')

                        # Atomic replace
                        temp_file.replace(self.file_path)
                    finally:
                        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

                return True
            except BlockingIOError:
                time.sleep(0.1 * (attempt + 1))
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.1 * (attempt + 1))

        raise TimeoutError("Could not acquire write lock after retries")
