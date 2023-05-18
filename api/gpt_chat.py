"""
This module provides functions for working with OpenAI's API.
"""

import ast
import openai


def chat_gpt(prompt):
    """
    Generates a response to the given prompt using OpenAI's GPT-4 model.

    Args:
        prompt (str): The prompt to generate a response for.

    Returns:
        str: The generated response.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an in car AI assistant."},
            {"role": "user", "content": f"{prompt}"},
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5,
        frequency_penalty=0,
        presence_penalty=0,
    )
    # Extract the text part of the response
    response_text = response.choices[0].message["content"].strip()
    return response_text


def chat_gpt_custom(processed_data):
    """
    Extracts VIN number from processed data.

    Args:
        processed_data (str): The processed data containing the VIN response.

    Returns:
        str: The extracted VIN number.
    """
    if "VIN response:" in processed_data:
        vin = processed_data.split("VIN response: ")[1].split("\n")[0].strip()
        decoded_data = processed_data.split("Decoded VIN: ")[1].strip()
        vehicle_data = ast.literal_eval(decoded_data)

        if vehicle_data:
            response = (
                f"The VIN is {vin}. This is a {vehicle_data['Model Year']} "
                f"{vehicle_data['Make']} {vehicle_data['Model']} with a "
                f"{vehicle_data['Displacement (L)']} engine. The trim level is "
                f"{vehicle_data['Trim'] if vehicle_data['Trim'] else 'unknown'}."
            )
        else:
            response = "couldn't retrieve information for the provided VIN."
    else:
        response = chat_gpt(processed_data)

    return response
