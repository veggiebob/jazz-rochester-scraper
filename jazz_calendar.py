import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class JazzCalendar:
    service: Resource
    auth_dir: str

    def __init__(self, auth_dir='creds/google'):
        self.auth_dir = auth_dir
        creds = self._authenticate_google_calendar()
        self.service = build('calendar', 'v3', credentials=creds)
        self._jazz_calendar_id = None

    def _authenticate_google_calendar(self):
        creds = None
        # Check if token.json file exists, which stores user tokens.
        token_path = os.path.join(self.auth_dir, 'token.json')
        creds_path = os.path.join(self.auth_dir, 'credentials.json')
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, ask the user to log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for future use.
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds


    def add_calendar_event(self, event: dict):
        event = self.service.events().insert(calendarId=self.jazz_calendar_id, body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")

    @property
    def jazz_calendar_id(self) -> str:
        if self._jazz_calendar_id is None:
            entries = [
                calendar_entry['id']
                for calendar_entry in self.service.calendarList().list().execute()['items']
                if 'jazz' in calendar_entry['summary'].lower()
            ]
            if len(entries) == 0:
                raise Exception("Could not find jazz calendar!")
            self._jazz_calendar_id = entries[0]
        return self._jazz_calendar_id


def main():
    pass


if __name__ == '__main__':
    main()
