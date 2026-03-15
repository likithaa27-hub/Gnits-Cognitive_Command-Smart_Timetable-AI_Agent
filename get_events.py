import os
from datetime import datetime, timedelta, timezone
from calendar_auth import get_service

service = get_service()

now = datetime.now(timezone.utc)
week_later = now + timedelta(days=7)

events_result = service.events().list(
    calendarId="primary",
    timeMin=now.isoformat(),
    timeMax=week_later.isoformat(),
    maxResults=10,
    singleEvents=True,
    orderBy="startTime",
).execute()

events = events_result.get("items", [])

print("\nUpcoming events (next 7 days):\n")
if not events:
    print("No upcoming events.")
else:
    for event in events:
        summary = event.get("summary", "No Title")
        if "birthday" in summary.lower():
            continue
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"{summary} -> {start}")