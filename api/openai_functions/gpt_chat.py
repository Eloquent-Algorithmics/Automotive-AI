"""
This module provides functions for working with OpenAI's API.
"""
import json
import os
import ast
from config import OPENAI_API_KEY
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from halo import Halo

spinner = Halo(text='Loading...', spinner='dots')

# Instantiate OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def chat_gpt(prompt):
    """
    Generates a response to the given prompt using OpenAI's GPT-3.5-turbo or gpt-4 model.

    Args:
        prompt (str): The prompt to generate a response for.

    Returns:
        str: The generated response.
    """
    spinner.start()
    try:
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
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
        response_text = completion.choices[0].message.content.strip()
    except APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)
        response_text = "Error: The server could not be reached."
    except RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        response_text = "Error: Rate limit exceeded. Please try again later."
    except APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        response_text = f"Error: An API error occurred with status code {e.status_code}."
    finally:
        spinner.stop()
    return response_text


def chat_gpt_custom(processed_data):
    """
    Extracts VIN number from processed data or generates a response using OpenAI's API.

    Args:
        processed_data (str): The processed data containing the VIN response.

    Returns:
        str: The extracted VIN number or the generated response.
    """
    if "VIN response:" in processed_data:
        vin = processed_data.split("VIN response: ")[1].split("\n")[0].strip()
        decoded_data = processed_data.split("Decoded VIN: ")[1].strip()
        vehicle_data = ast.literal_eval(decoded_data)

        if vehicle_data:
            response = (
                f"The VIN is {vin}. This is a {vehicle_data['Model Year']} "
                f"{vehicle_data['Make']} {vehicle_data['Model']} with a "
                f"{vehicle_data['Displacement (L)']} engine. Trim level is "
                f"{vehicle_data['Trim'] if vehicle_data['Trim'] else 'none'}."
            )
        else:
            response = "couldn't retrieve information for the provided VIN."
    else:
        spinner.start()
        try:
            completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are an in car AI assistant."},
                    {"role": "user", "content": f"{processed_data}"},
                ],
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.5,
                frequency_penalty=0,
                presence_penalty=0,
            )
            response = completion.choices[0].message.content.strip()
        except APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)
            response = "Error: The server could not be reached."
        except RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
            response = "Error: Rate limit exceeded. Please try again later."
        except APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)
            response = f"Error: An API error occurred with status code {e.status_code}."
        finally:
            spinner.stop()

    return response


def chat_gpt_conversation(prompt, conversation_history):
    spinner.start()
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=conversation_history +
            [{"role": "user", "content": f"{prompt}"}],
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.5,
            frequency_penalty=0,
            presence_penalty=0,
        )
        response_text = response.choices[0].message.content.strip()
    except APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)
        response_text = "Error: The server could not be reached."
    except RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        response_text = "Error: Rate limit exceeded. Please try again later."
    except APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        response_text = f"Error: An API error occurred with status code {e.status_code}."
    finally:
        spinner.stop()
    return response_text


def load_conversation_history(file_path="conversation_history.json"):
    spinner.start()
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                conversation_history = json.load(f)
        else:
            conversation_history = [
                {"role": "system", "content": "You are an in car AI assistant."}
            ]
    except Exception as e:
        print(f"An error occurred while loading the conversation history: {e}")
        conversation_history = [
            {"role": "system", "content": "You are an in car AI assistant."}
        ]
    finally:
        spinner.stop()
    return conversation_history


def save_conversation_history(
    conversation_history, file_path="conversation_history.json"
):
    """
    Save the conversation history to a JSON file.

    Args:
        conversation_history (list): representing the conversation history.
        file_path (str, optional): JSON file where the conversation history.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f)
    except Exception as e:
        print(f"An error occurred while saving the conversation history: {e}")


def format_conversation_history_for_summary(conversation_history):
    spinner.start()
    formatted_history = ""
    for message in conversation_history:
        role = message["role"].capitalize()
        content = message["content"]
        formatted_history += f"{role}: {content}\n"
    spinner.stop()
    return formatted_history


def summarize_conversation_history_direct(conversation_history):
    spinner.start()
    try:
        formatted_history = format_conversation_history_for_summary(conversation_history)
        summary_prompt = f"Please summarize the following conversation history and retain all important information:\n\n{formatted_history}\nSummary:"

        messages = conversation_history + \
            [{"role": "user", "content": summary_prompt}]

        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # Set this to gpt-4, gpt-4-0314 or gpt-4-0613 model
            messages=messages,
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.5,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0,
        )

        summary_text = response.choices[0].message.content.strip()
        summarized_history = [
            {"role": "system", "content": "You are an in car AI assistant."}
        ]
        summarized_history.append({"role": "assistant", "content": summary_text})
    except APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)
        summarized_history = [{"role": "assistant", "content": "Error: The server could not be reached."}]
    except RateLimitError as e:
        print("A 429 status code was received; we should back off a bit.")
        summarized_history = [{"role": "assistant", "content": "Error: Rate limit exceeded. Please try again later."}]
    except APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        summarized_history = [{"role": "assistant", "content": f"Error: An API error occurred with status code {e.status_code}."}]
    finally:
        spinner.stop()
    return summarized_history
