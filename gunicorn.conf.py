# Gunicorn configuration for JackStatz Basketball Tracker
# Optimized for Server-Sent Events (SSE) support

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 1  # Use only 1 worker for SSE to work properly
worker_class = "gevent"  # Essential for SSE support
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeout settings (important for SSE)
timeout = 30
keepalive = 30
graceful_timeout = 30

# Logging
loglevel = "info"
accesslog = "access.log"
errorlog = "error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "jackstatz"

# Server mechanics
daemon = False
pidfile = "jackstatz.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed later)
keyfile = None
certfile = None

# Application
wsgi_app = "app:app"

# Preload application for better performance
preload_app = True

# Worker process management
worker_tmp_dir = "/dev/shm"  # Use RAM for better performance

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'FLASK_DEBUG=False'
]

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("🏀 JackStatz server is ready to serve requests")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
