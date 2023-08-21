# Dockerfile | Cannlytics Website
# Copyright (c) 2021-2023 Cannlytics
#
# Auhtors: Keegan Skeate <keegan@cannlytics.com>
# Created: 1/5/2021
# Updated: 7/5/2023
# License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

#------------------------------------------------------------------
# Python setup.
#------------------------------------------------------------------

# Use the official lightweight Python image.
# Images: https://hub.docker.com/_/python
# See: https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# TODO: Define The main Django application.
ENV APP website

# Listen to $PORT environment variable.
# Note: This default value facilitates local development.
ENV PORT 8080

# Keep Python from generating .pyc files in the container.
ENV PYTHONDONTWRITEBYTECODE 1

# Ensure print statements and log messages promptly appear in Cloud Logging.
ENV PYTHONUNBUFFERED True

#------------------------------------------------------------------
# Dependencies installation.
# Uncomment to supercharge with web automation, OCR, and QR codes.
# TODO: Can any of these commands be combined for faster publishing?
#------------------------------------------------------------------

# Install Chrome (to use Selenium for web automation).
RUN apt-get update && \
    apt-get install wget -y && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install C libraries (for image proecssing).
RUN apt-get update && \
    apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils imagemagick libzbar0

# Install `zbar` and set its required environment variables (for QR codes).
RUN apt-get update && apt-get install -y zbar-tools libzbar-dev
RUN dpkg -L libzbar-dev; ls -l /usr/include/zbar.h
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

#------------------------------------------------------------------
# General installation.
#------------------------------------------------------------------

# Install Python dependencies.
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Specificy the app directory.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy local code to the container image.
COPY . ./

# Switch to a non-root user.
# See: https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

#------------------------------------------------------------------
# Run the app.
#------------------------------------------------------------------

# Run the web service on container startup.
# For environments with multiple CPU cores, you can increase
# the number of workers to be equal to the cores available.
# See: https://docs.gunicorn.org/en/stable/design.html
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 16 --timeout 120 $APP.core.wsgi:application
