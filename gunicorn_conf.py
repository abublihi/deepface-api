import os

# Bind address
bind = "0.0.0.0:8000"

# Number of worker processes (configurable via environment variable)
workers = int(os.getenv("GUNICORN_WORKERS", "2"))

# Worker timeout in seconds
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))

# Worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Preload app for better performance
preload_app = True

# Graceful timeout
graceful_timeout = 30

# Keep alive
keepalive = 5
