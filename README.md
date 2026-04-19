# 📌 Cognitive Command Smart Timetable AI Agent

A Streamlit-based intelligent assistant designed to simplify task management through AI-powered command processing and seamless integration with Google services. This project demonstrates the practical application of modern technologies such as natural language processing, API integration, and data visualization in a student-focused academic setting.

## 🎯 Objective
The primary goal of this project is to develop a smart assistant capable of interpreting user commands and automating scheduling tasks, thereby improving productivity and showcasing real-world software development practices.

## 🚀 Key Features
- AI-powered natural language command processing using Groq / OpenAI / LangChain
- Integration with Google Calendar for automated scheduling
- Interactive user interface built with Streamlit
- Data handling and processing using Pandas
- Graphical insights and visualization using Matplotlib
- Secure authentication via Google OAuth 2.0
- Lightweight local database management using SQLite
- REST API communication for external services

## 🏗️ Project Structure
GNITS-COGNITIVE-COMMAND/
│
├── .streamlit/
│ ├── config.toml
│ └── secrets.toml
│
├── .venv/
│
├── app.py
├── app_clean.py
│
├── credentials.json
├── token.json
│
├── schedule.db
│
├── requirements.txt
├── README.md
└── .gitignore

## ⚙️ Installation and Setup

### Step 1: Clone the Repository
git clone https://github.com/your-username/your-repo-name.git  
cd your-repo-name  

### Step 2: Create and Activate Virtual Environment
python -m venv .venv  

Windows:  
.venv\Scripts\activate  


### Step 3: Install Required Dependencies
pip install -r requirements.txt  

## 🔐 API Configuration

### Environment Variables (.env)
Create a `.env` file in the root directory and add:
OPENAI_API_KEY=your_openai_key  
GROQ_API_KEY=your_groq_key  

### Streamlit Secrets (Recommended)
Alternatively, configure `.streamlit/secrets.toml`:
OPENAI_API_KEY = "your_openai_key"  
GROQ_API_KEY = "your_groq_key"  

## 📅 Google Calendar Integration Setup

1. Navigate to Google Cloud Console and create a new project  
2. Enable the Google Calendar API  
3. Configure OAuth consent screen  
4. Create OAuth Client ID credentials  
5. Download the credentials file and rename it as `credentials.json`  
6. Place the file in the project root directory  
7. Run the application and authenticate via browser  
8. A `token.json` file will be generated automatically after successful login  

## ▶️ Running the Application
streamlit run app.py  

Alternatively:
streamlit run app_clean.py  

## 🗄️ Database
The application uses a local SQLite database (`schedule.db`) to store:
- Scheduled events  
- User tasks  
- Command history  

## 🧪 Educational Use Cases
- Demonstrates integration of AI APIs in real-world applications  
- Illustrates full-stack development using Python and Streamlit  
- Provides hands-on experience with OAuth authentication  
- Showcases database management using SQLite  
- Encourages understanding of modular and scalable coding practices  

## ⚠️ Important Guidelines
The following files should not be uploaded to public repositories:
.venv/  
credentials.json  
token.json  
.streamlit/secrets.toml  
.env  

### Recommended .gitignore Entries
.venv/  
__pycache__/  
*.pyc  
credentials.json  
token.json  
.streamlit/secrets.toml  
.env  

## 🛠️ Troubleshooting

Google Authentication Issues:  
Delete `token.json` and restart the application  

API Errors:  
Ensure all API keys are correctly configured  

Dependency Issues:  
pip install --upgrade streamlit  

## 🤝 Contribution Guidelines
Students and contributors are encouraged to:
1. Fork the repository  
2. Create a feature branch  
3. Commit meaningful changes  
4. Push updates to GitHub  
5. Submit a Pull Request  

## 📄 License
This project is developed for academic and educational purposes.

## 👨‍💻 Authors
Developed as part of a student team project (GNITS)

## 🔮 Future Scope
- Voice-based command interaction  
- Enhanced UI/UX design  
- Multi-user authentication system  
- Cloud-based database integration  
- Advanced analytics dashboard  

