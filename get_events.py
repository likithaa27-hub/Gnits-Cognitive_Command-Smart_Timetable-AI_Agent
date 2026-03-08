import os.path
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())

service = build('calendar', 'v3', credentials=creds)

# Get today's time in UTC
now = datetime.now(timezone.utc)
week_later = now + timedelta(days=7)

time_min = now.isoformat()
time_max = week_later.isoformat()

print("\nUpcoming events (next 7 days):\n")

# ONLY your calendar
calendarId='primary'

events_result = service.events().list(
    calendarId=calendarId,
    timeMin=time_min,
    timeMax=time_max,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

if not events:
    print("No upcoming events.")
else:
    for event in events:

        summary = event.get('summary', 'No Title')

        # Skip birthdays
        if "birthday" in summary.lower():
            continue

        start = event['start'].get('dateTime', event['start'].get('date'))

        print(summary, "->", start)