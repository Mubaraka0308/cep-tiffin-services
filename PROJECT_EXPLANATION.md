# 📘 CEP Tiffin Services (Khane ki Khoj) — Complete Project Guide & Viva Preparation

> **For College Students & Viva Evaluators**  
> **Course:** Community Engagement Project (CEP) — Second Year Engineering  
> **Focus Area:** Pune Hostel Student Food Security & Local Mess Modernization  
> **Field Research Locations:** Sarita Vihar, Dhankawadi, Katraj, Bibwewadi (Pune, Maharashtra)

---

## 1. Project Objective
The objective of this project is to develop a reliable, full-stack community food platform connecting college hostel students with local home-based tiffin providers and small messes in Pune. The platform eliminates meal uncertainty, improves daily food hygiene transparency, simplifies advance leave communication, and empowers local home cooks (aunties/mess owners) to manage their daily menu, advertising, and student customer counts without middlemen.

---

## 2. Problem Being Solved
Through our 7-week CEP ground research, student surveys, vendor surveys, and offline kitchen visits in Sarita Vihar and Dhankawadi, we identified distinct pain points on both sides:

* **Student Problems:**
  1. **Meal Uncertainty:** Sudden kitchen closures leaving students without lunch or dinner.
  2. **Hygiene Doubts:** Inability to know whether kitchens are clean and food is prepared in sanitary conditions.
  3. **Fake / Scattered Reviews:** Relying on unreliable word-of-mouth or obsolete WhatsApp groups.
  4. **Communication Friction:** Calling or texting multiple numbers just to ask if food is ready or if extra rotis can be added.

* **Tiffin Provider Problems:**
  1. **Lack of Advertising & Outreach:** Small home cooks cannot afford commissions charged by major commercial delivery apps.
  2. **Unpredictable Demand:** Not knowing how many students will eat each day, leading to food wastage or shortages.
  3. **Leave Communication:** Having to send hundreds of individual WhatsApp messages when closed for a festival or emergency.
  4. **Direct Student Relationship:** Wanting direct contact with hostelites to build a loyal customer base.

---

## 3. Main Users & Role-Based Access Control (RBAC)
1. **Student / Customer (`student`):**
   * Searches and filters tiffins by area (Dhankawadi, Sarita Vihar, Katraj), meal type (Veg, Non-Veg, Jain), and budget.
   * Views daily menus, prices, and today's kitchen hygiene photo.
   * Receives advance leave notifications if a provider schedules a holiday.
   * Directly chats with tiffin providers.
   * Submits genuine reviews with optional photo proof of their meal.
   * Subscribes to monthly mess cards or trial packages.

2. **Tiffin Provider / Mess (`provider`):**
   * Manages daily menu (adds, edits, deletes dishes, and sets prices).
   * Uploads daily kitchen and food preparation hygiene photos.
   * Schedules advance leave notices (start date, end date, reason) which automatically notifies all connected students.
   * Tracks customer count and views non-sensitive student subscriber details.
   * Chats directly with students and answers meal inquiries.
   * Publishes promotional announcements and discount advertisements.

---

## 4. Key Features
* **Role-Based Authentication:** Secure JWT-based registration and login with bcrypt password hashing.
* **Provider Discovery & Filtering:** Real-time search by location, dietary preference, max price, and availability.
* **Daily Hygiene Proof:** Providers post daily kitchen cleanliness photos with timestamps and honest disclaimers (transparent proof, not a laboratory certification).
* **Advance Leave Pre-Notice & Alert Broadcast:** Providers schedule leaves with reasons; all connected students instantly receive alerts.
* **Direct Student-Provider Chat:** Seamless HTTP polling communication (refreshes every 3 seconds) with read receipts and timestamps.
* **Genuine Weekly Ratings with Meal Proof:** Prevents rating spam (1 review per 24 hours) and allows students to upload photos of their actual meal box.
* **Active Customer Count:** Displays live student subscription counts so providers can accurately forecast grocery purchases.
* **Promotional Advertisements:** Local providers publish semester deals, festival sweets, or discounts directly on the student feed.

---

## 5. Technology Stack
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+)
* **Backend:** Python 3, FastAPI, Uvicorn
* **Database:** PostgreSQL (with SQLAlchemy ORM)
* **Data Validation:** Pydantic v2
* **Authentication:** PyJWT, Passlib / Bcrypt
* **Architecture:** Monolithic REST API + Static Single-Origin Serving

---

## 6. Why HTML, CSS, and Vanilla JavaScript?
* **Simplicity & Understandability:** No complex React build tools, Webpack bundles, or `node_modules` required.
* **Direct DOM Control:** Standard JavaScript `fetch()` and `localStorage` are straightforward to explain during viva.
* **Fast Performance:** Pure browser-native HTML/CSS loads instantly on any computer or mobile browser.
* **Longevity:** Pure web standards remain readable and maintainable for any second-year student.

