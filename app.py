from datetime import datetime, timedelta, date
import calendar
import sqlite3
import io

import pandas as pd
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import matplotlib.pyplot as plt
from groq import Groq
import icalendar
from icalendar import Calendar, Event

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============ THEME CONFIGURATION ============
DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
ACCENT_COLOR = "#3b82f6"
ACCENT_HOVER = "#2563eb"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
BORDER_COLOR = "#334155"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
ERROR_COLOR = "#ef4444"
INFO_COLOR = "#3b82f6"

PRIORITY_COLORS = {
    "high": "#ef4444",
    "medium": "#f59e0b",
    "low": "#10b981"
}

# ============ MODERN SAAS THEME CSS ============
saas_theme = f"""
<style>
    * {{
        color-scheme: dark;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {DARK_BG};
    }}

    [data-testid="stSidebar"] {{
        background-color: {DARK_BG};
        border-right: 1px solid {BORDER_COLOR};
    }}

    [data-testid="stHeader"] {{
        background-color: {DARK_BG};
        border-bottom: 1px solid {BORDER_COLOR};
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {TEXT_PRIMARY} !important;
        font-weight: 700 !important;
    }}

    h1 {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }}

    p, span, label, div {{
        color: {TEXT_PRIMARY} !important;
    }}

    [data-testid="stMetricContainer"] {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }}

    [data-testid="stMetricContainer"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.1) !important;
        border-color: {ACCENT_COLOR} !important;
    }}

    [data-testid="stMetricContainer"] > div:first-child {{
        color: {ACCENT_COLOR} !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}

    [data-testid="stMetricContainer"] > div:last-child {{
        color: {TEXT_PRIMARY} !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }}

    [data-testid="stForm"] {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }}

    [data-testid="stTabs"] {{
        background-color: transparent !important;
    }}

    button[data-baseweb="tab"] {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {TEXT_SECONDARY} !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        margin-right: 8px !important;
    }}

    button[data-baseweb="tab"]:hover {{
        background-color: {BORDER_COLOR} !important;
        color: {TEXT_PRIMARY} !important;
        border-color: {ACCENT_COLOR} !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #6366f1 100%) !important;
        color: white !important;
        border-color: {ACCENT_COLOR} !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }}

    .stTextInput > div > div {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
        transition: all 0.3s ease !important;
    }}

    .stTextInput > div > div:focus {{
        border-color: {ACCENT_COLOR} !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }}

    .stSelectbox > div > div {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
    }}

    .stDateInput > div > div {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
    }}

    .stTimeInput > div > div {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        color: {TEXT_PRIMARY} !important;
    }}

    .stMultiSelect > div > div {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #6366f1 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, {ACCENT_HOVER} 0%, #4f46e5 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
    }}

    .stButton > button:active {{
        transform: translateY(0) !important;
    }}

    .stSuccess {{
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid {SUCCESS_COLOR} !important;
        border-radius: 8px !important;
        color: {SUCCESS_COLOR} !important;
        padding: 12px 16px !important;
    }}

    .stError {{
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid {ERROR_COLOR} !important;
        border-radius: 8px !important;
        color: {ERROR_COLOR} !important;
        padding: 12px 16px !important;
    }}

    .stWarning {{
        background-color: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid {WARNING_COLOR} !important;
        border-radius: 8px !important;
        color: {WARNING_COLOR} !important;
        padding: 12px 16px !important;
    }}

    .stInfo {{
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid {INFO_COLOR} !important;
        border-radius: 8px !important;
        color: {INFO_COLOR} !important;
        padding: 12px 16px !important;
    }}

    [data-testid="stExpander"] {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}

    [data-testid="stExpander"] > details > summary {{
        background-color: {BORDER_COLOR} !important;
        color: {TEXT_PRIMARY} !important;
        font-weight: 600 !important;
    }}

    [data-testid="stDataFrame"] {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}

    [data-testid="stTable"] {{
        background-color: {CARD_BG} !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}

    [data-testid="stTable"] th {{
        background-color: {BORDER_COLOR} !important;
        color: {TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }}

    [data-testid="stTable"] td {{
        color: {TEXT_SECONDARY} !important;
        padding: 12px !important;
        border-bottom: 1px solid {BORDER_COLOR} !important;
    }}

    .stDivider {{
        border-color: {BORDER_COLOR} !important;
        margin: 24px 0 !important;
    }}

    hr {{
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent 0%, {BORDER_COLOR} 50%, transparent 100%) !important;
        margin: 24px 0 !important;
    }}

    [data-testid="stChatMessage"] {{
        background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }}

    ::-webkit-scrollbar {{
        width: 8px !important;
    }}

    ::-webkit-scrollbar-track {{
        background: {DARK_BG} !important;
    }}

    ::-webkit-scrollbar-thumb {{
        background: {BORDER_COLOR} !important;
        border-radius: 4px !important;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {ACCENT_COLOR} !important;
    }}

    @media (max-width: 768px) {{
        [data-testid="stMetricContainer"] {{
            padding: 16px !important;
        }}

        .stButton > button {{
            padding: 10px 20px !important;
            font-size: 14px !important;
        }}
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    [data-testid="stVerticalBlock"] > div {{
        animation: fadeIn 0.5s ease-out !important;
    }}

    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    button:focus, input:focus, select:focus, textarea:focus {{
        outline: 2px solid {ACCENT_COLOR} !important;
        outline-offset: 2px !important;
    }}
</style>
"""

