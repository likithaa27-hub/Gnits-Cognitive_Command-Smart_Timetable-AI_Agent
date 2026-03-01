import streamlit as st

st.title("AI Smart Timetable Agent")

st.write("Week 1: Project Setup Completed And Tested")

event = st.text_input("Enter event name")

if st.button("Add Event"):
    st.success(f"Event '{event}' added successfully!")