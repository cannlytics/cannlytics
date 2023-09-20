"""
Cannabis Licenses | License Mao
Copyright (c) 2022-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
    Candace O'Sullivan-Sutherland <https://github.com/candy-o>
Created: 9/22/2022
Updated: 9/19/2023
License: <https://github.com/cannlytics/cannabis-data-science/blob/main/LICENSE>

Description: 

    Map the adult-use cannabis retailers permitted in the United States:

    ✓ Alaska
    ✓ Arizona
    ✓ California
    ✓ Colorado
    ✓ Connecticut
    ✓ Delaware
    ✓ Illinois
    ✓ Maine
    ✓ Massachusetts
    ✓ Michigan
    ✓ Missouri
    ✓ Montana
    ✓ Nevada
    ✓ New Jersey
    X New York (Under development)
    ✓ New Mexico
    ✓ Oregon
    ✓ Rhode Island
    ✓ Vermont
    X Virginia (Expected 2024)
    ✓ Washington

"""
# External imports.
import folium
import pandas as pd


def create_retailer_map(
        df,
        color='crimson',
        filename=None,
        lat='premise_latitude',
        long='premise_longitude',
    ):
    """Create a map of licensed retailers."""
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=3,
        control_scale=True,
    )
    for _, row in df.iterrows():
        folium.Circle(
            radius=5,
            location=[row[lat], row[long]],
            color=color,
        ).add_to(m)
    if filename:
        m.save(filename)
    return m


# === Test ===
if __name__ == '__main__':

    # Read all licenses.
    data = pd.read_csv('../data/all/licenses-all-latest.csv')
    data = data.loc[
        (~data['premise_latitude'].isnull()) &
        (~data['premise_longitude'].isnull())
    ]

    # Create a map of all licenses.
    map_file = '../analysis/figures/cannabis-licenses-map.html'
    m = create_retailer_map(data, filename=map_file)
    print('Saved map to', map_file)

    # FIXME: Create a PNG image of the map.
    # import io
    # from PIL import Image

    # img_data = m._to_png(30)
    # img = Image.open(io.BytesIO(img_data))
    # img.save('../analysis/figures/cannabis-licenses-map.png')
