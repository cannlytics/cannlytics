"""
Augment Plants Dataset
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/29/2022
Updated: 1/31/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: This script calculates various statistics from the plants data using
relevant fields from the lab results, licensees, inventories,
inventory types, sales, and strains datasets.

Data sources:

    - WA State Traceability Data January 2018 - November 2021
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=1
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=2

Data Guide:

    - Washington State Leaf Data Systems Guide
    https://lcb.wa.gov/sites/default/files/publications/Marijuana/traceability/WALeafDataSystems_UserManual_v1.37.5_AddendumC_LicenseeUser.pdf

Resources:

    - Plotting data on a map
    https://matplotlib.org/basemap/users/examples.html

"""
# Standard imports.
import gc
import json

# External imports.
import pandas as pd

# Internal imports
from utils import get_number_of_lines

#------------------------------------------------------------------------------
# Read plants data.
#------------------------------------------------------------------------------

# Define useful metadata about the plants data.
# plants_size = get_number_of_lines('D:/leaf-data/Plants_0.csv')
plants_size = 30_538_973
plants_datatypes = {
    'mme_id': 'string',
}
plants_date_fields = [
    'created_at',
    'updated_at',
]
plants_columns = list(plants_datatypes.keys()) + plants_date_fields

# Example:
# plants = pd.read_csv(
#     'D:/leaf-data/Plants_0.csv',
#     sep='\t',
#     encoding='utf-16',
#     usecols=plants_columns,
#     dtype=plants_datatypes,
#     parse_dates=plants_date_fields,
#     # skiprows=skiprows,
#     nrows=1000,
# )

#------------------------------------------------------------------------------
# Count the number of plants by date by licensee.
# Future work: Determine which licensees are operating at any given time.
#------------------------------------------------------------------------------

# Specify the time range to calculate statistics.
# time_range = pd.date_range(start='2018-02-01', end='2021-11-30')
# time_range = pd.date_range(start='2019-02-01', end='2021-11-30')
# time_range = pd.date_range(start='2019-07-01', end='2021-11-30')
time_range = pd.date_range(start='2021-02-01', end='2021-11-30')

# Read all plants, then iterate over dates.
plants = pd.read_csv(
    'D:/leaf-data/Plants_0.csv',
    sep='\t',
    encoding='utf-16',
    usecols=plants_columns,
    dtype=plants_datatypes,
    parse_dates=plants_date_fields,
    # skiprows=skiprows,
    # nrows=chunk_size,
)

# Iterate over the days, counting plants in total and by licensee.
daily_plant_count = []
plant_panel = []

for date in time_range:

    day = date.date()

    # Count the total number of plants.
    current_plants = plants.loc[
        (plants.created_at.dt.date >= day) &
        (plants.updated_at.dt.date <= day)
    ]
    total_plants = len(current_plants)

    # Count the total plants by licensee.
    # Note: May be overly complex as was originally written for shards.
    licensees = list(current_plants.mme_id.unique())
    licensees_total_plants = {}
    for licensee in licensees:
        licensee_plants = current_plants.loc[current_plants['mme_id'] == licensee]
        licensees_total_plants[licensee] = len(licensee_plants)
    
    # Keep track of the totals counted for the date.
    daily_plant_count.append([date, total_plants, len(licensees)])
    for mme_id, count in licensees_total_plants.items():
        plant_panel.append({
            'date': date,
            'mme_id': mme_id,
            'total_plants': count,
        })
    print('Calculated total for', day, total_plants)

# Clean up unused variables.
try:
    del current_plants
    del licensee_plants
    del plants
    gc.collect()
except NameError:
    pass

# Save the daily total series.
daily_plant_data = pd.DataFrame(daily_plant_count)
daily_plant_data.columns = ['date', 'total_plants', 'total_cultivators']
daily_plant_data.to_csv('D:/leaf-data/augmented/daily_plant_data_2020c.csv')

# Save the daily panel series.
panel_plant_data = pd.DataFrame(plant_panel)
panel_plant_data.to_csv('D:/leaf-data/augmented/daily_licensee_plant_data_2020c.csv')


#------------------------------------------------------------------------------
# Augment plants data with licensee data.
#------------------------------------------------------------------------------

# TODO: Add latitude and longitude for each day / licensee observation.
# licensees_file_name = 'D:/leaf-data/augmented/augmented-washington-state-licensees.csv'
# licensee_fields = {
#     'code': 'string',
#     'latitude': 'string',
#     'longitude': 'string',
#     'name': 'string',
# }
# licensees = pd.read_csv(
#     licensees_file_name,
#     usecols=list(licensee_fields.keys()),
#     dtype=licensee_fields,
# )
# geocoded_plant_data = pd.merge(
#     left=panel_plant_data,
#     right=licensees,
#     how='left',
#     left_on='mme_id',
#     right_on='code'
# )
# geocoded_plant_data = geocoded_plant_data.loc[
#     (~geocoded_plant_data.longitude.isnull()) &
#     (~geocoded_plant_data.latitude.isnull())
# ]


#------------------------------------------------------------------------------
# Future work: Augment plants data with sales data.
#------------------------------------------------------------------------------

# sales_0_size = get_number_of_lines('D:/leaf-data/Sales_0.csv')
# sales_1_size = get_number_of_lines('D:/leaf-data/Sales_1.csv')
# sales_2_size = get_number_of_lines('D:/leaf-data/Sales_2.csv')
# sales_items_0_size = get_number_of_lines('D:/leaf-data/SaleItems_0.csv')
# sales_items_1_size = get_number_of_lines('D:/leaf-data/SaleItems_1.csv')
# sales_items_2_size = get_number_of_lines('D:/leaf-data/SaleItems_2.csv')
# sales_items_3_size = get_number_of_lines('D:/leaf-data/SaleItems_3.csv')
# sales_0_size = 100_000_001
# sales_1_size = 100_000_001
# sales_2_size = 28_675_356
# sales_items_0_size = 90_000_001
# sales_items_1_size = 90_000_001
# sales_items_2_size = 90_000_001
# sales_items_3_size = 76_844_111


