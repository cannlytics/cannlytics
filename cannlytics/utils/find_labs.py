# -*- coding: utf-8 -*-
"""
Find Labs | Cannlytics
Copyright © 2021 Cannlytics
Author: Keegan Skeate <keegan@cannlytics.com>
Created: 1/10/2021

License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Resources:
    https://stackoverflow.com/questions/54416896/how-to-scrape-email-and-phone-numbers-from-a-list-of-websites
    https://hackersandslackers.com/scraping-urls-with-beautifulsoup/
    https://developers.google.com/maps/documentation/timezone/overview

Description:
    Find data points for all cannabis-testing labs using any existing
    information about the labs.
"""
from datetime import datetime
from math import isnan
from pandas import DataFrame
from phonenumbers import timezone, parse, format_number, PhoneNumberFormat
from .logistics import geocode_addresses, get_place_details
from .scraper import get_page_metadata, get_phone, get_email


def find_lab_data(lab):
    """Find as many data points as possible about a lab.
    Expects a default lab dictionary with at least the lab's name.
    Where a lab is represented as:
        {
            "name": "",
            "website": "",
            "image_url": "",
            "phone": "",
            "email": "",
            "street": "",
            "city": "",
            "state": "",
            "zip": "",
            "description": "",
            "hours": "",
            "theme_color": "",
            "timezone": "",
        }
    """

    # Format address if needed.
    if lab.get("formatted_address") and not lab.get("street"):
        try:
            address_parts = lab["formatted_address"].split(",")
            lab["street"] = address_parts[0]
            lab["city"] = address_parts[1].title().strip()
            lab["zip"] = address_parts[2].replace(lab["state"], "").strip()
        except IndexError:
            pass

    # Try to get the place details for the lab.
    try:
        details = get_place_details(lab["name"])
        lab = {**details, **lab}
    except IndexError:
        pass

    # TODO: Parse store hours.

    # Get the lab's website.
    if lab.get("website"):
        url = lab["website"]
        # TODO: Prepend http:// if necessary.
    else:
        print("TODO: Implement custom search for website")
        return

    # Try to get metadata from the lab's website.
    try:
        response, html, metadata = get_page_metadata(url)
        lab = {**lab, **metadata}
    except:
        pass

    # Try to find any email on the website.
    if not lab.get("email"):
        try:
            if not isnan(lab.get("email")):
                lab["email"] = get_email(html, response)
        except TypeError:
            pass

    # Try to find a phone number on the lab's website.
    if not lab.get("phone"):
        try:
            if not isnan(lab.get("phone")):
                lab["phone"] = get_phone(html, response)
        except TypeError:
            pass

    # Format any phone number and get it's timezone.
    try:
        number = parse(lab["phone"], "US")
        lab["phone"] = format_number(
            number,
            PhoneNumberFormat.NATIONAL,  # TODO: Handle international labs.
        )
        # lab["phone_number"] = # TODO: Format number for links
        lab["timezone"] = timezone.time_zones_for_number(number)[0]
        # Optional: Use Google timezone service.
        # https://developers.google.com/maps/documentation/timezone/overview
    except:
        pass

    # Optional: Get any contacts

    # Optional: Get analyses

    return lab


def clean_string_columns(df):
    """Clean string columns in a dataframe."""
    try:
        df.email = df.email.str.lower()
        df.website = df.website.str.lower()
    except AttributeError:
        pass
    str_columns = ["name", "trade_name", "city", "county"]
    for column in str_columns:
        try:
            df[column] = df[column].astype(str).str.title()
            df[column] = df[column].astype(str).str.replace("Llc", "LLC")
            df[column] = df[column].astype(str).str.replace("L.L.C.", "LLC")
            df[column] = df[column].astype(str).str.strip()
        except (AttributeError, KeyError):
            pass
    return df


def find_labs(labs, output_file=False):
    """Find data points for all labs in a list."""

    # Get data points for each lab.
    lab_data = []
    labs = DataFrame(labs)
    labs = clean_string_columns(labs)
    for index, row in labs.iterrows():
        values = row.to_dict()
        data = find_lab_data(values)
        lab_data.append(data)
        print("Found data for:", values["name"])

    # Geocode addresses.
    try:
        labs = DataFrame(lab_data)
        labs = geocode_addresses(labs)
    except:
        print(
            'Geocoding requires Firebase with Firestore document:\n\n\
            admin/google: { google_maps_api_key: "xyx" }\n\n\
            Initialize Firebase by setting GOOGLE_APPLICATION_CREDENTIALS\
            environment variable.'
        )

    # Save results
    if output_file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"./data/labs_{timestamp}.xlsx"
        labs.to_excel(output_file, index=False, sheet_name="Labs")

    return labs
