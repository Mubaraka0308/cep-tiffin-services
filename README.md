# 🍲 Khane ki Khoj — CEP Tiffin Services

A realistic, full-stack college Community Engagement Project (CEP) connecting hostel students with verified local tiffin providers and messes in Pune (Dhankawadi, Sarita Vihar, Katraj, Bibwewadi).

Developed as part of the Second-Year Engineering Community Engagement Project based on 7 weeks of student surveys, vendor field interviews, and Figma wireframes.

---

## 🌟 Core Features

### For Students:
1. **Discovery & Filtering:** Search tiffins by Pune area, dietary preference (Pure Veg, Veg & Non-Veg, Jain), and budget.
2. **Daily Hygiene Updates:** View daily kitchen cleanliness and food prep photos submitted by the cooks.
3. **Advance Leave Alerts:** Real-time alert notifications when a provider schedules leave or kitchen maintenance.
4. **Direct Chat:** Send messages directly to tiffin aunties/mess owners (extra chapatis, timings, preferences).
5. **Genuine Weekly Reviews:** Star ratings and review comments with optional student meal photo proofs.
6. **Tiffin Subscriptions:** Easily order monthly lunch & dinner mess cards or 3-day trial packs.

### For Providers:
1. **Menu Management:** Add, edit, and delete daily dishes, thalis, and prices.
2. **Daily Hygiene Proof:** Upload daily photos of sanitized kitchen counters and utensils.
3. **Advance Leave Pre-Notice:** Set leave dates and reasons; automatically broadcasts alerts to subscribed students.
4. **Customer Count Tracking:** View active student subscribers to accurately forecast daily grocery requirements.
5. **Direct Customer Chat:** Reply directly to student meal inquiries.
6. **Advertisements & Offers:** Publish promotional discounts and announcements to attract hostel students.

---

## 🛠️ Technology Stack

* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Zero build tools, runs directly in browser)
* **Backend:** Python 3, FastAPI, Uvicorn
* **Database:** PostgreSQL (with SQLAlchemy ORM)
* **Validation:** Pydantic v2
* **Authentication:** PyJWT, Bcrypt password hashing
* **Testing:** 20 automated tests in `test_app.py` (via HTTPX & Starlette TestClient)

---

## 📁 Project Structure

```text
cep-tiffin-services/
├── backend/
│   ├── main.py               # Main application entry & static mounts
│   ├── database.py           # PostgreSQL connection & SQLAlchemy engine
│   ├── models.py             # Database models (users, providers, menus, ratings)
│   ├── schemas.py            # Pydantic validation schemas
│   ├── auth_utils.py         # Bcrypt password hashing & JWT tokens
│   ├── seed_data.py          # Realistic Pune demo data
│   └── routers/              # Modular API endpoints
│       ├── auth.py
│       ├── providers.py
│       ├── menu.py
│       ├── ratings.py
│       ├── hygiene.py
│       ├── availability.py
│       ├── advertisements.py
│       ├── chat.py
│       └── notifications.py
├── frontend/
│   ├── index.html            # Landing page
│   ├── login.html            # Login page (with 1-click demo buttons)
│   ├── register.html         # Registration page (Student / Provider)
│   ├── student-dashboard.html# Discovery, search, and subscriptions
│   ├── provider-dashboard.html# Kitchen management dashboard
│   ├── provider-profile.html # Detailed tiffin profile & reviews
│   ├── chat.html             # Direct messaging window
│   ├── css/                  # style.css, dashboard.css, responsive.css
│   └── js/                   # api.js, auth.js, student.js, provider.js, chat.js
├── uploads/                  # Uploaded hygiene and meal proof images
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── test_app.py               # 20 Automated system tests
├── PROJECT_EXPLANATION.md    # Viva guide and 30-point technical breakdown
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* Python 3.10 or higher
* PostgreSQL (Optional for local testing; SQLite fallback is enabled if PostgreSQL is inactive)

### 2. Setup Virtual Environment
```bash
# Clone or navigate to the project directory
cd "c:\Users\mubbs\OneDrive\Desktop\cep tiffin services"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Default `.env` configuration:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tiffin_db
SECRET_KEY=college_cep_tiffin_services_secret_key_2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=uploads
```

*(Note: If PostgreSQL is not active on your machine, `backend/database.py` automatically detects this and falls back to a local SQLite database `tiffin_services.db` so the app is always functional!)*

### 5. PostgreSQL Database Setup (If using PostgreSQL)
1. Open pgAdmin or `psql` command line:
   ```sql
   CREATE DATABASE tiffin_db;
   ```
2. Update username/password in your `.env` file if different from `postgres:postgres`.
3. The database tables and demo seed data will be automatically created on server start!

### 6. Start the Application
Run Uvicorn:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 7. Access in Browser
* **Main Website:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Student Dashboard:** [http://127.0.0.1:8000/student-dashboard.html](http://127.0.0.1:8000/student-dashboard.html)
* **Provider Dashboard:** [http://127.0.0.1:8000/provider-dashboard.html](http://127.0.0.1:8000/provider-dashboard.html)
* **Interactive API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🔑 Demo Login Credentials (For Viva Evaluation)

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Student** | `aarav_student` | `password123` | Student at PIET, staying in Dhankawadi hostel |
| **Student** | `priya_student` | `password123` | Student at Symbiosis, staying in Sarita Vihar |
| **Provider** | `annapurna_tiffin` | `password123` | Sunita Tai's Tiffins, Dhankawadi (Pure Veg) |
| **Provider** | `ghar_ka_swad` | `password123` | Ramesh Patil's Mess, Sarita Vihar (Veg & Non-Veg) |
| **Provider** | `homebite_tiffins` | `password123` | Kavita Sharma's Tiffins, Katraj (Jain available) |

*(Tip: On `login.html`, click the quick demo buttons to auto-fill these credentials instantly!)*

---

## 🧪 Automated Testing
Run the automated test suite verifying all 20 core student and provider flows:
```bash
python test_app.py
```
Expected output:
```text
ALL 20 CEP PROJECT AUTOMATED SYSTEM TESTS PASSED SUCCESSFULLY!
```

---
