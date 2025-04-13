from arklex.env.tools.tools import register_tool
from datetime import datetime, timedelta
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_user_availability_imple(month):
    # Step 1: Google Calendar API init
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'arklex/env/tools/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Step 2: Convert input like '2025-06' to start/end
    start = f"{month}-01T00:00:00Z"
    end_date = datetime.strptime(f"{month}-01", "%Y-%m-%d") + timedelta(days=31)
    end = end_date.strftime("%Y-%m-01T00:00:00Z")

    # Step 3: Fetch events
    events_result = service.events().list(calendarId='primary', timeMin=start,
                                          timeMax=end, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Step 4: Parse busy days
    busy_days = set()
    for event in events:
        start_date = event['start'].get('date', event['start'].get('dateTime', ''))[:10]
        busy_days.add(start_date)

    all_days = [(datetime.strptime(f"{month}-01", "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range(31)
                if (datetime.strptime(f"{month}-01", "%Y-%m-%d") + timedelta(days=i)).month == int(month[-2:])]

    free_days = [d for d in all_days if d not in busy_days]

    return {"available_dates": free_days}

@register_tool(
    "Query user's Google Calendar and return available travel dates for a given month (YYYY-MM)",
    [
        {
            "name": "month",
            "type": "string",
            "description": "Month string in format YYYY-MM",
            "prompt": "Which month do you want to check availability?",
            "required": True
        }
    ],
    [
        {
            "name": "available_dates",
            "type": "list",
            "value": [],
            "description": "List of dates when user is free"
        }
    ]
)

def get_user_availability(month):
    # 包裝為 Arklex 能觸發的無參函數版本
    return get_user_availability_imple(month)  # 假設這是 chatbot input

# @register_tool(
#     name="get_user_availability",
#     description="Query user's Google Calendar and return available travel dates for a given month (YYYY-MM)",
#     slots=["month"],
#     outputs=["available_dates"]
# )

# def get_user_availability():
#     # 包裝為 Arklex 能觸發的無參函數版本
#     return get_user_availability_imple("2025-06")

# def get_user_availability_impl(month):
#     # 真正邏輯
#     ...
#     return {"available_dates": [...]}

# @register_tool(
#     "Check calendar availability for travel",
#     [
#         {
#             "name": "month",
#             "type": "string",
#             "description": "Month in YYYY-MM format",
#             "prompt": "Which month do you want to check?",
#             "required": True
#         }
#     ],
#     [
#         {
#             "name": "available_dates",
#             "type": "list",
#             "value": [],
#             "description": "List of available travel dates"
#         }
#     ]
# )