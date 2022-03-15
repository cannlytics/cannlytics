# Dockerfile | Cannlytics Website
# Copyright (c) 2021-2022 Cannlytics
#
# Auhtors: Keegan Skeate <keegan@cannlytics.com>
# Created: 1/5/2021
# Updated: 1/10/2022
# License: MIT License <https://github.com/cannlytics/cannlytics-website/blob/main/LICENSE>

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim-buster

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Keeps Python from generating .pyc files in the container.
ENV PYTHONDONTWRITEBYTECODE 1

# Setting this ensures that print statements and log messages
# promptly appear in Cloud Logging.
ENV PYTHONUNBUFFERED True

# Install dependencies.
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Specificy directory.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy local code to the container image.
COPY . ./

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# Run the web service on container startup. Here we use the gunicorn
# webserver, with 4 worker process (1 by default) and 16 threads (8 by default).
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# See:
# https://docs.gunicorn.org/en/stable/design.html#how-many-workers
# https://docs.gunicorn.org/en/stable/design.html#how-many-threads
CMD exec gunicorn --bind :$PORT --workers 4 --threads 16 --timeout 120 website.core.wsgi:application
