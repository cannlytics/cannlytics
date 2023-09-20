"""
Massachusetts Cannabis Control Commission (CCC) Open Data API Wrapper
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 4/5/2022
Updated: 9/19/2023
License: MIT License <https://opensource.org/licenses/MIT>

Data sources:

    - Massachusetts Cannabis Control Commission Data Catalog
    https://masscannabiscontrol.com/open-data/data-catalog/

TODO:

    - [ ] Create a data guide.
    - [ ] Work on the dynamics of the column types.

FIXME: SQL queries do not appear to work.

"""
# Standard imports.
import io
import os
from typing import Any, Optional

# External imports.
import pandas as pd
from requests import Session

# Internal imports.
from cannlytics.utils.constants import DEFAULT_HEADERS


OPENDATA_ENDPOINTS = {
    'agent-gender-stats': 'hhjg-atjk',
    'agent-ethnicity-stats': 'pt2c-wb44',
    'licensees': 'albs-all',
    'licensees-approved': 'hmwt-yiqy',
    'licensees-pending': 'piib-tj3f',
    'licensees-demographics': '5dkg-e39p',
    'licensees-under-review-stats': 'pebi-jpc4',
    'licensees-application-stats': 'n6qz-us6r',
    'retail-sales-stats': '87rp-xn9v',
    'retail-sales-weekly': 'dt9b-i6ds',
    'retail-price-per-ounce': 'rqtv-uenj',
    'medical-stats': 'g5mj-5pg3',
    'plants': 'meau-plav',
    'sales': 'fren-z7jq',
}
OPENDATA_BOOLEAN_COLUMNS = [
    'activity_date',
    'app_create_date',
    'facilityisexpired',
    'facilityismedical',
    'facilityisretail',
    'facilityiscultivation',
    'facilityisdispensaryorstore',
    'facilityisinfusedmanufacturer',
    # is_abutters_notified
    'not_a_dbe',
    'priority',
]
OPENDATA_DATETIME_COLUMNS = [
    'activitysummarydate',
    'sale_period',
    'saledate',
]
OPENDATA_NUMERIC_COLUMNS = [
    'abutters_count',
    'application_fee',
    'average_spent',
    'countbasedtotal',
    'dollarcountbasedtotal',
    'dollarweightbasedtotal',
    'gross_sales',
    'harvestactivecount',
    'latitude',
    'lic_fee_amount',
    'longitude',
    'percent_total',
    'plantdestroyedcount',
    'plantfloweringcount',
    'plantharvestedcount',
    'plantvegetativecount',
    'price_per_ounce',
    'quantity',
    'square_footage_establishment',
    'strainactivecount',
    'total',
    'total_dollars',
    'totalprice',
    'total_units',
    'units',
    'weightbasedtotal',
]
OPENDATA_CODINGS = {
    '= 1 oz': 'price_per_ounce',
}


class APIError(Exception):
    """A primary error raised by the Open Data API."""

    def __init__(self, response):
        message = self.get_response_messages(response)
        super().__init__(message)
        self.response = response

    def get_response_messages(self, response):
        """Extract error messages from a Open Data API response.
        Args:
            response (Response): A request response from the Open Data API.
        Returns:
            (str): Returns any error messages.
        """
        try:
            return response.json()
        except:
            return response.text


