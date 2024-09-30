import base64
import os
import datetime
import binascii
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import (
    EMAIL_PROVIDER,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    GMAIL_ADDRESS,
)

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://mail.google.com/",
          "https://www.googleapis.com/auth/calendar"]

creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            SCOPES,
        )
        print("Flow object:", flow)
        creds = flow.run_local_server(port=8080)
    with open("token.json", "w") as token:
        token.write(creds.to_json())

gmail_service = build("gmail", "v1", credentials=creds)
calendar_service = build("calendar", "v3", credentials=creds)


def send_email(subject, body, to=GMAIL_ADDRESS):
    message = {"subject": subject, "body": body, "to": to}
    create_message_and_send(message)


def create_message_and_send(message):
    to = message["to"]
    subject = message["subject"]
    body = message["body"]
    message = f"Subject: {subject}\n\n{body}"
    message_bytes = message.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(message_bytes)
    base64_message = base64_bytes.decode("utf-8")

    raw_message = {"raw": base64_message}
    send_message = (
        gmail_service.users().messages().send(userId="me", body=raw_message).execute()
    )
    print(F"Message Id: {send_message['id']}")


def get_next_google_calendar_event():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = (
        calendar_service.events()
        .list(calendarId="primary", timeMin=now, maxResults=1, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        return "No upcoming events found."
    else:
        event = events[0]
        start = event["start"].get("dateTime", event["start"].get("date"))
        return f"Next event: {event['summary']} at {start}"


def delete_email(message_id):
    gmail_service.users().messages().delete(userId='me', id=message_id).execute()


def get_emails_google(user_object_id=None):
    results = gmail_service.users().messages().list(
        userId='me', labelIds=['INBOX'], maxResults=5).execute()
    messages = results.get('messages', [])

    emails = []
    for message in messages:
        msg = gmail_service.users().messages().get(
            userId='me', id=message['id']).execute()

        sender, subject, body = extract_email_data(msg)

        snippet = body[:100] if body else 'N/A'
        emails.append({'id': message['id'], 'subject': subject,
                      'from': sender, 'snippet': snippet})
    return emails


def extract_email_data(msg):
    headers = msg['payload']['headers']
    sender = ''
    subject = ''
    for header in headers:
        if header['name'].lower() == 'from':
            sender = header['value']
        elif header['name'].lower() == 'subject':
            subject = header['value']

    if 'parts' in msg['payload']:
        parts = msg['payload']['parts']
        body = ''
        for part in parts:
            part_body = part['body'].get('data', '')
            try:
                decoded_body_bytes = base64.urlsafe_b64decode(part_body)
                decoded_body = decoded_body_bytes.decode(errors='ignore')
            except binascii.Error as e:
                print(f"Error decoding base64-encoded data: {e}")
                decoded_body = ''

            if part['mimeType'] == 'text/plain':
                body = decoded_body
            elif part['mimeType'] == 'text/html' and not body:
                soup = BeautifulSoup(decoded_body, 'html.parser')
                body = soup.get_text()

        if not body and parts:
            body = decoded_body
    else:
        body = msg['payload']['body'].get('data', '')
        try:
            body_bytes = base64.urlsafe_b64decode(body)
            body = body_bytes.decode(errors='ignore')
        except binascii.Error as e:
            print(f"Error decoding base64-encoded data: {e}")
            body = ''

    return sender, subject, body
