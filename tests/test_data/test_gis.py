"""
Tests for GIS tools
===================
`cannlytics.data.gis` with fake `fredapi`, `googlemaps`, and `zipcodes`
modules: no network, no API keys, no optional libraries.
"""
import sys
import types

import pandas as pd
import pytest

from cannlytics.data import gis as gis_package
from cannlytics.data.gis import gis

@pytest.fixture
def fakes(monkeypatch):
    """Install fake FRED, Google Maps, and ZIP-code libraries."""
    state = {'series': pd.Series(dtype=float), 'geocode': [], 'place': {}, 'counties': {}, 'clients': []}

    class Fred:
        def __init__(self, api_key=None):
            state['fred_key'] = api_key

        def get_series(self, code, start=None, end=None):
            state['code'] = code
            return state['series']

    class Client:
        def __init__(self, key=None):
            state['clients'].append(key)

        def geocode(self, address):
            state.setdefault('addresses', []).append(address)
            return state['geocode']

        def distance_matrix(self, start, end, mode='driving'):
            return {'rows': [{'elements': [{'distance': {'value': 12_345}, 'duration': {'value': 900}}]}]}

        def directions(self, start, end, mode='driving', departure_time=None):
            return [{'legs': [{'distance': {'value': 1_000}, 'duration': {'value': 60}}], 'overview_polyline': {'points': 'abc'}}]

    places = types.ModuleType('googlemaps.places')
    places.find_place = lambda client, query, kind: {'candidates': [{'place_id': 'P1'}]}
    places.place = lambda client, place_id, fields=None: {'result': dict(state['place'])}
    googlemaps = types.ModuleType('googlemaps')
    googlemaps.Client, googlemaps.places = Client, places
    fredapi = types.ModuleType('fredapi')
    fredapi.Fred = Fred
    zipcodes = types.ModuleType('zipcodes')
    zipcodes.matching = lambda z: [{'county': state['counties'][z]}] if z in state['counties'] else []
    for name, module in (('fredapi', fredapi), ('googlemaps', googlemaps), ('googlemaps.places', places), ('zipcodes', zipcodes)):
        monkeypatch.setitem(sys.modules, name, module)
    monkeypatch.setenv('GOOGLE_MAPS_API_KEY', 'KEY')
    return state

class TestImport:

    def test_imports_without_any_extra_and_all_lists_names(self):
        assert all(isinstance(name, str) and hasattr(gis_package, name) for name in gis_package.__all__)

    def test_a_missing_library_names_the_extra(self, monkeypatch):
        monkeypatch.setitem(sys.modules, 'fredapi', None)
        with pytest.raises(ImportError, match=r'cannlytics\[utils\]'):
            gis.get_state_data('wa', 'POP')

class TestApiKey:

    def test_environment_first(self, monkeypatch):
        monkeypatch.setenv('GOOGLE_MAPS_API_KEY', 'FROM_ENV')
        assert gis.get_google_maps_api_key() == 'FROM_ENV'

    def test_env_file_is_read_without_changing_the_environment(self, monkeypatch, tmp_path):
        monkeypatch.delenv('GOOGLE_MAPS_API_KEY', raising=False)
        (tmp_path / '.env').write_text('GOOGLE_MAPS_API_KEY=FROM_FILE\nOTHER=1\n')
        monkeypatch.chdir(tmp_path)
        assert gis.get_google_maps_api_key() == 'FROM_FILE'
        import os
        assert 'GOOGLE_MAPS_API_KEY' not in os.environ and 'OTHER' not in os.environ

    def test_nothing_anywhere_names_every_place_looked(self, monkeypatch, tmp_path):
        monkeypatch.delenv('GOOGLE_MAPS_API_KEY', raising=False)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(gis, '_key_from_secret_manager', lambda: (_ for _ in ()).throw(RuntimeError('no creds')))
        monkeypatch.setattr(gis, '_key_from_firestore', lambda: None)
        with pytest.raises(RuntimeError, match='Secret Manager or Firestore'):
            gis.get_google_maps_api_key()

    def test_secret_manager_before_firestore(self, monkeypatch, tmp_path):
        monkeypatch.delenv('GOOGLE_MAPS_API_KEY', raising=False)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(gis, '_key_from_secret_manager', lambda: 'SECRET')
        monkeypatch.setattr(gis, '_key_from_firestore', lambda: pytest.fail('Firestore consulted first'))
        assert gis.get_google_maps_api_key() == 'SECRET'

class TestFred:

    def test_one_observation_by_position_works_on_a_date_index(self, fakes):
        # pandas 3 no longer reads series[0] as "first" on a date index.
        fakes['series'] = pd.Series([7_812.0], index=pd.to_datetime(['2025-01-01']))
        assert gis.get_state_data('wa', 'pop') == 7_812.0 and fakes['code'] == 'WAPOP'

    def test_population_scales_formats_and_skips_missing(self, fakes):
        fakes['series'] = pd.Series([7_812.88, float('nan')], index=pd.to_datetime(['2025-01-01', '2026-01-01']))
        record = gis.get_state_population('wa')
        assert record == {'population': 7_812_880, 'population_formatted': '7,812,880', 'population_source_code': 'WAPOP',
                          'population_source': 'https://fred.stlouisfed.org/series/WAPOP', 'population_at': '2025-01-01'}

class TestAddresses:

    @pytest.mark.parametrize('text, parsed', [
        ('1 Main St, Lacey, WA 98503, USA', {'street': '1 Main St', 'city': 'Lacey', 'state': 'WA', 'zipcode': '98503'}),
        ('1 Main St, Suite 5, Lacey, WA 98503-1234, USA', {'street': '1 Main St, Suite 5', 'city': 'Lacey', 'state': 'WA', 'zipcode': '98503-1234'}),
        ('Lacey, WA, USA', {'city': 'Lacey', 'state': 'WA'}),
        ('Somewhere far away', {}), ('', {}),
    ])
    def test_parse_formatted_address(self, text, parsed):
        assert gis.parse_formatted_address(text) == parsed

    def test_search_for_address(self, fakes):
        fakes['place'] = {'formatted_address': '1 Main St, Lacey, WA 98503, USA', 'geometry': {'location': {'lat': 47.0, 'lng': -122.8}}}
        fakes['counties'] = {'98503': 'Thurston County'}
        result = gis.search_for_address('Cannlytics Lacey')
        assert result['latitude'] == 47.0 and result['city'] == 'Lacey' and result['county'] == 'Thurston County'
        assert 'geometry' not in result and fakes['clients'] == ['KEY']

    def test_geocode_in_place(self, fakes):
        fakes['geocode'] = [{'formatted_address': 'F', 'geometry': {'location': {'lat': 1.0, 'lng': 2.0}},
                             'address_components': [{'types': ['administrative_area_level_1'], 'short_name': 'WA', 'long_name': 'Washington'},
                                                    {'types': ['administrative_area_level_2'], 'short_name': 'T', 'long_name': 'Thurston County'}]}]
        data = pd.DataFrame({'street': ['1 Main St'], 'city': ['Lacey'], 'state': ['wa'], 'zip_code': ['98503']}, index=['a'])
        out = gis.geocode_addresses(data)
        assert out is data and data.loc['a', 'state'] == 'WA' and data.loc['a', 'county'] == 'Thurston County'
        assert fakes['addresses'] == ['1 Main St, Lacey, wa 98503']

    def test_distance_is_meters_and_route_is_a_triple(self, fakes):
        assert gis.get_transfer_distance('K', 'a', 'b') == (12_345, 900)
        assert gis.get_transfer_route('K', 'a', 'b') == (1_000, 60, 'abc')
