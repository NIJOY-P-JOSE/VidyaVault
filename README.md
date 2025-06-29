# 🎓 VidyaVault (Gemini-Powered)

> *An academic project showcase platform powered by Django — now enhanced with Google Gemini via Vertex AI for smarter project exploration.*

---

## 🧠 Project Overview

**VidyaVault** is a Django-based platform that allows students to upload and showcase their final-year or academic projects. It enables users to explore peer submissions, receive structured faculty evaluations, and view performance through dashboards and leaderboards.

💡 In this GenAI-enhanced version, VidyaVault integrates a **Gemini-powered chatbot** (via Vertex AI) that helps users **understand each project** by analyzing its README and code. It acts as a learning companion for students, giving instant explanations and summaries.

---

## 🚀 Key Features

- 📤 Upload and manage academic/final-year projects  
- 🔍 Explore peer submissions with filters and search  
- 🧑‍🏫 Faculty scoring system  
- 📈 Dashboard for participation and tech usage  
- 🏆 Leaderboard based on scores and likes  
- 💬 Comment system with threaded replies  
- 🤖 **Gemini AI assistant**: Ask questions about the project

---

## 🤖 Gemini AI Integration (via Vertex AI)

VidyaVault includes an AI assistant on each project page using **Google’s Gemini API**:

| Feature | Description |
|--------|-------------|
| 💬 Chat with AI | Ask questions about the project README/code |
| 🧠 Model | `gemini-1.5-flash` via Vertex AI |
| 🛡️ Privacy | Chat resets on reload; no history stored |
| 📚 Scope | Only project-specific files like `README.md`, `.py`, `.html` |
| 📎 Prompting | Injects system instructions to restrict scope and ensure relevance |

> This integration enhances the learning experience by enabling contextual Q&A without altering the original project code.

---

## 🔧 Technical Stack

### ✅ Backend

- **Framework**: Django 4.2  
- **Language**: Python 3.10+  
- **Database**: SQLite (dev) / PostgreSQL (prod)  
- **Auth**: Django's User model + custom roles  
- **AI API**: Google Gemini via `google-generativeai` Python SDK  
- **.env**: Securely stores `GOOGLE_API_KEY`

### ⚙️ Core Models

| Model | Purpose |
|-------|---------|
| `Project` | Stores metadata, team, GitHub link |
| `UserProfile` | User role, batch, department |
| `ProjectScore` | Faculty evaluation |
| `Comment` | Threaded discussions |

---

## 🎨 Frontend

- **Bootstrap 5** for layout and responsive UI  
- **Font Awesome** for icons  
- **Django Templates** for page structure  
- **JavaScript**: Chatbot UI and fetch logic  
- **Markdown support** using `marked.js` in chatbot replies

---

## 📊 Dashboard Features

- Charts: Department-wise participation  
- Tech stack usage visualization  
- Skills word cloud from project tags  

---

## 🧠 AI Assistant Flow

1. User clicks "Ask AI About This Project"
2. Enters a question related to the project (e.g., "What does this project do?")
3. Django backend builds a prompt using:
   - Static instruction
   - README/code content (retrieved or embedded)
4. Gemini responds with an explanation or breakdown
5. UI shows formatted response with Markdown support

---

## 📁 Folder Structure

```text
vidyavault/
├── manage.py                   # Django project starter
├── .env                        # Contains secrets like GOOGLE_API_KEY
│
├── vidyavault/                 # Project settings and URL configurations
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── projects/                   # Main Django app
│   ├── models.py               # Project, Score, Comment models
│   ├── views.py                # Views for listing, detail, upload, etc.
│   ├── chatbot_gemini.py       # Gemini API integration
│   ├── urls.py                 # App-specific URLs
│
├── templates/
│   ├── base.html               # Base layout
│   ├── registration/          # Auth pages
│   │   ├── login.html
│   │   └── register.html
│   └── projects/              # Project-related templates
│       ├── home.html
│       ├── about.html
│       ├── dashboard.html
│       ├── leaderboard.html
│       ├── profile.html
│       ├── project_detail.html
│       ├── project_list.html
│       ├── upload_project.html
│       ├── admin_review.html
│       ├── score_project.html
│
└── media/                      # Uploaded project files
```


---

## 🧪 Setup & Run

```bash
# Clone repo
git clone https://github.com/NIJOY-P-JOSE/VidyaVault.git
cd VidyaVault

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your Google Gemini API key
echo "GOOGLE_API_KEY=your_api_key" > .env

# Run server
python manage.py runserver
```

---

## 📽️ Demo Video


https://github.com/user-attachments/assets/194c3093-9bbc-414b-a0b4-da881228da45



---

## 🙋 Contact

- **Name**: Nijoy P Jose  
- **Email**: nijoypjose@gmail.com 