---

## 7. Why FastAPI?
* **High Performance:** Built on Starlette and Pydantic, making it one of the fastest Python frameworks.
* **Automatic OpenAPI / Swagger Documentation:** Automatically generates live interactive API documentation at `/docs`.
* **Built-in Type Checking & Validation:** Reduces backend bugs by enforcing request and response models via Pydantic.
* **Beginner-Friendly:** Clear routing with Python decorators (`@app.get()`, `@app.post()`).

---

## 8. Why PostgreSQL?
* **Relational Integrity:** Perfect for relational data like users, providers, menus, subscriptions, and messages connected via Foreign Keys.
* **ACID Compliance:** Ensures transactions (like subscriptions or reviews) are safe and never partially written.
* **Industry Standard:** Demonstrates industry-grade SQL database knowledge for second-year student engineering portfolios.

---

## 9. Why SQLAlchemy?
* **Object Relational Mapper (ORM):** Maps Python classes (`User`, `Provider`, `MenuItem`) directly to PostgreSQL database tables.
* **SQL Injection Prevention:** Uses parameterized queries automatically, preventing malicious database injection attacks.
* **Clean Code:** Avoids messy raw SQL strings scattered throughout router files.
* **Portability:** Can connect to PostgreSQL in production and safely fall back to local SQLite if PostgreSQL service is paused during local testing.

---

## 10. Folder Structure
```text
cep-tiffin-services/
├── backend/                  # FastAPI Application
│   ├── main.py               # Main application entry, CORS, and static file mounts
│   ├── database.py           # PostgreSQL / SQLAlchemy connection engine & session
│   ├── models.py             # Database table definitions (SQLAlchemy ORM)
│   ├── schemas.py            # Input/output schemas and validation (Pydantic)
│   ├── auth_utils.py         # Password hashing (bcrypt) and JWT verification
│   ├── seed_data.py          # Realistic Pune demo data (Dhankawadi, Sarita Vihar)
│   └── routers/              # Modular API endpoints
│       ├── auth.py           # Registration, login, and user profile info
│       ├── providers.py      # Provider listing, filtering, stats, subscriptions
│       ├── menu.py           # Dishes and thali CRUD operations
│       ├── ratings.py        # Reviews, weekly ratings, and meal proof uploads
│       ├── hygiene.py        # Daily kitchen hygiene updates
│       ├── availability.py   # Leave pre-notices and student alert broadcasts
│       ├── advertisements.py # Marketing banners and discounts
│       ├── chat.py           # Direct messaging and conversation threads
│       └── notifications.py  # User notifications and alerts
│
├── frontend/                 # Clean, responsive user interface
│   ├── index.html            # Landing page with CEP research story and featured messes
│   ├── login.html            # Dual login page with one-click demo credentials
│   ├── register.html         # Role-based sign up (Student vs Provider)
│   ├── student-dashboard.html# Discovery, search, filters, and subscriptions
│   ├── provider-dashboard.html# Kitchen dashboard (menus, hygiene, leaves, customers)
│   ├── provider-profile.html # Detailed tiffin profile with reviews and order buttons
│   ├── chat.html             # Direct student-to-provider messaging window
│   ├── css/
│   │   ├── style.css         # Theme colors, navbar, hero, cards, and toasts
│   │   ├── dashboard.css     # Stats cards, tables, modal dialogs, and chat layout
│   │   └── responsive.css    # Mobile, tablet, and desktop layout adjustments
│   └── js/
│       ├── api.js            # Central API client, JWT injection, and toast alerts
│       ├── auth.js           # Form submission handlers for login and registration
│       ├── student.js        # Filtering, discovery cards, and subscription modal
│       ├── provider.js       # Menu CRUD, hygiene upload, leave scheduling
│       └── chat.js           # Polling chat engine (updates every 3 seconds)
│
├── uploads/                  # Local storage for uploaded photos
│   ├── hygiene/              # Daily kitchen hygiene proofs
│   ├── advertisements/       # Promotional banners
│   └── ratings/              # Student meal proof photos
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # Project setup and execution guide
├── test_app.py               # 20 automated end-to-end system tests
└── PROJECT_EXPLANATION.md    # This viva guide
```

---

