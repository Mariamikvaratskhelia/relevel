# relevel
# ReLevel 🇩🇪

### Level up your future in Germany.

ReLevel is a web platform designed to help international students organize their journey toward studying in Germany. It brings important parts of the application and preparation process together in one place — from researching universities and managing documents to preparing for student life in Germany.

The goal is to make the process of studying abroad more structured, accessible, and manageable.

---

## ✨ Features

### 🎓 Student Dashboard
- Personalized student dashboard
- Profile completion checklist
- Overview of study goals and next steps
- Planned study start date

### 👤 Registration & Onboarding
- User registration and login
- Student profile creation
- Educational background and study preferences
- Study goals and certificate recognition status

### 🔎 University Finder
- Filter institutions by city, subject, degree, language, and institution type
- Explore universities, universities of applied sciences, and Studienkollegs

*Currently uses example university data.*

### 📁 Document Manager
- Upload and organize important documents
- Categories for school certificates, passports, language certificates, transcripts, motivation letters, and visa documents

### 🤖 Study Assistant
- Question-and-answer interface for topics related to studying in Germany
- Covers topics such as Studienkolleg, admission requirements, visa preparation, and German grammar

*Currently uses predefined, keyword-based responses.*

### 🌍 Life in Germany
- Information about accommodation
- Bank accounts and health insurance
- Address registration
- Public transportation

### 👥 Student Community
- Example student groups for different interests and study goals

### ⚙️ Profile Settings
- Edit personal information and study preferences
- Theme and notification preferences
- Password management

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Django | Backend framework |
| Django REST Framework | REST API |
| SimpleJWT | Token-based authentication |
| PostgreSQL | Production database |
| SQLite | Local development database |
| Redis | Caching and task broker |
| Celery | Background task processing |
| HTML / CSS | Frontend templates and styling |
| Gunicorn | Application server |
| WhiteNoise | Static file serving |
| drf-spectacular | API documentation |
| Docker | Application containerization |
| Git & GitHub | Version control |

---

## 🏗️ Project Structure

```text
relevel/
│
├── portfolio_site/
│   └── portfolio_site/
│       ├── config/
│       │   ├── settings.py
│       │   ├── urls.py
│       │   ├── wsgi.py
│       │   └── celery.py
│       │
│       ├── portfolio/
│       │   ├── migrations/
│       │   ├── templates/
│       │   ├── models.py
│       │   ├── views.py
│       │   ├── forms.py
│       │   ├── serializers.py
│       │   ├── urls.py
│       │   ├── site_urls.py
│       │   ├── tasks.py
│       │   └── admin.py
│       │
│       ├── manage.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── docker-compose.yml
│
├── public/
│   └── _redirects
│
└── README.md
```

---

## 🚀 Getting Started

Follow these steps to run ReLevel locally.

### 1. Clone the repository

```bash
git clone https://github.com/Mariamikvaratskhelia/relevel.git
cd relevel
```

### 2. Navigate to the Django project

```bash
cd portfolio_site/portfolio_site
```

### 3. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Configure the environment variables required by `config/settings.py`.

For local development, use a secure development secret key and keep sensitive credentials out of version control.

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

---

## 🔌 API Documentation

ReLevel includes a REST API built with Django REST Framework.

| Endpoint | Description |
|---|---|
| `/api/users/` | User information |
| `/api/projects/` | Project data |
| `/api/skills/` | Skills |
| `/api/contact/` | Contact messages |
| `/api/token/` | Obtain JWT tokens |
| `/api/token/refresh/` | Refresh JWT tokens |
| `/api/schema/` | API schema |
| `/api/docs/` | Swagger API documentation |

Local API documentation:

```text
http://127.0.0.1:8000/api/docs/
```

---

## 📌 Development Status

ReLevel is an ongoing project. Its core Django foundation and several main features are implemented, while other parts are still being developed.

| Feature | Status |
|---|---|
| User registration and login | Implemented |
| Student profiles | Implemented |
| Onboarding | Implemented |
| Dashboard and profile checklist | Implemented |
| Document uploads | Implemented |
| REST API | Implemented |
| University Finder | Example data |
| Study Roadmap | Static content |
| Study Assistant | Rule-based prototype |
| Student Community | Example groups |
| Life in Germany | Static information |
| Background email tasks | Task code implemented |

---

## 🗺️ Future Improvements

Planned development includes:

- [ ] Verified and regularly updated university database
- [ ] Personalized study and application roadmap
- [ ] AI-powered study assistant
- [ ] Application deadline tracker and reminders
- [ ] Interactive student community
- [ ] Persistent document storage
- [ ] Email notifications
- [ ] Further API and production security improvements

---

## 🧠 Project Motivation

Moving to another country to pursue higher education can be challenging. International students often have to navigate unfamiliar admission systems, language requirements, documentation, deadlines, and everyday practical matters.

ReLevel was created to bring these steps together and make the journey toward studying in Germany easier to understand and organize.

---

---

*ReLevel — Level up your future in Germany.*
