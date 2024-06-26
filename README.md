# Vehicle Routing Optimizer API

This project is a prototype developed as part of my Master's Thesis on the Capacitated Vehicle Routing Problem With Time Windows. The core functionality is implemented in the [solver.py](https://github.com/A-M-Amine/Vehicle-Routing-Optimizer/blob/main/api/optimizer/solver.py) script, which provides insight into the algorithmic approach used.

## Current State Update (26/06/2024):

Please note that the API itself was my first attempt at using the Django and Django Rest framework. Consequently, I cannot guarantee its stability or execution reliability at this stage. While I intend to revisit this project when time permits, I am unable to commit to a specific timeline.

## Overview

This is a RESTful web API that uses Google OR-Tools and Open Route Service API to solve the Vehicle Routing Problem (
VRP) with time windows and capacity constraints. The project allows users to input a list of locations, a set of
vehicles with capcacities, and other parameters, and outputs the optimal routes for each vehicle to visit all locations
while minimizing the total travel time and distance. The project can be used for various applications such as delivery,
transportation, logistics, etc.

## Features

- Supports multiple vehicles with different capacities
- Supports time windows for each location
- Supports different optimization algortihms, such as guided local search and Tabu search
- Returns a detailed route plan for each vehicle, including the sequence of locations, GeoJson path, and the travel
  distance and time
- Returns a summary of the optimization results, including the total distance, time, and cost for all vehicles

## How to use

- Clone this repository or download the zip file
- Create and activate a virtual environment (optional but recommended)
- Install the dependencies using pip install -r requirements.txt
- Run the migrations using python manage.py migrate
- Create a superuser using python manage.py createsuperuser
- Run the development server using python manage.py runserver

### Endpoints

The API has 3 main endpoints:

- `/optimizer`: This endpoint allows you to submit a configuration request and get back a configuration setup result.
  You need to provide a JSON object with the following parameters:
    - `name`: A unique name for the optimizer instance
    - `vehicles`: A list of vehicle ids
    - `depot`: The coordinates of the depot location

  Here is an example of a valid request body:

  ```json
  {
    "name": "genesis",
    "depot": [37.00,4.2855],
    "vehicles": [1,2]
  }
  ```

- `/optimizedroute/`: (description will be added soon)
- `/vehicles/`:  (description will be added soon)
