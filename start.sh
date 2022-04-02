#!/bin/bash


if [ $# -eq 0 ]; then
    echo "Usage: start.sh [PROCESS_TYPE](server/beat/worker)"
    exit 1
fi

PROCESS_TYPE=$1

if [ "$PROCESS_TYPE" = "server" ]; then
    if [ "$DJANGO_DEBUG" = "true" ]; then
        daphne -b 0.0.0.0 doodhwaley.asgi:application
    else
        daphne -b 0.0.0.0 doodhwaley.asgi:application
    fi
elif [ "$PROCESS_TYPE" = "beat" ]; then
        celery -A doodhwaley beat -l debug --scheduler django_celery_beat.schedulers:DatabaseScheduler --pidfile /tmp/celerybeat.pid
elif [ "$PROCESS_TYPE" = "worker" ]; then
        celery -A doodhwaley worker -l debug
fi