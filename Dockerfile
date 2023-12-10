# Dockerfile | Cannlytics Website
# Copyright (c) 2021-2023 Cannlytics
#
# Auhtors: Keegan Skeate <keegan@cannlytics.com>
# Created: 1/5/2021
# Updated: 9/10/2023
# License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

# Python setup.
FROM python:3.10-slim

# Environment Variables.
ENV APP=website \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=True \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    APP_HOME=/app

# General Installation: Python dependencies and set directory.
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt
WORKDIR $APP_HOME

# Install necessary packages.
# https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update && \
    apt-get install -y \
        tesseract-ocr \
        libtesseract-dev \
        gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils imagemagick libzbar0 zbar-tools libzbar-dev \
        wget && \
    wget http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_120.0.6099.71-1_amd64.deb && \
    dpkg -i google-chrome-stable_120.0.6099.71-1_amd64.deb; apt-get -fy install && \
    apt-get clean && rm -rf /var/lib/apt/lists/* 

# Verify zbar installation. (unnecessary?)
# RUN dpkg -L libzbar-dev; ls -l /usr/include/zbar.h

# Copy local code to the container image.
COPY . ./

# Use non-root user.
RUN useradd appuser && chown -R appuser /app
USER appuser

# Run the app.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 $APP.core.wsgi:application