## 11. Purpose of Every Major File
* `backend/main.py`: Creates the FastAPI application, mounts uploads and frontend static directories, registers API routers, and seeds the database.
* `backend/database.py`: Establishes the database engine, creates session factories, and defines `get_db()`.
* `backend/models.py`: Defines the relational database tables using SQLAlchemy ORM.
* `backend/schemas.py`: Defines the input validation and response schemas using Pydantic.
* `backend/auth_utils.py`: Manages bcrypt password hashing and JWT token encoding/decoding.
* `backend/seed_data.py`: Seeds realistic Pune provider and student data so the platform is ready for demonstration.
* `frontend/js/api.js`: Handles all HTTP communication between the browser and backend, storing the JWT token in `localStorage`.
* `frontend/js/chat.js`: Manages the direct chat conversations and messages with automatic polling every 3 seconds.
* `test_app.py`: Contains 20 comprehensive automated tests validating the entire application from registration to chat.

---

## 12. Database Tables
1. `users`: Stores login credentials, hashed password, role (`student` or `provider`), email, and phone number.
2. `students`: Stores student college name, hostel area, and meal preferences.
3. `providers`: Stores tiffin service name, owner name, address, area, base meal prices, and leave dates.
4. `menu_items`: Stores daily dishes, thali descriptions, category (Veg/Non-Veg/Jain), meal type, price, and availability.
5. `ratings`: Stores star ratings (1-5), review text, optional meal verification photo, and timestamp.
6. `hygiene_updates`: Stores daily kitchen/utensil photo paths, descriptions, timestamps, and disclaimers.
7. `availability_logs`: Keeps an audit trail of provider availability changes.
8. `advertisements`: Stores promotional announcements, banner images, and validity dates.
9. `customer_subscriptions`: Tracks subscribed students per provider, yielding an accurate **Customer Count**.
10. `conversations`: Represents a direct chat thread between one student and one provider.
11. `messages`: Stores individual chat messages, timestamps, and read receipts.
12. `notifications`: Stores user notifications (leave alerts, new messages, reviews).

---

## 13. Database Relationships
* `users.id` 1-to-1 with `students.user_id`
* `users.id` 1-to-1 with `providers.user_id`
* `providers.id` 1-to-Many with `menu_items.provider_id`
* `providers.id` 1-to-Many with `ratings.provider_id`
* `students.id` 1-to-Many with `ratings.student_id`
* `providers.id` 1-to-Many with `hygiene_updates.provider_id`
* `providers.id` 1-to-Many with `advertisements.provider_id`
* `providers.id` 1-to-Many with `customer_subscriptions.provider_id`
* `students.id` 1-to-Many with `conversations.student_id`
* `providers.id` 1-to-Many with `conversations.provider_id`
* `conversations.id` 1-to-Many with `messages.conversation_id`

---

## 14. Key API Endpoints
* **Auth:**
  * `POST /api/auth/register` — Create student or provider account
  * `POST /api/auth/login` — Authenticate and return JWT token
  * `GET /api/auth/me` — Get current logged-in user profile
* **Providers:**
  * `GET /api/providers` — Search and filter providers (area, price, cuisine, availability)
  * `GET /api/providers/{id}` — Full provider profile details
  * `PUT /api/providers/current/me` — Provider updates profile
  * `GET /api/providers/dashboard/stats` — Metrics for provider dashboard
  * `GET /api/providers/dashboard/customers` — Active customer directory
  * `POST /api/providers/{id}/subscribe` — Student subscribes to tiffin
* **Menu:**
  * `GET /api/providers/{id}/menu` — List menu items
  * `POST /api/providers/menu` — Provider adds new dish
  * `PUT /api/menu/{id}` — Provider edits dish
  * `DELETE /api/menu/{id}` — Provider removes dish
* **Hygiene:**
  * `GET /api/providers/{id}/hygiene/today` — Today's hygiene update
  * `POST /api/providers/hygiene` — Provider uploads daily hygiene photo
* **Availability & Leave:**
  * `GET /api/providers/{id}/availability` — Check availability and leave notice
  * `POST /api/providers/availability` — Provider updates status and broadcasts alert
* **Chat:**
  * `GET /api/conversations` — List conversations
  * `POST /api/conversations` — Start or open conversation
  * `GET /api/conversations/{id}/messages` — Get conversation message history
  * `POST /api/conversations/{id}/messages` — Send direct message
* **Ratings:**
  * `GET /api/providers/{id}/ratings` — List ratings and calculate weekly averages
  * `POST /api/providers/{id}/ratings` — Student submits review and meal proof

---

## 15. Frontend → Backend Communication
1. Browser JavaScript initiates an asynchronous `fetch()` call.
2. If the user is logged in, `frontend/js/api.js` automatically attaches the header:  
   `Authorization: Bearer <token>`
3. FastAPI receives the HTTP request on the designated port (8000).
4. FastAPI validates the incoming JSON or form data against the Pydantic schema in `backend/schemas.py`.
5. If invalid, FastAPI immediately returns an HTTP 422 or 400 error with descriptive messages.
6. If valid, the router executes business logic and returns a JSON response.
7. JavaScript receives the JSON and updates the DOM dynamically without reloading the entire page.

