# 🌱 SmartSeason — Field Monitoring System

A web application for tracking crop progress across multiple fields during a growing season.

Built with **Django** (server-side rendering), **plain CSS**, **vanilla JavaScript**, and **PostgreSQL**.

---

## Demo Credentials

After running `seed_data` (see setup below):

| Role            | Username | Password  |
|-----------------|----------|-----------|
| Admin/Coord.    | `admin`  | `admin123`|
| Field Agent 1   | `agent1` | `agent123`|
| Field Agent 2   | `agent2` | `agent123`|

---

## Project Structure

```
smartseason/               ← project root
├── smartseason/           ← Django project config (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/              ← Custom User model, login, user management
│   ├── models.py          ← User with role field (admin / field_agent)
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── fields/                ← Core app: Field + FieldUpdate models
│   ├── models.py          ← Field (with computed status), FieldUpdate
│   ├── views.py           ← Dashboard, CRUD, log update
│   ├── forms.py
│   └── urls.py
├── core/                  ← Shared utilities
│   └── management/
│       └── commands/
│           └── seed_data.py   ← Creates demo data
├── templates/             ← All HTML templates
│   ├── base.html          ← Navbar, sidebar, flash messages layout
│   ├── accounts/
│   │   ├── login.html
│   │   ├── manage_users.html
│   │   └── confirm_delete_user.html
│   └── fields/
│       ├── admin_dashboard.html
│       ├── agent_dashboard.html
│       ├── field_list.html
│       ├── field_detail.html
│       ├── field_form.html    ← Used for both create and edit
│       ├── log_update.html
│       └── field_confirm_delete.html
├── static/
│   ├── css/main.css       ← All styles (earthy palette, responsive)
│   └── js/main.js         ← Hamburger menu, alerts, active nav
├── requirements.txt
├── manage.py
└── pythonanywhere_wsgi.py ← Paste into PA's WSGI editor
```

---

## Local Setup (Step by Step)

### Prerequisites
- Python 3.10 or newer
- PostgreSQL installed and running
- Git (optional)

### Step 1 — Create the database

Open your PostgreSQL prompt (or pgAdmin) and run:

```sql
CREATE DATABASE smartseason_db;
CREATE USER smartseason_user WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE smartseason_db TO smartseason_user;
```

### Step 2 — Create a virtual environment

```bash
cd smartseason
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure the database

Open `smartseason/settings.py` and update the `DATABASES` section with your
PostgreSQL credentials, OR set environment variables:

```bash
# Windows (Command Prompt)
set DB_NAME=smartseason_db
set DB_USER=smartseason_user
set DB_PASSWORD=your_password_here

# macOS/Linux
export DB_NAME=smartseason_db
export DB_USER=smartseason_user
export DB_PASSWORD=your_password_here
```

### Step 5 — Run migrations

```bash
python manage.py migrate
```

This creates all the database tables.

### Step 6 — Create demo data

```bash
python manage.py seed_data
```

This creates the demo users and 6 sample fields so you can explore the app immediately.

### Step 7 — Collect static files (optional for local dev)

```bash
python manage.py collectstatic
```

### Step 8 — Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## Deploying to PythonAnywhere

PythonAnywhere is a hosting platform that supports Django natively. Here is the full process.

### 1. Create a PythonAnywhere account

Go to https://www.pythonanywhere.com and sign up for a free account.

### 2. Upload your project

In PythonAnywhere, open a **Bash console** and clone or upload your project:

```bash
# Option A — clone from GitHub
git clone https://github.com/yourusername/smartseason.git ~/smartseason

# Option B — upload a zip
# Use the "Files" tab to upload a zip, then unzip it:
unzip smartseason.zip -d ~/smartseason
```

### 3. Create a virtual environment on PythonAnywhere

```bash
cd ~/smartseason
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

PythonAnywhere's **free plan** only includes MySQL. For PostgreSQL you have two options:

**Option A (Recommended for free plan):** Use an external PostgreSQL provider like
[Supabase](https://supabase.com) (free tier) or [Neon](https://neon.tech) (free tier).
They give you a connection string — use the host, port, user, password, and db name
from that string in your settings.

**Option B:** Upgrade to a PythonAnywhere paid plan, which includes PostgreSQL.

### 5. Configure the WSGI file

In PythonAnywhere:
1. Go to the **Web** tab
2. Click **"Add a new web app"** → Manual configuration → Python 3.10
3. Click the **WSGI configuration file** link
4. Replace its entire contents with the contents of `pythonanywhere_wsgi.py`
5. Update `yourusername` and the database credentials in that file
6. Click **Save**

### 6. Configure static files

In the **Web** tab, scroll to "Static files" and add:

| URL      | Directory                                      |
|----------|------------------------------------------------|
| `/static/` | `/home/yourusername/smartseason/staticfiles/` |

Then in your Bash console:

```bash
cd ~/smartseason
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 7. Run migrations on PythonAnywhere

```bash
cd ~/smartseason
source venv/bin/activate
python manage.py migrate
python manage.py seed_data
```

### 8. Reload the web app

Back in the Web tab, click the big green **Reload** button.

Visit `yourusername.pythonanywhere.com` — your app is live!

---

## Design Decisions

### Authentication
- Django's built-in `AbstractUser` is extended with a single `role` field (`admin` or `field_agent`).
- This keeps auth simple — one user table, all of Django's session/password machinery included.
- No third-party auth packages needed.

### Access Control
- A custom `admin_required` decorator (wrapping `@login_required`) checks the role and returns HTTP 403 for non-admins.
- Field agents are further restricted in views: they can only see and update fields where `assigned_to == request.user`.
- This is enforced at the view level, not just the template level, so it cannot be bypassed by navigating directly to a URL.

### Field Status Logic
Status is a **computed property** on the `Field` model — it is never stored in the database. It is recalculated fresh every time it is needed from the field's current data. This avoids stale data.

The three rules, applied in order:

1. **Completed** — `current_stage == 'harvested'`
2. **At Risk** — either:
   - Today is past `expected_harvest_date` and the field is not harvested, OR
   - The last `FieldUpdate` was more than 7 days ago (stale monitoring), OR
   - The field has never been updated and was planted more than 7 days ago
3. **Active** — everything else

### Server-Side Rendering
All HTML is rendered by Django templates on the server. No JavaScript framework. This keeps the codebase simple, fast-loading, and easy to understand. Vanilla JS is used only for UI enhancements (hamburger menu, auto-dismiss alerts) — the app is fully functional with JavaScript disabled.

### Update History as Audit Trail
Every time an agent logs a field update, a `FieldUpdate` record is created with a timestamp, the agent who logged it, the stage at that moment, and their notes. This creates an immutable audit trail. The field's `current_stage` is updated to match the latest update automatically.

---

## Assumptions Made

1. A field can only be assigned to one agent at a time.
2. Admins can also log field updates (useful for coordinators who are also in the field).
3. Deleting a user sets `assigned_to = NULL` on their fields (fields are not deleted).
4. The "At Risk — no update in 7 days" rule applies to all stages except Harvested.
5. The expected harvest date is optional; without it, only the 7-day staleness rule applies.
