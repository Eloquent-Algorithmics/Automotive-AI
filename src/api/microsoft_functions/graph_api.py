"""
This module demonstrates how to work with OS, Base64, and DateTime libraries.
"""
import os
import base64
import datetime
import importlib
import msal
import requests
import dateparser
import pytz
from dateutil.parser import isoparse
from twilio.rest import Client
import api.microsoft_functions.ms_authserver as ms_authserver
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_PHONE_NUMBER,
    TEXT_TO_PHONE_NUMBER,
    GRAPH_EMAIL_ADDRESS,
    GRAPH_CLIENT_ID,
    GRAPH_CLIENT_SECRET,
    GRAPH_TENANT_ID,
    EMAIL_PROVIDER,
)

# Set up authentication with Microsoft Graph API
authority = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}"
client_id = GRAPH_CLIENT_ID
client_secret = GRAPH_CLIENT_SECRET
scope = ["https://graph.microsoft.com/.default"]
redirect_uri = "http://localhost:8000"

user_object_id = None


if EMAIL_PROVIDER == "365":
    authorization_code = ms_authserver.get_auth_code()

    app = msal.ConfidentialClientApplication(
        client_id=client_id, client_credential=client_secret, authority=authority
    )

    result = app.acquire_token_by_authorization_code(
        authorization_code, scope, redirect_uri=redirect_uri
    )

    if "access_token" in result:
        access_token = result["access_token"]
        refresh_token = result["refresh_token"]
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))
        raise ValueError("Could not authenticate with Microsoft Graph API")


def perform_graph_api_request(authorization_code):
    """
    Perform a Graph API request using the given authorization code.

    Args:
        authorization_code (str): The authorization code used for request.

    Returns:
        None: Just an example, modify return type based on implementation.
    """
    pass


def refresh_access_token():
    """
    Refreshes the access token using the global refresh_token and scope.
    Updates the global access_token variable with the new token.
    """
    global access_token
    result = app.acquire_token_by_refresh_token(refresh_token, scope)
    if "access_token" in result:
        access_token = result["access_token"]
    else:
        print("Failed to refresh access token.")
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))


def get_user_object_id(user_principal_name):
    """
    Retrieves the user object ID based on the given user principal name.

    Args:
        user_principal_name (str): email address of the user.

    Returns:
        str: The user object ID.
    """
    global user_object_id

    if user_object_id is not None:
        return user_object_id

    url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        user_data = response.json()
        return user_data["id"]
    else:
        if response.status_code == 401:
            refresh_access_token()
            return get_user_object_id(user_principal_name)
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None


def get_next_appointment(user_object_id):
    """
    Get the user's next calendar appointment using Microsoft Graph API.

    Returns:
        dict: The next appointment details as a dictionary.
    """

    url = "https://graph.microsoft.com/v1.0/me/calendarview"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    start_time = datetime.datetime.now(pytz.utc)
    end_time = start_time + datetime.timedelta(days=1)
    start_time_str = start_time.isoformat()
    end_time_str = end_time.isoformat()
    params = {
        "startDateTime": start_time_str,
        "endDateTime": end_time_str,
        "$orderby": "start/dateTime",
        "$top": 1,
    }
    print(f"URL: {url}")
    print(f"Params: {params}")
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data["value"]:
            appointment = data["value"][0]
            raw_start_time = appointment["start"]["dateTime"]
            raw_end_time = appointment["end"]["dateTime"]
            print(f"Raw start time: {raw_start_time}")
            print(f"Raw end time: {raw_end_time}")

            eastern = pytz.timezone("US/Eastern")
            start_time = (
                isoparse(raw_start_time).replace(tzinfo=pytz.utc).astimezone(eastern)
            )
            end_time = (
                isoparse(raw_end_time).replace(tzinfo=pytz.utc).astimezone(eastern)
            )

            subject = appointment["subject"]
            location = appointment.get("location", {}).get("displayName", "unknown")
            send_maps_link(location)
            formatted_start_time = start_time.strftime('%I:%M %p')
            formatted_end_time = end_time.strftime('%I:%M %p')
            return (
                f"Your next appointment is {subject} at {location} "
                f"from {formatted_start_time} to {formatted_end_time}."
            )

        else:
            return "You don't have any appointments scheduled for today."
    else:
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return "Sorry, I couldn't retrieve your calendar information."


