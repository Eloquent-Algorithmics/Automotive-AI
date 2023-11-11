"""
This module contains functions to handle voice commands using ELM327.
"""
import threading
import pandas as pd
import serial
from config import SERIAL_PORT, BAUD_RATE
from datastreams.flask_air_fuel_datastream import start_datastream, app
from voice.voice_recognition import (
    recognize_speech,
    recognize_command,
    tts_output,
    handle_common_voice_commands,
)
from utils.commands import voice_commands, ELM327_COMMANDS
from utils.serial_commands import (
    send_command,
    process_data,
    send_diagnostic_report,
    parse_vin_response,
    decode_vin,
)
from api.openai_functions.gpt_chat import chat_gpt_custom


def handle_voice_commands_elm327(user_object_id):
    """
    Listen for voice commands from the user and execute them.

    Args:
        user_object_id: The user object ID for Microsoft Graph API.

    Returns:
        None
    """
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        timeout=1,
    )
    standby_phrases = ["enter standby mode", "go to sleep", "stop listening"]
    wakeup_phrases = ["wake up", "i need your help", "start listening"]

    standby_mode = False
    datastream_process = None

    while True:
        if not standby_mode:
            print("\nPlease say a command:")
        text = recognize_speech()
        if text:
            if any(phrase in text.lower() for phrase in standby_phrases):
                standby_mode = True
                print("Entering standby mode.")
                tts_output("Entering standby mode.")
                continue

            if standby_mode and any(
                phrase in text.lower() for phrase in wakeup_phrases
            ):
                standby_mode = False
                print("Exiting standby mode.")
                tts_output("Exiting standby mode.")
                continue

            if standby_mode:
                continue

            cmd = handle_common_voice_commands(user_object_id)

            if cmd == "START_DATA_STREAM":
                print("Starting data stream...")
                tts_output("Starting data stream...")
                datastream_thread = threading.Thread(target=start_datastream)
                datastream_thread.daemon = True
                datastream_thread.start()

            elif cmd == "STOP_DATA_STREAM":
                print("Stopping data stream...")
                tts_output("Stopping data stream...")
                with app.test_request_context():
                    app.do_teardown_request()

            elif cmd == "SAVE_DATA_TO_SPREADSHEET":
                print("Saving data to spreadsheet...")
                tts_output("Saving data to spreadsheet...")
                data = app.view_functions["data"]()
                df = pd.DataFrame(data["sensor_data"]).T
                df.columns = [sensor.name for sensor in supported_sensors]
                df.to_excel("datastream_output.xlsx", index=False)
                print("Data saved to datastream_output.xlsx")
                tts_output("Data saved to datastream_output.xlsx")

            if cmd and (cmd in ELM327_COMMANDS):
                if cmd == "send_diagnostic_report":
                    send_diagnostic_report(ser)
                    print("Diagnostic report sent to your email.")
                    tts_output("The report has been sent to your email.")
                else:
                    response = send_command(ser, cmd)
                    print(f"Raw response: {response}")
                    if "NO DATA" not in response:
                        value = None
                        if cmd == "0105":
                            value = int(response.split()[2], 16) - 40
                            value = (value * 9 / 5) + 32
                            print(f"Engine Coolant Temperature (F): {value}")
                            processed_data = (
                                f"{text}: {response} - "
                                f"Engine Coolant Temperature (F): {value}"
                            )
                        elif cmd == "010C":
                            value = (
                                int(response.split()[2], 16) * 256
                                + int(response.split()[3], 16)
                            ) / 4
                            print(f"Engine RPM: {value}")
                            processed_data = (
                                f"{text}: {response} - " f"Engine RPM: {value}"
                            )
                        elif cmd == "0902":
                            vin_response = parse_vin_response(response)
                            print(f"VIN response: {vin_response}")
                            vehicle_data = decode_vin(vin_response)
                            print(f"Decoded VIN: {vehicle_data}")
                            processed_data = (
                                f"VIN response: {vin_response}\n"
                                f"Decoded VIN: {vehicle_data}"
                            )
                        else:
                            processed_data = process_data(
                                text, response, value)

                        chatgpt_response = chat_gpt_custom(processed_data)
                        print(f"ChatGPT Response: {chatgpt_response}")
                        tts_output(chatgpt_response)
                    else:
                        print(f"{text} not available.")

                if cmd == "START_DATASTREAM":
                    if datastream_process is None:
                        print("Starting datastream...")
                        tts_output("Starting datastream...")
                        datastream_process = subprocess.Popen(
                            ["python", "datastreams/air_fuel_datastream.py"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )
                    else:
                        print("Datastream is already running.")
                        tts_output("Datastream is already running.")

                elif cmd == "STOP_DATASTREAM":
                    if datastream_process is not None:
                        print("Stopping datastream...")
                        tts_output("Stopping datastream...")
                        datastream_process.terminate()
                        datastream_process = None
                    else:
                        print("Datastream is not running.")
                        tts_output("Datastream is not running.")

            else:
                print("Command not recognized. Please try again.")
        else:
            print("Command not recognized. Please try again.")
