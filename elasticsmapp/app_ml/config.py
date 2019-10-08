from os import environ as env

PORT = int(env.get("PORT", 8080))

# Gunicorn config
bind = ":" + str(PORT)
workers = 1
timeout = 600
