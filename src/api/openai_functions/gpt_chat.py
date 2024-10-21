"""
This module provides functions for working with OpenAI's API.
"""

import ast
import inspect
import json
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import azure.cognitiveservices.speech as speechsdk

from openai import (
    APIConnectionError,
    APIStatusError,
    AzureOpenAI,
    OpenAI,
    RateLimitError,
)
from rich.console import Console

from utils.functions import available_functions, tools

console = Console()

openai_client = None
openai_model_arg = None

azure_credential = None


def get_azure_credential():
    """
    Retrieves the Azure credential for authentication.
    """
    global azure_credential  # Declare it as global to modify the global variable
    if azure_credential is None:
        azure_credential = DefaultAzureCredential(
            exclude_shared_token_cache_credential=True
        )
    return azure_credential


def configure_openai():
    """
    Asynchronously configures the OpenAI client based on environment variables.

    This function sets up the OpenAI client using different configurations depending on
    the environment variables provided. It supports local OpenAI endpoints,
    Azure OpenAI endpoints, and OpenAI API keys.

    Raises:
        ValueError: If required environment variables for Azure OpenAI are missing or
        if no OpenAI configuration is provided.

    Environment Variables:
        LOCAL_OPENAI_ENDPOINT: The local endpoint for OpenAI.
        AZURE_OPENAI_ENDPOINT: The Azure endpoint for OpenAI.
        AZURE_OPENAI_API_KEY: The API key for Azure OpenAI.
        AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME: The deployment name for Azure OpenAI ChatGPT.
        AZURE_OPENAI_API_VERSION: The API version for Azure OpenAI.
        OPENAICOM_API_KEY: The API key for OpenAI.
        OPENAICOM_MODEL: The model name for OpenAI (default is "gpt-4o-mini").

    """
    global openai_client, openai_model_arg

    client_args = {}
    if os.getenv("LOCAL_OPENAI_ENDPOINT"):
        client_args["api_key"] = "no-key-required"
        client_args["base_url"] = os.getenv("LOCAL_OPENAI_ENDPOINT")
        openai_client = OpenAI(
            **client_args,
        )
    elif os.getenv("AZURE_OPENAI_ENDPOINT"):
        if os.getenv("AZURE_OPENAI_API_KEY"):
            client_args["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
        else:
            client_args["azure_ad_token_provider"] = get_bearer_token_provider(
                get_azure_credential(), "https://cognitiveservices.azure.com/.default"
            )
        if not os.getenv("AZURE_OPENAI_ENDPOINT"):
            raise ValueError("AZURE_OPENAI_ENDPOINT is required for Azure OpenAI")
        if not os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME"):
            raise ValueError(
                "AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME is required for Azure OpenAI"
            )
        openai_client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION") or "2024-06-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            **client_args,
        )
        # Note: Azure OpenAI takes the deployment name as the model name
        openai_model_arg = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME")
    elif os.getenv("OPENAICOM_API_KEY"):
        client_args["api_key"] = os.getenv("OPENAICOM_API_KEY")
        openai_client = OpenAI(
            **client_args,
        )
        openai_model_arg = os.getenv("OPENAICOM_MODEL") or "gpt-4o-mini"
    else:
        raise ValueError(
            "No OpenAI configuration provided. Check your environment variables."
        )