---

## 16. Backend → Database Communication
1. In `backend/database.py`, `create_engine` creates a connection pool to PostgreSQL.
2. In the router function, FastAPI injects an active database session using the dependency `db: Session = Depends(get_db)`.
3. SQLAlchemy models are queried using Python syntax:  
   `db.query(Provider).filter(Provider.area == "Dhankawadi").all()`
4. SQLAlchemy translates this Python expression into secure SQL:  
   `SELECT * FROM providers WHERE area = 'Dhankawadi';`
5. After creating or updating records, `db.commit()` saves changes to PostgreSQL.
6. The `finally: db.close()` block in `get_db()` ensures database connections are never leaked.

---

## 17. Student Workflow
1. Student opens `index.html` or `student-dashboard.html`.
2. Student types "Dhankawadi" in the search box and selects "Pure Veg".
3. Student sees matching providers like "Annapurna Tiffin Services".
4. Student clicks **"View Profile"** to inspect dishes, pricing, today's hygiene photo, and ratings.
5. Student clicks **"💬 Chat with Cook"** to ask if extra chapatis can be added.
6. Student clicks **"🍲 Subscribe"** and selects "Monthly Lunch & Dinner" with hostel room details.
7. After eating, student submits a 5-star review with a photo proof of the meal box.

---

## 18. Provider Workflow
1. Provider logs in via `login.html` and lands on `provider-dashboard.html`.
2. Provider checks the **Customer Count** metric card to see active student orders.
3. Provider navigates to **"Menu Management"** to add a special Sunday dish.
4. Provider takes a photo of their sanitized kitchen and uploads it in **"Daily Hygiene Update"**.
5. When going on leave, provider sets leave dates and message under **"Availability & Leave Notice"**, alerting students in advance.
6. Provider opens **"Student Messages"** to reply to student inquiries.

---

## 19. Common Errors and Solutions
* **Error:** `OperationalError: connection to localhost:5432 failed`  
  **Solution:** PostgreSQL service is not started. Start PostgreSQL service in Windows Services or run `net start postgresql-x64-16`. The app also has automatic SQLite fallback so testing is never interrupted.
* **Error:** `401 Unauthorized / Token Expired`  
  **Solution:** JWT token in `localStorage` has expired. Log in again via `login.html`.
* **Error:** `403 Forbidden`  
  **Solution:** A student tried to perform a provider-only action (e.g. adding a menu item) or vice-versa. Log in with the appropriate role.

---

## 20. Suggested Viva Questions & Beginner-Friendly Answers

**Q1: What is the main community problem this project addresses?**  
*Answer:* Many college hostel students in areas like Dhankawadi and Sarita Vihar struggle to find predictable, hygienic daily meals, while local home cooks and small tiffin providers struggle with advertising, unpredictable customer counts, and sudden leave communications. Our project bridges this gap directly without commercial commissions.

**Q2: Why did your team choose FastAPI instead of Django or Flask?**  
*Answer:* FastAPI is lightweight, extremely fast, provides automatic input validation via Pydantic, and generates interactive Swagger API documentation automatically. Unlike Django, it avoids unnecessary bloat for a student project.

**Q3: How do you prevent password theft if the database is exposed?**  
*Answer:* Passwords are never stored in plain text. We hash all passwords using `bcrypt` with a unique cryptographic salt before saving them in the database. When a user logs in, we compare the entered password with the stored hash using `bcrypt.checkpw()`.

**Q4: How does role-based access control (RBAC) work in your backend?**  
*Answer:* When a user logs in, their role (`student` or `provider`) is encoded into a signed JWT token. In FastAPI, our `require_role("provider")` dependency checks this token on protected endpoints. If a student tries to add a menu item, the server returns an HTTP 403 Forbidden status.

**Q5: How does your direct chat work without complex WebSockets?**  
*Answer:* We store chat messages in the database. When the chat screen is open, our JavaScript uses lightweight HTTP polling every 3 seconds to fetch new messages. This is simple, reliable, and avoids the complexity of WebSocket connection state management.

**Q6: What is the significance of the "Daily Hygiene Update" feature?**  
*Answer:* In our student survey, hygiene was a major concern for hostelites. Providers can upload a daily photo of their sanitized kitchen counters and food prep. We explicitly label it as provider-submitted proof so students can see transparency without claiming false scientific certifications.

**Q7: How does the Advance Leave Pre-Notice help students?**  
*Answer:* Tiffin aunties occasionally close for family functions or emergencies. By entering their leave dates and reason in advance, our backend automatically broadcasts notification alerts to all subscribed students so they can arrange alternative meals without panic.
