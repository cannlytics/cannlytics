"""
Cannlytics Module | Cannlytics
Copyright (c) 2021-2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/5/2021
Updated: 8/13/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: This module contains the Cannlytics class,
the entry point into Cannlytics features and functionality.
"""
# Standard imports.
from datetime import datetime
import logging
import os
import tempfile
from typing import Dict, Optional, Union

# External imports
from dotenv import dotenv_values

# Internal imports.
from cannlytics.firebase import initialize_firebase
from cannlytics.metrc import initialize_metrc


class Cannlytics:
    """An instance of this class is the entry point to interface with
    the core Cannlytics logic."""

    def __init__(
            self,
            config: Optional[Union[Dict, str]] = './.env',
            license_number: Optional[str] = None,
            state: Optional[str] = None,
            firebase: Optional[bool] = False,
            metrc: Optional[bool] = False,
            openai: Optional[bool] = False,
            logs: Optional[bool] = True,
            name: Optional[str] = 'cannlytics',
    ) -> None:
        """Initialize a Cannlytics class.
        Args:
            config (str, dict): A .env file or configuration with variables:
                `GOOGLE_APPLICATION_CREDENTIALS`
                `LICENSE_NUMBER`
                `METRC_VENDOR_API_KEY`
                `METRC_USER_API_KEY`
                `METRC_STATE`
                `OPENAI_API_KEY`
            license_number (str): A primary license number (optional).
            state (str): A state abbreviation (optional).
            firebase (bool): Initialize the Firebase module, default `False` (optional).
            metrc (bool): Initialize the Metrc module, default `False` (optional).
            openai (bool): Initialize the OpenAI module, default `False` (optional).
            logs (bool): Initialize the logs, default `True` (optional).
            name (str): The name of the log file, default `cannlytics` (optional).
        """
        # Initialize the Cannlytics class state.
        if isinstance(config, dict):
            self.config = config
        else:
            self.config = dotenv_values(config)
        self.database = None
        self.license = self.config.get('LICENSE_NUMBER', license_number)
        self.state = self.config.get('METRC_STATE', state)
        self.storage = None
        self.track = None

        # Initialize logs.
        if logs:
            self.initialize_logs(name=name)

        # Initialize Firebase.
        if firebase:
            self.initialize_firebase(self.config)

        # Initialize Metrc.
        if metrc:
            self.initialize_traceability(
                self.config,
                primary_license=self.license,
                state=self.state
            )

        # Initialize OpenAI.
        if openai:
            self.initialize_openai(self.config.get('OPENAI_API_KEY'))


    def create_log(self, message: str):
        """Create a log.
        Args:
            (message): Print a given message to the logs.
        """
        try:
            self.logger.debug(str(message))
        except KeyError:
            raise ValueError({'message': '`logs=True` but no logger initialized. Use `client.initialize_logs()`.'})


    def initialize_logs(self, name: Optional[str] = 'cannlytics'):
        """Initialize logs with a timestamped temp file."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'{name}-{timestamp}.log')
        logging.getLogger(name).handlers.clear()
        logging.basicConfig(
            filename=temp_file,
            filemode='w+',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        self.logger = logging.getLogger(name)
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
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials
        self.database = initialize_firebase()
        self.storage = config.get('FIREBASE_STORAGE_BUCKET')
        # TODO: Map all firebase function to cannlytics.<function_name>, passing DB as an argument.
        self.create_log('Firebase client initialized.')
        return self.database
    

    def initialize_openai(self, openai_api_key=None):
        """Initialize OpenAI with Google Secret Manager or .env variable."""
        import openai
        if openai_api_key is None:
            try:
                import google.auth
                from cannlytics.firebase import access_secret_version
                self.initialize_firebase()
                _, project_id = google.auth.default()
                openai_api_key = access_secret_version(
                    project_id=project_id,
                    secret_id='OPENAI_API_KEY',
                    version_id='latest',
                )
            except:
                openai_api_key = self.config.get('OPENAI_API_KEY')
        openai.api_key = openai_api_key
        self.create_log('OpenAI initialized.')


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
        self.create_log('Traceability client initialized.')
        return self.track


    # TODO: Make data and statistics readily available through
    # the main Cannlytics class.
