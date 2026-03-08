from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

creds = Credentials.from_authorized_user_file('token.json', SCOPES)

service = build('calendar', 'v3', credentials=creds)

calendar_list = service.calendarList().list().execute()

for calendar in calendar_list['items']:
    print(calendar['summary'], "->", calendar['id'])