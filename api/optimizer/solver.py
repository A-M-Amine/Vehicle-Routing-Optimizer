import openrouteservice as ors
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import random
from creds import ORS_KEY
import json


def route_matrix_via_api(locations):
    api_key = ORS_KEY

    # Define the client
    client = ors.Client(key=api_key)

    # Specify the travel mode and the returned metrics
    profile = 'driving-car'
    metrics = ['distance', 'duration']

    # Get the distance matrix
    matrix = client.distance_matrix(
        locations=locations,
        profile=profile,
        metrics=metrics
    )

    matrix_dict = {'matrix': matrix}
    return matrix_dict


def solver(matrix=0, num_vehicles=2, depot=0):
    # Get the distance and times matrices using the driving-car profile
    distance_matrix = matrix['distances']

    time_matrix = matrix['durations']

    cities = ["LOC" + str(i) if i != depot else "Depot" for i in range(len(matrix['distances'][0]))]

    # Generate random time windows for each city
    random.seed(42)
    time_windows = []
    for i in range(len(cities)):

        if depot == i:
            time_windows.append((0, 0))  # depot has no time window
        else:
            # earliest start time between 7 am and 12 pm
            start = random.randint(7, 12) * 3600
            # latest end time between 1 and 4 hours after start
            end = start + random.randint(1, 4) * 3600
            time_windows.append((start, end))

    # Create the data model
    data = {}
    data['distance_matrix'] = distance_matrix
    data['time_matrix'] = time_matrix
    data['time_windows'] = time_windows
    data['num_vehicles'] = num_vehicles
    data['depot'] = depot

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])

    # Create the routing model
    routing = pywrapcp.RoutingModel(manager)

    # Define a callback for the distance matrix
    def distance_callback(from_index, to_index):
        # Returns the distance between the two nodes
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    # Register the distance callback with the routing model
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc (distance)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Define a callback for the time matrix
    def time_callback(from_index, to_index):
        # Returns the travel time between the two nodes
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    # Register the time callback with the routing model
    time_callback_index = routing.RegisterTransitCallback(time_callback)

    # Add a dimension for time and set its span upper bound to a large value (24 hours)
    routing.AddDimension(
        time_callback_index,
        24 * 3600,  # allow waiting time
        24 * 3600,  # maximum time per vehicle
        False,  # don't force start cumul to zero since we have a depot with a specific start time window
        'Time'
    )

    # Get the time dimension object
    time_dimension = routing.GetDimensionOrDie('Time')

    # Add time window constraints for each location except depot
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == depot:
            continue  # skip depot
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node (depot)
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data['time_windows'][depot][0], data['time_windows'][depot][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(manager.GetNumberOfVehicles()):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Set the local search metaheuristic to guided local search
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    # Set the time limit for the search
    search_parameters.time_limit.seconds = 30

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # return the result if found
    if solution:
        return get_solution(data, manager, routing, solution)
    else:
        return {'ERROR': 'Solution not found'}


def get_solution(data, manager, routing, solution):
    result = {}
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    routes = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            index = solution.Value(routing.NextVar(index))

        time_var = time_dimension.CumulVar(index)
        node_index = manager.IndexToNode(index)
        route.append(node_index)
        route_time = solution.Min(time_var)
        routes.append({'vehicle_id': vehicle_id,
                       'path': route,
                       'route_time': route_time})
        total_time += route_time

    result['vehicle_routes'] = routes
    # result['total_time'] = total_time
    return result


