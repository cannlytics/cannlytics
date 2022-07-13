"""
Cannlytics Module | Cannlytics
Copyright (c) 2021-2022 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/5/2021
Updated: 7/12/2022
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: This module contains the Cannlytics class,
the entry point into Cannlytics features and functionality.
"""
# Standard imports.
import logging
from os import environ
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
            lims: Optional[bool] = False,
            metrc: Optional[bool] = False,
            paypal: Optional[bool] = False,
            quickbooks: Optional[bool] = False,
    ) -> None:
        """Initialize a Cannlytics class.
        Args:
            config (str, dict): A .env file or configuration with variables:
                `GOOGLE_APPLICATION_CREDENTIALS`
                `LICENSE_NUMBER`
                `METRC_VENDOR_API_KEY`
                `METRC_USER_API_KEY`
                `METRC_STATE`
            license_number (str): A primary license number (optional).
            state (str): A state abbreviation (optional).
            firebase (bool): Initialize the Firebase module, default `False` (optional).
            lims (bool): Initialize the LIMS module, default `False` (optional).
            metrc (bool): Initialize the Metrc module, default `False` (optional).
            paypal (bool): Initialize the PayPal module, default `False` (optional).
            quickbooks (bool): Initialize the QuickBooks module, default `False` (optional).
        """
        if isinstance(config, dict):
            self.config = config
        else:
            self.config = dotenv_values(config)
        self.database = None
        self.license = self.config.get('LICENSE_NUMBER', license_number)
        self.state = self.config.get('METRC_STATE', state)
        self.storage = None
        self.track = None
        self.initialize_logs()
        # TODO: Test / ensure module initialization errors are skipped.
        if firebase:
            self.initialize_firebase(self.config)
        if metrc:
            self.initialize_traceability(
                self.config,
                primary_license=self.license,
                state=self.state
            )
        # TODO: Initialize modules if specified.
        # lims
        # paypal
        # quickbooks


    def create_log(self, message: str):
        """Create a log.
        Args:
            (message): Print a given message to the logs.
        """
        self.logger.debug(message)


    def initialize_logs(self):
        """Initialize logs.
        """
        # Optional: Reduce duplication of logging code (also in the Metrc module)?
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
        self.create_log('Traceability client initialized.')
        return self.track


    # Optional: Make `paypal` available through the interface?


    # Optional: Make `lims` available through the interface?


    # Optional: Make `quickbooks` available through the interface?
    

    # Optional: Make `charts` available through the interface?


    # Optional: Make `stats` available through the interface?


    # Optional: Make `utils` available through the interface?


    # Future work: Use models that have their own functions.


    # TODO: Make data and statistics readily available through
    # the main Cannlytics class.
