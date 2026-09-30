"""
Geographic Information Systems (GIS) Data | Cannlytics
Copyright (c) 2021-2026 Cannlytics and Cannlytics Contributors

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 11/5/2021
Updated: 9/28/2026
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:
    Geographic tools: state data and population from the Federal
    Reserve's FRED, geocoding and place search with Google Maps, and
    driving distance and routes between two points.

    The libraries are imported when a function needs them, so this
    module always imports; a function whose library is missing names
    the extra to install (``pip install "cannlytics[utils]"``).
"""
# Standard imports:
import importlib
import logging
import os
import re
from datetime import datetime
from time import sleep
from typing import Any, Dict, List, Optional, Tuple, Union

# External imports:
from dotenv import dotenv_values

# Module logger. A library must not print to stdout.
logger = logging.getLogger(__name__)

def _require(module: str, extra: str = 'utils') -> Any:
    """Import an optional library, or say which extra provides it."""
    try:
        return importlib.import_module(module)
    except ImportError as error:
        raise ImportError(f'{module} is needed here: pip install "cannlytics[{extra}]"') from error

# === Google Maps API key ===

def _key_from_secret_manager() -> Optional[str]:
    """The key from Google Secret Manager, in the default credentials' project."""
    import google.auth
    from cannlytics.firebase import access_secret_version
    _, project_id = google.auth.default()
    return access_secret_version(project_id=project_id, secret_id='GOOGLE_MAPS_API_KEY', version_id='latest')

def _key_from_firestore() -> Optional[str]:
    """The key from the Firestore document ``admin/google``."""
    from cannlytics.firebase import get_document, initialize_firebase
    data = get_document('admin/google', database=initialize_firebase())
    return (data or {}).get('google_maps_api_key')

def get_google_maps_api_key(env_file: str = '.env') -> str:
    """Find a Google Maps API key.

    Looks, in order, in the environment variable ``GOOGLE_MAPS_API_KEY``,
    in ``env_file`` (read, not loaded: the environment is not changed),
    in Google Secret Manager, and in the Firestore document
    ``admin/google``. The last two need ``cannlytics[firebase]`` and
    credentials; their failures are logged, not raised.

    Returns:
        The key.

    Raises:
        RuntimeError: If no source has one.
    """
    key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if key:
        return key
    if env_file and os.path.exists(env_file):
        key = dotenv_values(env_file).get('GOOGLE_MAPS_API_KEY')
        if key:
            return key
    for name, source in (('Secret Manager', _key_from_secret_manager), ('Firestore', _key_from_firestore)):
        try:
            key = source()
        except Exception as error:
            logger.warning('No Google Maps API key from %s: %s', name, error)
            continue
        if key:
            return key
    raise RuntimeError(
        'No Google Maps API key: set GOOGLE_MAPS_API_KEY in the environment or in '
        f'{env_file!r}, or store it in Secret Manager or Firestore (admin/google).'
    )

def initialize_googlemaps(env_file: Optional[str] = './.env') -> Any:
    """A Google Maps client, keyed from ``env_file`` or ``get_google_maps_api_key``."""
    googlemaps = _require('googlemaps')
    key = None
    if env_file and os.path.exists(env_file):
        key = dotenv_values(env_file).get('GOOGLE_MAPS_API_KEY')
    return googlemaps.Client(key=key or get_google_maps_api_key())

# === FRED ===

def get_state_data(
        state: str,
        code: str,
        fred_api_key: Optional[str] = None,
        district: Optional[str] = '',
        obs_start: Optional[Any] = None,
        obs_end: Optional[Any] = None,
    ) -> Any:
    """A state's series from FRED, by series code.

    Args:
        state: The state's abbreviation, in either case.
        code: The FRED code after the state, for example ``'POP'``.
        fred_api_key: A FRED API key (free at
            https://fred.stlouisfed.org/docs/api/api_key.html), or
            ``None`` to use the environment variable ``FRED_API_KEY``.
        district: A suffix some series take.
        obs_start: The first observation date.
        obs_end: The last observation date.

    Returns:
        The single value if the series has one observation, else the
        series (a pandas Series indexed by date).
    """
    fredapi = _require('fredapi')
    series = fredapi.Fred(api_key=fred_api_key).get_series(
        f'{state.upper()}{code.upper()}{(district or "").upper()}', obs_start, obs_end,
    )
    return series.iloc[0] if len(series) == 1 else series

