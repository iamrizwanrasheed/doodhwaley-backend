# Dockerfile for Django Applications
# Section 1- Base Image
FROM python:3.9-slim
# Section 2- Python Interpreter Flags
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG False
ENV DJANGO_SETTINGS_MODULE doodhwaley.settings
# Section 3- Working Directory
WORKDIR /app
# Section 4- System Dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        libpq-dev \
        python3-dev \
        pkg-config \
        gcc \
    && rm -rf /var/lib/apt/lists/*
# Section 5- Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Section 6- Copy Project
COPY . .
# Section 7- Make Shell Scripts Executable
RUN if [ -f "build_files.sh" ]; then chmod +x build_files.sh; fi
RUN if [ -f "entrypoint.sh" ]; then chmod +x entrypoint.sh; fi
RUN if [ -f "start.sh" ]; then chmod +x start.sh; fi
# Section 8- Create Static Directory
RUN mkdir -p staticfiles
# Section 9- Collect Static Files with Environment Variables
RUN DJANGO_SETTINGS_MODULE=doodhwaley.settings \
    DEBUG=False \
    SECRET_KEY=dummy-key-for-collectstatic \
    python manage.py collectstatic --noinput
# Section 10- Expose Port
EXPOSE 8000
# Section 11- Command
CMD gunicorn doodhwaley.wsgi:application --bind 0.0.0.0:$PORT