#------------------------------------------------------------------------------
# Future work: Augment plants data with transfer data.
#------------------------------------------------------------------------------

# inventory_types_size = get_number_of_lines('D:/leaf-data/InventoryTypes_0.csv')
# inventory_types_size = 57_016_229

# batches_size = get_number_of_lines('D:/leaf-data/Batches_0.csv')
# batches_size = 47_292_622


#------------------------------------------------------------------------------
# TODO: Plot weekly and monthly average number of plants.
#------------------------------------------------------------------------------




#------------------------------------------------------------------------------
# TODO: Video Plot of Plant Production (The Plant Canopy).
#------------------------------------------------------------------------------


# SCRAP

# from datetime import datetime, timedelta
# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs

# fig = plt.figure(figsize=(19.2, 10.8))
# ax = plt.axes(
#     projection=ccrs.Mercator(
#         central_longitude=0,  
#         min_latitude=-65,
#         max_latitude=70
#     )
# )
# ax.background_img(name='BM', resolution='low')
# ax.set_extent([-170, 179, -65, 70], crs=ccrs.PlateCarree())


#  Plot data bubbles on the map.
# colors = {
#     'AI': '#02b3e4',
#     'Aut Sys': '#f95c3c' ,
#     'Business': '#ff5483',
#     'Developers': '#ecc81a'
# }
# for school, school_data in grads.groupby('School'):

#     grad_counts = school_data.groupby(['Long', 'Lat']).count()
    
#     # Get lists for longitudes and latitudes of graduates
#     index = list(grad_counts.index)
#     longs = [each[0] for each in index]
#     lats = [each[1] for each in index]
#     sizes = grad_counts['School']*10
#     school_name = ' '.join(school.split()[2:])
    
#     ax.scatter(
#         longs,
#         lats,
#         s=sizes,
#         color=colors[school_name],
#         alpha=0.8,
#         transform=ccrs.PlateCarree()
#     )

#  Add text to the figure.
# fontname = 'Open Sans'
# fontsize = 28
# # Positions for the date and grad counter
# date_x = -53
# date_y = -50
# date_spacing = 65
# # Positions for the school labels
# name_x = -70
# name_y = -60      
# name_spacing = {'Developers': 0,
#                 'AI': 55,
#                 'Business': 1.9*55,
#                 'Aut Sys': 3*55}
# # Date text
# ax.text(date_x, date_y, 
#         f"{date.strftime('%b %d, %Y')}", 
#         color='white',
#         fontname=fontname, fontsize=fontsize*1.3,
#         transform=ccrs.PlateCarree())
# # Total grad counts
# ax.text(date_x + date_spacing, date_y, 
#         "GRADUATES", color='white',
#         fontname=fontname, fontsize=fontsize,
#         transform=ccrs.PlateCarree())
# ax.text(date_x + date_spacing*1.7, date_y, 
#         f"{grads.groupby(['Long', 'Lat']).count()['School'].sum()}",
#         color='white', ha='left',
#         fontname=fontname, fontsize=fontsize*1.3,
#         transform=ccrs.PlateCarree())
# for school_name in ['Developers', 'AI', 'Business', 'Aut Sys']:
#     ax.text(name_x + name_spacing[school_name], 
#             name_y, 
#             school_name.upper(), ha='center',
#             fontname=fontname, fontsize=fontsize*1.1,
#             color=colors[school_name],
#             transform=ccrs.PlateCarree())
# # Expands image to fill the figure and cut off margins
# fig.tight_layout(pad=-0.5)


# Create a function to create the chart for each date.

# def make_grads_map(date, data, ax=None, resolution='low'):
    
#     if ax is None:
#         fig = plt.figure(figsize=(19.2, 10.8))
#         ax = plt.axes(projection=ccrs.Mercator(
#             min_latitude=-65,
#             max_latitude=70,
#         ))
    
#     ax.background_img(name='BM', resolution=resolution)
#     ax.set_extent([-170, 179, -65, 70], crs=ccrs.PlateCarree())
#     grads = data[data['Grad Date'] < date] 
    

# # Generate an image for each day between start_date and end_date.
# start_date = datetime(2017, 1, 1)
# end_date = datetime(2018, 3, 15)
# fig = plt.figure(figsize=(19.2, 10.8))
# ax = plt.axes(projection=ccrs.Mercator(
#     min_latitude=-65,
#     max_latitude=70,
# ))
# for ii, days in enumerate(range((end_date - start_date).days)):
#     date = start_date + timedelta(days)
#     ax = make_grads_map(date, df, ax=ax, resolution='full')
#     fig.tight_layout(pad=-0.5)
#     fig.savefig(
#         f"frames/frame_{ii:04d}.png",
#         dpi=100,     
#         frameon=False,
#         facecolor='black'
#     )
#     ax.clear()


#------------------------------------------------------------------------------
# TODO: Create a video from each image.
# ffmpeg -framerate 21 -i figures/canopy-%4d.png -c:v h264 -r 30 -s 1920x1080 ./canopy.mp4
# Optional: Add Vivaldi music!
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Optional: Explore interactive plotting with folium
# https://nbviewer.org/github/python-visualization/folium/blob/main/examples/GeoJSONMarker.ipynb
# https://python-visualization.github.io/folium/quickstart.html
#------------------------------------------------------------------------------

