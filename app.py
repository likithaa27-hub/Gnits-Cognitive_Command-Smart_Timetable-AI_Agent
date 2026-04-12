from datetime import datetime, timedelta, date
import calendar
import sqlite3

import pandas as pd
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Color schemes
PRIORITY_COLORS = {
    "High": "#dc3545",
    "Medium": "#ffc107",
    "Low": "#28a745"
}

TYPE_COLORS = {
    "Exam": "#6f42c1",
    "Course": "#0d6efd",
    "Assignment": "#28a745"
}

# Modern SaaS Theme
DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
ACCENT_COLOR = "#3b82f6"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
BORDER_COLOR = "#334155"


def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    return service


def add_to_google_calendar(title, date_obj):
    service = get_calendar_service()
    event = {
        'summary': title,
        'start': {'date': date_obj.strftime("%Y-%m-%d")},
        'end': {'date': date_obj.strftime("%Y-%m-%d")},
    }
    service.events().insert(calendarId='primary', body=event).execute()


def priority_badge(priority):
    """Returns HTML badge with color for priority"""
    color = PRIORITY_COLORS.get(priority, "#000000")
    return f"<span style='background-color:{color};color:white;padding:4px 8px;border-radius:4px;font-weight:bold;margin-left:8px'>{priority}</span>"


def get_assignments_with_id():
    """Get assignments with their row IDs for deletion"""
    return c.execute("SELECT rowid, title, subject, deadline, priority FROM assignments").fetchall()


def get_exams_with_id():
    """Get exams with their row IDs for deletion"""
    return c.execute("SELECT rowid, subject, date FROM exams").fetchall()


def get_courses_with_id():
    """Get courses with their row IDs for deletion"""
    return c.execute("SELECT rowid, subject, day, time FROM courses").fetchall()


