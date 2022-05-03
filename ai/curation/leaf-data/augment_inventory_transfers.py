"""
Augment inventory transfers data.
Copyright (c) 2022 Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 1/29/2022
Updated: 1/29/2022
License: MIT License <https://opensource.org/licenses/MIT>

Description: This script calculates various statistics from the inventory
transfers data.

Data sources:

    - WA State Traceability Data January 2018 - November 2021
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=1
    https://lcb.app.box.com/s/e89t59s0yb558tjoncjsid710oirqbgd?page=2

Data Guide:

    - Washington State Leaf Data Systems Guide
    https://lcb.wa.gov/sites/default/files/publications/Marijuana/traceability/WALeafDataSystems_UserManual_v1.37.5_AddendumC_LicenseeUser.pdf

Data available at:

    - https://cannlytics.com/data/market/augmented-washington-state-sales
"""
# Standard imports.
import gc
import json

# External imports.
import pandas as pd

# Internal imports
from utils import get_number_of_lines


#------------------------------------------------------------------------------
# Read inventory transfer data.
#------------------------------------------------------------------------------

# TODO: Read in the transfers.

file_name = 'InventoryTransfers_0.csv'

# TODO: Match the transfers with their items.

file_name = 'InventoryTransferItems_0.csv'


#------------------------------------------------------------------------------
# TODO: Augment transfer data with licensee data.
#------------------------------------------------------------------------------

# transfers_size = get_number_of_lines('D:/leaf-data/InventoryTransfers_0.csv')
transfers_size = 1_959_813

# transfer_items_size = get_number_of_lines('D:/leaf-data/InventoryTransferItems_0.csv')
transfer_items_size = 28_076_179


#------------------------------------------------------------------------------
# TODO: Analysis of inventory transfers.
#------------------------------------------------------------------------------

# Who is transferring what to whom?


# Data Points: Calculate travel time and distance of planned route.

# Figure: Create contrail map of all transfers.

# Figure: Create contrail map of each specific type of transfer.

# Figure: Calculate daily miles travelled (and time travelled).

# Statistic: Calculate monthly and yearly miles travelled (and time travelled).


#------------------------------------------------------------------------------
# TODO: Contrails Map
#------------------------------------------------------------------------------

"""
TODO: Adapt to plot transfers
draw Atlantic Hurricane Tracks for storms that reached Cat 4 or 5.
part of the track for which storm is cat 4 or 5 is shown red.
ESRI shapefile data from http://nationalatlas.gov/mld/huralll.html
"""
# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
# # Lambert Conformal Conic map.
# m = Basemap(llcrnrlon=-100.,llcrnrlat=0.,urcrnrlon=-20.,urcrnrlat=57.,
#             projection='lcc',lat_1=20.,lat_2=40.,lon_0=-60.,
#             resolution ='l',area_thresh=1000.)
# # read shapefile.
# shp_info = m.readshapefile('../../../examples/huralll020','hurrtracks',drawbounds=False)
# # find names of storms that reached Cat 4.
# names = []
# for shapedict in m.hurrtracks_info:
#     cat = shapedict['CATEGORY']
#     name = shapedict['NAME']
#     if cat in ['H4','H5'] and name not in names:
#         # only use named storms.
#         if name != 'NOT NAMED':  names.append(name)
# # plot tracks of those storms.
# for shapedict,shape in zip(m.hurrtracks_info,m.hurrtracks):
#     name = shapedict['NAME']
#     cat = shapedict['CATEGORY']
#     if name in names:
#         xx,yy = zip(*shape)
#         # show part of track where storm > Cat 4 as thick red.
#         if cat in ['H4','H5']:
#             m.plot(xx,yy,linewidth=1.5,color='r')
#         elif cat in ['H1','H2','H3']:
#             m.plot(xx,yy,color='k')
# # draw coastlines, meridians and parallels.
# m.drawcoastlines()
# m.drawcountries()
# m.drawmapboundary(fill_color='#99ffff')
# m.fillcontinents(color='#cc9966',lake_color='#99ffff')
# m.drawparallels(np.arange(10,70,20),labels=[1,1,0,0])
# m.drawmeridians(np.arange(-100,0,20),labels=[0,0,0,1])
# plt.title('Atlantic Hurricane Tracks (Storms Reaching Category 4, 1851-2004)')
# plt.show()
