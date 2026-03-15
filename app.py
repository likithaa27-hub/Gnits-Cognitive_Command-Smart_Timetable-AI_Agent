import os
import streamlit as st
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

def get_redirect_uri():
    # Change this to your actual app URL when deploying
    return "http://localhost:8501"

def get_client_config():
    return {
        "web": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "redirect_uris": [get_redirect_uri()],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

def build_flow():
    flow = Flow.from_client_config(
        get_client_config(),
        scopes=SCOPES,
        redirect_uri=get_redirect_uri(),
    )
    return flow

def credentials_to_dict(creds):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }

def dict_to_credentials(d):
    return Credentials(
        token=d["token"],
        refresh_token=d.get("refresh_token"),
        token_uri=d["token_uri"],
        client_id=d["client_id"],
        client_secret=d["client_secret"],
        scopes=d.get("scopes"),
    )

def get_calendar_service():
    if "credentials" not in st.session_state:
        return None

    creds = dict_to_credentials(st.session_state["credentials"])

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            st.session_state["credentials"] = credentials_to_dict(creds)
        except Exception as e:
            st.session_state.pop("credentials", None)
            st.error(f"Session expired, please log in again: {e}")
            return None

    return build("calendar", "v3", credentials=creds)

def get_upcoming_events(service, days=7):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days)
    try:
        result = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = result.get("items", [])
        return [e for e in events if "birthday" not in e.get("summary", "").lower()]
    except Exception as e:
        st.error(f"Failed to fetch events: {e}")
        return []

def format_event_time(event):
    start = event["start"].get("dateTime", event["start"].get("date"))
    end = event["end"].get("dateTime", event["end"].get("date"))
    try:
        if "T" in start:
            s = datetime.fromisoformat(start)
            e = datetime.fromisoformat(end)
            return s.strftime("%a, %b %d at %I:%M %p"), e.strftime("%I:%M %p")
        else:
            return datetime.fromisoformat(start).strftime("%a, %b %d"), "All day"
    except Exception:
        return start, end

def main():
    st.set_page_config(page_title="Smart Timetable AI Agent", page_icon="📅", layout="wide")
    st.title("📅 Smart Timetable AI Agent")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Handle OAuth callback
    query_params = st.query_params
    auth_code = query_params.get("code")
    auth_error = query_params.get("error")

    if auth_error:
        st.error(f"Google login failed: {auth_error}")
        st.query_params.clear()

    if auth_code and "credentials" not in st.session_state:
        try:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            flow = build_flow()
            flow.fetch_token(code=auth_code)
            st.session_state["credentials"] = credentials_to_dict(flow.credentials)
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.query_params.clear()

    # Show login screen if not authenticated
    if "credentials" not in st.session_state:
        st.subheader("Please sign in with Google to continue.")
        flow = build_flow()
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        st.link_button("🔐 Sign in with Google", auth_url)

        st.info(
            "**Setup:** Make sure your Google Cloud OAuth credentials have this redirect URI:\n\n"
            f"`{get_redirect_uri()}`"
        )
        return

    service = get_calendar_service()
    if not service:
        st.button("Log out", on_click=lambda: st.session_state.pop("credentials", None))
        return

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📆 Upcoming Events")
        days = st.slider("Days to look ahead", 1, 30, 7)
        if st.button("🔄 Refresh"):
            st.rerun()

        events = get_upcoming_events(service, days=days)

        if not events:
            st.info("No upcoming events found.")
        else:
            for event in events:
                summary = event.get("summary", "No Title")
                location = event.get("location", "")
                description = event.get("description", "")
                start, end = format_event_time(event)
                with st.expander(f"📌 {summary} — {start}"):
                    st.write(f"**Time:** {start} → {end}")
                    if location:
                        st.write(f"**Location:** {location}")
                    if description:
                        st.write(f"**Notes:** {description}")

        st.divider()
        if st.button("🚪 Sign Out"):
            st.session_state.clear()
            st.rerun()

    with col_right:
        st.subheader("🤖 AI Scheduling Assistant")
        st.caption("Powered by Gemini — ask about your schedule")

        for msg in st.session_state["chat_history"]:
            st.chat_message(msg["role"]).write(msg["content"])

        user_input = st.chat_input("Ask about your schedule...")
        if user_input:
            st.session_state["chat_history"].append({"role": "user", "content": user_input})

            events = get_upcoming_events(service, days=14)
            events_text = "\n".join(
                f"- {e.get('summary','No Title')}: {format_event_time(e)[0]}"
                for e in events
            ) or "No upcoming events."

            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain.schema import HumanMessage, AIMessage

                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=os.environ["GOOGLE_API_KEY"],
                    temperature=0.7,
                )
                messages = [
                    HumanMessage(content=(
                        f"You are a Smart Timetable Assistant for students.\n"
                        f"Upcoming events:\n{events_text}\n\n"
                        f"Answer this: {user_input}"
                    ))
                ]
                response = llm.invoke(messages).content
            except Exception as e:
                response = f"AI error: {e}"

            st.session_state["chat_history"].append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()