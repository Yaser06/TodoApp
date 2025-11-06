"""
SSE Manager - Server-Sent Events for real-time updates
"""
import json
import queue
import time


class SSEManager:
    """Manages Server-Sent Events for real-time client updates"""

    def __init__(self):
        self.clients = []

    def add_client(self, q):
        """Add a new SSE client"""
        self.clients.append(q)

    def remove_client(self, q):
        """Remove disconnected client"""
        if q in self.clients:
            self.clients.remove(q)

    def notify_all(self, event_type, data):
        """Notify all connected clients of an event"""
        dead_clients = []

        for q in self.clients:
            try:
                q.put({
                    'event': event_type,
                    'data': data,
                    'timestamp': time.time()
                }, timeout=1)
            except (queue.Full, Exception):
                # Client is dead or slow
                dead_clients.append(q)

        # Clean up dead clients
        for q in dead_clients:
            self.remove_client(q)

    def stream(self):
        """SSE generator function"""
        q = queue.Queue(maxsize=50)
        self.add_client(q)

        try:
            # Send initial heartbeat
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"

            while True:
                try:
                    # Wait for message or heartbeat
                    msg = q.get(timeout=30)

                    event = msg.get('event', 'message')
                    data = msg.get('data', {})

                    yield f"event: {event}\ndata: {json.dumps(data)}\n\n"

                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"event: heartbeat\ndata: {json.dumps({'ping': time.time()})}\n\n"

        except GeneratorExit:
            # Client disconnected
            pass
        finally:
            self.remove_client(q)