def get_state_population(
        state: str,
        fred_api_key: Optional[str] = None,
        district: Optional[str] = '',
        obs_start: Optional[Any] = None,
        obs_end: Optional[Any] = None,
        multiplier: Optional[float] = 1000.0,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """A state's resident population from FRED (series ``<STATE>POP``).

    FRED reports thousands of people; ``multiplier`` converts them.
    Missing observations are skipped.

    Returns:
        One dictionary (the latest observation, by default) or a list,
        each with ``population``, ``population_formatted``,
        ``population_source_code``, ``population_source``, and
        ``population_at`` (ISO date).
    """
    fredapi = _require('fredapi')
    code = f'{state.upper()}POP{(district or "").upper()}'
    series = fredapi.Fred(api_key=fred_api_key).get_series(code, obs_start, obs_end)
    observations = []
    for index, value in series.items():
        if value != value:  # NaN: no observation
            continue
        population = int(round(value * multiplier))
        observations.append({
            'population': population,
            'population_formatted': f'{population:,}',
            'population_source_code': code,
            'population_source': f'https://fred.stlouisfed.org/series/{code}',
            'population_at': index.isoformat()[:10],
        })
    return observations[0] if len(observations) == 1 else observations

# === Google Maps ===

def geocode_addresses(
        data: Any,
        api_key: Optional[str] = None,
        pause: Optional[float] = 0.0,
        address_field: Optional[str] = '',
    ) -> Any:
    """Geocode the addresses in a DataFrame, in place.

    Args:
        data: The DataFrame. Without ``address_field`` it needs
            ``street``, ``city``, ``state``, and ``zip_code`` columns.
        api_key: A Google Maps API key (default: ``get_google_maps_api_key``).
        pause: Seconds to wait between requests.
        address_field: A column holding whole addresses.

    Returns:
        The same DataFrame, with ``formatted_address``, ``latitude``,
        ``longitude``, ``state`` (overwritten with Google's code),
        ``state_name``, and ``county`` filled where Google finds the address.
    """
    googlemaps = _require('googlemaps')
    client = googlemaps.Client(key=api_key or get_google_maps_api_key())
    for position, (index, item) in enumerate(data.iterrows()):
        if position and pause:
            sleep(pause)
        address = item[address_field] if address_field else f'{item.street}, {item.city}, {item.state} {item.zip_code}'
        results = client.geocode(address)
        if not results:
            continue
        result = results[0]
        data.at[index, 'formatted_address'] = result['formatted_address']
        data.at[index, 'latitude'] = result['geometry']['location']['lat']
        data.at[index, 'longitude'] = result['geometry']['location']['lng']
        for component in result['address_components']:
            kind = component['types'][0] if component['types'] else ''
            if kind == 'administrative_area_level_1':
                data.at[index, 'state'] = component['short_name']
                data.at[index, 'state_name'] = component['long_name']
            elif kind == 'administrative_area_level_2':
                data.at[index, 'county'] = component['long_name']
    return data

_STATE_ZIP = re.compile(r'^([A-Z]{2})(?:\s+(\d{5}(?:-\d{4})?))?$')

def parse_formatted_address(formatted_address: str) -> Dict[str, str]:
    """Split a Google formatted address into street, city, state, and ZIP code.

    ``'1 Main St, Suite 5, Lacey, WA 98503, USA'`` gives street
    ``'1 Main St, Suite 5'``, city ``'Lacey'``, state ``'WA'``, and
    zipcode ``'98503'``. Parts that are not there are left out.
    """
    parts = [part.strip() for part in formatted_address.split(',') if part.strip()]
    if parts and parts[-1] in ('USA', 'United States'):
        parts = parts[:-1]
    parsed = {}
    match = _STATE_ZIP.match(parts[-1]) if parts else None
    if not match:
        return parsed
    parsed['state'] = match.group(1)
    if match.group(2):
        parsed['zipcode'] = match.group(2)
    if len(parts) >= 2:
        parsed['city'] = parts[-2]
    if len(parts) >= 3:
        parsed['street'] = ', '.join(parts[:-2])
    return parsed

def search_for_address(
        query: str,
        api_key: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
    """Find the address of a place by name with Google Places.

    Args:
        query: The text to search for, such as a business name and city.
        api_key: A Google Maps API key (default: ``get_google_maps_api_key``).
        fields: Place fields to request (default: the formatted address
            and location).

    Returns:
        The place's fields, with ``latitude`` and ``longitude`` and,
        from the formatted address, ``street``, ``city``, ``state``,
        ``zipcode``, and ``county`` (``''`` when unknown).

    Raises:
        IndexError: If no place matches.
    """
    googlemaps = _require('googlemaps')
    places = importlib.import_module('googlemaps.places')
    client = googlemaps.Client(key=api_key or get_google_maps_api_key())
    fields = fields or ['formatted_address', 'geometry/location/lat', 'geometry/location/lng']
    search = places.find_place(client, query, 'textquery')
    place = places.place(client, search['candidates'][0]['place_id'], fields=fields)
    result = dict(place['result'])
    candidate = {}
    geometry = result.pop('geometry', None)
    if geometry:
        candidate['latitude'] = geometry['location']['lat']
        candidate['longitude'] = geometry['location']['lng']
    if result.get('formatted_address'):
        candidate.update(parse_formatted_address(result['formatted_address']))
        candidate['county'] = ''
        if candidate.get('zipcode'):
            try:
                matches = _require('zipcodes').matching(candidate['zipcode'])
                candidate['county'] = matches[0]['county'] if matches else ''
            except (ImportError, ValueError, TypeError) as error:
                logger.debug('No county for %s: %s', candidate['zipcode'], error)
    return {**result, **candidate}

def get_transfer_distance(
        api_key: str,
        start: str,
        end: str,
        mode: str = 'driving',
    ) -> Tuple[int, int]:
    """The distance and travel time between two places.

    Args:
        api_key: A Google Maps API key.
        start: The origin, as ``'lat,long'`` or an address.
        end: The destination, likewise.
        mode: ``'driving'`` (default), ``'walking'``, ``'bicycling'``,
            or ``'transit'``.

    Returns:
        ``(meters, seconds)``.
    """
    googlemaps = _require('googlemaps')
    matrix = googlemaps.Client(key=api_key).distance_matrix(start, end, mode=mode)
    element = matrix['rows'][0]['elements'][0]
    return element['distance']['value'], element['duration']['value']

def get_transfer_route(
        api_key: str,
        start: str,
        end: str,
        departure_time: Optional[datetime] = None,
        mode: str = 'driving',
    ) -> Tuple[int, int, str]:
    """The route between two places.

    Args:
        api_key: A Google Maps API key.
        start: The origin, as ``'lat,long'`` or an address.
        end: The destination, likewise.
        departure_time: When to leave (default: now).
        mode: ``'driving'`` (default), ``'walking'``, ``'bicycling'``,
            or ``'transit'``.

    Returns:
        ``(meters, seconds, polyline)``, the polyline in Google's
        encoded format.
    """
    googlemaps = _require('googlemaps')
    directions = googlemaps.Client(key=api_key).directions(
        start, end, mode=mode, departure_time=departure_time or datetime.now(),
    )
    leg = directions[0]['legs'][0]
    return leg['distance']['value'], leg['duration']['value'], directions[0]['overview_polyline']['points']

__all__ = [
    'geocode_addresses', 'get_google_maps_api_key', 'get_state_data', 'get_state_population',
    'get_transfer_distance', 'get_transfer_route', 'initialize_googlemaps', 'parse_formatted_address',
    'search_for_address',
]
