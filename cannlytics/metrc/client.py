"""
Metrc Client | Cannlytics
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 11/5/2021
Updated: 1/23/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

This module contains the `Metrc` class responsible for communicating
with the Metrc API.

TODO: Implement the remaining Metrc functionality:

    [ ] GET /transfers/v1/templates/{id}/transporters
    [ ] GET /transfers/v1/templates/{id}/transporters/details
    [ ] Implement return created/updated objects for all endpoints.

"""
# Standard imports.
from datetime import datetime
from json import dumps
import logging
import os
import tempfile

# External imports.
from pandas import read_excel
from requests import Session

# Internal imports.
from .constants import parameters, DEFAULT_HISTORY
from .exceptions import MetrcAPIError
from .models import (
    Delivery,
    Category,
    Employee,
    Facility,
    Item,
    Location,
    Harvest,
    Package,
    Patient,
    Plant,
    PlantBatch,
    LabResult,
    Receipt,
    Strain,
    Transfer,
    TransferTemplate,
    Transaction,
    Waste,
)
from .urls import (
    METRC_API_BASE_URL,
    METRC_API_BASE_URL_TEST,
    METRC_BATCHES_URL,
    METRC_EMPLOYEES_URL,
    METRC_FACILITIES_URL,
    METRC_LOCATIONS_URL,
    METRC_HARVESTS_URL,
    METRC_ITEMS_URL,
    METRC_LAB_RESULTS_URL,
    METRC_PACKAGES_URL,
    METRC_PATIENTS_URL,
    METRC_PLANTS_URL,
    METRC_RECEIPTS_URL,
    METRC_SALES_URL,
    METRC_STRAINS_URL,
    METRC_TRANSACTIONS_URL,
    METRC_TRANSFERS_URL,
    METRC_TRANSFER_PACKAGES_URL,
    METRC_TRANSFER_TEMPLATE_URL,
    METRC_UOM_URL,
)
from ..utils.utils import (
    camel_to_snake,
    clean_dictionary,
    get_timestamp,
)


