# Gunicorn configuration for production
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/gunicorn/ycsmp_access.log"
errorlog = "/var/log/gunicorn/ycsmp_error.log"
loglevel = "info"

# Process naming
proc_name = "ycsmp_gunicorn"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/ycsmp.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn level)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"