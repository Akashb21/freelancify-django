# 📘 Freelancify — Comprehensive Project & Architecture Guide

Welcome to the **Freelancify Project Guide**. This document provides an end-to-end, detailed breakdown of the application architecture, user workflows, database schema relationships, interactive component mechanics, and codebase mapping to help developers, administrators, and reviewers fully understand the entire project.

---

## 📑 Table of Contents
1. [Project Overview & Core Mission](#1-project-overview--core-mission)
2. [High-Level Architecture & Technology Stack](#2-high-level-architecture--technology-stack)
3. [End-to-End User Workflows & Journey Maps](#3-end-to-end-user-workflows--journey-maps)
4. [Database Schema & Data Model Relationships](#4-database-schema--data-model-relationships)
5. [Key Feature Implementations Deep-Dive](#5-key-feature-implementations-deep-dive)
6. [Functional Requirements Traceability Matrix](#6-functional-requirements-traceability-matrix)
7. [Developer Operations & Maintenance Guide](#7-developer-operations--maintenance-guide)

---

## 1. Project Overview & Core Mission

**Freelancify** is a full-stack, modern web application designed to connect clients seeking software development services with verified freelancers and developers.

### Primary Goals:
* **Showcase Developer Portfolios**: Give developers a rich, glassmorphic space to display their skills, experience, packages, and interactive project live demos.
* **Streamline Discovery**: Enable clients to find developers easily using advanced multi-filter search (skills, hourly rates, experience, availability).
* **Direct Hiring Workflow**: Facilitate direct project requests, negotiations, stateful status tracking (`PENDING` ➔ `ACCEPTED` ➔ `COMPLETED`), and reviews.
* **Real-Time Communication**: Offer instant live chat via WebSockets backed by ASGI/Django Channels.

---

## 2. High-Level Architecture & Technology Stack

Freelancify follows Django's clean **MVT (Model-View-Template)** architecture augmented with **ASGI WebSockets** for asynchronous real-time capabilities.

```
                  ┌──────────────────────────────────────────────┐
                  │                 CLIENT BROWSER               │
                  │   HTML5 / Custom Dark CSS / JavaScript ES6   │
                  └──────┬───────────────────────────────┬───────┘
                         │                               │
                HTTP / HTTPS                     WebSocket (ws://)
                         │                               │
                         ▼                               ▼
                  ┌──────────────┐               ┌──────────────┐
                  │  WSGI Server │               │  ASGI Server │
                  │  (Gunicorn)  │               │   (Daphne)   │
                  └──────┬───────┘               └──────┬───────┘
                         │                              │
                         ▼                              ▼
             ┌─────────────────────────────────────────────────────┐
             │                   DJANGO BACKEND                    │
             │                                                     │
             │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
             │  │  users   │  │   jobs   │  │  chat (Channels) │  │
             │  └──────────┘  └──────────┘  └──────────────────┘  │
             │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
             │  │ contracts│  │ payments │  │    dashboard     │  │
             │  └──────────┘  └──────────┘  └──────────────────┘  │
             └──────────────────────────┬──────────────────────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │  SQLite / Postgres  │
                             │  Relational DB      │
                             └─────────────────────┘
```

### Stack Breakdown:
* **Backend Core**: Django 5.0+ (Python 3.11+) handles business logic, URL routing, authentication, ORM database operations, forms, and template rendering.
* **Real-time Engine**: `channels` + `daphne` (ASGI) powering real-time chat via WebSockets (`ChatConsumer`).
* **Document Generation**: `reportlab` library generating programmatic PDF invoices for completed transactions.
* **Database**: SQLite (default for development/testing) or PostgreSQL (production-ready).
* **Frontend Design System**: Custom Obsidian dark mode CSS (`base.html`), HSL-tailored cyan/indigo accent glows, glassmorphism, responsive grid layouts, FontAwesome 6 icons, and zero heavy third-party CSS dependencies.

---

## 3. End-to-End User Workflows & Journey Maps

### 🅰️ Client Journey: Hiring a Developer

```
[1. Land on Home Page] ──► [2. Search Developers / Projects]
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────┐
│ [3. View Developer Profile (e.g., Rahul Kumar)]             │
│ - Inspect Skills, Experience, Rate (₹800/hr), Bio           │
│ - Preview Portfolio Projects & Click [Live Demo] Modal      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
     ┌──────────────────────────────────────────────────┐
     │ [4. Click "Hire Me / Send Project Request"]      │
     │ - Enter Title, Tech Stack, Budget & Deadline     │
     └─────────────────────────┬────────────────────────┘
                               │
                               ▼
     ┌──────────────────────────────────────────────────┐
     │ [5. Real-Time Chat & Discussion]                 │
     │ - Communicate via /chat/ with instant messaging  │
     └─────────────────────────┬────────────────────────┘
                               │
                               ▼
     ┌──────────────────────────────────────────────────┐
     │ [6. Status Acceptance & Payment]                 │
     │ - Developer accepts request (PENDING ➔ ACCEPTED) │
     │ - Client views contract & downloads PDF Invoice  │
     └─────────────────────────┬────────────────────────┘
                               │
                               ▼
     ┌──────────────────────────────────────────────────┐
     │ [7. Work Completion & Review]                    │
     │ - Request marked COMPLETED                       │
     │ - Client leaves 5-Star Rating & Review           │
     └──────────────────────────────────────────────────┘
```

### 🅱️ Developer Journey: Showcasing & Earning

1. **Register as Freelancer**: Select `FREELANCER` during signup.
2. **Build Profile**: Add professional title (*Full Stack Developer*), hourly rate (`₹800`), bio, availability status, experience (*2+ years*), education (*B.Tech CS*), and skills taxonomy tags.
3. **Publish Portfolio Projects & Services**:
   - Add projects with GitHub links, description, and technology tags.
   - Package fixed-price services (e.g. *Full Stack Web App - ₹15,000*).
4. **Manage Requests**:
   - Receive notifications when a client submits a project request.
   - Accept or decline requests from the **Freelancer Dashboard**.
5. **Collaborate & Submit Work**: Chat with clients, deliver project artifacts, and receive reviews to boost rating average.

---

## 4. Database Schema & Data Model Relationships

The data layer consists of 5 interconnected Django applications:

```
 ┌──────────────┐         1:1         ┌──────────────┐
 │  CustomUser  ├────────────────────►│   Profile    │
 └──────┬───────┘                     └──────┬───────┘
        │                                    │
        │ 1:N (Sender/Receiver)              │ M:N via Profile.skills
        ▼                                    ▼
 ┌──────────────┐                     ┌──────────────┐
 │   Message    │                     │    Skill     │
 └──────┬───────┘                     └──────────────┘
        │
        │ N:1                                1:N
        ▼                                 ┌──┴───────────┐
 ┌──────────────┐                         ▼              ▼
 │ Conversation │               ┌───────────┐  ┌───────────────┐
 └──────────────┘               │  Service  │  │PortfolioProject│
                                └───────────┘  └───────────────┘
```

### Key Models & Fields:

1. **`users.CustomUser`**:
   - Inherits `AbstractUser`. Adds `role` (`CLIENT`, `FREELANCER`, `ADMIN`), `phone`, `location`, `profile_picture`.
2. **`users.Profile`**:
   - OneToOne with `CustomUser`. Stores `title`, `bio`, `hourly_rate`, `currency`, `experience`, `education`, `availability`, `github_link`, `linkedin_link`, `resume`, `rating_average`, `rating_count`.
3. **`users.Favorite`**:
   - Tracks saved developers (`client` ForeignKey to `CustomUser`, `freelancer` ForeignKey to `CustomUser`).
4. **`jobs.Job` & `jobs.Category`**:
   - Traditional job postings with budget, category slug, requirements, and linked `Proposal` submissions.
5. **`jobs.Service`**:
   - Fixed-price developer service packages (`title`, `description`, `starting_price`, `delivery_days`, `technologies`).
6. **`jobs.PortfolioProject`**:
   - Developer showcase items (`title`, `description`, `image`, `technologies`, `github_url`, `demo_url`, `role_description`).
7. **`jobs.ProjectRequest`**:
   - Direct client-to-freelancer hiring requests (`client`, `freelancer`, `title`, `description`, `budget`, `deadline_days`, `status`: `PENDING`, `ACCEPTED`, `REJECTED`, `COMPLETED`).
8. **`chat.Conversation` & `chat.Message`**:
   - Thread between 2 users (`participant1`, `participant2`). Messages store `sender`, `content`, `timestamp`, `is_read`.
9. **`payments.Transaction`**:
   - Tracks payment activity (`user`, `amount`, `payment_method`, `status`, `stripe_payment_id`, `timestamp`).

---

## 5. Key Feature Implementations Deep-Dive

### 5.1 Interactive Live Demo Staging Sandbox Modal
* **Location**: Defined globally in `templates/base.html` and triggered via JavaScript `openDemoModal(...)`.
* **Mechanism**: When a user clicks `[Live Demo]` on a portfolio card:
  1. A modal slides in over the page with backdrop blur.
  2. JavaScript dynamically populates the project title, simulated staging URL (`https://staging.freelancify.dev/preview/...`), tech badges, and creator details.
  3. Clicking "Contact Creator to Request Live Walkthrough" closes the modal and redirects directly to `/chat/?user_id=<creator_id>`.

### 5.2 Real-Time WebSocket Chat with Fallback
* **ASGI Consumer**: `chat/consumers.py` (`ChatConsumer`).
* **WebSocket Route**: `ws/chat/<room_name>/`.
* **Fallback**: `chat/views.py` provides standard AJAX endpoints (`send_message_ajax` & `get_messages_ajax`) so chat functions seamlessly even if WebSockets are blocked by proxies or firewalls.

### 5.3 Programmatic PDF Invoice Generation
* **Location**: `payments/utils.py` (`generate_invoice_pdf`).
* **Mechanism**: Uses **ReportLab** `SimpleDocTemplate`, `Paragraph`, `Table`, and `Drawing` canvas shapes to programmatically draw a sleek branded PDF invoice with line items, total calculation, transaction ID, and branding.

---

## 6. Functional Requirements Traceability Matrix

Every single functional requirement from the specification is fully implemented and mapped to codebase files:

| Spec Section | Requirement Name | Implemented Codebase Files |
|---|---|---|
| **#1 & #2** | Purpose & User Roles | `users/models.py` (`CustomUser.ROLE_CHOICES`), `users/views.py` |
| **#3** | Authentication & Signup | `users/views.py` (`register_view`, `login_view`), `users/forms.py` |
| **#4** | Freelancer Profile & Rahul Kumar Spec | `users/models.py` (`Profile`), `jobs/management/commands/seed_data.py` |
| **#5 & #22** | Portfolio Showcase & Live Demo | `jobs/models.py` (`PortfolioProject`), `templates/base.html` (`openDemoModal`) |
| **#6 & #7** | Developer Discovery & Filters | `users/views.py` (`freelancer_list_view`), `templates/users/freelancer_list.html` |
| **#9** | Package Services | `jobs/models.py` (`Service`), `users/views.py` (`profile_detail_view`) |
| **#10 & #12**| Project Requests & Hiring | `jobs/models.py` (`ProjectRequest`), `jobs/views.py` (`create_project_request`) |
| **#11** | Client-Developer Chat | `chat/models.py`, `chat/consumers.py`, `templates/chat/inbox.html` |
| **#13 & #14**| Freelancer & Client Dashboards | `dashboard/views.py` (`dashboard_view`), `templates/dashboard/` |
| **#15** | Saved Developers / Favorites | `users/models.py` (`Favorite`), `users/views.py` (`toggle_favorite`) |
| **#16** | Reviews & Ratings | `contracts/models.py` (`Review`), `users/models.py` (`Profile.rating_average`) |
| **#17** | Notification System | `users/models.py` (`Notification`), `users/context_processors.py` |
| **#18** | Admin Management Panel | `freelancify/urls.py` (`/admin/`), standard Django Admin models |
| **#19** | Modern Home Page | `dashboard/views.py` (`home_view`), `templates/home.html` |
| **#24 & #25**| Categories & Skills Taxonomy | `jobs/models.py` (`Category`), `users/models.py` (`Skill`), `seed_data.py` |

---

## 7. Developer Operations & Maintenance Guide

### Re-seeding the Database
To reset and re-seed clean test data at any time:
```bash
python manage.py flush --no-input
python manage.py seed_data
```

### Running Automated Test Suite
Ensure zero regressions across all components:
```bash
python manage.py test
```

### Customizing UI & Glassmorphism Theme
The design tokens are centralized in `templates/base.html` inside the `<style>` block:
* `--bg-dark`: `#0B0F19` (Obsidian background)
* `--accent-cyan`: `#06B6D4` (Primary interactive cyan)
* `--accent-indigo`: `#6366F1` (Gradient indigo glow)
* `--card-bg`: `rgba(17, 24, 39, 0.7)` (Glassmorphism backdrop container)

---

*This guide completes the architectural overview of Freelancify.*
