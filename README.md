# Smart Timetable Assistant AI Agent Development Project


## Project Overview
Build an AI-powered calendar management agent that helps students organize their academic schedules, track assignment deadlines, manage exam dates, and automatically resolve scheduling conflicts. Students can interact naturally with the agent to find free slots, reschedule events, and receive intelligent reminders. You'll master calendar API integration, scheduling algorithms, and conversational AI while creating a comprehensive time management assistant.
Domain Focus: Productivity Technology & Calendar Management
 Core Skills: Calendar API integration, scheduling algorithms, conflict resolution, time management automation, conversational agents


## Week 1 Progress
In Week 1, we set up the foundation for the Smart Timetable Assistant AI Agent Development Project. I created a public GitHub repository and structured the project properly with essential files like the main application file, requirements file, README, and gitignore file.
I installed Git and configured it with GitHub to manage version control. I set up the development environment using Python and VS Code and installed all required libraries such as Streamlit, Google API libraries, and LangChain.
I built a basic Streamlit interface to verify that the project runs successfully. The application was tested locally in the browser to ensure the setup is working correctly.
This week focused on creating a strong technical base so that Google Calendar integration and scheduling features can be implemented smoothly in the upcoming weeks.

## Tech Stack
For this project, we are going to  use  the following technologies and tools:

-Python – Main programming language used to build the application logic.

-Streamlit – Used to create the web-based user interface for the AI Smart Timetable Agent.

-Google Calendar API (google-api-python-client) – Used to integrate and interact with Google Calendar for event management.

-Google Authentication Libraries (google-auth, google-auth-oauthlib, google-auth-httplib2) – Used to securely authenticate users and connect to Google services.

-LangChain – Used to build the AI-powered conversational agent and manage AI workflows.

-langchain-google-genai – Used to connect LangChain with Google’s Generative AI models.

-python-dotenv – Used to manage environment variables securely, such as API keys and credentials.

## Week 2 Progress
In Week 2, the focus was on integrating the Smart Timetable Assistant with Google Calendar to enable real-time event management. The Google Calendar API was configured through the Google Cloud Console, where a project was created and OAuth credentials were generated to allow secure authentication.

Using the Google authentication libraries, the application was updated to support the OAuth login flow. When the application runs for the first time, users are prompted to log in to their Google account and grant calendar access. After successful authentication, a token file is generated and stored locally to maintain the session for future use.

The Streamlit application was enhanced to connect with the Google Calendar API and retrieve upcoming events from the user’s primary calendar. The system now displays events scheduled within the next seven days, allowing users to view their upcoming schedule directly inside the application.

Additionally, functionality was implemented to allow users to create new calendar events through the Streamlit interface. Users can enter the event title, date, and time, and the application automatically adds the event to their Google Calendar.

This week focused on building the core calendar integration and authentication workflow, enabling the application to interact with Google Calendar and manage events dynamically. This establishes the foundation required for implementing AI-powered scheduling and smart timetable generation in the upcoming weeks.
## Week 3 Progress

In Week 3, we focused on simplifying the application by removing the Google Calendar authentication and API integration. This helped reduce complexity and allowed us to concentrate on building the core scheduling features of the system.

We implemented a manual event management system where users can add events using simple input fields. The events are temporarily stored and displayed within the application interface.

A basic conflict detection feature was developed to identify overlapping events. When a user tries to add an event at a time that already exists, the system displays a warning message to prevent scheduling conflicts.

Additionally, a simple free time finder feature was introduced to show available time slots. This helps users quickly identify when they are free for planning other activities.

We also improved the user interface using Streamlit components to make the application more structured and user-friendly. Unnecessary files and complex code were removed to keep the project clean and easy to maintain.
## Week 4 Progress

In Week 4, we enhanced the application by adding a conversational scheduling assistant. The system can now process basic natural language queries such as finding free time, viewing events, and checking assignments.

We integrated event management and assignment tracking with the assistant, allowing users to interact with the system more intuitively. This improved the usability and made the application behave like a simple AI-based scheduling agent.

The assistant can now respond to queries and provide relevant information based on stored data, completing the core scheduling functionality of the project.

## Week 5 Progress
During Week 5, we enhanced the Smart Timetable AI Agent by implementing an Academic Schedule Management system focused on student productivity. We developed modules to manage courses, exams, and assignments using a structured database, along with automatic study plan generation based on upcoming exam schedules. A key feature added was the integration of Google Calendar using OAuth 2.0, enabling seamless synchronization of exam events with the user’s personal calendar. We also implemented basic conflict detection, workload alerts, and a simple smart assistant to handle user queries related to schedules and free time. Additionally, we maintained version control using GitHub to manage and update the project efficiently. These improvements made the system more practical, organized, and useful for academic planning.

## Week 6 Progress
In Week 6, the Smart Timetable AI Agent was developed into a fully functional scheduling system with strong core features. The calendar module allows users to add courses and automatically generates a weekly timetable based on selected days and timings. Users can also create custom events, and the system includes a conflict detection mechanism that prevents overlapping schedules while suggesting the next available free slot. This ensures efficient time management and avoids scheduling errors.

The assignment and study planning module was implemented to help users manage academic tasks effectively. Users can add assignments with deadlines and priority levels (high, medium, low), and the system intelligently allocates study time based on available free slots. High-priority tasks are given more focus, ensuring deadlines are met. This demonstrates a working logic for automated scheduling and workload balancing.

Additionally, an analytics dashboard was built to provide insights into time usage. It visualizes planned hours using charts, calculates total busy and free time, and provides alerts for heavy workloads or underutilized schedules. Overall, Week 6 successfully delivers a complete and practical timetable management system with scheduling, conflict handling, study planning, and analytics, forming a strong foundation for further enhancements.


## Week 7 Progress
In Week 7, we focused on improving the user interface and enhancing the overall usability of the Smart Timetable Assistant. The navigation system was redesigned by replacing the sidebar with a horizontal top navigation bar, allowing users to easily switch between Home, Calendar, Courses, Exams, Assignments, and Dashboard sections. A modern dark theme was implemented across the entire application to provide a consistent and professional look. We also introduced a color-coded priority system for assignments and notifications, where high priority tasks appear in red, medium in yellow, and low in green, helping users quickly identify urgent work.

The calendar module was enhanced with structured monthly, weekly, and daily views, and events such as exams, courses, and assignments were displayed using different colors for better clarity. Full edit and delete functionality was added for courses, exams, assignments, and personal events, allowing users to manage their schedules more efficiently. The dashboard was redesigned to display upcoming exams, pending assignments, and deadline notifications in a clean layout with card-based alerts for overdue and upcoming tasks.

Additionally, we improved data presentation using styled tables, added CSV export functionality for assignments, and enhanced forms with better layout and input styling. Visual dividers and improved spacing were also introduced across pages to enhance readability. Overall, Week 7 focused on UI redesign, usability improvements, and feature refinement, making the Smart Timetable Assistant more polished, user-friendly, and ready for real-world usage.