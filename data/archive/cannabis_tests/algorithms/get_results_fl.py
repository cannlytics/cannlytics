"""
Florida cannabis licenses and lab results
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 5/18/2023
Updated: 5/18/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description:

    Archive Florida cannabis license data.

Data Sources:

    - [Florida Labs](https://knowthefactsmmj.com/cmtl/)
    - [Florida Licenses](https://knowthefactsmmj.com/mmtc/)

Resources:

    - 'https://www.reddit.com/r/FLMedicalTrees/search/?q=COA'
    - https://www.reddit.com/r/FLMedicalTrees/comments/1272per/anyone_have_batch_s_they_can_share_for_our/
    - https://www.reddit.com/r/FLMedicalTrees/comments/vdnpqf/coa_accumulation/

"""
# Standard imports:
from datetime import datetime
import os
from time import sleep
from typing import Optional

# External imports:
from bs4 import BeautifulSoup
from cannlytics.utils.constants import DEFAULT_HEADERS
from cannlytics.data.gis import geocode_addresses
from dotenv import dotenv_values
import pandas as pd
import requests

# Selenium imports.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

# Specify where your data lives.
DATA_DIR = '../data/fl'
ENV_FILE = '../../../../.env'


#-----------------------------------------------------------------------
# Parse Kaycha Labs COAs.
#-----------------------------------------------------------------------

# Initialize Selenium.
try:
    service = Service()
    options = Options()
    options.add_argument('--window-size=1920,1200')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options, service=service)
except:
    driver = webdriver.Edge()

# Load the license page.
url = 'https://yourcoa.com/company/company?t=Jungle+Boys'
driver.get(url)

# Find all <a> tags with "coa-download" in the href attribute
links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="coa-download"]')

# Extract the href attribute from each link
download_links = [link.get_attribute('href') for link in links]
download_links = list(set(download_links))

# Print the download links
for link in download_links:
    print(link)



# TODO: Get a list of Florida companies.

# FIND:
# url = 'https://yourcoa.com/company/company?t=Planet+13+Florida+Inc'
# Surterra Wellness
# Sunburn
# Sanctuary Cannabis
# Insa - Cannabis for Real Life
# House of Platinum Cannabis
# GTI (Rise Dispensaries) [privat?]
# Trulieve [private?]
# Gold Leaf
# Cookies Florida, Inc.
# Liberty Health Sciences, FL (3,924+ COAs)
url = 'https://yourcoa.com/company/company?t=Cookies+Florida%2C+Inc.'
url = 'https://yourcoa.com/company/company?t=Liberty+Health+Sciences%2C+FL'

# Sunnyside COAs (886+ COAs).
url = 'https://yourcoa.com/company/company?t=Sunnyside'

# Curaleaf COAs (8,905+ COAs)
url = 'https://yourcoa.com/company/company/17?t=CURALEAF+FLORIDA+LLC'

# Fluent (70+ COAs).
url = 'https://yourcoa.com/company/company?t=Fluent'

# Grow Health (28 COAs).
url = 'https://yourcoa.com/company/company/303?t=GrowHealthy'

# Cannabis (3 COAs).
url = 'https://yourcoa.com/company/company?t=Cannabist'

# VidaCann (4 COAs).
url = 'https://yourcoa.com/company/company?t=VidaCann'

# Jungle Boys (2 COAs).
url = 'https://yourcoa.com/company/company?t=Jungle+Boys'

# Green Dragon (0 COAs).
url = 'https://yourcoa.com/company/company?t=Green+Dragon'

# Muv (0 COAs).
url = 'https://yourcoa.com/company/company?t=Muv'

# Milk and Cookies (0 COAs).
url = 'https://yourcoa.com/company/company?t=Cookies'

# Ayr Wellness (0 COAs).
url = 'https://yourcoa.com/company/company?t=Ayr'

# Revolution (0 COAs).
url = 'https://yourcoa.com/company/company?t=Revolution'


# TODO: Create slugs for each company

# Get a company's slug.
slug = 'Sunnyside'

# Request each page until the maximum is reached.
page = 0
iterate = True
coa_urls = []
while iterate:

    # Get the first/next page of COAs.
    page += 1
    url = f'https://yourcoa.com/company/company?t={slug}&page={page}'
    response = requests.get(url, headers=DEFAULT_HEADERS)
    if response.status_code != 200:
        print(f"Request failed with status {response.status_code}")

    # Get the download URLs.
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    links = [x['href'] for x in links if 'coa-download' in x['href']]
    links = list(set(links))
    coa_urls.extend(links)

    # See if the next button is disabled to know when to stop iterating.
    next_element = soup.find(class_='next')
    if not next_element:
        iterate = False
    elif next_element and 'disabled' in next_element.get('class', []):
        iterate = False

    # Otherwise pause to respect the server.
    sleep(3)


# TODO: Get all COA PDF links on a given page.


# TODO: Download each PDF.


# TODO: Begin to parse lab results from the PDFs!




# TODO: Parse a COA from a URL.
url = 'https://yourcoa.com/coa/coa-download?sample=DA20708002-010'
url = 'https://yourcoa.com/coa/coa-download?sample=DA30314006-007-mrk'
url = 'https://www.trulieve.com/files/lab-results/35603_0001748379.pdf'
# Broken: https://yourcoa.com/company/company?t=Green+Ops+FL+OpCo+LLC


#-----------------------------------------------------------------------
# ACS Labs
#-----------------------------------------------------------------------

# VIA Trulieve URL.
url = 'https://www.trulieve.com/files/lab-results/18362_0003059411.pdf'

# ACS Labs URL.
url = 'https://portal.acslabcannabis.com/qr-coa-view?salt=QUFEQzA2Mi0wNjAzMjItOTlQUi1SMzUtMDcxNDIwMjI='


#-----------------------------------------------------------------------
# TerpLife Labs
#-----------------------------------------------------------------------

# TODO: Get COAs from TerpLife Labs
url = 'https://www.terplifelabs.com/coa/'

# TODO: Search for strains, e.g. ChryTop


# TODO: Download all PDFs.


# TODO: Extract data from the PDFs.



#-----------------------------------------------------------------------
# US Cannalytics Labs
#-----------------------------------------------------------------------

us_cannalytics_coa = 'https://www.vidacann.com/wp-content/uploads/2023/04/Batch-0653-0603-5236-3992-Lot-8391-232004.pdf'


#-----------------------------------------------------------------------
# Method Testing Labs
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
# Modern Canna
#-----------------------------------------------------------------------

# Parse COAs from URL.
url = 'https://moderncanna.com/coa/GD22003-07.pdf'
url = 'https://moderncanna.com/coa/GF23007-01.pdf'



#-----------------------------------------------------------------------
# 710 Labs
#-----------------------------------------------------------------------

# Get list of COA lists.
lists_url = 'https://support.theflowery.co/hc/en-us/sections/7240468576283-Drop-Information'

# Get COA URLs.
list_url = 'https://support.theflowery.co/hc/en-us/articles/14986163938459-Drop-20-05-01-23-'





#-----------------------------------------------------------------------
# Lab result analysis.
#-----------------------------------------------------------------------

# Heatmap of lab results throughout the state.
