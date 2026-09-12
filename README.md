# Freelancify 🚀 — Modern Freelance Marketplace & Developer Showcase Platform

![Freelancify Banner](https://img.shields.io/badge/Django-5.0+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![WebSockets](https://img.shields.io/badge/Channels-WebSockets-010101?style=for-the-badge&logo=socketdotio&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**Freelancify** is a feature-packed, modern freelance marketplace and developer portfolio showcase web application built with **Django**, **Django Channels (WebSockets)**, and a custom **Obsidian Dark Mode UI Design System**.

It bridges the gap between clients looking for tech talent and freelancers showcasing their services, portfolio projects, and skills.

---

## 🌟 Key Highlights & Features

### 👤 1. Multi-Role Authentication & Access Control
- **Three User Roles**: Client, Freelancer/Developer, and Administrator.
- **Dedicated Onboarding**: Seamless registration flow allowing users to choose their role (`CLIENT` vs `FREELANCER`).
- **Profile Completion Metric**: Dynamic calculation tracking profile completeness (skills, rate, bio, photo, social links).

### 👨‍💻 2. Rich Developer Profiles & Portfolios
- **Detailed Developer Cards**: Photo, full name, professional title, bio, location, hourly rate (`₹/hr` or `$`), experience level, and education background.
- **Availability Badges**: Real-time status indicators (*Available for hire*, *Busy*, *Not accepting requests*).
- **Portfolio Showcase**: High-resolution project visual cards with taggable tech stacks (`React`, `Django`, `Python`, `PostgreSQL`).
- **Interactive Live Demo Sandbox Modal**: Clicking `[Live Demo]` opens an in-app interactive staging environment modal rather than external redirects, complete with live status checks and direct developer contact triggers.

### 🔎 3. Freelancer & Project Discovery Engine
- **Full-Text Search**: Search developers by name, professional title, skill set, or technology.
- **Multi-Parameter Filtering**: Filter developers by experience (e.g., *2+ years*), hourly rate range, availability, and specific technical skills (e.g., *Python*, *React*, *Django*).
- **Favorites System**: Clients can 1-click save developers to their "Saved Developers" list.

### 💼 4. Direct Hiring & Project Request Workflow
- **Service Listings**: Freelancers can offer fixed-price packaged services with delivery turnarounds.
- **Hiring Request Modal**: Clients can request custom projects directly from developer profiles specifying budget, deadline, required technologies, and project scope.
- **Stateful Workflow**: Lifecycle tracking across `PENDING`, `ACCEPTED`, `REJECTED`, and `COMPLETED` statuses.

### 💬 5. Real-Time Chat & Messaging System
- **WebSockets via ASGI/Channels**: Real-time instant messaging between clients and developers with dynamic unread message counts.
- **HTTP/AJAX Fallback**: Robust fallback ensuring uninterrupted messaging in non-WebSocket environments.
- **Contextual Links**: Initiate chat threads directly from developer profiles or project requests.

### 📊 6. Role-Specific Dashboards
- **Freelancer Dashboard**: Tracks Active Project Requests, Completed Projects, Total Services Offered, Profile Completion Rate, and Client Reviews.
- **Client Dashboard**: Manages Sent Requests, Active Projects, Hired Developers, Saved Favorites, and Recent Transactions.

### 💳 7. Payments & PDF Invoice Generation
- **Payment Processing**: Simulated Stripe checkout experience for funded requests and milestones.
- **Automated PDF Invoices**: Built-in PDF generator powered by **ReportLab** allowing users to download official transaction receipts directly from their dashboard.

### 🛡️ 8. Admin Control Panel
- Manage platform users, approve developer profiles, monitor service listings, resolve disputes, and maintain categories/skills taxonomy.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Framework** | Django 5.x | Core Python Web Framework & ORM |
| **Real-time Server** | Django Channels + Daphne | ASGI WebSocket handling for live chat |
| **Database** | SQLite / PostgreSQL | Relational storage for users, jobs, chat, & contracts |
| **PDF Engine** | ReportLab | Programmatic PDF invoice generation |
| **Frontend** | HTML5, CSS3, JavaScript | Custom Obsidian Dark Mode CSS & FontAwesome icons |
| **Task Engine** | Django Management Commands | Data seeding and administrative tasks |

---

## 📁 Directory & Project Structure

```
Freelancify_Project/
├── freelancify/               # Django Core Settings & Routing
│   ├── settings.py            # Apps, Database, ASGI/WSGI, Static & Media setup
│   ├── urls.py                # Main project routing table
│   ├── asgi.py                # ASGI & WebSockets routing configuration
│   └── wsgi.py                # Standard WSGI deployment entry point
│
├── users/                     # User Management & Developer Profiles App
│   ├── models.py              # CustomUser, Profile, Skill, Favorite, Notification
│   ├── views.py               # Login, Register, Profile Detail, Edit, Favorites
│   ├── forms.py               # Custom registration & profile editing forms
│   └── context_processors.py  # Global navbar badges (unread notifications & messages)
│
├── jobs/                      # Projects, Portfolios, Services & Requests App
│   ├── models.py              # Category, Job, Service, PortfolioProject, ProjectRequest
│   ├── views.py               # Portfolio showcase, Project details, Project Request flow
│   └── management/commands/   # Custom management commands (`seed_data.py`)
│
├── chat/                      # Real-time Messaging App
│   ├── models.py              # Conversation, Message
│   ├── consumers.py           # Django Channels WebSocket Consumer (`ChatConsumer`)
│   ├── routing.py             # WebSocket URL patterns (`ws/chat/<room>/`)
│   └── views.py               # Inbox & AJAX chat view handlers
│
├── contracts/                 # Hiring Contracts & Reviews App
│   └── models.py              # Contract, WorkSubmission, Review
│
├── payments/                  # Payment Transactions & PDF Invoices App
│   ├── models.py              # Transaction model
│   ├── utils.py               # ReportLab PDF invoice generator (`generate_invoice_pdf`)
│   └── views.py               # Payment checkout & invoice download views
│
├── dashboard/                 # Client & Freelancer Unified Dashboards
│   └── views.py               # Home view (`/`) & Role-based Dashboard view (`/dashboard/`)
│
├── templates/                 # Modular Django HTML Templates
│   ├── base.html              # Global navigation, dark mode styling & Live Demo modal
│   ├── home.html              # Modern Hero, Search, Categories & Showcase landing page
│   ├── users/                 # Profile detail, developer search, login, signup templates
│   ├── jobs/                  # Project showcase & project request templates
│   ├── chat/                  # Real-time chat inbox & thread templates
│   └── dashboard/             # Role-specific dashboard templates
│
├── static/                    # CSS, JavaScript & Global Assets
├── media/                     # User uploaded avatars, project images & resumes
├── db.sqlite3                 # Local SQLite database
├── manage.py                  # Django CLI manager
├── requirements.txt           # Python dependencies
└── README.md                  # Project overview documentation
```

---

## ⚡ Quick Start & Local Setup

### 1. Prerequisites
- **Python 3.11+** installed on your system.
- `pip` & `virtualenv` (recommended).

### 2. Clone repository & create virtual environment
```bash
git clone <repository-url>
cd Freelancify_Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py makemigrations users jobs contracts chat payments
python manage.py migrate
```

### 5. Seed Test Data & Demo Accounts
Run the seed command to automatically populate skills, categories, developer profiles (including **Rahul Kumar**), portfolio projects, services, and test chat conversations:
```bash
python manage.py seed_data
```

### 6. Start the Development Server
To run with full WebSocket real-time chat support:
```bash
python manage.py runserver 8000
```
Or run directly via ASGI:
```bash
daphne -p 8000 freelancify.asgi:application
```

Access the platform in your browser at: **`http://127.0.0.1:8000/`**

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username | Password | Key Highlights |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Full access to Django Admin Panel (`/admin/`) |
| **Freelancer** | `rahul_kumar` | `pass123` | **Rahul Kumar** — Full Stack Dev (React, Django, Python, PostgreSQL, ₹800/hr) |
| **Freelancer** | `dev_master` | `pass123` | **David Chen** — Senior Python Architect (₹1200/hr) |
| **Client** | `techcorp` | `pass123` | **Sarah Jenkins (TechCorp)** — Active hiring requests & saved developers |

---

## 🧪 Running Unit & Integration Tests

Verify system health and test suites across all Django apps:
```bash
python manage.py test
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more details.
