"""
This module demonstrates how to work with OS, Base64, and DateTime libraries.
"""
import os
import base64
import msal
import requests
import datetime
from datetime import date, time
import dateparser
import importlib
import pytz
from dateutil.parser import isoparse
import api.ms_authserver as ms_authserver
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_PHONE_NUMBER,
    TEXT_TO_PHONE_NUMBER,
    GRAPH_EMAIL_ADDRESS,
    GRAPH_CLIENT_ID,
    GRAPH_CLIENT_SECRET,
    GRAPH_TENANT_ID,
)

# Set up authentication with Microsoft Graph API
authority = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}"
client_id = GRAPH_CLIENT_ID
client_secret = GRAPH_CLIENT_SECRET
scope = ["https://graph.microsoft.com/.default"]
redirect_uri = "http://localhost:8000"

# Get the authorization code from ms_authserver
authorization_code = ms_authserver.get_auth_code()

user_object_id = None

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

user_principal_name = GRAPH_EMAIL_ADDRESS


def perform_graph_api_request(authorization_code):
    # Your code to perform the Graph API request using the authorization_code
    pass


def refresh_access_token():
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
    global user_object_id

    if user_object_id is not None:  # Add this block
        return user_object_id

    url = f"https://graph.microsoft.com/v1.0/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
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
    Get the user's next appointment from their calendar using Microsoft Graph API.

    Returns:
        dict: The next appointment details as a dictionary.
    """
    # Get the user's next appointment from their calendar
    url = f"https://graph.microsoft.com/v1.0/me/calendarview"
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
    response = requests.get(url, headers=headers, params=params)
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
            return f"Your next appointment is {subject} at {location} from {start_time.strftime('%I:%M %p')} to {end_time.strftime('%I:%M %p')}."
        else:
            return "You don't have any appointments scheduled for today."
    else:
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return "Sorry, I couldn't retrieve your calendar information."


def send_maps_link(address):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    maps_link = f"https://www.google.com/maps?q={address.replace(' ', '+')}"
    message = client.messages.create(
        body=f"Here's the address for your next appointment: {maps_link}",
        from_=TWILIO_FROM_PHONE_NUMBER,
        to=TEXT_TO_PHONE_NUMBER,
    )
    print(f"Message sent: {message.sid}")


def extract_date(text):
    nlp = importlib.import_module("voice_recognition").nlp
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            parsed_date = dateparser.parse(ent.text)
            if parsed_date:
                return parsed_date.date()
    return None


def create_new_appointment(recognize_speech, tts_output):
    # Create a new appointment in the user's calendar
    url = f"https://graph.microsoft.com/v1.0/me/events"
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
    )  # Replace with your local timezone
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
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        return "Appointment created successfully."
    else:
        return "Sorry, I couldn't create the appointment."


def get_emails():
    url = f"https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    params = {
        "$top": 10,  # Adjust the number of emails to fetch
        "$select": "subject,from,receivedDateTime,body",
        "$orderby": "receivedDateTime desc",
    }
    response = requests.get(url, headers=headers, params=params)
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
    url = f"https://graph.microsoft.com/v1.0/me/sendMail"  # Updated URL
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
    response = requests.post(url, headers=headers, json=email_data)

    if response.status_code == 202:
        print("Email sent successfully")
    else:
        if response.status_code == 401:
            refresh_access_token()
            send_email_with_attachments(to, subject, body, attachments)
        else:
            print(f"Error: {response.status_code}")
            print(response.json())


if __name__ == "__main__":
    user_principal_name = GRAPH_EMAIL_ADDRESS
    user_object_id = get_user_object_id(user_principal_name)

