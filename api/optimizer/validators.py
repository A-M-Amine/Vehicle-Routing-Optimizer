from django.core.exceptions import ValidationError
from rest_framework.response import Response
import json


def validate_locations_value(params):
    # Try to parse the string as a JSON array
    try:
        lst = json.loads(params)
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
    try:
        locations = json.loads(locations)
        if depot < 0 or depot > len(locations) - 1:
            return False, "Depot Index out of bounds"

        return True, ""
    except json.JSONDecodeError:
        # The string is not a valid JSON array
        return False, "Locations Data must be a valid JSON array."
