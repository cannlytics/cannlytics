"""
Tests for cannlytics.metrc: the transport layer and the models
==============================================================
The HTTP session is mocked, so no Metrc key or network is needed. These
tests cover what every one of the client's ~120 endpoint methods relies
on: authentication, URLs, parameters, timeouts, reconnection, errors,
logging, and clean-up. Live-sandbox checks belong in tests marked
``integration``.
"""
import logging
import os
import stat
import sys
from unittest.mock import MagicMock

import pytest
import requests

from cannlytics import metrc
from cannlytics.metrc import Metrc, MetrcAPIError, initialize_metrc
from cannlytics.metrc.models import Facility, Model, Plant

def _read(path):
    with open(path, encoding='utf-8') as file:
        return file.read()

def file_handlers():
    """The `metrc` logger's own file handlers (pytest adds capture handlers)."""
    return [h for h in logging.getLogger('metrc').handlers if isinstance(h, logging.FileHandler)]

def response(status=200, payload=None, text=''):
    reply = MagicMock()
    reply.status_code = status
    reply.text = text
    if payload is None and text:
        reply.json.side_effect = ValueError('not json')
    else:
        reply.json.return_value = payload
    reply.request.method = 'GET'
    reply.request.url = 'https://sandbox-api-ok.metrc.com/x'
    reply.request.body = None
    return reply

@pytest.fixture
def track():
    client = Metrc('vendor-key', 'user-key', primary_license='LIC-1', state='ok')
    client.session = MagicMock()
    client.session.request.return_value = response(payload=[])
    yield client
    client.close()

class TestConstruction:

    def test_basic_auth_and_sandbox_url(self):
        client = Metrc('vendor', 'user', state='ok')
        assert client.session.auth == ('vendor', 'user')
        assert client.base == 'https://sandbox-api-ok.metrc.com'
        client.close()

    def test_production_url(self):
        client = Metrc('vendor', 'user', state='ca', test=False)
        assert client.base == 'https://api-ca.metrc.com'
        client.close()

    def test_logging_is_off_by_default(self):
        client = Metrc('vendor', 'user')
        assert client.logs is False and client.logger is None and client.log_file is None
        client.close()

    def test_initialize_metrc_shortcut(self):
        client = initialize_metrc('vendor', 'user', primary_license='L', state='or')
        assert isinstance(client, Metrc) and client.primary_license == 'L'
        assert client.base == 'https://api-or.metrc.com' and client.logs is False
        client.close()

    def test_context_manager_closes_the_session(self):
        with Metrc('vendor', 'user') as client:
            client.session = MagicMock()
            session = client.session
        session.close.assert_called_once()

    def test_star_import_works(self):
        namespace = {}
        exec('from cannlytics.metrc import *', namespace)
        assert namespace['Metrc'] is Metrc
        assert all(isinstance(name, str) for name in metrc.__all__)

    def test_metrc_is_core(self, monkeypatch):
        # The client must not need Firebase (an optional extra).
        assert 'cannlytics.firebase' not in vars(sys.modules['cannlytics.metrc.models'])

class TestRequest:

    def test_every_request_carries_the_default_timeout(self, track):
        track.request('get', '/facilities/v1/')
        call = track.session.request.call_args
        assert call.args == ('GET', 'https://sandbox-api-ok.metrc.com/facilities/v1/')
        assert call.kwargs == {'json': None, 'params': None, 'timeout': 60}

    def test_timeout_is_configurable_per_client_and_per_call(self):
        client = Metrc('v', 'u', timeout=5)
        client.session = MagicMock()
        client.session.request.return_value = response(payload=[])
        client.request('get', '/x')
        assert client.session.request.call_args.kwargs['timeout'] == 5
        client.request('get', '/x', timeout=120)
        assert client.session.request.call_args.kwargs['timeout'] == 120

    def test_no_endpoint_method_bypasses_request(self):
        # Every HTTP call goes through Metrc.request, the one place that
        # sets the timeout. Checked on the syntax tree, not by grep.
        import ast
        import inspect
        tree = ast.parse(inspect.getsource(sys.modules['cannlytics.metrc.client']))
        [cls] = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Metrc']
        offenders = []
        for method in (n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name != 'request'):
            for node in ast.walk(method):
                if isinstance(node, ast.Attribute) and node.attr in {'get', 'post', 'put', 'delete', 'request'}:
                    owner = node.value
                    if isinstance(owner, ast.Attribute) and owner.attr == 'session':
                        offenders.append((method.name, node.lineno))
        assert offenders == []

    def test_a_timeout_propagates(self, track):
        track.session.request.side_effect = requests.exceptions.Timeout('slow')
        with pytest.raises(requests.exceptions.Timeout):
            track.get_facilities()

    def test_dropped_connection_rebuilds_the_session_once(self, track, monkeypatch):
        dead = track.session
        dead.request.side_effect = requests.exceptions.ConnectionError('reset')
        fresh = MagicMock()
        fresh.request.return_value = response(payload=[{'Id': 1}])
        monkeypatch.setattr('cannlytics.metrc.client.Session', lambda: fresh)
        assert track.request('get', '/x') == [{'Id': 1}]
        dead.close.assert_called_once()
        assert track.session is fresh and fresh.auth == ('vendor-key', 'user-key')
        assert fresh.request.call_args.kwargs['timeout'] == 60

    def test_the_builtin_connection_error_is_not_the_requests_one(self):
        # Why the pre-1.0.0 `except ConnectionError` never fired.
        assert not issubclass(requests.exceptions.ConnectionError, ConnectionError)

    def test_a_second_failure_is_raised(self, track, monkeypatch):
        track.session.request.side_effect = requests.exceptions.ConnectionError('reset')
        fresh = MagicMock()
        fresh.request.side_effect = requests.exceptions.ConnectionError('still down')
        monkeypatch.setattr('cannlytics.metrc.client.Session', lambda: fresh)
        with pytest.raises(requests.exceptions.ConnectionError):
            track.request('get', '/x')
        assert fresh.request.call_count == 1

    def test_non_json_success_returns_text(self, track):
        track.session.request.return_value = response(text='OK')
        assert track.request('post', '/x') == 'OK'

    @pytest.mark.parametrize('status', [400, 401, 403, 404, 413, 429, 500])
    def test_error_statuses_raise(self, track, status):
        track.session.request.return_value = response(status, payload={'Message': 'No.'})
        with pytest.raises(MetrcAPIError, match='No.') as caught:
            track.request('get', '/x')
        assert caught.value.response.status_code == status

class TestErrors:

    @pytest.mark.parametrize('payload, message', [
        ({'Message': 'Bad tag.'}, 'Bad tag.'),
        ({'message': 'lowercase'}, 'lowercase'),
        (['first', 'second'], 'first\nsecond'),
        ([{'row': 0, 'message': 'Row 0 bad.'}, {'row': 1, 'message': 'Row 1 bad.'}], 'Row 0 bad.\nRow 1 bad.'),
    ])
    def test_messages(self, payload, message):
        assert str(MetrcAPIError(response(400, payload=payload))) == message

    def test_unparseable_body(self):
        assert str(MetrcAPIError(response(500, text='<html>'))) == 'Unknown Metrc API error'

class TestParameters:

    def test_known_parameters_are_renamed_and_empty_ones_dropped(self, track):
        params = track.format_params(license_number='LIC-1', start='2026-01-01', end='')
        assert params == {'licenseNumber': 'LIC-1', 'lastModifiedStart': '2026-01-01'}

    def test_primary_license_is_the_fallback(self, track):
        track.get_employees()
        assert track.session.request.call_args.kwargs['params'] == {'licenseNumber': 'LIC-1'}
        track.get_employees(license_number='LIC-2')
        assert track.session.request.call_args.kwargs['params'] == {'licenseNumber': 'LIC-2'}

    def test_create_locations_default_is_not_shared_between_calls(self):
        import inspect
        assert inspect.signature(Metrc.create_locations).parameters['types'].default is None

class TestEndpoints:

    def test_get_facilities_returns_models(self, track):
        track.session.request.return_value = response(payload=[
            {'Name': 'Cannlytics Lab', 'License': {'Number': 'LIC-1', 'LicenseType': 'Testing'}},
        ])
        [facility] = track.get_facilities()
        assert isinstance(facility, Facility)
        assert facility.name == 'Cannlytics Lab'
        assert facility.license == {'number': 'LIC-1', 'license_type': 'Testing'}

    def test_get_facility_matches_by_license(self, track):
        track.session.request.return_value = response(payload=[
            {'Name': 'A', 'License': {'Number': 'LIC-1'}}, {'Name': 'B', 'License': {'Number': 'LIC-2'}},
        ])
        assert track.get_facility('LIC-2').name == 'B'
        assert track.get_facility('LIC-9') is None

class TestModels:

    def test_keys_become_snake_case_properties(self):
        plant = Plant(None, {'Id': 7, 'Label': 'TAG', 'StrainName': 'Blue Dream', 'GrowthPhase': 'Flowering'})
        assert (plant.uid, plant.label, plant.strain_name) == (7, 'TAG', 'Blue Dream')

    def test_to_dict_drops_the_client(self):
        plant = Plant(MagicMock(), {'Id': 7}, license_number='LIC-1')
        assert plant.to_dict() == {'id': 7}

    def test_from_dict(self):
        assert Model.from_dict(None, {'Id': 3}).uid == 3

    def test_missing_attribute_obeys_the_data_model(self):
        plant = Plant(None, {'Id': 7})
        assert not hasattr(plant, 'harvested_date')
        assert getattr(plant, 'harvested_date', 'n/a') == 'n/a'
        with pytest.raises(AttributeError, match='harvested_date'):
            plant.harvested_date  # noqa: B018 (the access is the test)
        with pytest.raises(KeyError):      # what it raised before 1.0.0
            plant.harvested_date  # noqa: B018

    def test_models_can_be_copied(self):
        import copy
        plant = Plant(None, {'Id': 7, 'Label': 'TAG'})
        assert copy.copy(plant).label == 'TAG'

class TestLogging:

    @pytest.fixture
    def logged(self):
        client = Metrc('vendor', 'user', logs=True)
        client.session = MagicMock()
        client.session.request.return_value = response(payload=[{'Id': 1}])
        yield client
        path = client.log_file
        client.close()
        if path and os.path.exists(path):
            os.remove(path)

    def test_the_root_logger_is_never_touched(self):
        root = logging.getLogger()
        before = (root.level, list(root.handlers))
        client = Metrc('vendor', 'user', logs=True)
        try:
            assert (root.level, list(root.handlers)) == before
            assert logging.getLogger('metrc').propagate is False
        finally:
            path = client.log_file
            client.close()
            os.remove(path)

    def test_requests_are_written_to_the_log_file(self, logged):
        logged.request('get', '/facilities/v1/')
        logged.close_logs()
        text = _read(logged.log_file)
        assert 'Metrc initialized.' in text and 'Status code: 200' in text and '[{"Id": 1}]' in text

    @pytest.mark.skipif(os.name == 'nt', reason='POSIX permission bits')
    def test_log_file_is_owner_only(self, logged):
        # Request bodies can carry patient identifiers; /tmp is shared.
        assert stat.S_IMODE(os.stat(logged.log_file).st_mode) == 0o600

    def test_api_keys_are_never_logged(self, logged):
        logged.request('get', '/x')
        logged.close_logs()
        text = _read(logged.log_file)
        assert 'vendor' not in text and 'user' not in text.replace('user_api_key', '')

    def test_close_releases_the_handler_and_is_repeatable(self, logged):
        assert len(file_handlers()) == 1
        logged.close()
        logged.close()
        assert file_handlers() == []

    def test_two_clients_do_not_pile_up_handlers(self):
        paths = []
        for _ in range(3):
            client = Metrc('vendor', 'user', logs=True)
            paths.append(client.log_file)
            client.close()
        assert file_handlers() == []
        for path in paths:
            os.remove(path)
