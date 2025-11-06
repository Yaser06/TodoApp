#!/usr/bin/env python3
"""
Task Board Backend - Minimal Flask + SSE
Auto-detects available port (9090-9099)
"""
import os
import socket
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from file_manager import TaskFileManager
from sse import SSEManager
from watcher import start_file_watcher

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Global managers
sse_manager = SSEManager()
file_manager = None


def find_available_port(start_port=9090, end_port=9099):
    """Find first available port in range"""
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            if result != 0:  # Port is available
                return port
        except:
            continue

    raise RuntimeError(f"No available ports in range {start_port}-{end_port}")


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "task-board"}), 200


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        data = file_manager.read_tasks()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task (user-created)"""
    try:
        new_task = request.json

        # Add metadata
        new_task['source'] = 'manual'
        new_task['status'] = 'backlog'

        # Read current tasks
        data = file_manager.read_tasks()

        # Generate ID - check ALL columns for existing IDs
        all_tasks = []
        for column in ['backlog', 'inProgress', 'blocked', 'done']:
            all_tasks.extend(data.get(column, []))

        # Extract numeric IDs and find max
        existing_nums = []
        for t in all_tasks:
            task_id = t.get('id', '')
            if task_id.startswith('T') and len(task_id) > 1:
                try:
                    num = int(task_id[1:])
                    existing_nums.append(num)
                except ValueError:
                    continue

        # Generate next ID
        next_id = max(existing_nums) + 1 if existing_nums else 1
        task_id = f"T{next_id:03d}"
        new_task['id'] = task_id

        # Add to backlog
        if 'backlog' not in data:
            data['backlog'] = []
        data['backlog'].append(new_task)

        # Write back
        file_manager.write_tasks(data)

        # Notify SSE clients
        sse_manager.notify_all('task_created', new_task)

        return jsonify(new_task), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task (only if not in progress OR manual)"""
    try:
        updates = request.json
        data = file_manager.read_tasks()

        # Find task and its column
        task = None
        task_column = None
        for column in ['backlog', 'inProgress', 'done']:
            tasks = data.get(column, [])
            for t in tasks:
                if t.get('id') == task_id:
                    task = t
                    task_column = column
                    break
            if task:
                break

        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Only allow updates if task is NOT in inProgress column OR is manual
        if task_column == 'inProgress' and task.get('source') != 'manual':
            return jsonify({"error": "Cannot update task in progress (AI owns it)"}), 403

        # Update task
        task.update(updates)

        # If task was in DONE, move it back to BACKLOG (so AI can re-process)
        if task_column == 'done':
            # Remove from done
            data['done'] = [t for t in data.get('done', []) if t.get('id') != task_id]

            # Add to backlog
            if 'backlog' not in data:
                data['backlog'] = []
            data['backlog'].append(task)

        # Write back
        file_manager.write_tasks(data)

        # Notify SSE clients
        sse_manager.notify_all('task_updated', task)

        return jsonify(task), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tasks/<task_id>/priority', methods=['PATCH'])
def change_priority(task_id):
    """Change task priority"""
    try:
        new_priority = request.json.get('priority')
        data = file_manager.read_tasks()

        # Find and update
        for column in ['backlog', 'inProgress', 'done']:
            tasks = data.get(column, [])
            for task in tasks:
                if task.get('id') == task_id:
                    # Don't allow priority change for in-progress AI tasks
                    if task.get('status') == 'inProgress' and task.get('source') != 'manual':
                        return jsonify({"error": "Cannot change priority of running task"}), 403

                    task['pri'] = new_priority
                    file_manager.write_tasks(data)
                    sse_manager.notify_all('priority_changed', task)
                    return jsonify(task), 200

        return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/stream')
def stream():
    """SSE endpoint for real-time updates"""
    return sse_manager.stream(), 200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    }


@app.route('/')
def serve_frontend():
    """Serve React frontend"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)


def on_file_change():
    """Callback when backlog.yaml changes"""
    try:
        data = file_manager.read_tasks()
        sse_manager.notify_all('file_changed', data)
    except Exception as e:
        print(f"Error reading file on change: {e}", file=sys.stderr)


def main():
    global file_manager

    # Find available port
    try:
        port_range = os.environ.get('PORT_RANGE', '9090-9099')
        start, end = map(int, port_range.split('-'))
        port = find_available_port(start, end)
    except:
        port = 9090

    # Get backlog path
    backlog_path = Path(os.environ.get('BACKLOG_PATH', '../../memory-bank/work/backlog.yaml'))

    # Initialize file manager
    file_manager = TaskFileManager(backlog_path)

    # Start file watcher
    start_file_watcher(backlog_path, on_file_change)

    # Print startup info
    print("=" * 60)
    print("🚀 Task Board Started")
    print("=" * 60)
    print(f"📍 URL: http://localhost:{port}")
    print(f"📊 Monitoring: {backlog_path}")
    print(f"💡 Tip: Open browser and watch tasks in real-time!")
    print("=" * 60)
    print()

    # Run server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()
