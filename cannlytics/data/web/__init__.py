"""
Cannlytics Web Data Initialization | Cannlytics
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 7/2/2023
Updated: 7/2/2023
"""
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
        find_company_address,
        find_company_linkedin,
        find_company_url,
        download_google_drive_file,
    )

    __all__ = [
        format_params,
        get_page_metadata,
        get_page_description,
        get_page_image,
        get_page_favicon,
        get_page_theme_color,
        get_page_phone_number,
        get_page_email,
        find_company_address,
        find_company_linkedin,
        find_company_url,
        download_google_drive_file,
    ]
except ImportError:
    pass