class OpenData(object):
    """An instance of this class communicates with the
    Cannabis Control Commission of the Commonwealth of Massachusetts'
    Open Data catalog."""

    def __init__(self, headers=None) -> None:
        """Initialize an Open Data API client.
        Args:
            headers (dict): Headers for HTTP requests (optional).
        """
        self.base = 'https://masscannabiscontrol.com/resource/'
        self.endpoints = OPENDATA_ENDPOINTS
        if headers is None:
            self.headers = DEFAULT_HEADERS
        else:
            self.headers = headers
        self.session = Session()

    def get(self, endpoint:str, params: Optional[dict] = None) -> Any:
        """Make a request to the API.
        Args:
            endpoint (str): The API endpoint.
            params (dict): A dictionary of parameters.
        Returns:
            (DataFrame): The HTTP data formatted as a DataFrame.
        """
        url = os.path.join(self.base, f'{endpoint}.csv')
        try:
            response = self.session.get(url, headers=self.headers, params=params)
        except ConnectionError:
            self.session = Session()
            response = self.session.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            raise APIError(response)
        # Deprecated JSON: 2023-09-19
        # try:
        #     body = response.json()
        # except:
        #     body = json.loads(response.text.replace('\r', '').replace('\ufeff', ''))
        # data = pd.DataFrame(body)
        data = pd.read_csv(io.StringIO(response.text))
        data.columns = map(str.lower, data.columns)
        data.columns = [x.replace('$', 'dollars').replace('%', 'percent') for x in data.columns]
        data.rename(columns=OPENDATA_CODINGS, inplace=True)
        for key in list(set(OPENDATA_BOOLEAN_COLUMNS).intersection(data.columns)):
            data[key] = data[key].astype(bool, errors='ignore')
        for key in list(set(OPENDATA_DATETIME_COLUMNS).intersection(data.columns)):
            data[key] = pd.to_datetime(data[key], errors='ignore')
        for key in list(set(OPENDATA_NUMERIC_COLUMNS).intersection(data.columns)):
            data[key] = data[key].astype(float, errors='ignore')
        return data

    def get_agents(self, dataset: Optional[str] = 'gender-stats') -> Any:
        """Get agent statistics.
        Args:
            dataset (str): An optional dataset filter:
                * `gender-stats` (default)
                * `ethnicity-stats`
        Returns:
            (DataFrame): The agent data formatted as a DataFrame.
        """
        key = 'agent'
        if dataset:
            key += '-' + dataset
        endpoint = self.endpoints[key]
        return self.get(endpoint)

    def get_licensees(
            self,
            dataset: Optional[str] = '',
            limit: Optional[int] = 10_000,
            order_by: Optional[str] = 'app_create_date',
            ascending: Optional[bool] = False,
        ) -> Any:
        """Get Massachusetts licensee data and statistics.
        Args:
            dataset (str): An optional dataset filter:
                * `approved`
                * `pending`
                * `demographics`
                * `under-review-stats`
                * `application-stats`
            limit (int): A limit to the number of returned observations.
            order_by (str): The field to order the results, `app_create_date` by default.
            ascending (bool): If ordering results, ascending or descending. Descending by default.
        Returns:
            (DataFrame): The licensees data formatted as a DataFrame.
        """
        key = 'licensees'
        if dataset:
            key += '-' + dataset
        endpoint = self.endpoints[key]
        params = {
            '$limit': limit,
            '$order': order_by,
        }
        if not ascending:
            params['$order'] += ' DESC'
        return self.get(endpoint, params=params)

    def get_retail(
            self,
            dataset: Optional[str] = 'sales-stats',
            limit: Optional[int] = 10_000,
            order_by: Optional[str] = 'date',
            ascending: Optional[bool] = False,
        ) -> Any:
        """Get Massachusetts retail data and statistics.
        Args:
            dataset (str): An optional dataset filter:
                * `sales-stats` (default)
                * `sales-weekly`
                * `price-per-ounce`
            limit (int): A limit to the number of returned observations.
            order_by (str): The field to order the results, `app_create_date` by default.
            ascending (bool): If ordering results, ascending or descending. Descending by default.
        Returns:
            (DataFrame): The retail data formatted as a DataFrame.
        """
        key = 'retail'
        key += '-' + dataset
        endpoint = self.endpoints[key]
        params = {
            '$limit': limit,
            '$order': order_by,
        }
        if not ascending:
            params['$order'] += ' DESC'
        return self.get(endpoint, params=params)

    def get_medical(self, dataset: Optional[str] = 'stats') -> Any:
        """Get Massachusetts medical stats.
        Args:
            dataset (str): The specific medical dataset to retrieve.
        Returns:
            (DataFrame): The medical data formatted as a DataFrame.
        """
        key = 'medical'
        key += '-' + dataset
        endpoint = self.endpoints[key]
        return self.get(endpoint)

    def get_plants(
            self,
            limit: Optional[int] = 10_000,
            order_by: Optional[str] = 'activitysummarydate',
            ascending: Optional[bool] = False,
        ) -> Any:
        """Get Massachusetts cultivation data and statistics.
        Args:
            limit (int): A limit to the number of returned observations.
            order_by (str): The field to order the results, `app_create_date` by default.
            ascending (bool): If ordering results, ascending or descending. Descending by default.
        Returns:
            (DataFrame): The plant data formatted as a DataFrame.
        """
        key = 'plants'
        endpoint = self.endpoints[key]
        params = {
            '$limit': limit,
            '$order': order_by,
        }
        if not ascending:
            params['$order'] += ' DESC'
        return self.get(endpoint, params=params)

    def get_sales(
            self,
            limit: Optional[int] = 10_000,
            order_by: Optional[str] = 'activitysummarydate',
            ascending: Optional[bool] = False,
        ) -> Any:
        """Get Massachusetts sales data.
        Args:
            limit (int): A limit to the number of returned observations.
            order_by (str): The field to order the results, `app_create_date` by default.
            ascending (bool): If ordering results, ascending or descending. Descending by default.
        Returns:
            (DataFrame): The sales data formatted as a DataFrame.
        """
        key = 'sales'
        endpoint = self.endpoints[key]
        params = {
            '$limit': limit,
            '$order': order_by,
        }
        if not ascending:
            params['$order'] += ' DESC'
        return self.get(endpoint, params=params)
