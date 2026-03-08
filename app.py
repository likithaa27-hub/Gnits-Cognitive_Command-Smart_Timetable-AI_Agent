import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

creds = Credentials.from_authorized_user_file('token.json', SCOPES)

service = build('calendar', 'v3', credentials=creds)

st.title("📅 AI Smart Timetable")

# Current time and next 7 days
now = datetime.now(timezone.utc)
week_later = now + timedelta(days=7)

# Fetch events
events_result = service.events().list(
    calendarId='primary',
    timeMin=now.isoformat(),
    timeMax=week_later.isoformat(),
    singleEvents=True,
    orderBy='startTime'
).execute()

events = events_result.get('items', [])

# Display events
if not events:
    st.write("No upcoming events.")
else:
    for event in events:
        title = event.get('summary', '')

        # Skip birthdays
        if "birthday" in title.lower():
            continue

        start = event['start'].get('dateTime', event['start'].get('date'))

        st.write("###", title)
        st.write("Start:", start)