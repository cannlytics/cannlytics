import os

def print_directory_contents(path, indent_level=0):
    """
    Recursively prints the directory structure with files in a logical manner.
    
    Args:
    - path: The directory path to start from.
    - indent_level: The current level of indentation to represent directory depth.
    """
    # Ensure the path is absolute
    abs_path = os.path.abspath(path)
    
    # Get all entries in the directory sorted alphabetically
    entries = sorted(os.listdir(abs_path))
    
    for entry in entries:
        entry_path = os.path.join(abs_path, entry)
        indent = "    " * indent_level  # 4 spaces for each level
        
        if os.path.isdir(entry_path):
            print(f"{indent}+ {entry}/")  # Append '/' to directories for clarity
            # Recursively print the contents of the directory
            print_directory_contents(entry_path, indent_level + 1)
        else:
            print(f"{indent}- {entry}")  # Prefix files with '-'


# Example usage:
# Replace '/path/to/directory' with the actual directory path you want to inspect
# print_directory_contents(r"C:\Users\keega\Documents\cannlytics\cannlytics\datasets")
            

from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.firebase.develop import Firestore
from diagrams.programming.language import Python


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

# Render the diagram.
with Diagram(
        "Data Collection Process",
        show=False,
        filename="data_collection_process",
        outformat='png',
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
    with Cluster("Data Collection"):
        with Cluster("Algorithms"):
            lab_results_alg = Python("Get Lab Results")
            strains_alg = Python("Get Strains")
            licenses_alg = Python("Get Licenses")
            # lab_results_alg - strains_alg - licenses_alg

        data_collection_node = Server("Data Collection")

    with Cluster("Data Processing"):
        data_analysis = Server("Data Analysis")

    with Cluster("Data Storage"):
        firestore = Firestore("Firestore")

    data_collection_node >> Edge(color="darkgreen", style="dashed") >> data_analysis
    data_analysis >> Edge(color="darkgreen") >> firestore
