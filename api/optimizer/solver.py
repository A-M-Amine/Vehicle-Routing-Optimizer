import json
from api.optimizer.serializers import OptimizerSerializer
import openrouteservice as ors
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import random
from creds import ORS_KEY
import requests

LOCAL_SEARCH_ALGORITHMS = {"GLS": routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH,
                           "TS": routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH,
                           "SA": routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING}


# TODO check the time format and use minutes for durations
def route_matrix_via_api(locations):
    api_key = ORS_KEY

    client = ors.Client(key=api_key)

    # Specify the travel mode and the returned metrics
    profile = 'driving-car'
    metrics = ['distance', 'duration']

    try:
        output = client.distance_matrix(
            locations=locations,
            profile=profile,
            metrics=metrics
        )

        # convert values into integers required by OR-Tools to work
        output["distances"] = [list(map(int, row)) for row in output["distances"]]
        output["durations"] = [list(map(int, row)) for row in output["durations"]]

        result = {
            "locations": locations,
            "distances": output["distances"],  # distances in meters
            "durations": output["durations"]  # duration in seconds
        }

        for value in result.values():
            if any(element is None for row in value for element in row):
                return {'matrix': {}}

        return {'matrix': result}

    # Catch any exception from the API request
    except (requests.exceptions.RequestException, ors.exceptions.ApiError) as e:
        print(e)
        return {'matrix': {}}


# TODO make capacity flag respond to given data
def prepared_data(instance):
    serializer = OptimizerSerializer(instance=instance)

    locations = [serializer.data['depot']]
    demand = [0]
    time_windows = [[0, 1440]]

    for delivery in instance.deliveries.all():
        locations.append(delivery.coordinates)
        demand.append(delivery.package_size)
        time_windows.append(delivery.time_window)

    capacity = []
    for vehicle in instance.vehicles.all():
        capacity.append(vehicle.capacity)

    matrix = serializer.data['matrix']

    if matrix == {} or matrix['locations'] != locations:
        matrix = route_matrix_via_api(locations)
        optimizer_instance = serializer.update(instance=instance, validated_data=matrix)
        optimizer_instance.save()
        matrix = matrix['matrix']

    result = {
        "depot": serializer.data['depot'],
        "vehicles": serializer.data['vehicles'],
        "capacity": capacity,
        "locations": locations,
        "demand": demand,
        "time_windows": time_windows,
        "matrix": matrix,
        "Capacity_Constraint": True
    }

    return result


def solver(data_instance, solving_method):
    # depot is set to zero by default
    depot = 0

    deliveries = data_instance.deliveries.all()
    if len(deliveries) < 1:
        return False, {'Error': 'No Assigned delivery locations'}
    instance = prepared_data(data_instance)

    if instance['matrix'] == {}:
        return False, {'Error': 'Could not compute distance or time between Deliveries !'}

    distance_matrix = instance['matrix']['distances']
    time_matrix = instance['matrix']['durations']

    # Create the data model
    data = {}
    data['distance_matrix'] = distance_matrix
    data['time_matrix'] = time_matrix
    data['time_windows'] = instance['time_windows']
    data['num_vehicles'] = len(instance['vehicles'])
    data['depot'] = depot
    capacity_constraint = instance['Capacity_Constraint']
    # Add the capacity and demand arrays to the data model if Capacity_Demand is True
    if capacity_constraint:
        data['capacity'] = instance['capacity']
        data['demand'] = instance['demand']

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

    # Define a callback for the demand array if capacity_constraint is True
    if capacity_constraint:
        def demand_callback(from_index):
            # Returns the demand of the node
            from_node = manager.IndexToNode(from_index)
            return data['demand'][from_node]

        # Register the demand callback with the routing model
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        # Add a dimension for capacity and set its upper bound to the maximum capacity of each vehicle
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['capacity'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity'
        )

    # Set the local search metaheuristic to guided local search
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    method = LOCAL_SEARCH_ALGORITHMS.get(solving_method, None)
    if method:
        search_parameters.local_search_metaheuristic = method
    else:
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

    # Set the time limit for the search
    search_parameters.time_limit.seconds = 30

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # return the result if found
    if solution:

        return True, get_solution(data, manager, routing, solution, instance['locations'], instance['vehicles'],
                                  method)
    else:
        return False, {'Error': 'Solution not found'}


def get_solution(data, manager, routing, solution, locations, vehicles, method):
    locations = locations
    result = {}
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    total_distance = 0
    routes = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        route_index = []
        route_distance = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            node_index = manager.IndexToNode(index)
            route.append(locations[node_index])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

        time_var = time_dimension.CumulVar(index)
        node_index = manager.IndexToNode(index)
        route.append(locations[node_index])
        route_time = solution.Min(time_var)

        route_index = route[::]
        route = create_geojson(route)

        routes.append({'vehicle_id': vehicles[vehicle_id],
                       'path_index': route_index,
                       'route_time': route_time,
                       'route_distance': route_distance,
                       'path': route})
        total_time += route_time
        total_distance += route_distance
    result['vehicle_routes'] = routes
    result['total_time'] = total_time
    result['total_distance'] = total_distance

    if method:
        for key, value in LOCAL_SEARCH_ALGORITHMS.items():
            if method == value:
                result['local_search_algorithm'] = key
    else:
        result['local_search_algorithm'] = 'GLS'

    return result


def create_geojson(locations):
    # Define the API endpoint and the profile
    endpoint = "https://api.openrouteservice.org/v2/directions/"
    profile = "driving-car/geojson"

    # Define the request headers with your API key
    headers = {
        "Authorization": ORS_KEY,
        "Content-Type": "application/json"
    }

    # Define the request body with the locations
    body = {
        "coordinates": locations
    }

    # Send a POST request to the API endpoint with the profile, headers and body
    response = requests.post(endpoint + profile, headers=headers, json=body)
    # Check if the request was successful
    if response.status_code == 200:
        # Return the geojson file of the route
        return response.json()
    else:
        # Return an error message
        return response.json()["error"]


def random_time_windows(cities, depot):
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

    return time_windows