# DATABASE ----------------
conn = sqlite3.connect("schedule.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS courses (
    subject TEXT,
    day TEXT,
    time TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS exams (
    subject TEXT,
    date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS assignments (
    title TEXT,
    subject TEXT,
    deadline TEXT,
    priority TEXT
)''')

conn.commit()


# HELPERS ----------------
def get_courses():
    return c.execute("SELECT subject, day, time FROM courses").fetchall()


def get_exams():
    return c.execute("SELECT subject, date FROM exams").fetchall()


def get_assignments():
    return c.execute("SELECT title, subject, deadline, priority FROM assignments").fetchall()


def get_week_range(base_date):
    start = base_date - timedelta(days=base_date.weekday())
    return start, start + timedelta(days=6)


def build_calendar_entries(view, base_date):
    rows = []
    courses = get_courses()
    exams = get_exams()
    assignments = get_assignments()

    if view == "Daily":
        selected_str = base_date.strftime("%Y-%m-%d")

        for subject, exam_date in exams:
            if exam_date == selected_str:
                rows.append({
                    "Date": selected_str,
                    "Time": "All day",
                    "Type": "Exam",
                    "Title": subject,
                    "Details": "Exam day",
                    "Priority": ""
                })

        for title, subject, deadline, priority in assignments:
            if deadline == selected_str:
                rows.append({
                    "Date": selected_str,
                    "Time": "All day",
                    "Type": "Assignment",
                    "Title": title,
                    "Details": f"{subject}",
                    "Priority": priority
                })

        weekday_label = base_date.strftime("%a")
        for subject, day, time in courses:
            if day == weekday_label:
                rows.append({
                    "Date": selected_str,
                    "Time": time,
                    "Type": "Course",
                    "Title": subject,
                    "Details": f"{day} class",
                    "Priority": ""
                })

    elif view == "Weekly":
        start, end = get_week_range(base_date)

        for subject, exam_date in exams:
            exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
            if start <= exam_dt <= end:
                rows.append({
                    "Date": exam_date,
                    "Time": "All day",
                    "Type": "Exam",
                    "Title": subject,
                    "Details": "Exam day",
                    "Priority": ""
                })

        for title, subject, deadline, priority in assignments:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d").date()
            if start <= deadline_dt <= end:
                rows.append({
                    "Date": deadline,
                    "Time": "All day",
                    "Type": "Assignment",
                    "Title": title,
                    "Details": f"{subject}",
                    "Priority": priority
                })

        for delta in range(7):
            day_date = start + timedelta(days=delta)
            weekday_label = day_date.strftime("%a")
            for subject, day, time in courses:
                if day == weekday_label:
                    rows.append({
                        "Date": day_date.strftime("%Y-%m-%d"),
                        "Time": time,
                        "Type": "Course",
                        "Title": subject,
                        "Details": f"{day} class",
                        "Priority": ""
                    })

    elif view == "Monthly":
        year = base_date.year
        month = base_date.month
        month_start = date(year, month, 1)
        month_end = date(year, month, calendar.monthrange(year, month)[1])

        for subject, exam_date in exams:
            exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
            if month_start <= exam_dt <= month_end:
                rows.append({
                    "Date": exam_date,
                    "Time": "All day",
                    "Type": "Exam",
                    "Title": subject,
                    "Details": "Exam day",
                    "Priority": ""
                })

        for title, subject, deadline, priority in assignments:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d").date()
            if month_start <= deadline_dt <= month_end:
                rows.append({
                    "Date": deadline,
                    "Time": "All day",
                    "Type": "Assignment",
                    "Title": title,
                    "Details": f"{subject}",
                    "Priority": priority
                })

        days_in_month = calendar.monthrange(year, month)[1]
        for day_number in range(1, days_in_month + 1):
            day_date = date(year, month, day_number)
            weekday_label = day_date.strftime("%a")
            for subject, day, time in courses:
                if day == weekday_label:
                    rows.append({
                        "Date": day_date.strftime("%Y-%m-%d"),
                        "Time": time,
                        "Type": "Course",
                        "Title": subject,
                        "Details": f"{day} class",
                        "Priority": ""
                    })

    return sorted(rows, key=lambda item: (item["Date"], item["Time"]))


def render_calendar_grid(view, base_date, entries):
    """Render calendar as HTML grid with modern styling"""
    grid_css = f"""
    <style>
        .calendar-grid {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .calendar-grid th {{ background: {CARD_BG}; padding: 12px; text-align: center; font-weight: bold; border: 1px solid {BORDER_COLOR}; color: {TEXT_PRIMARY}; }}
        .calendar-grid td {{ padding: 10px; border: 1px solid {BORDER_COLOR}; min-height: 80px; vertical-align: top; background: {CARD_BG}; color: {TEXT_PRIMARY}; }}
        .day-cell {{ width: 14.28%; }}
        .day-number {{ font-weight: bold; margin-bottom: 8px; color: {ACCENT_COLOR}; }}
        .event-item {{ 
            display: block; margin: 3px 0; padding: 4px 6px; border-radius: 3px; 
            font-size: 11px; color: white; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .event-exam {{ background: #6f42c1; }}
        .event-course {{ background: #0d6efd; }}
        .event-assignment-high {{ background: #dc3545; }}
        .event-assignment-medium {{ background: #ffc107; color: black; }}
        .event-assignment-low {{ background: #28a745; }}
    </style>
    """

    if view == "Monthly":
        year = base_date.year
        month = base_date.month
        month_name = base_date.strftime("%B %Y")
        month_matrix = calendar.monthcalendar(year, month)

        html = [grid_css, f"<h4 style='text-align:center;color:{TEXT_PRIMARY};'>{month_name}</h4>"]
        html.append("<table class='calendar-grid'>")
        html.append("<tr>" + "".join(f"<th style='width:14.28%'>{day}</th>" for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]) + "</tr>")

        for week in month_matrix:
            html.append("<tr>")
            for day_num in week:
                if day_num == 0:
                    html.append("<td class='day-cell'></td>")
                else:
                    day_date = date(year, month, day_num).strftime("%Y-%m-%d")
                    events_html = ""
                    for item in entries:
                        if item["Date"] == day_date:
                            event_class = f"event-{item['Type'].lower()}"
                            if item["Type"] == "Assignment":
                                priority_class = item["Priority"].lower() if item["Priority"] else "low"
                                event_class = f"event-assignment-{priority_class}"
                            events_html += f"<span class='event-item {event_class}'>{item['Title']}</span>"
                    html.append(f"<td class='day-cell'><div class='day-number'>{day_num}</div>{events_html}</td>")
            html.append("</tr>")
        html.append("</table>")
        st.markdown("".join(html), unsafe_allow_html=True)

    elif view == "Weekly":
        start, end = get_week_range(base_date)
        html = [grid_css, "<table class='calendar-grid'>"]
        header = "<tr>"
        for i in range(7):
            day = (start + timedelta(days=i)).strftime("%a %d")
            header += f"<th style='width:14.28%'>{day}</th>"
        header += "</tr>"
        html.append(header)

        html.append("<tr>")
        for i in range(7):
            day_date = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            events_html = ""
            for item in entries:
                if item["Date"] == day_date:
                    event_class = f"event-{item['Type'].lower()}"
                    if item["Type"] == "Assignment":
                        priority_class = item["Priority"].lower() if item["Priority"] else "low"
                        event_class = f"event-assignment-{priority_class}"
                    events_html += f"<span class='event-item {event_class}'>{item['Title']} ({item['Time']})</span>"
            html.append(f"<td class='day-cell'>{events_html}</td>")
        html.append("</tr></table>")
        st.markdown("".join(html), unsafe_allow_html=True)

    else:
        if not entries:
            st.info("No events found for this day.")
            return
        for item in entries:
            type_color = TYPE_COLORS.get(item["Type"], "#000000")
            priority_html = ""
            if item["Priority"]:
                priority_html = priority_badge(item["Priority"])
            st.markdown(
                f"<div style='padding:12px;border-left:4px solid {type_color};background:{CARD_BG};margin-bottom:8px;border-radius:4px;border: 1px solid {BORDER_COLOR};'>"
                f"<strong style='color:{TEXT_PRIMARY}'>{item['Type']}</strong> — {item['Title']}<br>"
                f"<small style='color:{TEXT_SECONDARY}'>{item['Details']} at {item['Time']}</small><br>"
                f"{priority_html}</div>",
                unsafe_allow_html=True
            )


def find_conflicts():
    conflicts = []
    events = st.session_state.events
    courses = get_courses()
    exams = get_exams()
    assignments = get_assignments()

    for i, (name, event_time, event_date) in enumerate(events):
        for subject, course_day, course_time in courses:
            if course_time == event_time and event_date.strftime("%a") == course_day:
                conflicts.append(
                    f"Event '{name}' conflicts with course '{subject}' on {course_day} at {event_time}"
                )

        for title, subject, deadline, priority in assignments:
            if deadline == event_date.strftime("%Y-%m-%d"):
                conflicts.append(
                    f"Event '{name}' falls on assignment deadline '{title}'"
                )

    for subject, exam_date in exams:
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
        for title, _, deadline, _ in assignments:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d").date()
            if abs((exam_dt - deadline_dt).days) <= 2:
                conflicts.append(
                    f"Exam '{subject}' and assignment '{title}' are within 2 days."
                )

    return conflicts


# Apply Modern SaaS Theme
st.set_page_config(
    page_title="Smart Timetable AI Agent",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS for Modern SaaS Look
saas_css = f"""
<style>
    * {{ color-scheme: dark; }}
    
    [data-testid="stAppViewContainer"] {{ background-color: {DARK_BG}; }}
    
    [data-testid="stSidebar"] {{ background-color: {DARK_BG}; }}
    
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {{ background-color: {DARK_BG}; }}
    
    .stMainBlockContainer {{ padding: 2rem; background-color: {DARK_BG}; }}
    
    h1, h2, h3, h4, h5, h6 {{ color: {TEXT_PRIMARY} !important; }}
    
    p, span, label, div {{ color: {TEXT_PRIMARY} !important; }}
    
    [data-testid="stForm"] {{ background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR};
        border-radius: 8px;
        padding: 1.5rem; }}
    
    [data-testid="stMetricContainer"] {{ background-color: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 8px;
        padding: 1.5rem; }}
    
    button {{ border-radius: 6px !important;
        border: 1px solid {ACCENT_COLOR} !important;
        background-color: {ACCENT_COLOR} !important;
        color: white !important; }}
    
    button:hover {{ background-color: #2563eb !important; }}
    
    [data-testid="stDataFrame"] {{ background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR};
        border-radius: 8px; }}
    
    input, select, textarea {{ background-color: {CARD_BG} !important;
        border: 1px solid {BORDER_COLOR} !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 6px !important; }}
    
    .stRadio > label {{ color: {TEXT_PRIMARY} !important; }}
    
    .stSelectbox > label {{ color: {TEXT_PRIMARY} !important; }}
    
    .stTextInput > label {{ color: {TEXT_PRIMARY} !important; }}
    
    .stDateInput > label {{ color: {TEXT_PRIMARY} !important; }}
    
    .stDivider {{ background-color: {BORDER_COLOR} !important; }}
    
    .stAlert {{ background-color: {CARD_BG};
        border: 1px solid {BORDER_COLOR};
        border-radius: 8px; }}
</style>
"""

st.markdown(saas_css, unsafe_allow_html=True)

# Header with Title and Tagline
col1, col2 = st.columns([0.7, 0.3])
with col1:
    st.markdown(f"<h1 style='margin-bottom: 0.5rem;'>📅 Smart Timetable AI Agent</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {TEXT_SECONDARY}; margin-top: 0;'>Intelligent schedule management for modern learners</p>", unsafe_allow_html=True)

with col2:
    today = date.today()
    st.markdown(f"<p style='text-align: right; color: {TEXT_SECONDARY}; margin-top: 1rem;'>{today.strftime('%A, %B %d, %Y')}</p>", unsafe_allow_html=True)

st.markdown("")  # Spacing

# Navigation Bar
menu = st.radio(
    "Navigation",
    ["🏠 Home", "📆 Calendar", "📚 Courses", "📝 Exams", "✅ Assignments", "📊 Dashboard"],
    horizontal=True
)

menu = menu.split(" ", 1)[1]

if "events" not in st.session_state:
    st.session_state.events = []

if "assignments_session" not in st.session_state:
    st.session_state.assignments_session = []

current_date = date.today()


# ================= HOME =================
if menu == "Home":
    st.markdown(f"<p style='color: {TEXT_SECONDARY};'>Track events, classes, exams, and assignments with one powerful workspace.</p>", unsafe_allow_html=True)

    exams = get_exams()
    assignments = get_assignments()
    upcoming_exams = [
        e for e in exams if datetime.strptime(e[1], "%Y-%m-%d").date() >= current_date
    ]
    due_assignments = [
        a for a in assignments if datetime.strptime(a[2], "%Y-%m-%d").date() >= current_date
    ]
    upcoming_events = st.session_state.events

    # Metrics Cards
    col1, col2, col3 = st.columns(3, gap="large")
    col1.metric("📝 Upcoming exams", len(upcoming_exams))
    col2.metric("📚 Pending assignments", len(due_assignments))
    col3.metric("📅 Personal events", len(upcoming_events))

    st.divider()

    # Two Column Layout
    col_form, col_events = st.columns([0.6, 0.4], gap="large")

    with col_form:
        st.subheader("Add personal event")
        with st.form("add_event_form"):
            event_name = st.text_input("Event name")
            event_date = st.date_input("Event date", current_date)
            event_time = st.text_input("Event time (e.g., 10:00 AM)")
            submit_event = st.form_submit_button("Add Event", use_container_width=True)

        if submit_event:
            conflict_found = any(
                ev[1] == event_time and ev[2] == event_date
                for ev in st.session_state.events
            )
            if conflict_found:
                st.error("⚠️ An event already exists at that date and time.")
            elif not event_name.strip():
                st.error("Please enter an event name.")
            else:
                st.session_state.events.append((event_name, event_time, event_date))
                st.success("✅ Event added.")
                st.rerun()

    with col_events:
        st.subheader("Today's schedule")
        if st.session_state.events:
            today_items = [
                ev for ev in st.session_state.events if ev[2] == current_date
            ]
            if today_items:
                for ev in today_items:
                    st.markdown(f"<div style='padding:10px;background:{CARD_BG};border-radius:6px;margin-bottom:8px;border-left: 3px solid {ACCENT_COLOR};'><strong>{ev[0]}</strong><br><small style='color:{TEXT_SECONDARY};'>at {ev[1]}</small></div>", unsafe_allow_html=True)
            else:
                st.info("No personal events for today.")
        else:
            st.info("No personal events added yet.")

    st.divider()

    if st.session_state.events:
        st.subheader("Manage personal events")
        event_labels = [
            f"{idx+1}. {name} on {event_date} at {event_time}"
            for idx, (name, event_time, event_date) in enumerate(st.session_state.events)
        ]
        selected_index = st.selectbox(
            "Select event to edit or delete",
            list(range(len(event_labels))),
            format_func=lambda idx: event_labels[idx],
            key="event_select"
        )
        selected_name, selected_time, selected_date = st.session_state.events[selected_index]

        col_edit, col_del = st.columns(2, gap="large")
        with col_edit:
            with st.form("edit_event_form"):
                edit_name = st.text_input("Event name", value=selected_name)
                edit_date = st.date_input("Event date", value=selected_date)
                edit_time = st.text_input("Event time", value=selected_time)
                save_event = st.form_submit_button("✏️ Save changes", use_container_width=True)

            if save_event:
                if not edit_name.strip():
                    st.error("Event name cannot be empty.")
                else:
                    st.session_state.events[selected_index] = (edit_name, edit_time, edit_date)
                    st.success("Event updated.")
                    st.rerun()

        with col_del:
            st.write("")
            st.write("")
            if st.button("🗑️ Delete event", use_container_width=True, key="delete_event_btn"):
                st.session_state.events.pop(selected_index)
                st.success("Event removed.")
                st.rerun()

    st.divider()

    # Quick Assignment Tracker
    col_form, col_list = st.columns([0.6, 0.4], gap="large")

    with col_form:
        st.subheader("Quick assignment tracker")
        with st.form("quick_assignment_form"):
            task_name = st.text_input("Assignment title")
            task_deadline = st.date_input("Deadline", current_date)
            task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            submit_task = st.form_submit_button("Add quick assignment", use_container_width=True)

        if submit_task:
            if not task_name.strip():
                st.error("Please enter an assignment title.")
            else:
                st.session_state.assignments_session.append(
                    (task_name, task_deadline.strftime("%Y-%m-%d"), task_priority)
                )
                st.success("Assignment added to session.")
                st.rerun()

    with col_list:
        if st.session_state.assignments_session:
            st.subheader("Session assignments")
            for task, deadline, priority in st.session_state.assignments_session:
                st.markdown(
                    f"<div style='padding:10px;background:{CARD_BG};border-radius:6px;margin-bottom:8px;border-left: 3px solid {PRIORITY_COLORS[priority]};'><strong>{task}</strong><br><small style='color:{TEXT_SECONDARY};'>{deadline}</small> {priority_badge(priority)}</div>",
                    unsafe_allow_html=True
                )

    st.divider()
    if st.button("🔍 Check conflict resolution", use_container_width=True):
        conflicts = find_conflicts()
        if conflicts:
            for conflict in conflicts:
                st.warning(conflict)
        else:
            st.success("No conflicts found in your current schedule.")

# ================= CALENDAR =================
elif menu == "Calendar":
    st.subheader("Calendar View")
    col1, col2 = st.columns(2)
    with col1:
        view = st.radio("Select view", ["Monthly", "Weekly", "Daily"], horizontal=True)
    with col2:
        base_date = st.date_input("Reference date", current_date)
    st.divider()

    entries = build_calendar_entries(view, base_date)
    render_calendar_grid(view, base_date, entries)

    st.divider()
    st.markdown(f"<p style='color: {TEXT_SECONDARY};'>**Legend:** 🟦 Course | 🟪 Exam | 🟩 Assignment (Low) | 🟨 Assignment (Medium) | 🟥 Assignment (High)</p>", unsafe_allow_html=True)

# ================= COURSES =================
elif menu == "Courses":
    st.subheader("Course Timetable")
    col_form, col_space = st.columns([0.6, 0.4], gap="large")

    with col_form:
        with st.form("add_course_form"):
            subject = st.text_input("Subject")
            day = st.selectbox("Day", ["Mon", "Tue", "Wed", "Thu", "Fri"])
            time_value = st.text_input("Time")
            submit_course = st.form_submit_button("Add Course", use_container_width=True)

        if submit_course:
            if subject.strip() and time_value.strip():
                c.execute("INSERT INTO courses VALUES (?,?,?)",
                          (subject, day, time_value))
                conn.commit()
                st.success("Course added!")
                st.rerun()
            else:
                st.error("Please enter both subject and time.")

    st.divider()

    st.subheader("Weekly schedule")
    courses = get_courses()
    if courses:
        df = pd.DataFrame(courses, columns=["Subject", "Day", "Time"]).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Delete a course")
        courses_with_id = get_courses_with_id()
        delete_labels = [
            f"{subject} — {day} at {time}"
            for _, subject, day, time in courses_with_id
        ]
        selected_delete = st.selectbox(
            "Choose course to remove",
            list(range(len(delete_labels))),
            format_func=lambda idx: delete_labels[idx],
            key="course_delete"
        )
        if st.button("🗑️ Delete selected course", key="delete_course_btn", use_container_width=True):
            rowid = courses_with_id[selected_delete][0]
            c.execute("DELETE FROM courses WHERE rowid = ?", (rowid,))
            conn.commit()
            st.success("Course deleted.")
            st.rerun()
    else:
        st.info("No courses scheduled yet.")

# ================= EXAMS =================
elif menu == "Exams":
    st.subheader("Exams")
    col_form, col_space = st.columns([0.6, 0.4], gap="large")

    with col_form:
        with st.form("add_exam_form"):
            subject = st.text_input("Exam subject")
            exam_date = st.date_input("Exam date", current_date)
            submit_exam = st.form_submit_button("Add Exam", use_container_width=True)

        if submit_exam:
            if subject.strip():
                c.execute("INSERT INTO exams VALUES (?,?)",
                          (subject, exam_date.strftime("%Y-%m-%d")))
                conn.commit()
                add_to_google_calendar(subject, exam_date)
                st.success("Exam added and synced to Google Calendar.")
                st.rerun()
            else:
                st.error("Please enter an exam subject.")

    st.divider()

    st.subheader("Exam list")
    exams = get_exams()
    if exams:
        df = pd.DataFrame(exams, columns=["Subject", "Date"]).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Delete an exam")
        exams_with_id = get_exams_with_id()
        delete_labels = [
            f"{subject} on {date}"
            for _, subject, date in exams_with_id
        ]
        selected_delete = st.selectbox(
            "Choose exam to remove",
            list(range(len(delete_labels))),
            format_func=lambda idx: delete_labels[idx],
            key="exam_delete"
        )
        if st.button("🗑️ Delete selected exam", key="delete_exam_btn", use_container_width=True):
            rowid = exams_with_id[selected_delete][0]
            c.execute("DELETE FROM exams WHERE rowid = ?", (rowid,))
            conn.commit()
            st.success("Exam deleted.")
            st.rerun()
    else:
        st.info("No exams added yet.")

# ================= ASSIGNMENTS =================
elif menu == "Assignments":
    st.subheader("Assignments")
    col_form, col_space = st.columns([0.6, 0.4], gap="large")

    with col_form:
        with st.form("add_assignment_form"):
            title = st.text_input("Title")
            subject = st.text_input("Subject")
            deadline = st.date_input("Deadline", current_date)
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            submit_assign = st.form_submit_button("Add Assignment", use_container_width=True)

        if submit_assign:
            if title.strip() and subject.strip():
                c.execute("INSERT INTO assignments VALUES (?,?,?,?)",
                          (title, subject, deadline.strftime("%Y-%m-%d"), priority))
                conn.commit()
                st.success("Assignment added!")
                st.rerun()
            else:
                st.error("Please enter title and subject.")

    st.divider()

    assignments = get_assignments()
    if assignments:
        df = pd.DataFrame(assignments, columns=["Title", "Subject", "Deadline", "Priority"]).reset_index(drop=True)
        df["Status"] = df["Deadline"].apply(
            lambda d: "Due today" if datetime.strptime(d, "%Y-%m-%d").date() == current_date
            else ("Overdue" if datetime.strptime(d, "%Y-%m-%d").date() < current_date else "Upcoming")
        )
        st.dataframe(df.sort_values(["Status", "Deadline"]), use_container_width=True, hide_index=True)

        csv_data = df.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV",
            data=csv_data,
            file_name=f"assignments_{current_date}.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.divider()

        st.subheader("Deadline notifications")
        has_notifications = False
        for title, _, deadline, priority in assignments:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d").date()
            days_left = (deadline_dt - current_date).days
            if days_left < 0:
                st.markdown(
                    f"<div style='padding:10px;background:{CARD_BG};border-left:3px solid #dc3545;border-radius:6px;margin-bottom:8px;'><strong style='color:#dc3545'>🔴 Overdue</strong> — {title} due on {deadline} {priority_badge(priority)}</div>",
                    unsafe_allow_html=True
                )
                has_notifications = True
            elif days_left == 0:
                st.markdown(
                    f"<div style='padding:10px;background:{CARD_BG};border-left:3px solid #ffc107;border-radius:6px;margin-bottom:8px;'><strong style='color:#ffc107'>🟠 Due today</strong> — {title} {priority_badge(priority)}</div>",
                    unsafe_allow_html=True
                )
                has_notifications = True
            elif days_left <= 3:
                st.markdown(
                    f"<div style='padding:10px;background:{CARD_BG};border-left:3px solid #28a745;border-radius:6px;margin-bottom:8px;'><strong style='color:#28a745'>🟢 In {days_left} days</strong> — {title} {priority_badge(priority)}</div>",
                    unsafe_allow_html=True
                )
                has_notifications = True

        if not has_notifications:
            st.success("✅ No urgent deadlines!")

        st.divider()
        st.subheader("Delete an assignment")
        assignments_with_id = get_assignments_with_id()
        delete_labels = [
            f"{title} ({subject}) due {deadline} [{priority}]"
            for _, title, subject, deadline, priority in assignments_with_id
        ]
        selected_delete = st.selectbox(
            "Choose assignment to remove",
            list(range(len(delete_labels))),
            format_func=lambda idx: delete_labels[idx],
            key="assignment_delete"
        )
        if st.button("🗑️ Delete selected assignment", key="delete_assignment_btn", use_container_width=True):
            rowid = assignments_with_id[selected_delete][0]
            c.execute("DELETE FROM assignments WHERE rowid = ?", (rowid,))
            conn.commit()
            st.success("Assignment deleted.")
            st.rerun()
    else:
        st.info("No assignments added yet.")

# ================= DASHBOARD =================
elif menu == "Dashboard":
    st.subheader("Schedule Management Dashboard")
    st.divider()

    exams = get_exams()
    assignments = get_assignments()
    events = st.session_state.events

    upcoming_exams = sorted(
        [e for e in exams if datetime.strptime(e[1], "%Y-%m-%d").date() >= current_date],
        key=lambda x: x[1]
    )[:5]
    upcoming_assignments = sorted(
        [a for a in assignments if datetime.strptime(a[2], "%Y-%m-%d").date() >= current_date],
        key=lambda x: x[2]
    )[:5]

    if upcoming_exams or upcoming_assignments or events:
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.subheader("📅 Upcoming events")
            for subject, exam_date in upcoming_exams:
                st.markdown(f"<div style='padding:10px;background:{CARD_BG};border-radius:6px;margin-bottom:8px;'><strong>📝 {subject}</strong><br><small style='color:{TEXT_SECONDARY};'>{exam_date}</small></div>", unsafe_allow_html=True)

        with col2:
            st.subheader("✅ Pending work")
            for title, subject, deadline, priority in upcoming_assignments:
                days_left = (datetime.strptime(deadline, "%Y-%m-%d").date() - current_date).days
                st.markdown(
                    f"<div style='padding:10px;background:{CARD_BG};border-radius:6px;margin-bottom:8px;border-left:3px solid {PRIORITY_COLORS[priority]};'><strong>{title}</strong><br><small style='color:{TEXT_SECONDARY};'>{subject} • {days_left} days left</small></div>",
                    unsafe_allow_html=True
                )

        st.divider()

    st.subheader("Deadline notifications")
    has_alerts = False
    for title, subject, deadline, priority in assignments:
        deadline_dt = datetime.strptime(deadline, "%Y-%m-%d").date()
        days_left = (deadline_dt - current_date).days
        if days_left < 0:
            st.error(f"Overdue: {title} ({subject}) was due on {deadline}.")
            has_alerts = True
        elif days_left == 0:
            st.warning(f"Due today: {title} ({subject}).")
            has_alerts = True
        elif days_left <= 3:
            st.info(f"{title} ({subject}) is due in {days_left} days.")
            has_alerts = True

    if not has_alerts:
        st.success("✅ No urgent notifications!")

    st.divider()

    st.subheader("Conflict alerts")
    conflicts = find_conflicts()
    if conflicts:
        for conflict in conflicts:
            st.warning(conflict)
    else:
        st.success("✅ No schedule conflicts detected.")


