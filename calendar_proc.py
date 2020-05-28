#!/usr/bin/env python
# coding: utf-8

get_ipython().system('jupyter nbconvert --to script --no-prompt calendar_proc.ipynb')

from __future__ import print_function
from matplotlib import pyplot as plt
import matplotlib
matplotlib.rcParams.update({'font.size': 18})
from itertools import groupby
from statistics import mean
import datetime
import pickle
import os.path
# import re
try:
    from googleapiclient.discovery import build
except ImportError:
    print("Error, Module google-api-python-client required.")
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("Error, Module google-auth-httplib2 required.")
try:
    from google.auth.transport.requests import Request
except ImportError:
    print("Error, Module google-auth-oauthlib required.")
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
event_types = {
    "1":"work",
    "2":"ancillary",
    "3":"exercise",
    "4":"meal",
    "5":"break",
    "6":"off-time"
}
def classify(event):
    event_color = ""
    event_type = ""
    try:
        event_color = color_map[event['colorId']]
    except:
        event_color = color_map["-"]
    if event_color == "Basil" or "picogrid" in event["summary"].lower():
        return event_types["1"]
    elif event_color == "Sage":
        return event_types["2"]
    elif event_color == "Tangerine":
        return event_types["3"]
    elif event_color == "Blueberry" or event_color == "Graphite":
        return event_types["4"]
    elif event_color == "Flamingo":
        return event_types["5"]
    elif event_color == "Peacock" or event_color == "Banana":
        return event_types["6"]
    return "undefined"
        
        
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
    print(f'Getting the events in the {start_date[:10]} ~ {now[:10]} interval:')
    events_result = service.events().list(calendarId='primary', timeMin=start_date, timeMax=now,
                                        maxResults=2500, singleEvents=True, 
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(f"Total number of events: {len(events)}")
    days = {}
    if not events:
        print('No upcoming events found.')
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        event["duration"] = datetime.datetime.fromisoformat(end_time) -                             datetime.datetime.fromisoformat(start_time)
        start_day = start_time[:10]
        if start_day not in days:
            days[start_day] = []
        days[start_day].append(event)
        event["class"] = classify(event)
#         print(start_time, end_time, event['summary'], event["class"])
    date_arr = [datetime.date.fromisoformat(day) for day in days]
    start_of_day_arr = []
    work_hours_arr = []
    k = 0
#     print("N  Date        Work Hours  Rest Hours  Start of Day")
    for day in days:
        k+=1
        day_events = days[day]
        work_hours = datetime.timedelta()
        start_of_day = day_events[0]["start"].get('dateTime', event['start'].get('date'))
        if start_of_day == None:
            start_of_day = day_events[1]["start"].get('dateTime', event['start'].get('date'))
#         if day[]
        if day[:4] == "2020" and int(day[5:7]) < 5 and int(day[8:10]) < 26:    
            hr = int(start_of_day[11:13])+1
            start_of_day = start_of_day[:11] + (hr<10)*'0' + str(hr) + start_of_day[13:15]
        for event in day_events:
            if event["class"] == "work" or event["class"] == "ancillary":
                work_hours += event["duration"]
        rest_hours = datetime.timedelta(hours=16) - work_hours
        work_hours_arr.append(work_hours.total_seconds()/3600)
        start_of_day_arr.append(float(start_of_day[11:13])+float(start_of_day[14:16])/60)
    
    binned_start_of_day_arr = [int(round(tmstp)) for tmstp in start_of_day_arr]
    binned_grpd_strts = groupby(sorted(binned_start_of_day_arr), lambda p:p)
    binned_grpd_strts = [(group[0], len([i for i in group[1]])) for group in binned_grpd_strts]
    scale_f = max(binned_grpd_strts,key=lambda item:item[1])[1]/10
    
    sorted_mapping = sorted(zip(binned_start_of_day_arr, work_hours_arr))
    grouper = groupby(sorted_mapping, lambda p:p[0])
    averaged_binned_wrk_hrs = [(group[0], mean([pair[1] for pair in group[1]])) for group in grouper]
    
    movave_window = 7
    movave_work_hrs = []
    for i,num in enumerate(work_hours_arr):
        movave_work_hrs.append(mean(work_hours_arr[max(0,i-movave_window):i+1])*movave_window)
    
    print(f"Total number of days: {len(days)}/{window_size}")                        
# # Bar plot of average Work Hours vs Start of Day
#     plt.figure(figsize=(20,10))
#     plt.bar([pair[0] for pair in binned_grpd_strts], 
#             [pair[1]/scale_f for pair in binned_grpd_strts],
#             color="grey",
#             alpha=.85,
#             edgecolor="black",
#             width=.6,
#            )
#     plt.bar([pair[0] for pair in averaged_binned_wrk_hrs], 
#             [pair[1] for pair in averaged_binned_wrk_hrs],
#             color="darkgreen", 
#             alpha=.7,
#             edgecolor="black"
#            )    
#     plt.xlabel("Start of Day")
#     plt.ylabel("Work Hours (hr) / Observations (scaled)")
#     plt.show()
    
# # 2D histogram of Start of Day vs Work Hours    
#     plt.figure(figsize=(20,10))
#     plt.hist2d(start_of_day_arr,work_hours_arr)
#     plt.xlabel("Start of Day")
#     plt.ylabel("Work Hours")
#     plt.show()
    
# Scatter plot of Work Hours vs Time
    fig,ax = plt.subplots(figsize=(20,10),constrained_layout=True)
    dates = [datetime.date.fromisoformat(day) for day in days]
    plt.xlim((dates[0],dates[-1]))
    plt.grid()
    ax.scatter(dates, 
                work_hours_arr,
                marker='s',
                color='darkgreen',
               )
    ax.plot(dates,
             work_hours_arr,
             color='darkgreen',
             linestyle='--',
             linewidth=1,
             alpha=.6,
            )
    ax.set_ylabel("Daily Work Hours (hr)")
    secaxy = ax.twinx()
    secaxy.set_ylabel("Weekly Work Hours (hr)")
    secaxy.set_ylim((-2.75,56.5))
    secaxy.plot(dates,
                movave_work_hrs,
                linewidth=2)
    
    
    
    
if __name__ == '__main__':
    main()




