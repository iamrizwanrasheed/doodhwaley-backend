web: gunicorn doodhwaley.wsgi:application
worker: celery -A doodhwaley worker -l info
celery-beat: celery -A doodhwaley beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler