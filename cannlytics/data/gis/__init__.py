"""
Cannlytics GIS Data Initialization | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/2/2023
Updated: 6/12/2026
"""
# Dependency guard.
#
# This block previously read `except ImportError: pass`, which swallowed
# the failure entirely: the module imported successfully, exported
# nothing, and the user hit `AttributeError: module has no attribute
# ...` with no hint that a missing extra was the cause. Fail loudly and
# name the extra instead.
try:
    from .gis import (
        get_google_maps_api_key,
        get_state_data,
        get_state_population,
        geocode_addresses,
        search_for_address,
        get_transfer_distance,
        get_transfer_route,
        initialize_googlemaps,
    )

    __all__ = [
        get_google_maps_api_key,
        get_state_data,
        get_state_population,
        geocode_addresses,
        search_for_address,
        get_transfer_distance,
        get_transfer_route,
        initialize_googlemaps,
    ]
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        'cannlytics.data.gis requires the `utils` extra. Install it with:'
        '\n\n    pip install "cannlytics[utils]"\n'
    ) from _err