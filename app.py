
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st
import sqlite3
from datetime import datetime, timedelta
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    return service
def add_to_google_calendar(title, date):
    service = get_calendar_service()

    event = {
        'summary': title,
        'start': {'date': str(date)},
        'end': {'date': str(date)},
    }

    service.events().insert(calendarId='primary', body=event).execute()
# ---------------- DATABASE ----------------
conn = sqlite3.connect("schedule.db", check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS courses (
    subject TEXT, day TEXT, time TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS exams (
    subject TEXT, date TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS assignments (
    title TEXT, subject TEXT, deadline TEXT, priority TEXT
)''')

conn.commit()

# ---------------- UI SETUP ----------------
st.set_page_config(page_title="Smart Timetable AI Agent", page_icon="📅")
st.title("📅 Smart Timetable AI Agent")

menu = st.sidebar.selectbox("Menu", [
    "Home",
    "Courses",
    "Exams",
    "Assignments",
    "Dashboard"
])

# ---------------- SESSION STATE ----------------
if "events" not in st.session_state:
    st.session_state.events = []

if "assignments_session" not in st.session_state:
    st.session_state.assignments_session = []

# ================= HOME =================
if menu == "Home":

    # -------- ADD EVENT --------
    st.subheader("➕ Add Event")

    name = st.text_input("Event Name")
    time = st.text_input("Event Time (e.g., 10 AM)")

    if st.button("Add Event", key="add_event_btn"):
        conflict = False
        for e in st.session_state.events:
            if e[1] == time:
                conflict = True

        if conflict:
            st.error("⚠️ Conflict detected!")
        else:
            st.session_state.events.append((name, time))
            st.success("✅ Event Added")

    # -------- SHOW EVENTS --------
    st.subheader("📖 Your Events")

    if st.session_state.events:
        for e in st.session_state.events:
            st.write(f"📌 {e[0]} at {e[1]}")
    else:
        st.info("No events added yet.")

    # -------- FREE TIME --------
    st.subheader("⏰ Free Time Finder")

    if st.button("Check Free Time", key="free_time_btn"):
        st.write("You are free at:")
        st.write("• 2 PM – 4 PM")
        st.write("• 6 PM – 8 PM")

    # -------- SMART ASSISTANT --------
    st.subheader("🤖 Smart Assistant")

    user_query = st.text_input("Ask something")

    if user_query:
        query = user_query.lower()

        if "free" in query:
            st.success("You are free at 2 PM - 4 PM")

        elif "event" in query:
            if st.session_state.events:
                for e in st.session_state.events:
                    st.write(f"{e[0]} at {e[1]}")
            else:
                st.info("No events scheduled")

        elif "assignment" in query:
            if st.session_state.assignments_session:
                for a in st.session_state.assignments_session:
                    st.write(f"{a[0]} - Due: {a[1]}")
            else:
                st.info("No assignments added")

        elif "study" in query:
            st.success("📖 You can study at 6 PM")

        else:
            st.warning("Try: free time / events / assignments / study")

    # -------- QUICK ASSIGNMENTS (SESSION) --------
    st.subheader("📌 Quick Assignments (Session)")

    task = st.text_input("Assignment Name")
    deadline = st.text_input("Deadline")

    if st.button("Add Assignment", key="session_assign_btn"):
        st.session_state.assignments_session.append((task, deadline))
        st.success("Assignment added")

    for a in st.session_state.assignments_session:
        st.write(f"{a[0]} - Due: {a[1]}")


# ================= COURSES =================
elif menu == "Courses":
    st.header("📘 Course Timetable")

    subject = st.text_input("Subject")
    day = st.selectbox("Day", ["Mon","Tue","Wed","Thu","Fri"])
    time = st.text_input("Time")

    if st.button("Add Course", key="course_btn"):
        c.execute("INSERT INTO courses VALUES (?,?,?)",
                  (subject, day, time))
        conn.commit()
        st.success("Course added!")

    st.subheader("Weekly Schedule")
    courses = c.execute("SELECT * FROM courses").fetchall()

    for course in courses:
        st.write(course)

# ================= EXAMS =================
elif menu == "Exams":
    st.header("📝 Exams")

    subject = st.text_input("Exam Subject")
    exam_date = st.date_input("Exam Date")

    if st.button("Add Exam", key="exam_btn"):
        c.execute("INSERT INTO exams VALUES (?,?)",
                  (subject, str(exam_date)))
        conn.commit()

        # ✅ ADD GOOGLE CALENDAR HERE (CORRECT PLACE)
        add_to_google_calendar(subject, exam_date)

        st.success("Exam added + synced to Google Calendar ✅")

        st.subheader("📚 Study Plan")
        for i in range(3, 0, -1):
            study_day = exam_date - timedelta(days=i)
            st.write(f"{study_day} → Study {subject} (2 hrs)")

# ================= ASSIGNMENTS =================
elif menu == "Assignments":
    st.header("📌 Assignments (Database)")

    title = st.text_input("Title")
    subject = st.text_input("Subject")
    deadline = st.date_input("Deadline")
    priority = st.selectbox("Priority", ["Low","Medium","High"])

    if st.button("Add Assignment", key="db_assign_btn"):
        c.execute("INSERT INTO assignments VALUES (?,?,?,?)",
                  (title, subject, str(deadline), priority))
        conn.commit()
        st.success("Assignment added!")

    st.subheader("All Assignments")
    assignments = c.execute("SELECT * FROM assignments").fetchall()

    for a in assignments:
        st.write(a)


# ================= DASHBOARD =================
elif menu == "Dashboard":
    st.header("⚠ Workload Alerts")

    exams = c.execute("SELECT * FROM exams").fetchall()
    assignments = c.execute("SELECT * FROM assignments").fetchall()

    for e in exams:
        exam_date = datetime.strptime(e[1], "%Y-%m-%d")

        for a in assignments:
            deadline = datetime.strptime(a[2], "%Y-%m-%d")

            if abs((exam_date - deadline).days) <= 2:
                st.warning(f"{e[0]} exam & {a[0]} assignment are close!")


