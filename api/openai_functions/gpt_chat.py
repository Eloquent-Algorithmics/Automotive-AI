"""
This module provides functions for working with OpenAI's API.
"""
import os
import json
import ast
from rich.console import Console
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from config import OPENAI_API_KEY

# Instantiate OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
console = Console()


def chat_gpt(prompt):
    """
    Generates a response using OpenAI's API.

    Args:
        prompt (str): The prompt to generate a response for.

    Returns:
        str: The generated response.
    """
    with console.status("[bold green]Generating...", spinner="dots"):
        try:
            completion = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant.",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}",
                    },
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
            console.print("[bold red]The server could not be reached")
            console.print(e.__cause__)
            response_text = "Error: The server could not be reached."
        except RateLimitError as e:
            console.print(f"[bold red]A 429 status code.{e}")
            response_text = "Error: Rate limit exceeded. Try again later."
        except APIStatusError as e:
            console.print(f"[bold red]Error code was received{e}")
            console.print(e.status_code)
            console.print(e.response)
            response_text = f"API error occurred status code {e.status_code}"
    return response_text


def chat_gpt_custom(processed_data):
    """
    Extracts VIN number from processed data using OpenAI's API.

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
        with console.status("[bold green]Processing", spinner="dots"):
            try:
                completion = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI assistant.",
                        },
                        {
                            "role": "user",
                            "content": f"{processed_data}",
                        },
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
                console.print("[bold red]The server could not be reached")
                console.print(e.__cause__)
                response = "Error: The server could not be reached."
            except RateLimitError as e:
                console.print(f"[bold red]429 status code was received.{e}")
                response = "Error: Rate limit exceeded."
            except APIStatusError as e:
                console.print("[bold red]non-200-range status code received")
                console.print(e.status_code)
                console.print(e.response)
                response = f"Error: An API error occurred {e.status_code}."

    return response


def chat_gpt_conversation(prompt, conversation_history):
    """
    This function generates a response for the given prompt using GPT model.

    :param prompt: The input prompt for the GPT model.
    :type prompt: str
    :param conversation_history: The history of the conversation so far.
    :type conversation_history: list
    """
    with console.status("[bold green]Generating...", spinner="dots"):
        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=conversation_history
                + [{"role": "user", "content": f"{prompt}"}],
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.5,
                frequency_penalty=0,
                presence_penalty=0,
            )
            response_text = response.choices[0].message.content.strip()
        except APIConnectionError as e:
            console.print("[bold red]The server could not be reached")
            console.print(e.__cause__)
            response_text = "Error: The server could not be reached."
        except RateLimitError as e:
            console.print(f"[bold red]A 429 status code was received.{e}")
            response_text = "Error: Rate limit exceeded."
        except APIStatusError as e:
            console.print(f"[bold red]non-200-range status code received{e}")
            console.print(e.status_code)
            console.print(e.response)
            response_text = (
                f"Error: API error occurred with status code {e.status_code}."
            )
    return response_text


def load_conversation_history(file_path="conversation_history.json"):
    """
    This function loads conversation history from a JSON file.

    :param file_path: Defaults to "conversation_history.json".
    :return: A list of conversation messages.
    """
    with console.status("[bold green]Loading...", spinner="dots"):
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    conversation_history = json.load(f)
            else:
                conversation_history = [
                    {
                        "role": "system",
                        "content": "You are an AI assistant.",
                    }
                ]
        except IOError as io_error:
            console.print(f"[bold red]Error loading history: {io_error}")
            conversation_history = [
                {
                    "role": "system",
                    "content": "You are an AI assistant."
                }
            ]
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
    except IOError as io_error:
        print(f"An error occurred saving conversation history: {io_error}")


def format_conversation_history_for_summary(conversation_history):
    """
    Format the conversation history for summary display.

    Args:
        conversation_history (str): The conversation history as a string.

    Returns:
        str: The formatted conversation history.
    """
    with console.status("[bold green]Formatting...", spinner="dots"):
        formatted_history = ""
        for message in conversation_history:
            role = message["role"].capitalize()
            content = message["content"]
            formatted_history += f"{role}: {content}\n"
    return formatted_history


def summarize_conversation_history_direct(conversation_history):
    """
    This function summarizes the conversation history provided as input.

    :param conversation_history: A list of conversation messages.
    :return: None
    """
    with console.status("[bold green]Summarizing..", spinner="dots"):
        try:
            formatted_history = format_conversation_history_for_summary(
                conversation_history
            )
            summary_prompt = (
                "Please summarize the following conversation history and "
                "retain all important information:\n\n"
                f"{formatted_history}\nSummary:"
            )
            messages = conversation_history + [
                {"role": "user", "content": summary_prompt}
            ]

            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
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
                {"role": "system", "content": "You are an AI assistant"}
            ]
            summarized_history.append(
                {
                    "role": "assistant",
                    "content": summary_text
                }
            )
        except APIConnectionError as e:
            console.print("[bold red]The server could not be reached")
            console.print(e.__cause__)
            summarized_history = [
                {
                    "role": "assistant",
                    "content": "Error: The server could not be reached.",
                }
            ]
        except RateLimitError as e:
            console.print(f"[bold red]A 429 status code was received.{e}")
            summarized_history = [
                {
                    "role": "assistant",
                    "content": "Error: Rate limit exceeded. Try again later.",
                }
            ]
        except APIStatusError as e:
            console.print("[bold red]non-200-range status code received")
            console.print(e.status_code)
            console.print(e.response)
            summarized_history = [
                {
                    "role": "assistant",
                    "content": f"Error: API error {e.status_code}.",
                }
            ]
    return summarized_history
