import streamlit as st

st.set_page_config(page_title="Smart Timetable AI Agent", page_icon="📅")

st.title("📅 Smart Timetable AI Agent")

# Store events in session (so they don’t disappear)
if "events" not in st.session_state:
    st.session_state.events = []

# ---------------- ADD EVENT ----------------
st.subheader("➕ Add Event")

name = st.text_input("Event Name")
time = st.text_input("Event Time (e.g., 10 AM)")

if st.button("Add Event"):
    conflict = False

    for e in st.session_state.events:
        if e[1] == time:
            conflict = True

    if conflict:
        st.error("⚠️ Conflict detected!")
    else:
        st.session_state.events.append((name, time))
        st.success("✅ Event Added")

# ---------------- SHOW EVENTS ----------------
st.subheader("📖 Your Events")

if st.session_state.events:
    for e in st.session_state.events:
        st.write(f"📌 {e[0]} at {e[1]}")
else:
    st.info("No events added yet.")

# ---------------- FREE TIME ----------------
st.subheader("⏰ Free Time Finder")

if st.button("Check Free Time"):
    st.write("You are free at:")
    st.write("• 2 PM – 4 PM")
    st.write("• 6 PM – 8 PM")