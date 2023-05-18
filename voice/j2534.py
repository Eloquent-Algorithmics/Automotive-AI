"""
This module provides voice recognition functionality,
including speech recognition
and text-to-speech output.
"""

from voice.voice_recognition import (
    recognize_speech,
    tts_output,
    handle_common_voice_commands,
)
from j2534_cffi import find_j2534_passthru_dlls, J2534PassThru


def create_j2534_connection():
    """
    Creates a J2534 connection using the available passthru DLLs.

    Returns:
        A J2534 connection object or None if no suitable DLLs are found.
    """
    passthru_dlls = find_j2534_passthru_dlls()
    if not passthru_dlls:
        raise Exception("No J2534 passthru DLL found")
    device_name, passthru_dll = passthru_dlls[0]

    # Load the J2534 library
    j2534_lib = J2534PassThru(passthru_dll)

    # Open a J2534 device
    device = j2534_lib.open()

    # Set up the protocol configuration for ISO 15765 (CAN)
    config = {
        'ProtocolID': j2534_lib.PROTOCOL_ISO15765,
        'Flags': j2534_lib.PROTOCOL_ISO15765_FRAME_PAD,
        'BaudRate': 500000,  # You may need to adjust the baud rate depending on your device
    }

    # Connect to the J2534 device
    channel = device.connect(config)
    return channel


def send_command_j2534(channel, cmd):
    """
    Send a command to the J2534 device using the channel.

    Args:
        channel: The J2534 channel object used to communicate with the device.
        cmd (str): The command to send.

    Returns:
        str: The response from the J2534 device.
    """
    # Convert the command string to bytes
    cmd_bytes = cmd.encode("ascii")

    # Send the command using the J2534 channel
    channel.write(cmd_bytes)

    # Read the response
    response_bytes = channel.read()

    # Convert the response bytes to a string
    response = response_bytes.decode("ascii")

    return response


def handle_voice_commands_j2534(channel, user_object_id):
    """
    Listen for voice commands from the user and execute using J2534 channel.

    Args:
        channel: The J2534 channel object used to communicate with the device.
        user_object_id: The users email for Microsoft Graph API.

    Returns:
        None
        """
    standby_phrases = ["enter standby mode", "go to sleep", "stop listening"]
    wakeup_phrases = ["wake up", "i need your help", "start listening"]

    standby_mode = False

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

            cmd = handle_common_voice_commands(text, user_object_id)

        else:
            print("Command not recognized. Please try again.")