def chat_gpt(prompt):
    """
    Generates a response using OpenAI's API.

    Args:
        prompt (str): The prompt to generate a response for.

    Returns:
        str: The generated response.
    """
    speech_config = speechsdk.SpeechConfig(
        endpoint=f"wss://{os.getenv('AZURE_SPEECH_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
        subscription=os.getenv("AZURE_SPEECH_KEY"),
    )

    speech_config.speech_synthesis_voice_name = os.getenv("AZURE_SPEECH_VOICE")

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

    properties = dict()
    properties["SpeechSynthesis_FrameTimeoutInterval"] = "100000000"
    properties["SpeechSynthesis_RtfTimeoutThreshold"] = "10"
    speech_config.set_properties_by_name(properties)

    # create request with TextStream input type
    tts_request = speechsdk.SpeechSynthesisRequest(
        input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
    )
    tts_task = speech_synthesizer.speak_async(tts_request)

    with console.status("[bold green]Generating...", spinner="dots"):
        try:
            completion = openai_client.chat.completions.create(
                model=openai_model_arg,
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
                stream=True,
            )

            for chunk in completion:
                if len(chunk.choices) > 0:
                    chunk_text = chunk.choices[0].delta.content
                    if chunk_text:
                        print(chunk_text, end="")
                        tts_request.input_stream.write(chunk_text)

            # close tts input stream when GPT finished
            tts_request.input_stream.close()

            # wait all tts audio bytes return
            tts_task.get()

        except APIConnectionError as e:
            console.log(f"An error occurred: {e}")
            return "An error occurred while generating the response."


def chat_gpt_conversation(prompt, conversation_history):
    """
    Generates a conversation response and handles tool calls if present.
    Args:
        prompt (str): The user's input prompt for the conversation.
        conversation_history (list): A list of previous conversation messages,
        each represented as a dictionary with 'role' and 'content' keys.
    Returns:
        str: The generated response text.
    Raises:
        APIConnectionError: If there is an error connecting to the API.
    """

    # Include the new user message in the conversation history
    messages = conversation_history + [{"role": "user", "content": prompt}]

    # Set up speech synthesis configuration
    speech_config = speechsdk.SpeechConfig(
        endpoint=f"wss://{os.getenv('AZURE_SPEECH_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
        subscription=os.getenv("AZURE_SPEECH_KEY"),
    )

    speech_config.speech_synthesis_voice_name = os.getenv("AZURE_SPEECH_VOICE")

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

    properties = dict()
    properties["SpeechSynthesis_FrameTimeoutInterval"] = "100000000"
    properties["SpeechSynthesis_RtfTimeoutThreshold"] = "10"
    speech_config.set_properties_by_name(properties)

    # Create request with TextStream input type
    tts_request = speechsdk.SpeechSynthesisRequest(
        input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
    )
    tts_task = speech_synthesizer.speak_async(tts_request)

    # Initialize a variable to collect the assistant's response text
    assistant_response_text = ""

    with console.status("[bold green]Generating...", spinner="dots"):
        try:
            # Create a streaming completion request
            response = openai_client.chat.completions.create(
                model=openai_model_arg,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=512,
                n=1,
                stop=None,
                temperature=0.5,
                frequency_penalty=0,
                presence_penalty=0,
                stream=True,
            )

            # Iterate over the streamed response
            for chunk in response:
                if len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta.content
                    chunk_text = delta.get("content", "")
                    if chunk_text:
                        print(chunk_text, end="")
                        tts_request.input_stream.write(chunk_text)
                        assistant_response_text += chunk_text

            print("[GPT END]", end="")

            # Close TTS input stream when GPT finished
            tts_request.input_stream.close()

            # Wait for all TTS audio bytes to return
            tts_task.get()

            # Add the assistant's response to the conversation history
            conversation_history.append(
                {"role": "assistant", "content": assistant_response_text}
            )

            tool_calls = (
                response.choices[0].tool_calls
                if hasattr(chunk.choices[0].delta.content, "tool_calls")
                else []
            )

            if tool_calls:
                messages.append({"role": "system", "content": response})
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

                second_response = openai_client.chat.completions.create(
                    model=openai_model_arg,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.5,
                    top_p=0.5,
                    max_tokens=1024,
                    stream=True,
                )

                for chunk in second_response:
                    if len(chunk.choices) > 0:
                        chunk_text = chunk.choices[0].delta.content
                        if chunk_text:
                            print(chunk_text, end="")
                            tts_request.input_stream.write(chunk_text)

                # close tts input stream when GPT finished
                tts_request.input_stream.close()

                # wait all tts audio bytes return
                tts_task.get()
            else:
                return response, assistant_response_text

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

            response = openai_client.chat.completions.create(
                model=openai_model_arg,
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
                completion = openai_client.chat.completions.create(
                    model=openai_model_arg,
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
