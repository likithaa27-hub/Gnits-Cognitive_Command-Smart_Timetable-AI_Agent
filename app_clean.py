from datetime import datetime, timedelta, date
import calendar
import sqlite3

import pandas as pd
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.markdown("""
<style>
/* ===== DARK MODE AESTHETIC ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}

[data-testid="stHeader"] {
    background: #0f172a;
    border-bottom: 1px solid #334155;
}

[data-testid="stSidebar"] {
    background: #1e293b;
    border-right: 1px solid #334155;
}

/* ===== TABS ENHANCEMENT ===== */
button[data-baseweb="tab"] {
    font-size: 16px;
    padding: 12px 24px;
    margin-right: 8px;
    border-radius: 12px;
    background: #334155;
    color: #cbd5e1;
    border: 1px solid #475569;
    transition: all 0.3s ease;
}

button[data-baseweb="tab"]:hover {
    background: #475569;
    color: #f8fafc;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border-color: #6366f1;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
}

/* ===== CARDS AND COMPONENTS ===== */
div[data-testid="stExpander"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

div[data-testid="stExpander"] > div:first-child {
    background: #334155;
    border-radius: 12px 12px 0 0;
    color: #f1f5f9;
    font-weight: 600;
}

/* ===== METRICS CARDS ===== */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border: 1px solid #475569;
    border-radius: 12px;
    padding: 20px;
    margin: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease;
}

[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

[data-testid="metric-container"] > div:first-child {
    color: #6366f1;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="metric-container"] > div:last-child {
    color: #f1f5f9;
    font-size: 28px;
    font-weight: 700;
}

/* ===== FORM ELEMENTS ===== */
.stTextInput > div > div {
    background: #334155;
    border: 1px solid #475569;
    border-radius: 8px;
    color: #f1f5f9;
}

.stTextInput > div > div:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.stSelectbox > div > div {
    background: #334155;
    border: 1px solid #475569;
    border-radius: 8px;
    color: #f1f5f9;
}

.stDateInput > div > div {
    background: #334155;
    border: 1px solid #475569;
    border-radius: 8px;
    color: #f1f5f9;
}

.stTimeInput > div > div {
    background: #334155;
    border: 1px solid #475569;
    border-radius: 8px;
    color: #f1f5f9;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
}

.stButton > button:active {
    transform: translateY(0);
}

/* ===== ALERTS AND MESSAGES ===== */
.stSuccess {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    border: 1px solid #065f46;
    border-radius: 8px;
    color: white;
}

.stError {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
    border: 1px solid #991b1b;
    border-radius: 8px;
    color: white;
}

.stWarning {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    border: 1px solid #92400e;
    border-radius: 8px;
    color: white;
}

.stInfo {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    border: 1px solid #1e40af;
    border-radius: 8px;
    color: white;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    background: #334155;
    border: 1px solid #475569;
    border-radius: 12px;
    margin-bottom: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    margin-left: 20%;
}

[data-testid="stChatMessage"][data-testid*="assistant"] {
    background: #1e293b;
    margin-right: 20%;
}

/* ===== HEADERS AND TEXT ===== */
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9;
    font-weight: 700;
}

h1 {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stMarkdown p {
    color: #cbd5e1;
    line-height: 1.6;
}

/* ===== DIVIDERS ===== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, #475569 50%, transparent 100%);
    margin: 24px 0;
}

/* ===== TABLES ===== */
[data-testid="stTable"] {
    background: #1e293b;
    border-radius: 8px;
    overflow: hidden;
}

[data-testid="stTable"] th {
    background: #334155;
    color: #f1f5f9;
    font-weight: 600;
    padding: 12px;
    border-bottom: 1px solid #475569;
}

[data-testid="stTable"] td {
    color: #cbd5e1;
    padding: 12px;
    border-bottom: 1px solid #334155;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #1e293b;
}

::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #6366f1;
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 768px) {
    button[data-baseweb="tab"] {
        font-size: 14px;
        padding: 8px 16px;
    }

    [data-testid="metric-container"] {
        margin: 4px;
        padding: 16px;
    }

    .stButton > button {
        padding: 10px 20px;
        font-size: 14px;
    }
}

/* ===== ANIMATIONS ===== */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

div[data-testid="stVerticalBlock"] > div {
    animation: fadeIn 0.5s ease-out;
}

/* ===== ACCESSIBILITY ===== */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Focus indicators for accessibility */
button:focus, input:focus, select:focus, textarea:focus {
    outline: 2px solid #6366f1;
    outline-offset: 2px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    return service


def add_to_google_calendar(title, start_dt, end_dt):
    service = get_calendar_service()
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
    existing_events = service.events().list(
        calendarId='primary',
        q=title,
        timeMin=start_dt.isoformat() + 'Z',
        timeMax=end_dt.isoformat() + 'Z'
    ).execute()
    if not existing_events.get('items'):
        service.events().insert(calendarId='primary', body=event).execute()


def parse_event(event):
    if isinstance(event["start"], str):
        event["start"] = datetime.strptime(event["start"], "%Y-%m-%d %H:%M")
    if isinstance(event["end"], str):
        event["end"] = datetime.strptime(event["end"], "%Y-%m-%d %H:%M")
    return event


def card(title, content):
    st.markdown(f"""
    <div style="
        background-color:#1E293B;
        padding:15px;
        border-radius:12px;
        margin-bottom:10px;
        box-shadow:0 4px 10px rgba(0,0,0,0.3);
    ">
        <h4 style="color:#6366F1;">{title}</h4>
        <p style="color:#CBD5F5;">{content}</p>
    </div>
    """, unsafe_allow_html=True)


def check_conflict(new_event, events):
    for e in events:
        if not (new_event["end"] <= e["start"] or new_event["start"] >= e["end"]):
            return True
    return False


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
        ])

        assignment_text = "\n".join([
            f"{a['title']} due {a['deadline']} priority {a['priority']}"
            for a in assignments
        ])

        prompt = f"""
You are a smart academic scheduling assistant.

Rules:
- Be short and clear
- Give exact times
- Prioritize assignments by deadline
- Suggest practical study slots

Events:
{event_text}

Assignments:
{assignment_text}

User: {query}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # fast + free
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return "AI unavailable right now. Try asking about free time or study plan."


def load_courses():
    rows = c.execute("SELECT subject, days, start_time, end_time FROM courses_v2").fetchall()
    courses = []

    for subject, days, start_time, end_time in rows:
        days_list = [d.strip() for d in days.split(",") if d.strip()]
        try:
            start_hour = int(start_time.split(":")[0])
            end_hour = int(end_time.split(":")[0])
        except ValueError:
            continue

        courses.append({
            "name": subject,
            "days": days_list,
            "start_time": start_hour,
            "end_time": end_hour
        })

    return courses


def load_assignments():
    rows = c.execute("SELECT title, deadline, priority FROM assignments_v2").fetchall()
    assignments = []

    for title, deadline, priority in rows:
        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        assignments.append({
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

st.set_page_config(page_title="Smart Timetable AI Agent", page_icon="📅", layout="wide")

st.markdown("""
<h1 style='text-align: center; color: #6366F1;'>📅 Smart Timetable AI</h1>
<p style='text-align: center; font-size:18px; color: #94A3B8;'>
AI-powered academic planner with smart scheduling, conflict detection & analytics
</p>
""", unsafe_allow_html=True)

course_events = generate_classes(load_courses())
custom_events = load_custom_events()
all_events = sort_events(course_events + custom_events)
assignments = load_assignments()

if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

if "last_query" not in st.session_state:
    st.session_state.last_query = ""


col1, col2, col3 = st.columns(3)

col1.metric("📅 Events", len(all_events))
col2.metric("📚 Assignments", len(assignments))
col3.metric("⏱ Free Slots", len(find_free_slots(all_events)))

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Calendar",
    "📚 Study Plan",
    "🤖 AI Assistant",
    "📊 Analytics"
])

with tab1:
    st.markdown("## 📅 Calendar Dashboard")

    with st.expander("Add a course and generate weekly classes"):
        course_name = st.text_input("Course Name", key="course_name")
        course_days = st.multiselect("Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], key="course_days")
        course_start = st.selectbox("Start Hour", [f"{h:02d}:00" for h in range(7, 22)], index=3, key="course_start")
        course_end = st.selectbox("End Hour", [f"{h:02d}:00" for h in range(8, 23)], index=4, key="course_end")

        if st.button("📚 Save Course", use_container_width=True):
            if not course_name:
                st.error("Enter a course name.")
            elif not course_days:
                st.error("Select at least one day.")
            else:
                start_hour = int(course_start.split(":")[0])
                end_hour = int(course_end.split(":")[0])
                if start_hour >= end_hour:
                    st.error("Start time must be before end time.")
                else:
                    days_str = ", ".join(course_days)
                    c.execute("INSERT INTO courses_v2 VALUES (?, ?, ?, ?)",
                              (course_name, days_str, course_start, course_end))
                    conn.commit()
                    st.success("Course saved successfully!")
                    course_events = generate_classes(load_courses())
                    all_events = sort_events(course_events + custom_events)

    st.subheader("Weekly Course Schedule")
    if course_events:
        for event in course_events:
            st.write(f"• {event['title']} — {event['start'].strftime('%a %Y-%m-%d %H:%M')} to {event['end'].strftime('%H:%M')}")
    else:
        st.info("Add courses to build your weekly class timetable.")

    st.divider()
    st.subheader("Add Custom Event")

    event_title = st.text_input("Event Title", key="event_title")
    event_date = st.date_input("Event Date", key="event_date")
    event_start = st.time_input("Start Time", value=datetime.now().replace(hour=10, minute=0, second=0, microsecond=0).time(), key="event_start")
    event_end = st.time_input("End Time", value=datetime.now().replace(hour=11, minute=0, second=0, microsecond=0).time(), key="event_end")

    if st.button("➕ Add Event", use_container_width=True):
        start_dt = datetime.combine(event_date, event_start)
        end_dt = datetime.combine(event_date, event_end)
        if start_dt >= end_dt:
            st.error("Invalid time: start must be before end.")
        else:
            new_event = {"title": event_title or "Untitled Event", "start": start_dt, "end": end_dt, "source": "custom"}
            if check_conflict(new_event, all_events):
                st.error("⚠️ This event conflicts with an existing event!")
            else:
                st.session_state.custom_events.append(new_event)
                all_events = sort_events(course_events + st.session_state.custom_events)
                st.success("Event added successfully!")
                add_to_google_calendar(event_title or "Untitled Event", start_dt, end_dt)

    if st.button("🔍 Find Free Slot", use_container_width=True):
        next_slot = suggest_time(all_events)
        if next_slot:
            st.info(f"Next free slot: {next_slot.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No free slots available in the next 7 days.")

    if st.button("🗑️ Clear All Events", use_container_width=True):
        st.session_state.custom_events = []
        all_events = sort_events(course_events + st.session_state.custom_events)
        st.success("Cleared all custom events.")

    st.download_button(
        "Export Schedule",
        data=str(all_events),
        file_name="schedule.txt"
    )

    st.divider()
    st.subheader("Today's Schedule")
    today = datetime.now().date()
    today_events = [e for e in all_events if e["start"].date() == today]
    if today_events:
        for event in today_events:
            source = "Course" if event.get("source") == "course" else "Custom"
            card(event['title'], f"[{source}] {event['start'].strftime('%H:%M')} → {event['end'].strftime('%H:%M')}")
    else:
        st.markdown("""
        <div style='text-align:center; color:#94A3B8; padding:20px;'>
            <h4>No events today 📅</h4>
            <p>Enjoy your free day!</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📌 Upcoming Events")
    if all_events:
        for event in all_events:
            source = "Course" if event.get("source") == "course" else "Custom"
            st.write(f"• [{source}] {event['title']} — {event['start'].strftime('%Y-%m-%d %H:%M')} to {event['end'].strftime('%Y-%m-%d %H:%M')}")
    else:
        st.markdown("""
        <div style='text-align:center; color:#94A3B8; padding:40px;'>
            <h3>No events yet 📭</h3>
            <p>Add courses or events to get started</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("## 📚 Study Plan Dashboard")
    st.subheader("Add Assignment")

    assignment_title = st.text_input("Assignment Title", key="assignment_title")
    assignment_date = st.date_input("Deadline Date", key="assignment_date")
    assignment_time = st.time_input("Deadline Time", value=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0).time(), key="assignment_time")
    assignment_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="assignment_priority")

    if st.button("📝 Save Assignment", use_container_width=True):
        deadline_dt = datetime.combine(assignment_date, assignment_time)
        c.execute("INSERT INTO assignments_v2 VALUES (?,?,?)", (assignment_title or "Untitled Assignment", deadline_dt.strftime("%Y-%m-%d %H:%M"), assignment_priority.lower()))
        conn.commit()
        st.success("Assignment saved.")
        assignments = load_assignments()

    st.subheader("Assignments")
    if assignments:
        for a in assignments:
            priority_color = {"high": "#dc3545", "medium": "#ffc107", "low": "#28a745"}.get(a["priority"].lower(), "#6c757d")
            st.markdown(f"""
            <div style='background:#1e293b;border:1px solid #334155;border-radius:8px;padding:12px;margin-bottom:8px;border-left:4px solid {priority_color};'>
                <strong style='color:#f1f5f9;'>{a['title']}</strong><br>
                <small style='color:#94a3b8;'>Due: {a['deadline'].strftime('%Y-%m-%d %H:%M')} | Priority: {a['priority'].capitalize()}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Add assignments to activate smart study scheduling.")

    st.divider()
    st.subheader("Smart Study Plan")
    free_slots = find_free_slots(all_events)
    study_plan = allocate_study(assignments, free_slots)

    if study_plan:
        for item in study_plan:
            if item["priority"] == "high":
                st.error(f"• {item['task']} at {item['time'].strftime('%Y-%m-%d %H:%M')} | priority {item['priority'].capitalize()}")
            elif item["priority"] == "medium":
                st.warning(f"• {item['task']} at {item['time'].strftime('%Y-%m-%d %H:%M')} | priority {item['priority'].capitalize()}")
            else:
                st.info(f"• {item['task']} at {item['time'].strftime('%Y-%m-%d %H:%M')} | priority {item['priority'].capitalize()}")
    else:
        st.markdown("""
        <div style='text-align:center; color:#94A3B8; padding:40px;'>
            <h3>No study plan yet 📚</h3>
            <p>Add assignments to generate smart study scheduling</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("## 🤖 AI Assistant Dashboard")
    st.write("Ask about your schedule, free hours, study plan, or conflicts.")

    user_query = st.text_input("Ask AI", key="user_query")
    if st.button("🤖 Ask AI", use_container_width=True):
        st.session_state.ai_response = ask_ai(user_query, all_events, assignments)
        st.session_state.last_query = user_query

    if st.session_state.last_query:
        with st.chat_message("user"):
            st.write(st.session_state.last_query)

        with st.chat_message("assistant"):
            st.write(st.session_state.ai_response)

with tab4:
    st.markdown("## 📊 Analytics Dashboard")

    if all_events:
        event_rows = []
        for event in all_events:
            event_rows.append({
                "Title": event["title"],
                "Date": event["start"].strftime("%Y-%m-%d"),
                "Hours": round((event["end"] - event["start"]).total_seconds() / 3600, 2),
                "Source": event.get("source", "custom")
            })

        df_events = pd.DataFrame(event_rows)
        summary = df_events.groupby("Title", as_index=False)["Hours"].sum()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(summary["Title"], summary["Hours"])
        ax.set_ylabel("Hours")
        ax.set_title("Planned Hours by Subject/Event")
        plt.xticks(rotation=30)
        plt.tight_layout()
        st.pyplot(fig)
        busy_hours = df_events["Hours"].sum()
        free_hours = max(0, 24 * 7 - busy_hours)

        col1, col2, col3 = st.columns(3)

        col1.metric("📊 Busy Hours", f"{busy_hours} hrs")
        col2.metric("🟢 Free Hours", f"{free_hours} hrs")
        col3.metric("📅 Total Events", len(all_events))
    else:
        st.markdown("""
        <div style='text-align:center; color:#94A3B8; padding:40px;'>
            <h3>No events to analyze 📊</h3>
            <p>Add courses or events to see analytics</p>
        </div>
        """, unsafe_allow_html=True)

    if assignments:
        df_assignments = pd.DataFrame([
            {"Task": a["title"], "Priority": a["priority"].capitalize()} for a in assignments
        ])
        st.subheader("Assignments by Priority")
        st.table(df_assignments)
    else:
        st.markdown("""
        <div style='text-align:center; color:#94A3B8; padding:40px;'>
            <h3>No assignments to analyze 📝</h3>
            <p>Add assignments to see priority analytics</p>
        </div>
        """, unsafe_allow_html=True)

    if all_events:
        if busy_hours > 40:
            st.error("⚠️ Heavy workload this week!")
        elif busy_hours < 10:
            st.info("You have free time to utilize!")