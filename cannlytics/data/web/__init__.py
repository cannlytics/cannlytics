"""
Cannlytics Web Data Initialization | Cannlytics
Copyright (c) 2023-2025 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/2/2023
Updated: 9/28/2026
"""
# Dependency guard.
#
# This block previously read `except ImportError: pass`, which swallowed
# the failure entirely: the module imported successfully, exported
# nothing, and the user hit `AttributeError: module has no attribute
# ...` with no hint that a missing extra was the cause. Fail loudly and
# name the extra instead.
try:
    from .web import (
        format_params,
        get_page_metadata,
        get_page_description,
        get_page_image,
        get_page_favicon,
        get_page_theme_color,
        get_page_phone_number,
        get_page_email,
        initialize_selenium,
        download_google_drive_file,
        download_file_from_url,
        download_file_with_selenium,
    )

    __all__ = [
        'format_params',
        'get_page_metadata',
        'get_page_description',
        'get_page_image',
        'get_page_favicon',
        'get_page_theme_color',
        'get_page_phone_number',
        'get_page_email',
        'initialize_selenium',
        'download_google_drive_file',
        'download_file_from_url',
        'download_file_with_selenium',
    ]
except ImportError as _err:  # pragma: no cover
    raise ImportError(
        'cannlytics.data.web requires the `web` extra. Install it with:'
        '\n\n    pip install "cannlytics[web]"\n'
    ) from _err
