# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim
# FROM python:3.8-slim-buster

# Specificy directory.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install dependencies.
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy local code to the container image.
COPY . ./

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Setting this ensures print statements and log messages
# promptly appear in Cloud Logging.
ENV PYTHONUNBUFFERED True

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 console.core.wsgi:application
# CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 console.wsgi:application
