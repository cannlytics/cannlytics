"""
Cannlytics Module | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 11/5/2021
Updated: 1/10/2022
License: <https://github.com/cannlytics/cannlytics-engine/blob/main/LICENSE>

Description: This module contains the Cannlytics class,
the entry point into Cannlytics features and functionality.
"""
# Standard imports.
import logging
from os import environ
from typing import Dict, Optional # List, Type, Union

# External imports
from dotenv import dotenv_values

# Internal imports.
from .firebase import initialize_firebase
from .metrc import initialize_metrc


class Cannlytics:
    """An instance of this class is the entry point the top-level Cannlytics logic."""

    def __init__(self, config: Optional[Dict], env_file: str = './.env') -> None:
        """Initialize a Cannlytics class.
        Args:
            config (dict): Configuration options, including: `GOOGLE_APPLICATION_CREDENTIALS`,
                `METRC_VENDOR_API_KEY`, `METRC_USER_API_KEY`, and `METRC_STATE`.
            env_file (str): An optional .env file path to use instead of config.
        """
        if isinstance(config, dict):
            self.config = config
        else:
            self.config = dotenv_values(env_file)
        self.database = None
        self.license = None
        self.state = None
        self.storage = None
        self.track = None
        self.initialize_logs()
        # TODO: Initialize Firebase and Metrc by default?

    # Optional: Reduce duplication of logging code in the Metrc module?
    def create_log(self, message: str):
        """Create a log.
        Args:
            (message): Print a given message to the logs.
        """
        self.logger.debug(message)

    def initialize_logs(self):
        """Initialize logs.
        """
        logging.getLogger('cannlytics').handlers.clear()
        logging.basicConfig(
            filename='./tmp/cannlytics.log',
            filemode='w+',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        self.logger = logging.getLogger('cannlytics')
        self.logger.addHandler(console)

    def initialize_firebase(self, config: Optional[Dict] = None):
        """Initialize a Firebase account for back-end, cloud services.
        Args:
            config (dict): Optional configuration options to override any
                options provided to the Cannlytics class instance.
        Returns:
            (Client): A Firestore database client instance.
        """
        if config is None:
            config = self.config
        credentials = config['GOOGLE_APPLICATION_CREDENTIALS']
        environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
        self.database = initialize_firebase()
        self.storage = config.get('FIREBASE_STORAGE_BUCKET')
        # TODO: Map all firebase function to cannlytics.<function_name>, passing DB as an argument.
        self.create_log('Firebase client initialized.')
        return self.database

    def initialize_traceability(self, config=None, primary_license=None, state=None):
        """Initialize the traceability client.
        Args:
            config (dict): The configuration for the traceability client.
            primary_license (str): A primary license to initialize the traceability client.
        """
        if config is None:
            config = self.config
        if state is None:
            state = config.get('METRC_STATE', 'ca')
        self.track = initialize_metrc(
            vendor_api_key=config['METRC_VENDOR_API_KEY'],
            user_api_key=config['METRC_USER_API_KEY'],
            primary_license=primary_license,
            state=state,
        )
        return self.track
