import multiprocessing
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
threads = 2
worker_class = 'gthread'

# Memory leak prevention & worker recycling
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
