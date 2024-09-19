"""
This module is responsible for handling voice commands using speech recognition
and spacy.
"""

import spacy
import speech_recognition as sr

from api.openai_functions.gpt_chat import (
    chat_gpt,
    chat_gpt_conversation,
    load_conversation_history,
    save_conversation_history,
    summarize_conversation_history_direct,
    client,
    console,
)
from audio.audio_output import tts_output
from config import EMAIL_PROVIDER
from utils.commands import voice_commands
from utils.functions import available_functions, tools

if EMAIL_PROVIDER == "Google":
    from api.google_functions.google_api import (
        delete_email,
        get_emails_google,
    )

if EMAIL_PROVIDER == "365":
    from api.microsoft_functions.graph_api import (
        create_new_appointment,
        get_emails,
        get_next_appointment,
        send_email_with_attachments,
    )

nlp = spacy.load("en_core_web_md")


def get_similarity_score(text1, text2):
    """
    Compute the similarity score between two texts using spacy nlp pipeline.

    Args:
        text1 (str): The first text to compare.
        text2 (str): The second text to compare.

    Returns:
        float: The similarity score between the two texts.
    """
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)


def recognize_command(text, commands):
    """
    Recognizes a command from the given text.

    Args:
        text (str): The input text to recognize the command from.
        commands (list): A list of available commands.

    Returns:
        str: The recognized command if found, otherwise None.
    """
    if text is None:
        return None

    max_similarity = 0
    best_match = None

    for command in commands:
        similarity = get_similarity_score(text.lower(), command)

        if similarity > max_similarity:
            max_similarity = similarity
            best_match = command

    if max_similarity > 0.7:  # You can adjust this threshold
        return best_match
    else:
        return None


def recognize_speech():
    """
    Recognizes speech using the default microphone as the audio source.

    Returns:
        str: The recognized text if successful, otherwise None.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=3)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=30)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected")
            return None
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as request_error:
        print(f"Could not request results; {request_error}")
        return None


def handle_common_voice_commands(args, user_object_id=None, email_provider=None):
    """
    Handle common voice commands.

    Args:
        args: [description of args]
        user_object_id: [description of user_object_id]
        email_provider: [description of email_provider]

    Returns:
        [description of the return value, if any]
    """

    standby_phrases = ["enter standby mode", "go to sleep", "stop listening"]
    wakeup_phrases = ["wake up", "I need your help", "start listening"]

    standby_mode = False
    conversation_history = load_conversation_history()
    conversation_active = True

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

            if not standby_mode and conversation_active:
                if "summarize the conversation history" in text.lower():
                    conversation_history = summarize_conversation_history_direct(
                        conversation_history
                    )
                    save_conversation_history(conversation_history)
                    print("Conversation history summarized.")
                    tts_output("Conversation history summarized.")
                    continue

                if "clear all history" in text.lower():
                    conversation_history = [
                        {"role": "system", "content": "You are an in car AI assistant."}
                    ]
                    save_conversation_history(conversation_history)
                    print("Conversation history cleared.")
                    tts_output("Conversation history cleared.")
                    continue

                if "delete the last message" in text.lower():
                    if len(conversation_history) > 1:
                        conversation_history.pop()
                        save_conversation_history(conversation_history)
                        print("Last message removed.")
                        tts_output("Last message removed.")
                    else:
                        print("No messages to remove.")
                        tts_output("No messages to remove.")
                    continue

                if "end the conversation" in text.lower():
                    conversation_active = False
                    print("Ending the conversation.")
                    tts_output("Ending the conversation.")
                    continue

            if (
                not standby_mode
                and not conversation_active
                and "start a conversation" in text.lower()
            ):
                conversation_active = True
                print("Starting a conversation.")
                tts_output("What would you like to chat about?")
                continue

            if not standby_mode and conversation_active:
                chatgpt_response = chat_gpt_conversation(
                    text,
                    conversation_history,
                    available_functions,
                    client,
                    console,
                    tools,
                )
                conversation_history.append({"role": "user", "content": text})
                conversation_history.append(
                    {"role": "assistant", "content": chatgpt_response}
                )
                save_conversation_history(conversation_history)
                print(f"Assistant: {chatgpt_response}")
                tts_output(chatgpt_response)
                continue

            recognized_command = recognize_command(text, list(voice_commands.keys()))

            if recognized_command:
                cmd = voice_commands[recognized_command]

                if cmd == "next_appointment" and email_provider == "365":
                    next_appointment = get_next_appointment(user_object_id)
                    print(f"{next_appointment}")
                    tts_output(f"{next_appointment}")

                elif cmd == "create_appointment" and email_provider == "365":
                    create_new_appointment(recognize_speech, tts_output)
                    print("New appointment created.")
                    tts_output("New appointment has been created.")

                elif cmd == "check_outlook_email" and email_provider == "365":
                    emails = get_emails(user_object_id)
                    if emails:
                        for email in emails:
                            print(f"\nSubject: {email['subject']}")
                            print(f"From: {email['from']['emailAddress']['address']}")
                            print(f"Date: {email['receivedDateTime']}")
                            print(f"Body: {email['body']['content']}")
                    else:
                        print("No emails found.")

                elif cmd == "send_email" and email_provider == "365":
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
                        print("I didn't catch your question. Please try again.")
                        tts_output("I didn't catch your question. Please try again.")
                elif cmd == "check_google_email" and email_provider == "Google":
                    emails = get_emails_google(user_object_id=None)
                    if emails:
                        for email in emails:
                            print(f"\nFrom: {email['from']}")
                            print(f"Subject: {email['subject']}")
                            snippet = email.get("snippet", "N/A")
                            print(f"Body: {snippet}")
                            tts_output(
                                f"From: {email['from']}, Subject: {email['subject']}, Body: {snippet}"
                            )
                            tts_output("Would you like to delete this email?")
                            response = recognize_speech()
                            if response is not None and "yes" in response.lower():
                                delete_email(email["id"])
                                print("Email deleted.")
                                tts_output("Email deleted.")
                            else:
                                print("Email not deleted.")
                                tts_output("Email not deleted.")
                    else:
                        print("No emails found.")

                else:
                    continue
            else:
                if not standby_mode and not conversation_active:
                    print("Command not recognized. Please try again.")
                    continue
                elif conversation_active:
                    print("Unrecognized input. Please try again.")
                    continue
                else:
                    continue
