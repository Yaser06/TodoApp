"""
File Watcher - Monitor backlog.yaml for changes
"""
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class BacklogFileHandler(FileSystemEventHandler):
    """Handler for backlog.yaml file changes"""

    def __init__(self, file_path, callback):
        self.file_path = Path(file_path)
        self.callback = callback
        self.last_modified = 0

    def on_modified(self, event):
        """Called when file is modified"""
        if event.is_directory:
            return

        # Check if it's our file
        if Path(event.src_path).resolve() == self.file_path.resolve():
            import time
            current_time = time.time()

            # Debounce (avoid duplicate events)
            if current_time - self.last_modified > 0.5:
                self.last_modified = current_time
                self.callback()


def start_file_watcher(file_path, callback):
    """Start watching file for changes"""
    file_path = Path(file_path)

    event_handler = BacklogFileHandler(file_path, callback)
    observer = Observer()
    observer.schedule(event_handler, str(file_path.parent), recursive=False)

    # Start in background thread
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()

    return observer
