# SmartSeason

A field monitoring web application for tracking crop progress across multiple farm fields during a growing season. Administrators manage fields and agents, while field agents log observations and stage updates for their assigned fields.

Built with Django, plain CSS, vanilla JavaScript, and MySQL.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Demo Credentials](#demo-credentials)
- [Design Notes](#design-notes)

---

## Features

- Role-based access control with two user types: Admin and Field Agent
- Admins can create, assign, edit, and delete fields and manage user accounts
- Field agents can view and log updates only on fields assigned to them
- Computed field status (Active, At Risk, Completed) based on crop stage and update history
- Full update history per field, acting as an audit trail
- Responsive layout with mobile sidebar navigation

---

## Project Structure

```
smartseason/
├── smartseason/               Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  Custom user model, login, user management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── fields/                    Core application: fields and updates
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── core/
│   └── management/
│       └── commands/
│           └── seed_data.py   Populates the database with demo data
├── templates/
│   ├── base.html
│   ├── accounts/
│   └── fields/
├── static/
│   ├── css/main.css
│   └── js/main.js
├── manage.py
├── requirements.txt
└── .env
```

---

## Prerequisites

- Python 3.10 or newer
- MySQL 8.0 or newer, installed and running
- pip

---

## Local Setup

### 1. Create the database

Open a MySQL prompt and run:

```sql
CREATE DATABASE smartseason_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Create a virtual environment

```bash
cd smartseason
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (alongside `manage.py`) with the following:

```
SECRET_KEY=your-secret-key-here
DB_NAME=smartseason_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

### 5. Run migrations

```bash
python manage.py makemigrations accounts fields
python manage.py migrate
```

### 6. Load demo data

```bash
python manage.py seed_data
```

This creates sample users and fields so the application can be explored immediately after setup.

### 7. Configure static files

In `settings.py`, ensure this line reads:

```python
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 8. Start the development server

```bash
python manage.py runserver
```

The application will be available at https://web-production-2235c.up.railway.app/ (My deployment on Railway)

---

## Demo Credentials

These accounts are created by the `seed_data` command.

| Role         | Username | Password      |
|--------------|----------|-----------    |
| Admin        | Lerroy   | smartadmin123 |
| Field Agent  | Oscar    | smartuser123  |
| Field Agent  | Milly    | smartuser123  |

---

## Design Notes

### User Roles and Access Control

The built-in Django `AbstractUser` model is extended with a single `role` field. Two roles exist: `admin` and `field_agent`. A custom `admin_required` decorator enforces role checks at the view level, returning HTTP 403 for unauthorised access. Field agents are additionally restricted so they can only view or update fields where they are the assigned agent. This is enforced in the view logic, not just in templates.

### Field Status

Status is a computed property on the `Field` model and is never stored in the database. It is recalculated on each access from the field's current data. The rules applied in order are:

1. **Completed** — the field's current stage is Harvested
2. **At Risk** — the expected harvest date has passed and the crop is not yet harvested, or no update has been logged in the past 7 days
3. **Active** — all other cases

### Update History

Every time an agent logs an update, a `FieldUpdate` record is created with the timestamp, the agent, the crop stage at that time, and their observations. This forms an immutable log of activity for each field. The field's `current_stage` is kept in sync with the most recent update automatically.

### Frontend Approach

All pages are server-rendered Django templates. No JavaScript framework is used. Vanilla JavaScript handles only UI behaviour such as the mobile navigation menu and dismissible alert messages. The application is fully functional with JavaScript disabled.