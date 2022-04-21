"""
Get Cannabis Data for Maine
Copyright (c) 2021 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 9/23/2021
Updated: 10/5/2021
License: MIT License <https://github.com/cannlytics/cannlytics-ai/blob/main/LICENSE>

Data Sources:
    
    - Maine Adult-Use Cannabis Data: https://www.maine.gov/dafs/omp/open-data/adult-use

Resources:
    
    - Tableau Scraper: https://github.com/bertrandmartel/tableau-scraping

"""

from tableauscraper import TableauScraper as TS

# Get sales data.
sales_url = 'https://public.tableau.com/views/AdultUseRetailSales/AtaGlance?:embed=y&:display_count=n&:origin=viz_share_link'
ts = TS()
ts.loads(sales_url)
wb = ts.getWorkbook()
sales_data = wb.getWorksheet('Total to Date').data
product_data = wb.getWorksheet('Product Trend').data

# Get licensees data. (FIXME:)
licensees_url = 'https://public.tableau.com/views/AdultUseEstablishments/ApplicantandLicenseeSearch?:embed=y&:display_count=n&:origin=viz_share_link'
ts = TS()
ts.loads(licensees_url)
wb = ts.getWorkbook()

# Get counties that permit cannabis.
county_url = 'https://public.tableau.com/views/AdultUseMunicipalityOptIn/Municipality?:embed=y&:display_count=n&:origin=viz_share_link'


# ------
# SCRAP
# ------

# # switch to daily
# wb = wb.setParameter("Escala de Tempo DM Simp 4", "Dia")

# # show dataframe with daily data
# ws = wb.getWorksheet("Simples Demanda Máxima Semana Dia")
# print(ws.data)

# # switch to daily
# wb = wb.setParameter(
#     "Início Primeiro Período DM Simp 4", "01/01/2017")

# # show dataframe with daily data from 01/01/2017
# ws = wb.getWorksheet("Simples Demanda Máxima Semana Dia")
# print(ws.data)