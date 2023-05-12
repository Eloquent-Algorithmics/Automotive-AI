"""
This module provides functions for decoding VIN numbers.
"""

import requests


def decode_vin(vin):
    """
    Decodes a VIN number using an external API.

    Args:
        vin (str): The VIN number to decode.

    Returns:
        dict: A dictionary containing information about the vehicle.
    """
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return {item["Variable"]: item["Value"] for item in data["Results"]}
    else:
        return None


def parse_vin_response(response):
    """
    Parses a VIN response and returns a dictionary of vehicle information.

    Args:
        response (str): The response string to parse.

    Returns:
        dict: A dictionary containing information about the vehicle.
    """
    # Ensure the response has enough data
    if len(response.split()) >= 18:
        # Extract the 17-character VIN by concatenating the relevant bytes
        vin_data = response.split()[4:]
        vin = []
        for data in vin_data:
            if not data.endswith(":"):
                char = chr(int(data, 16))
                if char.isalnum():  # Check if the character is alphanumeric
                    vin.append(char)
        return "".join(vin)
    else:
        return None


def get_vehicle_data_from_nhtsa(vin):
    """
    Retrieves vehicle data from NHTSA API using VIN number.

    Args:
        vin (str): Vehicle Identification Number.

    Returns:
        dict: Dictionary containing vehicle data.
    """
    decoded_data = decode_vin(vin)
    if decoded_data:
        vehicle_data = {
            "Model Year": decoded_data.get("Model Year", "Unknown"),
            "Make": decoded_data.get("Make", "Unknown"),
            "Model": decoded_data.get("Model", "Unknown"),
            "Trim Level": decoded_data.get("Trim Level", "Unknown"),
            "Engine Displacement (L)": decoded_data.get("Displacement (L)", "Unknown"),
        }
        return vehicle_data
    else:
        return None
