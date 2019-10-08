# Gunicorn config
bind = ":" + str(PORT)
workers = 2
timeout = 300
