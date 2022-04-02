web: daphne doodhwaley.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channel_layer -v2
celery-worker: celery -A doodhwaley worker -l info
celery-beat: celery -A doodhwaley beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler