# Dockerfile for Django Applications
# Section 1- Base Image
FROM python:3.7-slim
# Section 2- Python Interpreter Flags
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
# Section 3- Compiler and OS libraries
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev python3-dev default-libmysqlclient-dev python-dev \
  && rm -rf /var/lib/apt/lists/*
# Section 4- Project libraries and User Creation
RUN pip install mysqlclient
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -rf /tmp/requirements.txt \
    && useradd -U meeran \
    && install -d -m 0755 -o meeran -g meeran ./app/staticfiles
# Section 5- Code and User Setup
ADD ./ /app
WORKDIR /app
USER meeran:meeran
COPY --chown=meeran:meeran . /app
RUN chmod +x ./*.sh
# Section 6- Docker Run Checks and Configurations
ENTRYPOINT [ "./entrypoint.sh" ]
CMD [ "./start.sh", "server" ]