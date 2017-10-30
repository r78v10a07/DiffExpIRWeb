#!/bin/bash

python3 ./bin/manage.py migrate                  # Apply database migrations
python3 ./bin/manage.py migrate main
python3 ./bin/manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
touch ./logs/gunicorn.log
touch ./logs/access.log
tail -n 0 -f ./logs/*.log &

# Start Gunicorn processes
echo "Starting Gunicorn."
exec gunicorn project.wsgi:application \
    --name diffexpirweb \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/access.log \
    "$@"
