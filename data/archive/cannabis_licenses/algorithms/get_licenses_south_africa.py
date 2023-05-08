# https://www.sahpra.org.za/approved-licences/


# TODO: Get cannabis cultivation licenses.


# TODO: Get Testing Laboratories licenses.


from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
my_map = Basemap(projection='ortho', lat_0=10, lon_0=13, resolution='l')
my_map.drawcoastlines(linewidth=1)
my_map.drawcountries(linewidth=0.5)
# Make plot larger
plt.gcf().set_size_inches(20, 10)
# Save to file
plt.savefig("Africa.svg")