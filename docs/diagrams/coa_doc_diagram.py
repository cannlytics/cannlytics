"""
COA Parsing Engine Diagram
Copyright (c) 2023 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 10/24/2023
Updated: 10/24/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.gcp.compute import GCF
from diagrams.gcp.database import Firestore
from diagrams.gcp.storage import GCS
from diagrams.onprem.client import User
from diagrams.programming.framework import Flutter
from PIL import Image


# Style.
graph_attr = {
    'dpi': '300',
}
node_attr = {
    'fontsize': '16',
    'fontcolor': 'black',
    'color': 'black',
    'fontname': 'times-bold',
}
edge_attr = {
    'color': 'black',
    'style': 'dashed',
}
title_graph_attr = {
    'fontsize': '24',
    'labelloc': 't',
    'fontname': 'times-bold',
}
cluster_graph_attr = {
    'fontsize': '24',
    'labelloc': 't',
    'fontname': 'times-bold',
}


with Diagram(
        '',
        show=False,
        filename='./docs/diagrams/cannlytics-diagram',
        outformat='png',
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ) as diag:

    # Users.
    dev = User('Developer')
    client = User('Business Client')
    consumer = User('Consumer')

    # Nodes.
    with Cluster('COA Parsing Engine', graph_attr=title_graph_attr):

        # API.
        with Cluster('API', graph_attr=cluster_graph_attr):
            # FIXME: This only works with absolute path.
            api = Custom('', r'.\docs\theme\assets\images\logos/cannlytics_coa_doc.png')

        # App.
        with Cluster('App', graph_attr=cluster_graph_attr):
            app = Flutter('Flutter Web')

        # Firebase.
        with Cluster('Firebase', graph_attr=cluster_graph_attr):
            firestore = Firestore('Database')
            storage = GCS('Storage')
            functions = GCF('Cloud Functions')

    # Connections.
    api << Edge(ltail='cluster_api', lhead='cluster_firestore', minlen='2') >> firestore
    api << Edge(ltail='cluster_api', lhead='cluster_storage', minlen='2') >> storage
    app << Edge(ltail='cluster_app', lhead='cluster_api', minlen='2') >> api
    app << Edge(ltail='cluster_app', lhead='cluster_client', minlen='2') >> client
    app << Edge(ltail='cluster_app', lhead='cluster_firestore', minlen='2') >> firestore
    app << Edge(ltail='cluster_app', lhead='cluster_storage', minlen='2') >> storage
    dev << Edge(ltail='cluster_dev', lhead='cluster_api', minlen='2') >> api
    dev << Edge(ltail='cluster_dev', lhead='cluster_app', minlen='2') >> app
    dev << Edge(ltail='cluster_dev', lhead='cluster_client', minlen='2') >> client
    client >> consumer
    functions >> api
    functions << firestore

# Show the diagram.
diag


def add_logo(diagram_path, logo_path, output_path, logo_size=None):
    """
    Adds a logo to the specified diagram image and saves the result.
    Args:
        diagram_path (str): Path to the diagram image file.
        logo_path (str): Path to the logo image file.
        output_path (str): Path where the resulting image should be saved.
        logo_size (tuple, optional): Desired size of the logo as (width, height). 
            If None, the original size is used. Default is None.
    """
    diagram = Image.open(diagram_path)
    logo = Image.open(logo_path)
    if logo_size is not None:
        logo = logo.resize(logo_size, Image.LANCZOS)
    position = (40, 40)
    diagram.paste(logo, position, logo)
    diagram.save(output_path)


# Add Cannlytics logo to diagram after it is generated.
add_logo(
    './docs/diagrams/cannlytics-diagram.png',
    './docs/theme/assets/images/logos/cannlytics_logo_with_text_light.png',
    './docs/diagrams/cannlytics-diagram.png',
    logo_size=(750, 150),
)
print('Diagram saved to ./docs/diagrams/cannlytics-diagram.png')
