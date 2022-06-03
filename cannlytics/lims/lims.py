"""
LIMS Client | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 12/10/2021
Updated: 12/10/2021
License: MIT License
"""
# Standard imports.
import logging

# External imports.
from json import dumps
from pandas import read_excel
from requests import Session

# Internal imports.
# from .constants import parameters, recall
# from .exceptions import MetrcAPIError
# from .models import *
# from .urls import *
# from ..utils.utils import clean_dictionary
from ..exceptions import CannlyticsAPIError


class LIMS(object):
    """An instance of this class communicates with the Metrc API."""

    def __init__(
            self,
            logs=True,
            test=True,
    ):
        """Initialize a Metrc API client.
        Args:
            logs (bool): Whether or not to log Metrc API requests, True by default.
            test (bool): Whether or not to use the test sandbox, True by default.
        """
        self.logs = logs
        self.test = test
        if logs:
            self.initialize_logs()

    def create_log(self, response):
        """Create a log given an HTTP response.
        Args:
            response (HTTPResponse): An HTTP request response.
        """
        try:
            self.logger.debug(f'Request: {response.request.method} {response.request.url}')
            self.logger.debug(f'Body: {response.request.body}')
            self.logger.debug(f'Status code: {response.status_code}')
            try:
                log = dumps(response.json())
                self.logger.debug(f'Response: {log}')
            except ValueError:
                self.logger.debug(f'Response: {response.text}')
        except KeyError:
            raise CannlyticsAPIError({'message': '`logs=True` but no logger initialized. Use `client.initialize_logs()`.'})

    def initialize_logs(self):
        """Initialize Metrc logs."""
        logging.getLogger('lims').handlers.clear()
        logging.basicConfig(
            filename='./tmp/cannlytics.log',
            filemode='w+',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        self.logger = logging.getLogger('lims')
        self.logger.addHandler(console)

    #------------------------------------------------------------------
    # Analyses
    #------------------------------------------------------------------

    # TODO: get_analysis, get_analyses, create_analysis, update_analysis,
    # create_analyses, update_analyses, delete_analysis

    #------------------------------------------------------------------
    # Analytes
    #------------------------------------------------------------------

    # TODO: get_analyte, get_analytes, create_analyte, update_analyte,
    # create_analytes, update_analytes, delete_analyte

    #------------------------------------------------------------------
    # Areas?
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Calculations?
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Data
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Instruments
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Measurements
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Projects
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Results
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Samples
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Transfers
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # Worksheets? Templates?
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # QC? Stats?
    #------------------------------------------------------------------