def send_maps_link(address):
    """
    Generates a Google Maps link for the given address and sends it.

    :param address: The address to generate the Google Maps link for.
    :type address: str
    """
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    maps_link = f"https://www.google.com/maps?q={address.replace(' ', '+')}"
    message = client.messages.create(
        body=f"Here's the address for your next appointment: {maps_link}",
        from_=TWILIO_FROM_PHONE_NUMBER,
        to=TEXT_TO_PHONE_NUMBER,
    )
    print(f"Message sent: {message.sid}")


def extract_date(text):
    """
    Extracts date from the given text using voice_recognition's NLP module.

    Args:
        text (str): The input text from which the date needs to be extracted.

    Returns:
        Date object: The extracted date from the input text.
    """
    nlp = importlib.import_module("voice.voice_recognition").nlp
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            parsed_date = dateparser.parse(ent.text)
            if parsed_date:
                return parsed_date.date()
    return None


def create_new_appointment(recognize_speech, tts_output):
    """
    Creates a new appointment in the user's calendar using Microsoft Graph API.

    Args:
        recognize_speech (function): A function to recognize speech input.
        tts_output (function): A function to output text-to-speech.

    Returns:
        None
    """
    url = "https://graph.microsoft.com/v1.0/me/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    print("What is the subject of the appointment?")
    tts_output("What is the subject of the appointment?")
    subject = recognize_speech()
    print("What is the location of the appointment?")
    tts_output("What is the location of the appointment?")
    location = recognize_speech()
    print("What is the date of the appointment?")
    tts_output("What is the date of the appointment?")
    date_str = recognize_speech()
    appointment_date = extract_date(date_str)
    if not appointment_date:
        return "Sorry, I couldn't understand the date. Please try again."
    print("What is the start time of the appointment?")
    tts_output("What is the start time of the appointment?")
    start_time_str = recognize_speech()
    start_time_obj = dateparser.parse(start_time_str)
    print("What is the end time of the appointment?")
    tts_output("What is the end time of the appointment?")
    end_time_str = recognize_speech()
    end_time_obj = dateparser.parse(end_time_str)

    local_timezone = pytz.timezone(
        "America/New_York"
    )
    start_time = local_timezone.localize(
        datetime.datetime.combine(appointment_date, start_time_obj.time())
    ).isoformat()
    end_time = local_timezone.localize(
        datetime.datetime.combine(appointment_date, end_time_obj.time())
    ).isoformat()

    data = {
        "subject": subject,
        "location": {"displayName": location},
        "start": {"dateTime": start_time, "timeZone": local_timezone.zone},
        "end": {"dateTime": end_time, "timeZone": local_timezone.zone},
    }
    response = requests.post(url, headers=headers, json=data, timeout=10)

    if response.status_code == 201:
        return "Appointment created successfully."
    else:
        return "Sorry, I couldn't create the appointment."


def get_emails(user_object_id):
    """
    Retrieves emails from the user's inbox using Microsoft Graph API.

    Returns:
        list: A list of email messages.
    """
    url = "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {
        "$top": 10,  # Adjust the number of emails to fetch
        "$select": "subject,from,receivedDateTime,body",
        "$orderby": "receivedDateTime desc",
    }
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data["value"]
    else:
        if response.status_code == 401:
            refresh_access_token()
            return get_emails()
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return None


def send_email_with_attachments(to, subject, body, attachments=None):
    """
    Send an email with attachments using Microsoft Graph API.

    :param to: The recipient's email address.
    :type to: str
    :param subject: The subject of the email.
    :type subject: str
    :param body: The body of the email.
    :type body: str
    :param attachments: A list of file paths to be attached to the email, defaults to None.
    :type attachments: list, optional
    """
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Prepare attachments
    prepared_attachments = []
    if attachments:
        for attachment in attachments:
            with open(attachment, "rb") as f:
                content_bytes = f.read()
            encoded_content = base64.b64encode(content_bytes).decode("utf-8")
            prepared_attachments.append(
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": os.path.basename(attachment),
                    "contentBytes": encoded_content,
                }
            )

    email_data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML" if body.startswith("<") else "Text",
                "content": body,
            },
            "toRecipients": [{"emailAddress": {"address": to}}],
            "attachments": prepared_attachments,
        },
        "saveToSentItems": "true",
    }
    response = requests.post(url, headers=headers, json=email_data, timeout=10)

    if response.status_code == 202:
        print("Email sent successfully")
    else:
        if response.status_code == 401:
            refresh_access_token()
            send_email_with_attachments(to, subject, body, attachments)
        else:
            print(f"Error: {response.status_code}")
            print(response.json())


if EMAIL_PROVIDER == "365":
    user_principal_name = GRAPH_EMAIL_ADDRESS
    user_object_id = get_user_object_id(user_principal_name)
