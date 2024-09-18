"""
This module provides functions for working with OpenAI's API.
"""

import os
import json
import ast
import inspect
from rich.console import Console
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from config import OPENAI_API_KEY
from utils.functions import tools, available_functions

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
                model="gpt-4o-mini",
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

            return response_text

        except APIConnectionError as e:
            console.log(f"An error occurred: {e}")
            return "An error occurred while generating the response."


def chat_gpt_conversation(
    prompt, conversation_history, available_functions, client, console, tools
):

    messages = conversation_history + [{"role": "user", "content": f"{prompt}"}]

    with console.status("[bold green]Generating...", spinner="dots"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.5,
                frequency_penalty=0,
                presence_penalty=0,
            )
            response_text = response.choices[0].message.content.strip()

            tool_calls = (
                response.choices[0].tool_calls
                if hasattr(response.choices[0], "tool_calls")
                else []
            )

            if tool_calls:
                messages.append({"role": "system", "content": response_text})
                executed_tool_call_ids = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name

                    if function_name not in available_functions:
                        continue

                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)

                    if inspect.iscoroutinefunction(function_to_call):
                        function_response = function_to_call(**function_args)
                    else:
                        function_response = function_to_call(**function_args)

                    if function_response is None:
                        function_response = "No response received from the function."
                    elif not isinstance(function_response, str):
                        function_response = json.dumps(function_response)

                    function_response_message = {
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                        "tool_call_id": tool_call.id,
                    }
                    executed_tool_call_ids.append(tool_call.id)
                    messages.append(function_response_message)

                second_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.5,
                    top_p=0.5,
                    max_tokens=1024,
                )

                return second_response
            else:
                return response_text
        except APIConnectionError as e:
            console.log(f"An error occurred: {e}")
            return "An error occurred while generating the response."


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
                    file_content = f.read().strip()
                    # Check if the file is not empty and contains valid JSON
                    if file_content:
                        conversation_history = json.loads(file_content)
                    else:
                        # File is empty or contains only whitespace
                        raise ValueError("File is empty or contains invalid JSON.")
            else:
                conversation_history = [
                    {
                        "role": "system",
                        "content": "You are an AI assistant.",
                    }
                ]
        except (IOError, ValueError) as error:
            console.print(f"[bold red]Error loading history: {error}")
            conversation_history = [
                {"role": "system", "content": "You are an AI assistant."}
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
                model="gpt-4o-mini",
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
            summarized_history.append({"role": "assistant", "content": summary_text})
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
                    model="gpt-4o-mini",
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