st.markdown(saas_theme, unsafe_allow_html=True)

# ============ HELPER FUNCTIONS ============
SCOPES = ['https://www.googleapis.com/auth/calendar']


@st.cache_resource
def get_calendar_service():
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        st.warning(f"Could not initialize Google Calendar: {str(e)}")
        return None


def add_to_google_calendar(title, start_dt, end_dt):
    try:
        service = get_calendar_service()
        if not service:
            return
        event = {
            'summary': title,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }
        service.events().insert(calendarId='primary', body=event).execute()
    except Exception as e:
        st.warning(f"Could not sync to Google Calendar: {str(e)}")


def generate_ics_calendar(events):
    """Generate iCalendar file from events"""
    cal = Calendar()
    cal.add('prodid', '-//Smart Timetable//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'Smart Timetable Schedule')
    cal.add('x-wr-timezone', 'Asia/Kolkata')

    for event in events:
        ics_event = Event()
        ics_event.add('summary', event['title'])
        ics_event.add('dtstart', event['start'])
        ics_event.add('dtend', event['end'])
        ics_event.add('dtstamp', datetime.now())
        ics_event.add('uid', f"{event['title']}_{event['start'].timestamp()}@smarttimetable")
        ics_event.add('description', f"Source: {event.get('source', 'custom')}")
        ics_event.add('location', 'Academic')
        cal.add_component(ics_event)

    return cal.to_ical()


def generate_schedule_report(events, assignments):
    """Generate a detailed schedule report"""
    report = io.StringIO()
    report.write("=" * 80 + "\n")
    report.write("SMART TIMETABLE - SCHEDULE REPORT\n")
    report.write("=" * 80 + "\n\n")
    
    report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # Events Summary
    report.write("CALENDAR EVENTS\n")
    report.write("-" * 80 + "\n")
    if events:
        for event in sorted(events, key=lambda x: x['start']):
            report.write(f"Title: {event['title']}\n")
            report.write(f"Date: {event['start'].strftime('%Y-%m-%d')}\n")
            report.write(f"Time: {event['start'].strftime('%H:%M')} - {event['end'].strftime('%H:%M')}\n")
            report.write(f"Duration: {(event['end'] - event['start']).total_seconds() / 3600:.1f} hours\n")
            report.write(f"Type: {event.get('source', 'custom').capitalize()}\n")
            report.write("-" * 80 + "\n")
    else:
        report.write("No events scheduled.\n\n")

    # Assignments Summary
    report.write("\nASSIGNMENTS\n")
    report.write("-" * 80 + "\n")
    if assignments:
        for a in sorted(assignments, key=lambda x: x['deadline']):
            report.write(f"Title: {a['title']}\n")
            report.write(f"Deadline: {a['deadline'].strftime('%Y-%m-%d %H:%M')}\n")
            report.write(f"Priority: {a['priority'].upper()}\n")
            days_left = (a['deadline'].date() - date.today()).days
            report.write(f"Days Left: {days_left}\n")
            report.write("-" * 80 + "\n")
    else:
        report.write("No assignments scheduled.\n\n")

    # Statistics
    report.write("\nSTATISTICS\n")
    report.write("-" * 80 + "\n")
    if events:
        total_hours = sum((e['end'] - e['start']).total_seconds() / 3600 for e in events)
        report.write(f"Total Events: {len(events)}\n")
        report.write(f"Total Scheduled Hours: {total_hours:.1f} hours\n")
    if assignments:
        report.write(f"Total Assignments: {len(assignments)}\n")
        high_priority = sum(1 for a in assignments if a['priority'].lower() == 'high')
        report.write(f"High Priority Tasks: {high_priority}\n")

    return report.getvalue()


def priority_badge(priority):
    """Return HTML badge for priority"""
    color = PRIORITY_COLORS.get(priority.lower(), TEXT_SECONDARY)
    return f"<span style='background-color:{color}20;color:{color};padding:4px 8px;border-radius:4px;font-weight:bold;border:1px solid {color};'>{priority.capitalize()}</span>"


def event_card(title, description, time_info, priority=None, event_type="custom"):
    """Render an event card with modern styling"""
    icon = "📅" if event_type == "custom" else "📚"
    priority_html = f" {priority_badge(priority)}" if priority else ""
    
    st.markdown(f"""
    <div style='
        background-color: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-left: 4px solid {ACCENT_COLOR};
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    '>
        <div style='display: flex; justify-content: space-between; align-items: start;'>
            <div style='flex: 1;'>
                <strong style='color: {TEXT_PRIMARY}; font-size: 16px;'>{icon} {title}</strong>
                <p style='color: {TEXT_SECONDARY}; margin: 8px 0 0 0; font-size: 14px;'>{description}</p>
                <small style='color: {TEXT_SECONDARY};'>{time_info}</small>
            </div>
            {priority_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_calendar_grid(year, month, events):
    """Render monthly calendar grid with proper HTML structure"""
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Build the calendar HTML with simpler approach
    html = f"""<div style="background-color:{CARD_BG};border:1px solid {BORDER_COLOR};border-radius:8px;padding:20px;margin:20px 0;">
    <h3 style="text-align:center;color:{TEXT_PRIMARY};margin-top:0;margin-bottom:20px;">{month_name} {year}</h3>
    <table style="width:100%;border-collapse:collapse;">
    <tr>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Mon</th>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Tue</th>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Wed</th>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Thu</th>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Fri</th>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Sat</th>
    <th style="background-color:{BORDER_COLOR};color:{TEXT_PRIMARY};padding:12px;text-align:center;font-weight:bold;border:1px solid {BORDER_COLOR};">Sun</th>
    </tr>"""
    
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += f"<td style='background-color:{DARK_BG};border:1px solid {BORDER_COLOR};height:120px;padding:8px;'></td>"
            else:
                day_events = [e for e in events if e['start'].day == day and e['start'].month == month and e['start'].year == year]
                
                events_html = ""
                for e in day_events:
                    source_color = ACCENT_COLOR if e.get('source') == 'course' else '#8b5cf6'
                    event_title = e['title'][:12]
                    event_time = e['start'].strftime('%H:%M')
                    events_html += f"<div style='background-color:{source_color};color:white;padding:3px 5px;margin:2px 0;border-radius:3px;font-size:10px;'><strong>{event_title}</strong> {event_time}</div>"
                
                html += f"<td style='background-color:{CARD_BG};border:1px solid {BORDER_COLOR};height:120px;padding:8px;vertical-align:top;'><div style='font-weight:bold;color:{ACCENT_COLOR};margin-bottom:6px;font-size:14px;'>{day}</div><div>{events_html}</div></td>"
        
        html += "</tr>"
    
    html += "</table></div>"
    
    st.markdown(html, unsafe_allow_html=True)


def check_conflict(new_event, events):
    for e in events:
        if not (new_event["end"] <= e["start"] or new_event["start"] >= e["end"]):
            return True
    return False


def find_conflicts(events, assignments):
    """Detect conflicts between events and assignments"""
    conflicts = []
    
    # Check event-to-event conflicts
    for i, e1 in enumerate(events):
        for e2 in events[i+1:]:
            if not (e1["end"] <= e2["start"] or e1["start"] >= e2["end"]):
                conflicts.append({
                    "type": "event",
                    "description": f"⚠️ '{e1['title']}' conflicts with '{e2['title']}'",
                    "severity": "high"
                })
    
    # Check assignment deadlines near exams
    for a in assignments:
        for e in events:
            if e['title'] != a['title']:
                days_diff = abs((a['deadline'].date() - e['start'].date()).days)
                if days_diff <= 1 and days_diff > 0:
                    conflicts.append({
                        "type": "deadline",
                        "description": f"⏰ Assignment '{a['title']}' due {days_diff} day(s) from event '{e['title']}'",
                        "severity": "medium"
                    })
    
    return conflicts


def find_free_slots(events, start_window=None, end_window=None):
    if start_window is None:
        start_window = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    if end_window is None:
        end_window = start_window + timedelta(days=7)
    free = []
    current = start_window

    while current < end_window:
        if current > datetime.now() and 9 <= current.hour < 21:
            clash = False
            for e in events:
                if e["start"] <= current < e["end"]:
                    clash = True
                    break
            if not clash:
                free.append(current)
        current += timedelta(hours=1)

    return free


def suggest_time(events, start_window=None, end_window=None):
    free = find_free_slots(events, start_window, end_window)
    return free[0] if free else None


def generate_classes(course_list):
    events = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for i in range(7):
        day_date = today + timedelta(days=i)
        day_name = day_date.strftime("%a")

        for course in course_list:
            if day_name in course["days"]:
                start = day_date.replace(hour=course["start_time"], minute=0)
                end = day_date.replace(hour=course["end_time"], minute=0)
                if end <= start:
                    continue
                events.append({
                    "id": f"{course['name']}_{day_date.strftime('%Y-%m-%d')}",
                    "title": course["name"],
                    "start": start,
                    "end": end,
                    "source": "course"
                })

    return events


def get_priority_score(priority):
    return {"high": 3, "medium": 2, "low": 1}.get(priority.lower(), 0)


def allocate_study(assignments, free_slots):
    plan = []
    assignments_sorted = sorted(assignments, key=lambda x: get_priority_score(x["priority"]), reverse=True)
    available_slots = free_slots.copy()

    for task in assignments_sorted:
        slots_needed = 2 if task["priority"].lower() == "high" else 1
        count = 0
        for slot in list(available_slots):
            if slot < task["deadline"] and count < slots_needed:
                plan.append({
                    "task": task["title"],
                    "deadline": task["deadline"],
                    "priority": task["priority"],
                    "time": slot
                })
                available_slots.remove(slot)
                count += 1
            if count >= slots_needed:
                break

    return plan


def ask_ai(query, events, assignments):
    if not query.strip():
        return ""

    try:
        event_text = "\n".join([
            f"{e['title']} from {e['start']} to {e['end']}"
            for e in events
        ]) if events else "No events scheduled"

        assignment_text = "\n".join([
            f"{a['title']} due {a['deadline']} priority {a['priority']}"
            for a in assignments
        ]) if assignments else "No assignments"

        prompt = f"""
You are a smart academic scheduling assistant.

Rules:
- Be short and clear
- Give exact times
- Prioritize assignments by deadline
- Suggest practical study slots
- Be encouraging and supportive

Events:
{event_text}

Assignments:
{assignment_text}

User: {query}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return "AI is currently unavailable. Try asking about free time or study recommendations."


def load_courses():
    rows = c.execute("SELECT rowid, subject, days, start_time, end_time FROM courses_v2").fetchall()
    courses = []

    for rowid, subject, days, start_time, end_time in rows:
        days_list = [d.strip() for d in days.split(",") if d.strip()]
        try:
            start_hour = int(start_time.split(":")[0])
            end_hour = int(end_time.split(":")[0])
        except ValueError:
            continue

        courses.append({
            "rowid": rowid,
            "name": subject,
            "days": days_list,
            "start_time": start_hour,
            "end_time": end_hour
        })

    return courses


def load_assignments():
    rows = c.execute("SELECT rowid, title, deadline, priority FROM assignments_v2").fetchall()
    assignments = []

    for rowid, title, deadline, priority in rows:
        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        assignments.append({
            "rowid": rowid,
            "title": title,
            "deadline": deadline_dt,
            "priority": priority
        })

    return assignments


def load_custom_events():
    if "custom_events" not in st.session_state:
        st.session_state.custom_events = []
    return st.session_state.custom_events


def sort_events(events):
    return sorted(events, key=lambda x: x["start"])


# ============ DATABASE SETUP ============
conn = sqlite3.connect("schedule.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS courses_v2 (
    subject TEXT,
    days TEXT,
    start_time TEXT,
    end_time TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS assignments_v2 (
    title TEXT,
    deadline TEXT,
    priority TEXT
)""")
conn.commit()

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Smart Timetable AI Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ HEADER ============
col_header_1, col_header_2 = st.columns([0.7, 0.3])

with col_header_1:
    st.markdown(f"<h1 style='margin-bottom: 0.5rem;'>📅 Smart Timetable AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {TEXT_SECONDARY}; margin-top: 0; font-size: 16px;'>AI-powered academic planner with smart scheduling, conflict detection & analytics</p>", unsafe_allow_html=True)

with col_header_2:
    today = date.today()
    st.markdown(f"<p style='text-align: right; color: {TEXT_SECONDARY}; margin-top: 1rem; font-size: 14px;'>{today.strftime('%A, %B %d, %Y')}</p>", unsafe_allow_html=True)

st.divider()

# ============ LOAD DATA ============
course_events = generate_classes(load_courses())
custom_events = load_custom_events()
all_events = sort_events(course_events + custom_events)
assignments = load_assignments()

if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

# ============ METRICS DASHBOARD ============
st.markdown("### 📊 Quick Overview")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4, gap="large")

with metric_col1:
    metric_col1.metric("📅 Events", len(all_events), "Total scheduled")

with metric_col2:
    metric_col2.metric("📚 Assignments", len(assignments), "To complete")

with metric_col3:
    free_slots_count = len(find_free_slots(all_events))
    metric_col3.metric("⏱ Free Slots", free_slots_count, "Next 7 days")

with metric_col4:
    conflicts = find_conflicts(all_events, assignments)
    metric_col4.metric("⚠️ Conflicts", len(conflicts), "Detected")

st.divider()

# ============ TABS ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Calendar",
    "📚 Study Plan",
    "🔄 Conflict Resolution",
    "🤖 AI Assistant",
    "📊 Analytics"
])

# ================= TAB 1: CALENDAR =================
with tab1:
    st.markdown("## 📅 Calendar Dashboard")
    
    # Calendar View Options
    col_cal_options1, col_cal_options2 = st.columns(2, gap="large")
    
    with col_cal_options1:
        view_mode = st.radio("📊 View Mode", ["Monthly", "Weekly", "Daily"], horizontal=True)
    
    with col_cal_options2:
        selected_month = st.selectbox("📆 Select Month", 
                                     [(i, calendar.month_name[i]) for i in range(1, 13)],
                                     format_func=lambda x: x[1],
                                     index=date.today().month - 1)

    if view_mode == "Monthly":
        st.divider()
        render_calendar_grid(date.today().year, selected_month[0], all_events)
    
    elif view_mode == "Weekly":
        st.divider()
        week_start = st.date_input("📅 Week Starting", date.today(), key="week_start")
        st.subheader(f"📅 Week of {week_start.strftime('%B %d, %Y')}")
        
        week_end = week_start + timedelta(days=6)
        week_events = [e for e in all_events if week_start <= e['start'].date() <= week_end]
        
        if week_events:
            for event in sorted(week_events, key=lambda x: x['start']):
                event_card(
                    event['title'],
                    f"{event['start'].strftime('%a')} class",
                    f"{event['start'].strftime('%H:%M')} → {event['end'].strftime('%H:%M')}"
                )
        else:
            st.info("ℹ️ No events scheduled for this week.")
    
    else:  # Daily
        st.divider()
        daily_date = st.date_input("📅 Select Date", date.today(), key="daily_date")
        st.subheader(f"📌 Schedule for {daily_date.strftime('%A, %B %d, %Y')}")
        
        daily_events = [e for e in all_events if e['start'].date() == daily_date]
        
        if daily_events:
            for event in sorted(daily_events, key=lambda x: x['start']):
                event_card(
                    event['title'],
                    f"[{event.get('source', 'custom').capitalize()}]",
                    f"{event['start'].strftime('%H:%M')} → {event['end'].strftime('%H:%M')}"
                )
        else:
            st.markdown(f"""
            <div style='text-align:center;color:{TEXT_SECONDARY};padding:40px;'>
                <h4>No events scheduled 📭</h4>
                <p>Add courses or events to fill your schedule</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    with st.expander("➕ Add Course & Generate Weekly Classes", expanded=False):
        col_course_1, col_course_2 = st.columns(2, gap="large")
        
        with col_course_1:
            course_name = st.text_input("📝 Course Name", key="course_name", placeholder="e.g., Data Structures")
        
        with col_course_2:
            course_days = st.multiselect("📅 Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], key="course_days")
        
        col_course_3, col_course_4 = st.columns(2, gap="large")
        
        with col_course_3:
            course_start = st.selectbox("⏰ Start Hour", [f"{h:02d}:00" for h in range(7, 22)], index=3, key="course_start")
        
        with col_course_4:
            course_end = st.selectbox("⏰ End Hour", [f"{h:02d}:00" for h in range(8, 23)], index=4, key="course_end")

        if st.button("📚 Save Course", use_container_width=True):
            if not course_name:
                st.error("❌ Enter a course name.")
            elif not course_days:
                st.error("❌ Select at least one day.")
            else:
                start_hour = int(course_start.split(":")[0])
                end_hour = int(course_end.split(":")[0])
                if start_hour >= end_hour:
                    st.error("❌ Start time must be before end time.")
                else:
                    days_str = ", ".join(course_days)
                    c.execute("INSERT INTO courses_v2 VALUES (?, ?, ?, ?)",
                              (course_name, days_str, course_start, course_end))
                    conn.commit()
                    st.success("✅ Course saved successfully!")
                    course_events = generate_classes(load_courses())
                    all_events = sort_events(course_events + custom_events)
                    st.rerun()

    st.divider()

    st.subheader("➕ Add Custom Event")
    col_event_1, col_event_2 = st.columns(2, gap="large")
    
    with col_event_1:
        event_title = st.text_input("📌 Event Title", key="event_title", placeholder="e.g., Project Meeting")
        event_date = st.date_input("📅 Event Date", key="event_date")
    
    with col_event_2:
        event_start = st.time_input("⏰ Start Time", value=datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).time(), key="event_start")
        event_end = st.time_input("⏰ End Time", value=datetime.now().replace(hour=11, minute=0, second=0, microsecond=0).time(), key="event_end")

    if st.button("➕ Add Event", use_container_width=True):
        start_dt = datetime.combine(event_date, event_start)
        end_dt = datetime.combine(event_date, event_end)
        if start_dt >= end_dt:
            st.error("❌ Invalid time: start must be before end.")
        else:
            new_event = {"title": event_title or "Untitled Event", "start": start_dt, "end": end_dt, "source": "custom"}
            if check_conflict(new_event, all_events):
                st.error("⚠️ This event conflicts with an existing event!")
            else:
                st.session_state.custom_events.append(new_event)
                all_events = sort_events(course_events + st.session_state.custom_events)
                st.success("✅ Event added successfully!")
                add_to_google_calendar(event_title or "Untitled Event", start_dt, end_dt)
                st.rerun()

    st.divider()

    st.subheader("🎯 Quick Actions")
    col_action_1, col_action_2, col_action_3 = st.columns(3, gap="large")
    
    with col_action_1:
        if st.button("🔍 Find Free Slot", use_container_width=True):
            next_slot = suggest_time(all_events)
            if next_slot:
                st.success(f"✅ Next free slot: {next_slot.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.info("ℹ️ No free slots available in the next 7 days.")
    
    with col_action_2:
        if st.button("🗑️ Clear All Events", use_container_width=True):
            st.session_state.custom_events = []
            all_events = sort_events(course_events + st.session_state.custom_events)
            st.success("✅ Cleared all custom events.")
            st.rerun()
    
    with col_action_3:
        if st.button("📥 Export Calendar (ICS)", use_container_width=True):
            ics_data = generate_ics_calendar(all_events)
            st.download_button(
                "📥 Download ICS File",
                data=ics_data,
                file_name=f"schedule_{date.today()}.ics",
                mime="text/calendar",
                use_container_width=True
            )

# ================= TAB 2: STUDY PLAN =================
with tab2:
    st.markdown("## 📚 Study Plan Dashboard")
    
    st.subheader("➕ Add Assignment")
    col_assign_1, col_assign_2 = st.columns(2, gap="large")
    
    with col_assign_1:
        assignment_title = st.text_input("📝 Assignment Title", key="assignment_title", placeholder="e.g., Math Homework")
        assignment_date = st.date_input("📅 Deadline Date", key="assignment_date")
    
    with col_assign_2:
        assignment_time = st.time_input("⏰ Deadline Time", value=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0).time(), key="assignment_time")
        assignment_priority = st.selectbox("🎯 Priority", ["High", "Medium", "Low"], key="assignment_priority")

    if st.button("📝 Save Assignment", use_container_width=True):
        if not assignment_title:
            st.error("❌ Enter an assignment title.")
        else:
            deadline_dt = datetime.combine(assignment_date, assignment_time)
            c.execute("INSERT INTO assignments_v2 VALUES (?,?,?)", (assignment_title, deadline_dt.strftime("%Y-%m-%d %H:%M"), assignment_priority.lower()))
            conn.commit()
            st.success("✅ Assignment saved.")
            assignments = load_assignments()
            st.rerun()

    st.divider()

    st.subheader("📋 Assignment Tracker")
    if assignments:
        for a in sorted(assignments, key=lambda x: x['deadline']):
            days_until = (a["deadline"].date() - date.today()).days
            
            if days_until < 0:
                status = "🔴 Overdue"
                status_color = ERROR_COLOR
            elif days_until == 0:
                status = "🟠 Due today"
                status_color = WARNING_COLOR
            else:
                status = f"🟢 In {days_until} days"
                status_color = SUCCESS_COLOR
            
            st.markdown(f"""
            <div style='background:{CARD_BG};border:1px solid {BORDER_COLOR};border-radius:8px;padding:16px;margin-bottom:12px;border-left:4px solid {PRIORITY_COLORS[a["priority"].lower()]};'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div style='flex: 1;'>
                        <strong style='color:{TEXT_PRIMARY};font-size:16px;'>{a['title']}</strong><br>
                        <small style='color:{TEXT_SECONDARY};'>Due: {a['deadline'].strftime('%Y-%m-%d %H:%M')} | {status}</small>
                    </div>
                    {priority_badge(a['priority'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📭 Add assignments to activate smart study scheduling.")

    st.divider()

    st.subheader("📊 Deadline Notifications")
    upcoming_assignments = [a for a in assignments if a['deadline'].date() >= date.today()]
    
    if upcoming_assignments:
        col_notif_1, col_notif_2 = st.columns(2, gap="large")
        
        with col_notif_1:
            st.markdown("**⚠️ Urgent Deadlines**")
            urgent = [a for a in upcoming_assignments if (a['deadline'].date() - date.today()).days <= 3]
            if urgent:
                for a in urgent:
                    days_left = (a['deadline'].date() - date.today()).days
                    st.warning(f"📌 {a['title']} — {days_left} day(s) left [{a['priority'].upper()}]")
            else:
                st.info("ℹ️ No urgent deadlines!")
        
        with col_notif_2:
            st.markdown("**📅 Upcoming Assignments**")
            for a in sorted(upcoming_assignments, key=lambda x: x['deadline'])[:5]:
                days_left = (a['deadline'].date() - date.today()).days
                st.markdown(f"• {a['title']} — {days_left} days left")
    else:
        st.success("✅ All deadlines completed!")

    st.divider()

    st.subheader("🎓 Smart Study Plan")
    free_slots = find_free_slots(all_events)
    study_plan = allocate_study(assignments, free_slots)

    if study_plan:
        st.markdown("**Recommended Study Schedule:**")
        for item in study_plan:
            color = PRIORITY_COLORS.get(item["priority"], TEXT_SECONDARY)
            st.markdown(f"""
            <div style='padding:12px;background:{CARD_BG};border-left:4px solid {color};border-radius:6px;margin-bottom:12px;border:1px solid {BORDER_COLOR};'>
                <strong style='color:{TEXT_PRIMARY};'>{item['task']}</strong><br>
                <small style='color:{TEXT_SECONDARY};'>Study at {item['time'].strftime('%Y-%m-%d %H:%M')} | Due {item['deadline'].strftime('%Y-%m-%d')} | {item['priority'].capitalize()} Priority</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align:center;color:{TEXT_SECONDARY};padding:40px;'>
            <h3>No study plan yet 📚</h3>
            <p>Add assignments to generate smart study scheduling</p>
        </div>
        """, unsafe_allow_html=True)

# ================= TAB 3: CONFLICT RESOLUTION =================
with tab3:
    st.markdown("## 🔄 Conflict Resolution")
    st.markdown(f"<p style='color:{TEXT_SECONDARY};'>Detect and resolve scheduling conflicts automatically.</p>", unsafe_allow_html=True)

    st.divider()

    st.subheader("🔍 Schedule Analysis")
    
    col_conflict_1, col_conflict_2 = st.columns(2, gap="large")
    
    with col_conflict_1:
        st.markdown("### 📊 Conflict Summary")
        conflicts = find_conflicts(all_events, assignments)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.metric("⚠️ Total Conflicts", len(conflicts))
        high_severity = len([c for c in conflicts if c['severity'] == 'high'])
        col_c2.metric("🔴 High Priority", high_severity)
        medium_severity = len([c for c in conflicts if c['severity'] == 'medium'])
        col_c3.metric("🟡 Medium Priority", medium_severity)
    
    with col_conflict_2:
        st.markdown("### 🎯 Resolution Status")
        if len(conflicts) == 0:
            st.success("✅ No conflicts detected! Your schedule is clean.")
        else:
            st.warning(f"⚠️ {len(conflicts)} conflict(s) found. Review details below.")

    st.divider()

    st.subheader("📋 Detailed Conflict Report")
    
    if conflicts:
        for idx, conflict in enumerate(conflicts, 1):
            severity_icon = "🔴" if conflict['severity'] == 'high' else "🟡"
            
            st.markdown(f"""
            <div style='background:{CARD_BG};border:1px solid {BORDER_COLOR};border-radius:8px;padding:16px;margin-bottom:12px;border-left:4px solid {"#ef4444" if conflict["severity"] == "high" else "#f59e0b"};'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div style='flex: 1;'>
                        <strong style='color:{TEXT_PRIMARY};font-size:16px;'>{severity_icon} Conflict #{idx}</strong><br>
                        <p style='color:{TEXT_SECONDARY};margin:8px 0 0 0;'>{conflict['description']}</p>
                    </div>
                    <span style='background:{"#ef444420" if conflict["severity"] == "high" else "#f59e0b20"};color:{"#ef4444" if conflict["severity"] == "high" else "#f59e0b"};padding:4px 8px;border-radius:4px;font-weight:bold;border:1px solid {"#ef4444" if conflict["severity"] == "high" else "#f59e0b"};'>{conflict['severity'].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align:center;color:{TEXT_SECONDARY};padding:40px;'>
            <h3>No conflicts found 🎉</h3>
            <p>Your schedule is optimized and conflict-free</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.subheader("💡 Resolution Suggestions")
    
    if conflicts:
        with st.expander("🔧 How to resolve conflicts", expanded=True):
            st.markdown("""
            ### Conflict Resolution Tips:
            
            1. **Event Overlaps**: Reschedule one of the conflicting events to a different time
            2. **Assignment Deadlines**: Move assignment deadlines to less busy days
            3. **Study Time**: Use the "Find Free Slot" feature to find optimal study times
            4. **Course Timing**: Adjust course timings if possible to avoid overlaps
            
            ### Priority-Based Approach:
            - **High Priority**: Fix immediately - these are time-critical
            - **Medium Priority**: Address within 2-3 days
            - **Low Priority**: Monitor but not urgent
            """)
    else:
        st.success("Your schedule is well-optimized with no conflicts!")

# ================= TAB 4: AI ASSISTANT =================
with tab4:
    st.markdown("## 🤖 AI Assistant Dashboard")
    st.markdown(f"<p style='color:{TEXT_SECONDARY};'>Ask about your schedule, free hours, study plan, or conflicts.</p>", unsafe_allow_html=True)

    st.divider()

    col_ai_1, col_ai_2 = st.columns([0.8, 0.2])
    
    with col_ai_1:
        user_query = st.text_input("💬 Ask AI Assistant", key="user_query", placeholder="e.g., When should I study for Math? What are my free slots?")
    
    with col_ai_2:
        st.write("")
        st.write("")
        if st.button("🤖 Ask AI", use_container_width=True):
            if user_query:
                st.session_state.ai_response = ask_ai(user_query, all_events, assignments)
                st.session_state.last_query = user_query

    if st.session_state.last_query:
        st.divider()
        
        with st.chat_message("user"):
            st.markdown(f"**You:** {st.session_state.last_query}")

        with st.chat_message("assistant"):
            st.markdown(f"{st.session_state.ai_response}")

# ================= TAB 5: ANALYTICS =================
with tab5:
    st.markdown("## 📊 Analytics Dashboard")

    st.divider()

    st.subheader("📈 Schedule Analytics")
    
    col_analytics_1, col_analytics_2 = st.columns(2, gap="large")

    with col_analytics_1:
        if all_events:
            event_rows = []
            for event in all_events:
                event_rows.append({
                    "Title": event["title"],
                    "Date": event["start"].strftime("%Y-%m-%d"),
                    "Hours": round((event["end"] - event["start"]).total_seconds() / 3600, 2),
                    "Source": event.get("source", "custom").capitalize()
                })

            df_events = pd.DataFrame(event_rows)
            summary = df_events.groupby("Title", as_index=False)["Hours"].sum().sort_values("Hours", ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor(DARK_BG)
            ax.set_facecolor(CARD_BG)
            
            top_events = summary.head(8)
            ax.barh(top_events["Title"], top_events["Hours"], color=ACCENT_COLOR, edgecolor=BORDER_COLOR, linewidth=1.5)
            ax.set_xlabel("Hours", color=TEXT_PRIMARY, fontweight='bold')
            ax.set_title("Time Allocation by Subject/Event", color=TEXT_PRIMARY, fontweight='bold', pad=20)
            ax.tick_params(colors=TEXT_PRIMARY)
            
            for spine in ax.spines.values():
                spine.set_color(BORDER_COLOR)
            
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            
            busy_hours = df_events["Hours"].sum()
            free_hours = max(0, 24 * 7 - busy_hours)

            col_stat_1, col_stat_2, col_stat_3, col_stat_4 = st.columns(4)
            col_stat_1.metric("📊 Busy Hours", f"{busy_hours:.1f} hrs", "This week")
            col_stat_2.metric("🟢 Free Hours", f"{free_hours:.1f} hrs", "This week")
            col_stat_3.metric("📅 Total Events", len(all_events), "Scheduled")
            col_stat_4.metric("📈 Avg Hours/Day", f"{busy_hours/7:.1f} hrs", "Per day")
        else:
            st.markdown(f"""
            <div style='text-align:center;color:{TEXT_SECONDARY};padding:40px;'>
                <h3>No events to analyze 📊</h3>
                <p>Add courses or events to see analytics</p>
            </div>
            """, unsafe_allow_html=True)

    with col_analytics_2:
        if assignments:
            df_assignments = pd.DataFrame([
                {
                    "Task": a["title"][:20],
                    "Priority": a["priority"].capitalize(),
                    "Days Left": (a["deadline"].date() - date.today()).days
                }
                for a in assignments
            ])
            
            st.subheader("📋 Assignment Overview")
            st.dataframe(df_assignments, use_container_width=True, hide_index=True)
            
            priority_counts = pd.Series([a["priority"].capitalize() for a in assignments]).value_counts()
            
            if len(priority_counts) > 0:
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                fig2.patch.set_facecolor(DARK_BG)
                ax2.set_facecolor(CARD_BG)
                
                colors_list = [PRIORITY_COLORS.get(p.lower(), TEXT_SECONDARY) for p in priority_counts.index]
                wedges, texts, autotexts = ax2.pie(
                    priority_counts.values,
                    labels=priority_counts.index,
                    colors=colors_list,
                    autopct='%1.1f%%',
                    startangle=90,
                    textprops={'color': TEXT_PRIMARY, 'fontweight': 'bold'}
                )
                
                ax2.set_title("Assignment Distribution by Priority", color=TEXT_PRIMARY, fontweight='bold', pad=20)
                plt.setp(autotexts, size=10, weight="bold")
                
                st.pyplot(fig2, use_container_width=True)
        else:
            st.markdown(f"""
            <div style='text-align:center;color:{TEXT_SECONDARY};padding:40px;'>
                <h3>No assignments to analyze 📝</h3>
                <p>Add assignments to see analytics</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📥 Export Options")
    
    col_export_1, col_export_2, col_export_3 = st.columns(3, gap="large")
    
    with col_export_1:
        if st.button("📅 Export Calendar (ICS)", use_container_width=True):
            ics_data = generate_ics_calendar(all_events)
            st.download_button(
                "📥 Download ICS",
                data=ics_data,
                file_name=f"schedule_{date.today()}.ics",
                mime="text/calendar",
                use_container_width=True
            )
    
    with col_export_2:
        if st.button("📊 Export Schedule Report", use_container_width=True):
            report = generate_schedule_report(all_events, assignments)
            st.download_button(
                "📥 Download Report",
                data=report,
                file_name=f"schedule_report_{date.today()}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with col_export_3:
        if st.button("📈 Export as CSV", use_container_width=True):
            if all_events:
                event_data = [{
                    "Title": e["title"],
                    "Date": e["start"].strftime("%Y-%m-%d"),
                    "Start Time": e["start"].strftime("%H:%M"),
                    "End Time": e["end"].strftime("%H:%M"),
                    "Type": e.get("source", "custom").capitalize()
                } for e in all_events]
                
                df_export = pd.DataFrame(event_data)
                csv = df_export.to_csv(index=False)
                
                st.download_button(
                    "📥 Download CSV",
                    data=csv,
                    file_name=f"events_{date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    st.divider()

    st.subheader("💡 Smart Insights & Recommendations")
    
    if all_events and assignments:
        insights = []
        
        if busy_hours > 40:
            insights.append(("🔴 Heavy Workload", "⚠️ You have more than 40 hours of scheduled time this week. Consider redistributing tasks or seeking extensions."))
        elif busy_hours < 10:
            insights.append(("🟢 Light Schedule", "ℹ️ You have plenty of free time this week. Great opportunity to focus on high-priority assignments."))
        else:
            insights.append(("🟡 Balanced Schedule", "✅ Your workload is well-distributed throughout the week."))
        
        overdue = sum(1 for a in assignments if (a['deadline'].date() - date.today()).days < 0)
        if overdue > 0:
            insights.append(("🔴 Overdue Tasks", f"⚠️ You have {overdue} overdue assignment(s). Address these immediately!"))
        
        urgent = sum(1 for a in assignments if 0 <= (a['deadline'].date() - date.today()).days <= 2)
        if urgent > 0:
            insights.append(("🟠 Urgent Deadlines", f"⏰ {urgent} assignment(s) due within the next 3 days."))
        
        conflicts = find_conflicts(all_events, assignments)
        if len(conflicts) > 0:
            insights.append(("⚠️ Schedule Conflicts", f"🔄 Found {len(conflicts)} conflict(s) in your schedule. Review them in the 'Conflict Resolution' tab."))
        
        for title, message in insights:
            with st.expander(title):
                st.markdown(message)