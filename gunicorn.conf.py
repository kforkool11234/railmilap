import multiprocessing

# Server socket settings
bind = "0.0.0.0:5000"
backlog = 1024  # Reduced from 2048

# Worker processes
worker_class = "eventlet"
workers = 1
worker_connections = 750  # Reduced from 1000
timeout = 120  # Reduced from 300
keepalive = 2

# Process naming
proc_name = "gunicorn_flask_socket"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Memory optimization
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Process management
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}