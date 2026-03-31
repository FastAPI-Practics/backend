import multiprocessing
import os

port = int(os.getenv('COMMON__PORT', '8000'))

bind = f'0.0.0.0:{port}'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
timeout = 30
graceful_timeout = 30
reload_app = True
preload_app = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
