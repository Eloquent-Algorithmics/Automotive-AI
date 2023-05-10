"""
This module decodes a Vehicle Identification Number (VIN) using the NHTSA API.
"""
import requests


def decode_vin(vin):
    """
    Decode a Vehicle Identification Number (VIN) using the NHTSA API.

    Args:
        vin (str): The VIN to decode.

    Returns:
        dict: A dictionary containing information about the vehicle.
    """
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        return {item["Variable"]: item["Value"] for item in data["Results"]}
    else:
        return None


def parse_vin_response(response):
    """
    Parse the response from the NHTSA API for a decoded VIN.

    Args:
        response (str): The response string from the NHTSA API.

    Returns:
        bool: True if the response contains enough data, False otherwise.
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
    Get vehicle data from the NHTSA API for a given VIN.

    Args:
        vin (str): The VIN (Vehicle Identification Number) of the vehicle.

    Returns:
        dict: A dictionary containing the decoded data for the vehicle.
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
