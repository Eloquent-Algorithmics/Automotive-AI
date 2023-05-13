"""
This module provides voice recognition functionality for various tasks such as:
- Speech recognition
- Text-to-speech output
- Voice commands
- Managing appointments
- Handling emails
- Interacting with GPT-based chat
"""

from voice_recognition import (
    recognize_speech,
    recognize_command,
    tts_output,
    voice_commands,
    get_next_appointment,
    create_new_appointment,
    get_emails,
    send_email_with_attachments,
    chat_gpt,
)


def handle_voice_commands_without_device(user_object_id):
    """
    Listen for voice commands from the user and execute them without using a device.

    Args:
        user_object_id: The user object ID for Microsoft Graph API.

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
            else:
                print("Command not recognized. Please try again.")
        else:
            print("Command not recognized. Please try again.")
