"""
Get SVG Data | Cannlytics

Author: Keegan Skeate
Contact: <keegan@cannlytics.com>
Created: 8/31/2021
Updated: 9/3/2021
License: MIT License <https://opensource.org/licenses/MIT>
"""

from xml.dom import minidom


def get_svg_d_strings(doc):
    """Get the data strings from an SVG."""
    return [path.getAttribute('d') for path
            in doc.getElementsByTagName('path')]

    
def get_svg_ids(doc):
    """Get the data strings from an SVG."""
    return [path.getAttribute('id') for path
                in doc.getElementsByTagName('path')]


def format_county_data(state, svg_file):
    """Format the data for a given county SVG file.
    First, data is parsed from an SVG.
    Second, objects (dicts) are created for each polygon."""
    doc = minidom.parse(svg_file)
    d_strings = get_svg_d_strings(doc)
    ids = get_svg_ids(doc)
    doc.unlink()
    
    county_data = {}
    county_paths = []
    for n in range(len(d_strings)):
        d_string = d_strings[n]
        _id = ids[n]
        name = _id.replace(f'{state}_', '').replace('_', ' ')
        county_paths.append({'id': _id, 'n': name, 'd': d_string})
        # Optional: Get stats for each state
        county_data[_id] = {'high': 0, 'mid': 0, 'low': 0, 'avg': 0}
    print(county_paths)

if __name__ == '__main__':

    # Define file.
    directory = r'../../../..\console\images\maps\state-maps'
    svg_file = f'{directory}/oklahoma_chloropleth_map.svg'
    
    # Get counties for given state.
    format_county_data('OK', svg_file)
