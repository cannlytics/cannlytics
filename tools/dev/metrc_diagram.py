"""
Metrc Diagram
Copyright (c) 2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/12/2023
Updated: 2/17/2023
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Note: This diagram is a work in progress!
"""
# Standard imports:
from urllib.request import urlretrieve

# External imports:

from diagrams import Cluster, Diagram, Edge, Node
from diagrams.custom import Custom


def create_node_label(fields):
    """Format dataset fields into a label for a node."""
    string = ''
    for k, v in fields.items():
        string += f'\n{k}: {v}'
    return string.lstrip('\n')


def create_dataset_node(title, fields, cluster_attr={}, node_attr={}):
    """Create a dataset node."""
    with Cluster(title, graph_attr=cluster_attr):
        label = create_node_label(fields)
        cluster = Node(label, **node_attr)
    return cluster


# def metrc_diagram(
#         filename=None,
#         direction='LR',
#         cluster_attr={},
#         graph_attr={},
#         node_attr={},
#         logo_path='ccrs-logo.png',
#     ):
#     """Render a diagram of Metrc data points."""

# Get an image of Metrc.
# download_ccrs_logo(logo_path)

# Draw diagram.
# with Diagram(
#     direction=direction,
#     filename=filename, 
#     graph_attr=graph_attr,
# ) as diagram:

#     # Areas node.
#     areas = create_dataset_node(
#         'Areas',
#         CCRS_DATASETS['areas']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Inventory node.
#     inventory = create_dataset_node(
#         'Inventory',
#         CCRS_DATASETS['inventory']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Inventory Adjustments node.
#     inventory_adjustments = create_dataset_node(
#         'Inventory Adjustments',
#         CCRS_DATASETS['inventory_adjustments']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Lab results node.
#     lab_results = create_dataset_node(
#         'Lab Results',
#         CCRS_DATASETS['lab_results']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Licensees node.
#     licensees = create_dataset_node(
#         'Licensees',
#         CCRS_DATASETS['licensees']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Plants node.
#     plants = create_dataset_node(
#         'Plants',
#         CCRS_DATASETS['plants']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Plant Destructions node.
#     plant_destructions = create_dataset_node(
#         'Plant Destructions',
#         CCRS_DATASETS['plant_destructions']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Products node.
#     products = create_dataset_node(
#         'Products',
#         CCRS_DATASETS['products']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Sale details node.
#     sale_details = create_dataset_node(
#         'Sale Details',
#         CCRS_DATASETS['sale_details']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Sale headers node.
#     sale_headers = create_dataset_node(
#         'Sale Headers',
#         CCRS_DATASETS['sale_headers']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Strains node.
#     strains = create_dataset_node(
#         'Strains',
#         CCRS_DATASETS['strains']['fields'],
#         cluster_attr,
#         node_attr,
#     )

#     # Define the relationships.
#     areas >> licensees
#     plants >> licensees
#     plants >> strains
#     plants >> areas
#     inventory >> strains
#     inventory >> products
#     inventory >> licensees
#     inventory >> areas
#     inventory_adjustments >> inventory
#     lab_results >> inventory
#     lab_results >> licensees
#     plant_destructions >> plants
#     products >> licensees
#     sale_details >> sale_headers
#     sale_details >> inventory
#     sale_headers >> licensees

#     # Define a CCRS node.
#     ccrs = Custom(
#         'WSLCB CCRS',
#         icon_path=logo_path,
#         fontsize='21',
#         fontname='Times-Roman bold',
#         fontcolor='#24292e',
#         margin='1.0',
#     )
#     edge = Edge(
#         label='Licensees submit data for traceability.\nWSLCB provides all datasets on FOIA request.',
#         color='red',
#         style='dashed',
#     )
#     ccrs << edge >> licensees
    
    # # Return the diagram.
    # return diagram


# Parameters.
filename = 'metrc_diagram'
direction ='LR'
cluster_attr = {
    'fontname': 'times bold',
    'fontsize': '18',
}
graph_attr = {
    'center': 'true',
    'pad': '1.0',
    'fontsize': '25',
    'fontname': 'Times-Roman',
    'fontcolor': '#000',
    'nodesep': '1.0',
    
}
node_attr = {
    'bgcolor': '#e8e8e8',
    'fixedsize': 'false',
    'labelloc': 't',
    'margin': '0.1',
    'color': '#e8e8e8',
}


# === Test ===
if __name__ == '__main__':
    pass

    # # Render the diagram.
    # diagram = ccrs_diagram(
    #     filename='ccrs_diagram',
    #     direction='LR',
    #     cluster_attr={
    #         'fontname': 'times bold',
    #         'fontsize': '18',
    #     },
    #     graph_attr={
    #         'center': 'true',
    #         'pad': '1.0',
    #         'fontsize': '25',
    #         'fontname': 'Times-Roman',
    #         'fontcolor': '#000',
    #         'nodesep': '1.0',
            
    #     },
    #     node_attr={
    #         'bgcolor': '#e8e8e8',
    #         'fixedsize': 'false',
    #         'labelloc': 't',
    #         'margin': '0.1',
    #         'color': '#e8e8e8',
    #     },
    # )
    # print('Diagram rendered:', diagram.filename)
