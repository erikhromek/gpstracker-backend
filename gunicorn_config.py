workers = 4
bind = "0.0.0.0:8000"
chdir = "/opt/gpstracker-backend/"
module = "app.wsgi:application"
loglevel = "warning"
timeout = "60"
worker_class = "gevent"
