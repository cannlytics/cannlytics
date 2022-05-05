"""
Django Server | Cannlytics Console
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/19/2021
Updated: 12/19/2021
License: License: MIT License <https://github.com/cannlytics/cannlytics-console/blob/main/LICENSE>

Description: A simple server to serve the main Django app.
"""
# External imports.
from waitress import serve

# Internal imports.
from core.wsgi import application

if __name__ == '__main__':
    serve(application, host='127.0.0.1', port=8000)
