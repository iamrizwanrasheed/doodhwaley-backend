#!/bin/bash
# entrypoint.sh file of Dockerfile
# Section 1- Bash options
set -o errexit
set -o pipefail
set -o nounset

mysql_ready() {
    python << END
import sys
import MySQLdb

try:
    db = MySQLdb.connect(host="${DJANGO_MYSQL_HOST}",    # your host, usually localhost
                        user="${DJANGO_MYSQL_USER}",         # your username
                        passwd="${DJANGO_MYSQL_PASSWORD}",  # your password
                        db="${DJANGO_MYSQL_DATABASE}")        # name of the data base
    db.close()
except MySQLdb.OperationalError:
    sys.exit(-1)
END
}

redis_ready() {
    python << END
import sys
from redis import Redis
from redis import RedisError
try:
    redis = Redis.from_url("${CELERY_BROKER_URL}", db=0)
    redis.ping()
except RedisError:
    sys.exit(-1)
END
}
# until mysql_ready; do
#     echo "Waiting for the MySQL Server"
#     sleep 3
# done
>&2 echo "Mysql available"
# until redis_ready; do
#   >&2 echo "Waiting for Redis to become available..."
#   sleep 5
# done
>&2 echo "Redis is available"
# Section 3- Idempotent Django commands
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
exec "$@"