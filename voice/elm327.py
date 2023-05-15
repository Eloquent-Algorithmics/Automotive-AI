"""
This module contains functions to handle voice commands using ELM327.
"""
from voice.voice_recognition import (
    recognize_speech,
    tts_output,
    voice_commands,
    ELM327_COMMANDS,
    send_command,
    process_data,
    send_diagnostic_report,
    parse_vin_response,
    decode_vin,
    get_next_appointment,
    create_new_appointment,
    get_emails,
    send_email_with_attachments,
    chat_gpt,
    chat_gpt_custom,
)


def handle_voice_commands_elm327(ser, user_object_id):
    """
    Listen for voice commands from the user and execute them.

    Args:
        ser: The serial port object used to communicate with the device.

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

            recognized_command = recognize_command(text, list(voice_commands.keys()))

            if recognized_command:
                cmd = voice_commands[recognized_command]

                if cmd == "next_appointment":
                    next_appointment = get_next_appointment(user_object_id)
                    print(f"{next_appointment}")
                    tts_output(f"{next_appointment}")

                elif cmd == "create_appointment":
                    create_new_appointment(recognize_speech, tts_output)
                    print("New appointment created.")
                    tts_output("New appointment has been created.")

                elif cmd == "send_diagnostic_report":
                    send_diagnostic_report(ser)
                    print("Diagnostic report sent to your email.")
                    tts_output("Diagnostic report has been sent to your email.")

                elif cmd == "check_outlook_email":
                    emails = get_emails(user_object_id)
                    if emails:
                        for email in emails:
                            print(f"\nSubject: {email['subject']}")
                            print(f"From: {email['from']['emailAddress']['address']}")
                            print(f"Date: {email['receivedDateTime']}")
                            print(f"Body: {email['body']['content']}")
                    else:
                        print("No emails found.")
                elif cmd == "send_email":
                    # Use predefined values or ask the user for email details.
                    email_to = "example@example.com"
                    subject = "Test email"
                    body = "This is a test email."
                    attachments = ["file1.txt", "file2.txt"]
                    send_email_with_attachments(email_to, subject, body, attachments)

                elif cmd == "ASK_CHATGPT_QUESTION":
                    print("Please ask your question:")
                    question = recognize_speech()
                    if question:
                        chatgpt_response = chat_gpt(question)
                        print(f"Answer: {chatgpt_response}")
                        tts_output(chatgpt_response)
                    else:
                        print("I didn't catch your question Please try again.")

                elif (
                    cmd in ELM327_COMMANDS
                ):  # Check if the command is in the ELM327_COMMANDS set
                    response = send_command(ser, cmd)
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
                            processed_data = f"{text}: {response} - Engine RPM: {value}"
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
                            processed_data = process_data(text, response, value)

                        chatgpt_response = chat_gpt_custom(processed_data)
                        print(f"ChatGPT Response: {chatgpt_response}")
                        tts_output(chatgpt_response)
                    else:
                        print(f"{text} not available.")
            else:
                print("Command not recognized. Please try again.")
        else:
            print("Command not recognized. Please try again.")
