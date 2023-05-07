from django.core.exceptions import ValidationError
from rest_framework.response import Response
import json
import numbers


def validate_locations_value(params):
    # Try to parse the string as a JSON array
    try:
        lst = params
        # Check if the result is a list
        if isinstance(lst, list):
            # Check if the list has at least two items

            if len(lst) < 2:
                # The list is too short
                return False, "Data must include at least two locations"
            else:
                return True, ""
        else:

            # The result is not a list
            return False, "Data must be a valid JSON array."

    except json.JSONDecodeError:
        # The string is not a valid JSON array
        return False, "Data must be a valid JSON array."


def validate_depot_value(locations, depot):
    locations = locations
    if depot < 0 or depot > len(locations) - 1:
        return False, "Depot Index out of bounds"

    return True, ""


def validate_coords(value):
    if not isinstance(value, list) or len(value) != 2:
        return False, 'coordinates must be a valid array that contain longitude & latitude only!'

    for item in value:
        if not isinstance(item, numbers.Real):
            return False, f'{item} is not a valid type for coordinates'

    return True, ''