class Metrc(object):
    """An instance of this class communicates with the Metrc API."""

    def __init__(
            self,
            vendor_api_key,
            user_api_key,
            logs=True,
            primary_license='',
            state='ma',
            test=True,
        ):
        """Initialize a Metrc API client.
        Args:
            vendor_api_key (str): Required Metrc API key, obtained from Metrc
                upon successful certification. The vendor API key is the
                software provider's secret used in every instance, regardless
                of location or licensee.
            user_api_key (str): Required user secret obtained
                from a licensee's Metrc user interface. The user's permissions
                determine the level of access to the Metrc API.
            logs (bool): Whether or not to log Metrc API requests, True by default.
            primary_license (str): A license to use if no license is provided
                on individual requests.
            state (str): The state of the licensee, Oklahoma (ok) by default.
            test (bool): Whether or not to use the test sandbox, True by default.

        Example:

        ```py
        track = metrc.Client(
            vendor_api_key='abc',
            user_api_key='xyz',
            primary_license='123',
            state='ma'
        )
        ```
        """
        self.logs = logs
        self.parameters = parameters
        self.primary_license = primary_license
        self.default_time_period = DEFAULT_HISTORY
        self.state = state
        self.test = test
        self.user_api_key = user_api_key
        self.vendor_api_key = vendor_api_key
        self.session = Session()
        self.session.auth = (vendor_api_key, user_api_key)
        if test:
            self.base = METRC_API_BASE_URL_TEST % state
        else:
            self.base = METRC_API_BASE_URL % state
        if logs:
            self.initialize_logs()


    def request(
            self,
            method,
            endpoint,
            data=None,
            params=None,
        ):
        """Make a request to the Metrc API."""
        url = self.base + endpoint
        try:
            response = getattr(self.session, method)(url, json=data, params=params)
        except ConnectionError:
            self.session = Session()
            self.session.auth = (self.vendor_api_key, self.user_api_key)
            response = getattr(self.session, method)(url, json=data, params=params)
        if self.logs:
            self.create_log(response)
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                return response.text
        else:
            raise MetrcAPIError(response)
    

    def format_params(self, **kwargs):
        """Format Metrc request parameters.
        Returns:
            (dict): Returns the parameters as a dictionary.
        """
        params = {}
        for param in kwargs:
            if kwargs[param]:
                key = self.parameters[param]
                params[key] = kwargs[param]
        return params


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
            raise MetrcAPIError({'message': '`logs=True` but no logger initialized. Use `client.initialize_logs()`.'})


    def initialize_logs(self):
        """Initialize Metrc logs."""
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'cannlytics-{timestamp}.log')
        logging.getLogger('metrc').handlers.clear()
        logging.basicConfig(
            filename=temp_file,
            filemode='w+',
            level=logging.DEBUG,
            format='%(asctime)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger = logging.getLogger('metrc')
        self.logger.addHandler(handler)
        self.logger.debug('Metrc initialized.')


    #-------------------------------------------------------------------
    # Facilities and employees
    #-------------------------------------------------------------------

    def get_facilities(self):
        """Get all facilities."""
        url = METRC_FACILITIES_URL
        response = self.request('get', url)
        return [Facility(self, x) for x in response]


    def get_facility(self, license_number=''):
        """Get a given facility by its license number."""
        url = METRC_FACILITIES_URL
        response = self.request('get', url)
        facility = None
        facilities = [Facility(self, x) for x in response]
        for obs in facilities:
            if obs.license_number == license_number:
                facility = obs
                break
        return facility
    

    def get_employees(self, license_number=''):
        """Get all employees.
        Args:
            license_number (str): A licensee's license number.
        """
        url = METRC_EMPLOYEES_URL
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        return [Employee(self, x) for x in response]


    #-------------------------------------------------------------------
    # Deliveries
    #-------------------------------------------------------------------

    def create_deliveries(self, data, license_number='', return_obs=False):
        """Create home deliver(ies).
        Args:
            data (list): A list of deliveries (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % 'deliveries'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Return created deliveries.


    def get_deliveries(
            self,
            uid='',
            action='active',
            license_number='',
            start='',
            end='',
            sales_start='',
            sales_end='',
        ):
        """Get sale(s).
        Args:
            uid (str): The UID for a delivery.
            action (str): The action to apply to the delivery, with options:
                `active` or `inactive`.
            license_number (str): A specific license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the last modified time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the last modified time.
            sales_start (str): An ISO 8601 formatted string to restrict the start
                by the sales time.
            sales_end (str): An ISO 8601 formatted string to restrict the end
                by the sales time.
        Returns:
            (list): Returns a list of Receipts.
        """
        if uid:
            url = METRC_SALES_URL % f'delivery/{uid}'
        else:
            url = METRC_SALES_URL % f'deliveries/{action}'
        params = self.format_params(
            license_number=license_number or self.primary_license,
            start=start,
            end=end,
            sales_start=sales_start,
            sales_end=sales_end,
        )
        response = self.request('get', url, params=params)
        try:
            return Receipt(self, response, license_number)
        except AttributeError:
            return [Receipt(self, x, license_number) for x in response]


    def get_return_reasons(self, license_number=''):
        """Get the possible return reasons for home delivery items.
        Args:
            license_number (str): A specific license number.
        Returns:
            (list): A list of return reasons.
        """
        url = METRC_SALES_URL % 'delivery/returnreasons'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def complete_deliveries(self, data, license_number='', return_obs=False):
        """Complete home delivery(ies).
        Args:
            data (list): A list of deliveries (dict) to complete.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % 'deliveries/complete'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)


    def delete_delivery(self, uid, license_number=''):
        """Delete a home delivery.
        Args:
            uid (str): The UID of a home delivery to delete.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % f'delivery/{uid}'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    def update_deliveries(self, data, license_number=''):
        """Update home delivery(ies).
        Args:
            data (list): A list of deliveries (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % 'deliveries'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)


    #-------------------------------------------------------------------
    # Harvests
    #-------------------------------------------------------------------

    def get_harvests(
            self,
            uid='',
            action='active',
            license_number='',
            start='',
            end='',
        ):
        """Get harvests.
        Args:
            uid (str): The UID of a harvest, takes precedent over action.
            action (str): A specific filter to apply, including:
                `active`, `onhold`, `inactive`, `waste/types`.
            license_number (str): The licensee's license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the last modified time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the last modified time.
        """
        if uid:
            url = METRC_HARVESTS_URL % uid
        else:
            url = METRC_HARVESTS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license, start=start, end=end)
        response = self.request('get', url, params=params)
        try:
            return Harvest(self, response, license_number)
        except AttributeError:
            try:
                return [Harvest(self, x, license_number) for x in response]
            except AttributeError:
                return response


    def finish_harvests(self, data, license_number='', return_obs=False):
        """Finish harvests.
        Args:
            data (list): A list of harvests (dict) to finish.
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'finish'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)


    def unfinish_harvests(self, data, license_number='', return_obs=False):
        """Unfinish harvests.
        Args:
            data (list): A list of harvests (dict) to unfinish.
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'unfinish'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)


    def remove_waste(self, data, license_number='', return_obs=False):
        """Remove's waste from a harvest.
        Args:
            data (list): A list of waste (dict) to unfinish.
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'removewaste'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)


    def move_harvests(self, data, license_number='', return_obs=False):
        """Move a harvests.
        Args:
            data (list): A list of harvests (dict) to move.
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'move'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)


    def create_harvest_packages(self, data, license_number='', return_obs=False):
        """Create packages from a harvest.
        Args:
            data (list): A list of packages (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'create/packages'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return packages created.


    def create_harvest_testing_packages(self, data, license_number='', return_obs=False):
        """Create packages from a harvest for testing.
        Args:
            data (list): A list of testing packages (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'create/packages/testing'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return packages created.


    #-------------------------------------------------------------------
    # Items
    #-------------------------------------------------------------------

    def get_item_categories(self, license_number=''):
        """Get all item categories.
        Args:
            license_number (str): A specific license number.
        Returns:
            (list): Returns a list of item categories (Category).
        """
        url = METRC_ITEMS_URL % 'categories'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return [Category(self, x, license_number) for x in response]
        except AttributeError:
            return response


    def get_item(
            self,
            uid='',
            action='active',
            license_number='',
        ):
        """Get an item.
        Args:
            uid (str): The UID of an item.
            action (str): A specific type of item to filter by:
                `active`, `categories`, `brands`.
            license_number (str): A specific license number.
        Returns:
            (Item): Returns a an item.
        """
        response = self.get_items(uid, action=action, license_number=license_number)
        try:
            return response[0]
        except AttributeError:
            return response


    def get_items(
            self,
            uid='',
            action='active',
            license_number='',
        ):
        """Get items.
        Args:
            uid (str): The UID of an item.
            action (str): A specific type of item to filter by:
                `active`, `categories`, `brands`.
            license_number (str): A specific license number.
        Returns:
            (list): Returns a list of items (Item).
        """
        if uid:
            url = METRC_ITEMS_URL % uid
        else:
            url = METRC_ITEMS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return Item(self, response, license_number)
        except AttributeError:
            try:
                return [Item(self, x, license_number) for x in response]
            except AttributeError:
                return response


    def create_item(self, data, license_number='', return_obs=False):
        """Create an item.
        Args:
            data (dict): An item to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the newly created item.
        """
        response = self.create_items([data], license_number=license_number)
        if return_obs:
            item_name = data['Name']
            items = self.get_items()
            for item in items:
                if item_name in item.name:
                    return item
            return None
        return response


    def create_items(self, data, license_number='', return_obs=False):
        """Create items.
        Args:
            data (list): A list of items (dict) to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the newly created items.
        """
        url = METRC_ITEMS_URL % 'create'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('post', url, data=data, params=params)
        if not return_obs or not response:
            return response
        else:
            item_names = [x['Name'] for x in data]
            return_items = []
            items = self.get_items()
            for item in items:
                for item_name in item_names:
                    if item_name in item.name:
                        return_items.append(item)
            return return_items


    def update_item(self, data, license_number='', return_obs=False):
        """Update an item.
        Args:
            data (dict): An item to update.
            license_number (str): A specific license number.
        """
        return self.update_items(self, [data], license_number)
        # TODO: Optionally return updated item.


    def update_items(self, data, license_number='', return_obs=False):
        """Update items.
        Args:
            data (list): A list of items (dict) to update.
            license_number (str): A specific license number.
        """
        url = METRC_ITEMS_URL % 'update'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated item.


    def delete_item(self, uid, license_number=''):
        """Delete item.
        Args:
            uid (str): The UID of an item to delete.
            license_number (str): A specific license number.
        """
        url = METRC_ITEMS_URL % uid
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    #-------------------------------------------------------------------
    # Lab Results
    #-------------------------------------------------------------------

    def get_lab_result(
            self,
            uid='',
            license_number='',
        ):
        """Get lab results.
        Args:
            uid (str): The UID of a lab result.
            license_number (str): A specific license number.
        Returns:
            (LabResult): Returns a a lab result.
        """
        response = self.get_lab_results(uid, license_number=license_number)
        try:
            return response[0]
        except AttributeError:
            return response


    def get_lab_results(
            self,
            uid='',
            license_number='',
        ):
        """Get lab results.
        Args:
            uid (str): The UID for a package.
            license_number (str): A specific license number.
        """
        url = METRC_LAB_RESULTS_URL % 'results'
        params = self.format_params(
            package_id=uid,
            license_number=license_number or self.primary_license,
        )
        response = self.request('get', url, params=params)
        return [LabResult(self, x) for x in response]


    def get_test_types(self, license_number=''):
        """Get required quality assurance analyses.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_LAB_RESULTS_URL % 'types'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_test_statuses(self, license_number=''):
        """Get pre-defined lab statuses.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_LAB_RESULTS_URL % 'states'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def post_lab_results(self, data, license_number='', return_obs=False):
        """Post lab result(s).
        Args:
            data (list): A list of lab results (dict) to create or update.
            license_number (str): A specific license number.
        """
        url = METRC_LAB_RESULTS_URL % 'record'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return created lab result.
        # track.get_packages(
        #     label=lab_package.label,
        #     license_number=lab.license_number
        # )


    def upload_coas(self, data, license_number='', return_obs=False):
        """Upload lab result CoA(s).
        Args:
            data (list): A list of CoAs (dict) to upload.
            license_number (str): A specific license number.
        """
        url = METRC_LAB_RESULTS_URL % 'labtestdocument'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)


    def release_lab_results(self, data, license_number='', return_obs=False):
        """Release lab result(s).
        Args:
            data (list): A list of package labels (dict) to release lab results.
            license_number (str): A specific license number.
        """
        url = METRC_LAB_RESULTS_URL % 'results/release'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)


    #-------------------------------------------------------------------
    # Locations
    #-------------------------------------------------------------------

    def get_location_types(self, license_number=''):
        """Get all location types for a given license.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_LOCATIONS_URL % 'types'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_location(
            self,
            uid='',
            license_number='',
        ):
        """Get a location.
        Args:
            uid (str): The UID of a location.
            license_number (str): A specific license number.
        Returns:
            (Location): Returns a a lab result.
        """
        response = self.get_locations(uid, license_number=license_number)
        try:
            return response[0]
        except AttributeError:
            return response


    def get_locations(
            self,
            uid='',
            action='active',
            license_number='',
        ):
        """Get locations.
        Args:
            uid (str): The UID of a location, takes precedent over action.
            action (str): A specific filter to apply, with options:
                `active`, `types`.
            license_number (str): A specific license number.
        """
        if uid:
            url = METRC_LOCATIONS_URL % uid
        else:
            url = METRC_LOCATIONS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return Location(self, response, license_number)
        except AttributeError:
            try:
                return [Location(self, x, license_number) for x in response]
            except:
                return response


    def create_location(
            self,
            name,
            location_type='default',
            license_number='',
            return_obs=False,
        ):
        """Create location.
        Args:
            name (str): A location name.
            location_type (str): An optional location type:
                `default`, `planting`, or `packing`.
                `default` is assigned by default.
            license_number (str): Optional license number filter.
        """
        return self.create_locations([name], [location_type], license_number)
        # TODO: Optionally return the created location.


    def create_locations(self, names, types=[], license_number='', return_obs=False):
        """Create location(s).
        Args:
            names (list): A list of locations (dict) to create.
            types (list): An optional list of location types:
                `default`, `planting`, or `packing`.
                `default` is assigned by default.
            license_number (str): Optional license number filter.
        """
        data = []
        for index, name in enumerate(names):
            try:
                location_type = types[index]
            except IndexError:
                location_type = 'Default Location Type'
            data.append({
                'Name': name,
                'LocationTypeName': location_type
            })
        url = METRC_LOCATIONS_URL % 'create'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return the created locations.


    def update_locations(self, data, license_number='', return_obs=False):
        """Update location(s).
        Args:
            data (list): A list of locations (dict) to update.
            license_number (str): Optional license number filter.
        """
        url = METRC_LOCATIONS_URL % 'update'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return the updated location.


    def delete_location(self, uid, license_number=''):
        """Delete location.
        Args:
            uid (str): The UID of a location to delete.
            license_number (str): Optional license number filter.
        """
        url = METRC_LOCATIONS_URL % uid
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    #-------------------------------------------------------------------
    # Packages
    #-------------------------------------------------------------------

    def get_adjustment_reasons(self, license_number=''):
        """Get reasons for adjusting packages."""
        objs = self.get_packages(
            action='adjust/reasons',
            license_number=license_number,
        )
        try:
            return [obj.to_dict() for obj in objs]
        except AttributeError:
            return objs


    def get_package_types(self, license_number=''):
        """Get all facilities.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % 'types'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_package(
            self,
            uid='',
            label='active',
            action='active',
            license_number='',
        ):
        """Get a package.
        Args:
            uid (str): The UID of an item.
            label (str): The tag label for a package.
            action (str): A specific type of item to filter by:
                `active`, `categories`, `brands`.
            license_number (str): A specific license number.
        Returns:
            (Item): Returns an item (Item).
        """
        response = self.get_packages(uid, label=label, action=action, license_number=license_number)
        try:
            return response[0]
        except AttributeError:
            return response


    def get_packages(
            self,
            uid='',
            label='',
            action='active',
            license_number='',
            start='',
            end='',
        ):
        """Get package(s).
        Args:
            uid (str): The UID for a package.
            label (str): The tag label for a package.
            license_number (str): A specific license number.
            action (str): `active`, `onhold`, `inactive`, `types`,
                `adjust/reasons`.
            start (str): Optional ISO date to restrict earliest modified transfers.
            end (str): Optional ISO date to restrict latest modified transfers.
        Returns:
            (list): Returns a list of packages (Packages).
        """
        if uid:
            url = METRC_PACKAGES_URL % uid
        elif label:
            url = METRC_PACKAGES_URL % label
        else:
            url = METRC_PACKAGES_URL % action
        license_number = license_number or self.primary_license
        params = self.format_params(license_number=license_number, start=start, end=end)
        response = self.request('get', url, params=params)
        try:
            return Package(self, response, license_number)
        except AttributeError:
            try:
                return [Package(self, x, license_number) for x in response]
            except AttributeError:
                return response


    def create_package(
            self,
            data,
            license_number='',
            qa=False,
            plantings=False,
            return_obs=False,
        ):
        """Create a single package."""
        return self.create_packages(
            [data],
            license_number=license_number,
            qa=qa,
            plantings=plantings,
            return_obs=return_obs,
        )
        

    def create_packages(
            self,
            data,
            license_number='',
            qa=False,
            plantings=False,
            return_obs=False,
        ):
        """Create packages.
        Args:
            data (list): A list of packages (dict) to create.
            license_number (str): A specific license number.
            qa (bool): If the packages are for QA testing.
            plantings (bool): If the packages are for planting.
        """
        url = METRC_PACKAGES_URL % 'create'
        if qa:
            url += '/testing'
        elif plantings:
            url += '/plantings'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return created packages.


    def update_package(self, data, license_number='', return_obs=False):
        """Update a given package."""
        return self.update_packages([data], license_number=license_number, return_obs=return_obs)


    def update_packages(self, data, license_number='', return_obs=False):
        """Update packages.
        Args:
            data (list): A list of packages (dict) to update.
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % 'update'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated packages.


    # FIXME: Does this Metrc API endpoint exist? Test and find out.
    def delete_package(self, uid, license_number=''):
        """Delete a package.
        Args:
            uid (str): The UID of a package to delete.
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % uid
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    def change_package_items(self, data, license_number='', return_obs=False):
        """Update package items.
        Args:
            data (list): A list of package items (dict) to update.
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % 'change/item'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated packages.


    def change_package_locations(self, data, license_number='', return_obs=False):
        """Update package item location(s).
        Args:
            data (list): A list of package items (dict) to move.
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % 'change/locations'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated packages.


    def manage_packages(self, data, action='adjust', license_number='', return_obs=False):
        """Adjust package(s).
        Args:
            data (list): A list of packages (dict) to manage.
            license_number (str): A specific license number.
            action (str): The action to apply to the packages, with options:
                `adjust`, `finish`, `unfinish`, `remediate`.
        """
        url = METRC_PACKAGES_URL % action
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated packages.


    def update_package_notes(self, data, license_number='', return_obs=False):
        """Update package note(s).
        Args:
            data (list): A list of package notes (dict) to update.
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % 'change/note'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)
        # TODO: Optionally return updated packages.


    def create_plant_batches_from_packages(self, data, license_number='', return_obs=False):
        """Create plant batch(es) from given package(s).
        Args:
            data (list): A list of plant batches (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_PACKAGES_URL % 'create/plantings'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated packages.


    #-------------------------------------------------------------------
    # Patients
    #-------------------------------------------------------------------

    def get_patient(self, uid, license_number=''):
        return self.get_patients(uid, license_number=license_number)


    def get_patients(self, uid='', action='active', license_number=''):
        """Get licensee member patients.
        Args:
            uid (str): A UID for a patient.
            action (str): An optional filter to apply: `active`.
            license_number (str): A licensee's license number to filter by.
        """
        if uid:
            url = METRC_PATIENTS_URL % uid
        else:
            url = METRC_PATIENTS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return Patient(self, response, license_number)
        except AttributeError:
            try:
                return [Patient(self, x, license_number) for x in response]
            except AttributeError:
                return response


    def create_patient(self, data, license_number='', return_obs=False):
        """Create a given patient."""
        return self.create_patients([data], license_number, return_obs)


    def create_patients(self, data, license_number='', return_obs=False):
        """Create patient(s).
        Args:
            data (list): A list of patient (dict) to add.
        """
        url = METRC_PATIENTS_URL % 'add'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return created patient.


    def update_patients(self, data, license_number='', return_obs=False):
        """Update strain(s).
        Args:
            data (list): A list of patients (dict) to update.
        """
        url = METRC_PATIENTS_URL % 'update'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)
        # TODO: Optionally return updated patients.


    def delete_patient(self, uid, license_number=''):
        """Delete patient.
        Args:
            uid (str): The UID of a patient to delete.
        """
        url = METRC_PATIENTS_URL % uid
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    #-------------------------------------------------------------------
    # Plant Batches
    #-------------------------------------------------------------------

    def create_plant_batch(self, data, license_number='', return_obs=False):
        """Create a plant batch.
        Args:
            data (dict): A plant batch to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                plant batch.
        Returns:
            (PlantBatch): Returns a plant batch class.
        """
        response = self.create_plant_batches([data], license_number=license_number)
        if return_obs:
            name = data['Name']
            start = get_timestamp(past=self.default_time_period, zone=self.state)
            objects = self.get_batches(start=start, license_number=license_number)
            for obs in objects:
                if obs.name == name:
                    return obs
            return None
        return response


    def create_plant_batches(self, data, license_number='', return_obs=False):
        """Create plant batches.
        Args:
            data (list): A list of plant batches (dict) to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                plant batches.
        Returns:
            (list): Returns a list of plant batch (PlantBatch) classes.
        """
        if self.state == 'ca':
            raise MetrcAPIError({'message': 'The request POST /plantbatches/v1/createplantings will not work in California due to "CanCreateOpeningBalancePlantBatches": false, this request is used in other states that allow Plant Batch creation.'})
        response = self.manage_batches(data, 'createplantings', license_number=license_number)
        if not return_obs:
            return response
        else:
            names = [x['Name'] for x in data]
            return_obs = []
            start = get_timestamp(past=self.default_time_period, zone=self.state)
            objects = self.get_batches(start=start, license_number=license_number)
            for obs in objects:
                for name in names:
                    if obs.name == name:
                        return_obs.append(obs)
            return return_obs


    def get_batch_types(self, license_number=''):
        """Get plant batch types.
        Args:
            license_number (str): A specific license number.
        """
        return self.get_batches(action='types', license_number=license_number)


    def get_batches(
            self,
            uid='',
            action='active',
            license_number='',
            start='',
            end=''
        ):
        """Get plant batches(s).
        Args:
            uid (str): The UID for a plant batch.
            action (str): The action to apply to the plants, with options:
                `active`, `inactive`, `types`.
            license_number (str): A specific license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the last modified time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the last modified time.
        """
        if uid:
            url = METRC_BATCHES_URL % uid
        else:
            url = METRC_BATCHES_URL % action
        params = self.format_params(license_number=license_number or self.primary_license, start=start, end=end)
        response = self.request('get', url, params=params)
        try:
            return PlantBatch(self, response, license_number)
        except AttributeError:
            try:
                return [PlantBatch(self, x, license_number) for x in response]
            except AttributeError:
                return response


    def manage_batches(self, data, action, license_number='', from_mother=False, return_obs=False):
        """Manage plant batch(es) by applying a given action.
        Args:
            data (list): A list of plants (dict) to manage.
            action (str): The action to apply to the plants, with options:
                `createplantings`, `createpackages`, `split`,
                `create/packages/frommotherplant`, `changegrowthphase`,
                `additives`, `destroy`.
            from_mother (bool): An optional parameter for the
                `createpackages` action.
        """
        url = METRC_BATCHES_URL % action
        params = self.format_params(from_mother=from_mother, license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated or created objects.


    def add_batch_additives(self, data, license_number='', return_obs=False):
        """Add additives to a given batch."""
        if isinstance(data, dict):
            objs = [data]
        else:
            objs = data
        return self.manage_batches(objs, 'additives', license_number or self.primary_license)


    def change_batch_growth_phase(self, data, license_number='', return_obs=False):
        """Change the growth phase of given batch(es)."""
        if isinstance(data, dict):
            objs = [data]
        else:
            objs = data
        return self.manage_batches(objs, 'changegrowthphase', license_number or self.primary_license)


    def create_plantings(self, data, license_number='', return_obs=False):
        """Create plantings from given batch."""
        if isinstance(data, dict):
            objs = [data]
        else:
            objs = data
        return self.manage_batches(objs, 'createplantings', license_number or self.primary_license)


    def create_plant_package_from_batch(self, data, license_number='', from_mother_plant=False, return_obs=False):
        """Create a plant package from a batch.
        Args:
            data (dict): The plant package data.
            license_number (str): A specific license number.
        """
        if from_mother_plant:
            return self.manage_batches([data], 'create/packages/frommotherplant', license_number=license_number)
        else:
            return self.manage_batches([data], 'createpackages', license_number=license_number)        
        # TODO: Optionally return created package.
   

    def destroy_batch_plants(self, data, license_number='', return_obs=False):
        """Destroy plants in a given batch."""
        if isinstance(data, dict):
            objs = [data]
        else:
            objs = data
        return self.manage_batches(objs, 'destroy', license_number or self.primary_license)


    def move_batches(self, data, license_number='', return_obs=False):
        """Move plant batch(es).
        Args:
            data (list): A list of plant batches (dict) to move.
        """
        url = METRC_BATCHES_URL % 'moveplantbatches'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)
        # TODO: Optionally return moved plant batch.


    def split_batch(self, data, license_number='', return_obs=False):
        """Split a given batch.
        Args:
            data (dict): Batch split data.
            license_number (str): A specific license number.
        """
        return self.split_batches([data], license_number=license_number)
        # TODO: Optionally return new batch.


    def split_batches(self, data, license_number='', return_obs=False):
        """Split multiple batches.
        Args:
            data (list): A list of batch splits (dict).
            license_number (str): A specific license number.
        """
        return self.manage_batches(data, action='split', license_number=license_number)
        # TODO: Optionally return new batches.


    #-------------------------------------------------------------------
    # Plants
    #-------------------------------------------------------------------

    def create_plant(self, data, license_number='', return_obs=False):
        """Create a plant.
        Args:
            data (dict): A plant to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                plant.
        Returns:
            (Plant): Returns a plant batch class.
        """
        response = self.create_plants([data], license_number=license_number)
        if return_obs:
            label = data['PlantLabel']
            return self.get_plants(label=label, license_number=license_number)
        return response


    def create_plants(self, data, license_number='', return_obs=False):
        """Use a plant to create an immature plant batch.
        Args:
            data (list): A list of plants (dict) to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                plants.
        Returns:
            (list): Returns a list of plants (Plants) classes.
        """
        url = METRC_PLANTS_URL % 'create/plantings'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('post', url, data=data, params=params)
        if not return_obs:
            return response
        else:
            names = [x['PlantLabel'] for x in data]
            return_obs = []
            start = get_timestamp(past=self.default_time_period, zone=self.state)
            objects = self.get_plants(
                action='vegetative',
                start=start,
                license_number=license_number,
            )
            for obs in objects:
                for name in names:
                    if obs.label == name:
                        return_obs.append(obs)
            return return_obs


    def create_plant_package(self, data, license_number='', return_obs=False):
        """Create plant package.
        Args:
            data (list): A list of plant packages (dict) to create.
            license_number (str): A specific license number.
        """
        return self.create_plant_packages([data], license_number)


    def create_plant_packages(self, data, license_number='', return_obs=False):
        """Create plant packages.
        Args:
            data (list): A list of plant packages (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_PLANTS_URL % 'create/plantbatch/packages'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)


    def get_plants(
            self,
            uid='',
            label='',
            action='',
            license_number='',
            start='',
            end=''
        ):
        """Get plant(s).
        Args:
            uid (str): The UID for a plant.
            label (str): The label for a given plant.
            action (str): A specific filter to apply, with options:
                `vegetative`, `flowering`, `onhold`,
                `inactive`, `additives`, `additives/types`,
                `growthphases`, `waste/methods`, `waste/reasons`.
            license_number (str): A specific license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the last modified time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the last modified time.
        """
        if uid:
            url = METRC_PLANTS_URL % uid
        elif label:
            url = METRC_PLANTS_URL % label
        else:
            url = METRC_PLANTS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license, start=start, end=end)
        response = self.request('get', url, params=params)
        try:
            return Plant(self, response, license_number)
        except AttributeError:
            try:
                return [Plant(self, x, license_number) for x in response]
            except AttributeError:
                return response


    def manage_plants(self, data, action, license_number='', return_obs=False):
        """Manage plant(s) by applying a given action.
        Args:
            data (list): A list of plants (dict) to manage.
            action (str): The action to apply to the plants, with options:
                `moveplants`, `changegrowthphases`, `destroyplants`,
                `additives`, `additives/bylocation`,
                `create/plantings`, `create/plantbatch/packages`,
                `manicureplants`, `harvestplants`.
            license_number (str): A specific license number.
        """
        url = METRC_PLANTS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return updated plants.


    def move_plants(self, data, license_number='', return_obs=False):
        """Move multiple plants.
        Args:
            data (list): A list of plant move data (dict).
            license_number (str): A specific license number.
        """
        return self.manage_plants(data, action='moveplants', license_number=license_number)
        # TODO: Optionally return updated plants.


    def destroy_plants(self, data, license_number=''):
        """Destroy plants."""
        return self.manage_plants(data, action='destroyplants', license_number=license_number)


    def flower_plants(self, data, license_number='', return_obs=False):
        """Flower plants."""
        return self.manage_plants(data, action='changegrowthphases', license_number=license_number)


    def harvest_plants(self, data, license_number='', return_obs=False):
        """Harvest plants."""
        return self.manage_plants(data, action='harvestplants', license_number=license_number)


    def manicure_plants(self, data, license_number='', return_obs=False):
        """Manicure plants."""
        return self.manage_plants(data, action='manicureplants', license_number=license_number)


    def add_plant_additives(self, data, license_number='', return_obs=False):
        """Add additive(s) to given plant(s)."""
        return self.manage_plants(data, action='additives', license_number=license_number)


    def get_additive_types(self, license_number='', return_obs=False):
        """Get additive types."""
        return self.get_plants(action='additives/types', license_number=license_number)
    

    def get_growth_phases(self, license_number='', return_obs=False):
        """Get growth phases."""
        return self.get_plants(action='growthphases', license_number=license_number)
    


    # TODO: "additives/bylocation")


    #-------------------------------------------------------------------
    # Sales
    #-------------------------------------------------------------------

    def get_receipts(
            self,
            uid='',
            action='active',
            license_number='',
            start='',
            end='',
            sales_start='',
            sales_end='',
        ):
        """Get sale(s).
        Args:
            uid (str): The UID for a plant batch.
            action (str): The action to apply to the plants, with options:
                `active` or `inactive`
            license_number (str): A specific license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the last modified time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the last modified time.
            sales_start (str): An ISO 8601 formatted string to restrict the start
                by the sales time.
            sales_end (str): An ISO 8601 formatted string to restrict the end
                by the sales time.
        Returns:
            (list): Returns a list of Receipts or a singular Receipt.
        """
        if uid:
            url = METRC_RECEIPTS_URL % uid
        else:
            url = METRC_RECEIPTS_URL % action
        params = self.format_params(
            license_number=license_number or self.primary_license,
            start=start,
            end=end,
            sales_start=sales_start,
            sales_end=sales_end,
        )
        response = self.request('get', url, params=params)
        try:
            return Receipt(self, response, license_number)
        except AttributeError:
            return [Receipt(self, x, license_number) for x in response]


    def get_transactions(
            self,
            license_number='',
            start='',
            end='',
        ):
        """Get transaction(s).
        Args:
            license_number (str): A specific license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the sales time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the sales time.
        Returns:
            (list): Returns either a list of Transactions or a singular Transaction.
        """
        if start and end:
            url = METRC_TRANSACTIONS_URL % f'{start}/{end}'
        else:
            url = METRC_SALES_URL % 'transactions'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return Transaction(self, response, license_number)
        except AttributeError:
            return [Transaction(self, x, license_number) for x in response]


    def get_customer_types(self, license_number=''):
        """Get all customer types.
        Args:
            license_number (str): A specific license number.
        Returns:
            (list): Returns a list of customer types (dict).
        """
        url = METRC_SALES_URL % 'customertypes'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def create_receipt(self, data, license_number='', return_obs=False):
        """Create a receipt.
        Args:
            data (dict): A receipts (dict) to create.
            license_number (str): A specific license number.
        """
        return self.create_receipts(data, license_number, return_obs)


    def create_receipts(self, data, license_number='', return_obs=False):
        """Create receipt(s).
        Args:
            data (list): A list of receipts (dict) to create.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % 'receipts'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return the created receipts.


    def update_receipts(self, data, license_number='', return_obs=False):
        """Update receipt(s).
        Args:
            data (list): A list of receipts (dict) to update.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % 'receipts'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)
        # TODO: Optionally return the updated receipts.


    def delete_receipt(self, uid, license_number=''):
        """Delete receipt.
        Args:
            uid (str): The UID of a receipt to delete.
            license_number (str): A specific license number.
        """
        url = METRC_SALES_URL % f'receipts/{uid}'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    def create_transactions(self, data, date, license_number='', return_obs=False):
        """Create transaction(s).
        Args:
            data (list): A list of transactions (dict) to create.
            date (str): An ISO 8601 formatted string of the transaction date.
            license_number (str): A specific license number.
        Return:
            (Transaction): Return the created transaction if `return_obs=True`.
        """
        url = METRC_TRANSACTIONS_URL % date
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return the created transactions.


    def update_transactions(self, data, date, license_number='', return_obs=False):
        """Update transaction(s).
        Args:
            data (list): A list of transactions (dict) to update.
            date (str): An ISO 8601 formatted string of the transaction date.
            license_number (str): A specific license number.
        Return:
            (list): Return a list of transactions (Transaction) if `return_obs=True`.
        """
        url = METRC_TRANSACTIONS_URL % date
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)
        # TODO: Optionally return the updated transactions.


    #-------------------------------------------------------------------
    # Strains
    #-------------------------------------------------------------------

    def get_strains(self, uid='', action='active', license_number=''):
        """Get strains.
        Args:
            uid (str): A UID for a strain.
            action (str): An optional filter to apply: `active`.
            license_number (str): A licensee's license number to filter by.
        """
        if uid:
            url = METRC_STRAINS_URL % uid
        else:
            url = METRC_STRAINS_URL % action
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return Strain(self, response, license_number)
        except AttributeError:
            return [Strain(self, x, license_number) for x in response]


    def create_strain(self, data, license_number='', return_obs=False):
        """Create a strain.
        Args:
            data (dict): A strain to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                strain (Strain).
        Returns:
            (Strain): Returns a strain class.
        """
        response = self.create_strains(
            [data],
            license_number=license_number,
            return_obs=return_obs,
        )
        if response:
            return response[0]
        return response


    def create_strains(self, data, license_number='', return_obs=False):
        """Create strain(s).
        Args:
            data (list): A list of strains (dict) to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                strains (Strain).
        Returns:
            (list): Returns a list of strains (Strains) classes.
        """
        url = METRC_STRAINS_URL % 'create'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('post', url, data=data, params=params)
        if not return_obs:
            return response
        else:
            names = [x['Name'] for x in data]
            return_obs = []
            objects = self.get_strains(license_number=license_number)
            for obs in objects:
                for name in names:
                    if obs.name == name:
                        return_obs.append(obs)
            return return_obs


    def update_strain(self, data, license_number='', return_obs=False):
        """Update strain.
        Args:
            data (list): A strain (dict) to update.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created strains.
        Returns:
            (Strain): Returns the updated strain.
        """
        response = self.update_strains(
            [data],
            license_number=license_number,
            return_obs=return_obs,
        )
        if response:
            return response[0]
        return response


    def update_strains(self, data, license_number='', return_obs=False):
        """Update strain(s).
        Args:
            data (list): A list of strains (dict) to update.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created strains.
        Returns:
            (list): Returns a list of strains (Strain) classes.
        """
        url = METRC_STRAINS_URL % 'update'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('post', url, data=data, params=params)
        if not return_obs:
            return response
        else:
            ids = [x['Id'] for x in data]
            return_obs = []
            for obs_id in ids:
                obs = self.get_strains(uid=obs_id, license_number=license_number)
                return_obs.append(obs)
            return return_obs


    def delete_strain(self, uid, license_number=''):
        """Delete strain.
        Args:
            uid (str): The UID of a strain to delete.
            license_number (str): A specific license number.
        """
        url = METRC_STRAINS_URL % uid
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    #-------------------------------------------------------------------
    # Transfers
    #-------------------------------------------------------------------

    def get_transfers(
            self,
            uid='',
            transfer_type='incoming',
            license_number='',
            start='',
            end='',
        ):
        """Get transfers.
        Args:
            uid (str): The UID for a transfer, takes precedent in query.
            transfer_type (str): The type of transfer:
                `incoming`, `outgoing`, or `rejected`.
            license_number (str): A specific license number.
            start (str): Optional ISO date to restrict earliest modified transfers.
            end (str): Optional ISO date to restrict latest modified transfers.
        """
        if uid:
            url = METRC_TRANSFERS_URL % f'{uid}/deliveries'
        else:
            url = METRC_TRANSFERS_URL % transfer_type
        params = self.format_params(license_number=license_number or self.primary_license, start=start, end=end)
        response = self.request('get', url, params=params)
        try:
            return Transfer(self, response, license_number)
        except AttributeError:
            return [Transfer(self, x, license_number) for x in response]


    def get_transfer_packages(self, uid, license_number='', action='packages'):
        """Get shipments.
        Args:
            uid (str): Required UID of a shipment.
            license_number (str): A specific license number.
            action (str): The filter to apply to transfers:
                `packages`, `packages/wholesale`, `requiredlabtestbatches`.
        """
        if action == 'requiredlabtestbatches':
            url = METRC_TRANSFER_PACKAGES_URL % (f'package/{uid}', action)
        else:
            url = METRC_TRANSFER_PACKAGES_URL % (uid, action)
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_transfer_types(self, license_number=''):
        """Get all transfer types.
        Args:
            license_number (str): A specific license number.
        Returns:
            (list): Returns transfer types (dict).
        """
        url = METRC_TRANSFERS_URL % 'types'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('get', url, params=params)
        try:
            return [clean_dictionary(x, camel_to_snake) for x in response]
        except:
            return response


    def get_package_statuses(self, license_number=''):
        """Get all package status choices.
        Args:
            license_number (str): A specific license number.
        Returns:
            (list): Returns package statuses (dict).
        """
        url = METRC_TRANSFERS_URL % 'delivery/packages/states'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_transporters(self, uid):
        """Get the data for a transporter.
        Args:
            uid (str): The ID of the shipment delivery.
        """
        url = METRC_TRANSFERS_URL % f'{uid}/transporters'
        return self.request('get', url)


    def get_transporter_details(self, uid):
        """Get the details of the transporter driver and vehicle.
        Args:
            uid (str): The ID of the shipment delivery.
        """
        url = METRC_TRANSFERS_URL % f'{uid}/transporters/details'
        return self.request('get', url)


    def create_transfer(self, data, license_number='', return_obs=False):
        """Create a transfer.
        Args:
            data (dict): A transfer to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                transfer.
        Returns:
            (Transfer): Returns the created transfer.
        """
        response = self.create_transfers(
            [data],
            license_number=license_number,
            return_obs=return_obs,
        )
        if response:
            return response[0]
        return response


    def create_transfers(self, data, license_number='', return_obs=False):
        """Create transfer(s).
        Args:
            data (list): A list of transfers (dict) to create.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created
                transfer.
        Returns:
            (list): Returns a list of transfers (Transfer).
        """
        url = METRC_TRANSFERS_URL % 'external/incoming'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return the created transfers.


    def update_transfer(self, data, license_number='', return_obs=False):
        """Update a given transfer.
        Args:
            data (dict): A transfer to update.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the created transfer.
        Returns:
            (Transfer): Returns transfer class.
        """
        response = self.update_transfers(
            [data],
            license_number=license_number,
            return_obs=return_obs,
        )
        if response:
            return response[0]
        return response


    def update_transfers(self, data, license_number='', return_obs=False):
        """Update transfer(s).
        Args:
            data (list): A list of transfers (dict) to update.
            license_number (str): A specific license number.
            return_obs (bool): Whether or not to get and return the updated transfers.
        Returns:
            (list): Returns a list of transfers (Transfer).
        """
        url = METRC_TRANSFERS_URL % 'external/incoming'
        params = self.format_params(license_number=license_number or self.primary_license)
        response = self.request('put', url, data=data, params=params)
        if not return_obs:
            return response
        else:
            ids = [x['TransferId'] for x in data]
            return_obs = []
            for obs_id in ids:
                obs = self.get_transfers(uid=obs_id, license_number=license_number)
                return_obs.append(obs)
            return return_obs


    def delete_transfer(self, uid, license_number=''):
        """Delete transfer.
        Args:
            uid (str): The UID of a transfer to delete.
            license_number (str): A specific license number.
        """
        url = METRC_TRANSFERS_URL % f'external/incoming/{uid}'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    #-------------------------------------------------------------------
    # Transfer Templates
    #-------------------------------------------------------------------

    # FIXME: Implement the following 2 endpoints:
    # GET /transfers/v1/templates/{id}/transporters
    # GET /transfers/v1/templates/{id}/transporters/details

    def get_transfer_templates(
            self,
            uid='',
            action='',
            license_number='',
            start='',
            end='',
        ):
        """Get transfer template(s).
        Args:
            uid (str): A UID for a transfer template.
            action (str): An optional filter to apply: `deliveries`, `packages`.
            license_number (str): A specific license number.
            start (str): An ISO 8601 formatted string to restrict the start
                by the sales time.
            end (str): An ISO 8601 formatted string to restrict the end
                by the sales time.
        """
        if action == 'deliveries':
            url = METRC_TRANSFER_TEMPLATE_URL % f'{uid}/deliveries'
        elif action == 'packages':
            url = METRC_TRANSFER_TEMPLATE_URL % f'delivery/{uid}/packages'
        else:
            url = (METRC_TRANSFER_TEMPLATE_URL % '').rstrip('/')
        params = self.format_params(license_number=license_number or self.primary_license, start=start, end=end)
        response = self.request('get', url, params=params)
        try:
            return TransferTemplate(self, response, license_number)
        except AttributeError:
            return [TransferTemplate(self, x, license_number) for x in response]


    def create_transfer_templates(self, data, license_number='', return_obs=False):
        """Create transfer_template(s).
        Args:
            data (list): A list of transfer templates (dict) to create.
        """
        url = (METRC_TRANSFER_TEMPLATE_URL % '').rstrip('/')
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('post', url, data=data, params=params)
        # TODO: Optionally return the created transfer templates.


    def update_transfer_templates(self, data, license_number='', return_obs=False):
        """Update transfer template(s).
        Args:
            data (list): A list of transfer templates (dict) to update.
        """
        url = (METRC_TRANSFER_TEMPLATE_URL % '').rstrip('/')
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('put', url, data=data, params=params)
        # TODO: Optionally return the updated transfer templates.


    def delete_transfer_template(self, uid, license_number=''):
        """Delete transfer template.
        Args:
            uid (str): The UID of a transfer template to delete.
        """
        url = METRC_TRANSFER_TEMPLATE_URL % uid
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('delete', url, params=params)


    #-------------------------------------------------------------------
    # Waste
    #-------------------------------------------------------------------

    def get_waste_methods(self, license_number=''):
        """Get all waste methods for a given license.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_PLANTS_URL % 'waste/methods'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_waste_reasons(self, license_number=''):
        """Get all waste reasons for plants for a given license.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_PLANTS_URL % 'waste/reasons'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def get_waste_types(self, license_number=''):
        """Get all waste types for harvests for a given license.
        Args:
            license_number (str): A specific license number.
        """
        url = METRC_HARVESTS_URL % 'waste/types'
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    #-------------------------------------------------------------------
    # Miscellaneous
    #-------------------------------------------------------------------

    def get_units_of_measure(self, license_number=''):
        """Get all units of measurement.
        Args:
            license_number (str): A specific license number.
        Returns:
            (list): Returns a list of units of measure (dict).
        """
        url = METRC_UOM_URL
        params = self.format_params(license_number=license_number or self.primary_license)
        return self.request('get', url, params=params)


    def import_tags(self, file_path, row_start=0, row_end=None, number=10):
        """Import plant and package tags.
        Args:
            file_path (str): The file location of the tags.
            row_start (int): The row at which to begin importing tags.
            row_end (int): The row at which to end importing tags.
            number (int): The number of tags to import.
        Returns:
            (dict): Returns the tags as a dictionary.
        """
        if row_end:
            number = row_end - row_start
        df = read_excel(
            file_path,
            skiprows=1 + row_start,
            nrows=number,
            header=None,
            names=['tag', 'type', 'status', 'commissioned', 'used', 'detached']
        )
        return df.to_dict('records')
