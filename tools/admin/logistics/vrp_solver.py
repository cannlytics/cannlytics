"""
Vehicle Routing Problem | Cannlytics

Authors: Keegan Skeate <keegan@cannlytics.com>
Created: 10/1/2021
Updated: 10/1/2021
License: MIT License <https://opensource.org/licenses/MIT>

Resources:
    
    - Managing Simple VRP with Google Maps Platform: https://woolpert.com/managing-simple-vrp-with-google-maps-platform/
    - Traveling Salesperson Problem: https://developers.google.com/optimization/routing/tsp

Description:
    
    Vehicles Routing Problem (VRP).

"""

import os
import gmaps
import googlemaps
import pandas as pd
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def create_data_model(distance_matrix, num_vehicles):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    return data

def extract_routes(num_vehicles, manager, routing, solution):
    routes = {}
    for vehicle_id in range(num_vehicles):
        routes[vehicle_id] = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            routes[vehicle_id].append(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
        routes[vehicle_id].append(manager.IndexToNode(index))
    return routes

def print_solution(num_vehicles, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Cost of the route: {}\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum route cost: {}'.format(max_route_distance))

def generate_solution(data, manager, routing):  
    """Solve the CVRP problem."""
    
    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    flattened_distance_matrix = [i for j in data['distance_matrix'] for i in j]
    max_travel_distance = 2 * max(flattened_distance_matrix)

    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        max_travel_distance,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    return solution

def solve_vrp_for(distance_matrix, num_vehicles):
    # Instantiate the data problem.
    data = create_data_model(distance_matrix, num_vehicles)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Solve the problem
    solution = generate_solution(data, manager, routing)
    
    if solution:
        # Print solution on console.
        print_solution(num_vehicles, manager, routing, solution)
        routes = extract_routes(num_vehicles, manager, routing, solution)
        return routes
    else:
        print('No solution found.')


def map_solution(depot, shipments, routes):
    colors = ['blue','red','green','#800080','#000080','#008080']
    for vehicle_id in routes:
        waypoints = []
        
        # skip depot (occupies first and last index)
        for shipment_index in routes[vehicle_id][1:-1]: 
            waypoints.append(shipments[shipment_index-1]['location'])
        
        if len(waypoints) == 0:
            print('Empty route:', vehicle_id)
        else:
            route_layer = gmaps.directions_layer(
                depot['location'], waypoints[-1], waypoints=waypoints[0:-1], show_markers=True,
                stroke_color=colors[vehicle_id], stroke_weight=5, stroke_opacity=0.5)
            fig.add_layer(route_layer)
            
            # complete the route from last shipment to depot
            return_layer = gmaps.directions_layer(
                waypoints[-1], depot['location'], show_markers=False,
                stroke_color=colors[vehicle_id], stroke_weight=5, stroke_opacity=0.5)
            fig.add_layer(return_layer)



if __name__ == '__main__':
   
    
    API_KEY = 'YOUR_API_KEY'
    gmaps.configure(api_key=API_KEY)
    
    depot = {
        'location': (29.399013114383962, -98.52633476257324)
    }
    
    depot_layer = gmaps.symbol_layer(
        [depot['location']], hover_text='Depot', info_box_content='Depot', 
        fill_color='white', stroke_color='red', scale=8
    )
    
    num_vehicles = 3
    
    shipments = [
        { 
            'name': 'Santa\'s Place',
            'location': (29.417361, -98.437544)
        },
        {
            'name': 'Los Barrios',
            'location': (29.486833, -98.508355)
        },
        {
            'name': 'Jacala',
            'location': (29.468601, -98.524849),
        },
        {
            'name': 'Nogalitos',
            'location': (29.394394, -98.530070)
        },
        {
            'name': 'Alamo Molino',
            'location': (29.351701, -98.514740)
        },
        {
            'name': 'Jesse and Sons',
            'location': (29.435115, -98.593962)
        },
        {
            'name': 'Walmart',
            'location': (29.417867, -98.680534)
        },
        {
            'name': 'City Base Entertainment',
            'location': (29.355400, -98.445857)
        },
        { 
            'name': 'Combat Medic Training',
            'location': (29.459497, -98.434057)
        }
    ]
    
    shipment_locations = [shipment['location'] for shipment in shipments]
    shipment_labels = [shipment['name'] for shipment in shipments]
    
    shipments_layer = gmaps.symbol_layer(
        shipment_locations, hover_text=shipment_labels, 
        fill_color='white', stroke_color='black', scale=4
    )
        
    fig = gmaps.figure()
    fig.add_layer(depot_layer)
    fig.add_layer(shipments_layer)
    
    fig
    
    
    def build_distance_matrix(depot, shipments, measure='distance'):
    
        gmaps_services = googlemaps.Client(key=API_KEY)
        origins = destinations = [item['location'] for item in [depot] + shipments]
        dm_response = gmaps_services.distance_matrix(origins=origins, destinations=destinations)
        dm_rows = [row['elements'] for row in dm_response['rows']]
        distance_matrix = [[item[measure]['value'] for item in dm_row] for dm_row in dm_rows]
        return distance_matrix
    
    try:
        objective = 'distance'  # distance or duration
        # Distance Matrix API takes a max 100 elements = (origins x destinations), limit to 10 x 10
        distance_matrix = build_distance_matrix(depot, shipments[0:9], objective)
        df = pd.DataFrame(distance_matrix)
    
    except:
        print('Something went wrong building distance matrix.')
    
    df
    
    try:
        routes = solve_vrp_for(distance_matrix, num_vehicles)
    except:
        print('Something went wrong solving VRP.')
    
    
    if routes:
        map_solution(depot, shipments, routes)
    else:
        print('No solution found.') 
    
    fig
    
    # Solve for duration.
    try:
        objective = 'duration'  # distance or duration
        distance_matrix = build_distance_matrix(depot, shipments[0:9], objective)
        df = pd.DataFrame(distance_matrix)
        routes = solve_vrp_for(distance_matrix, num_vehicles)
    except:
        print('Something went wrong solving for duration.')
    
    df
    
    # Map the solution.
    if routes:
        fig = gmaps.figure()
        fig.add_layer(depot_layer)
        fig.add_layer(shipments_layer)
        map_solution(depot, shipments, routes)
    else:
        print('No solution found.')   
    
    fig
