#!/usr/bin/env python
# coding: utf-8

get_ipython().system('jupyter nbconvert --to script --no-prompt calendar_proc.ipynb')

from __future__ import print_function
import datetime
import pickle
import os.path
try:
    from googleapiclient.discovery import build
except ImportError:
    print("Error, Module " + "google-api-python-client" + " required.")
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Error, Module " + "google-auth-httplib2" + " required.")
try:
    from google.auth.transport.requests import Request
except ImportError:
    print("Error, Module " + "google-auth-oauthlib" + " required.")
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

window_size = 60
color_map = {
    "1":"Lavender",
    "2":"Sage",
    "3":"Grape",
    "4":"Flamingo",
    "5":"Banana",
    "6":"Tangerine",
    "7":"Peacock",
    "8":"Graphite",
    "9":"Blueberry",
    "10":"Basil",
    "11":"Tomato",
    "-":"Peacock"
}


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    start_date = (datetime.datetime.today() - datetime.timedelta(window_size)).isoformat() + 'Z'
    print(f'Getting the events in the {start_date} - {now} interval:')
    events_result = service.events().list(calendarId='primary', timeMin=start_date, timeMax=now,
                                        maxResults=2500, singleEvents=True, 
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(f"Total number of events: {len(events)}")

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(start, end, event['summary'], end=" ")
        try:
            print(color_map[event['colorId']])
        except:
            print(color_map["-"])


if __name__ == '__main__':
    main()




