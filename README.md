# EMS Employee Management System

A Django-based employee management web application for tracking employee records, attendance, leave requests, payroll, and announcements.

## Overview

EMS is a simple internal management system built to help organizations manage employee information and workforce activities in one place. The application provides a dashboard for employees and supports core HR functions such as registration, attendance tracking, leave applications, payroll records, and communication through announcements.

## Features

- Employee registration and profile management
- Secure employee login
- Employee dashboard
- Attendance marking and history viewing
- Leave request submission and tracking
- Company announcements feed
- Payroll management for employees and staff
- Admin access through Django's built-in admin panel

## Tech Stack

- Python
- Django
- SQLite
- HTML, CSS, and Django templates

## Project Structure

```text
EMS/
├── EMS/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── employees/
│   ├── migrations/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── db.sqlite3
├── manage.py
├── requirements.txt
├── venv/
└── README.md
```

## Prerequisites

Before running this project, make sure you have:

- Python 3.10 or later
- pip
- virtual environment support

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd EMS
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

3. Install Django:

```bash
pip install django
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Create a superuser (optional, for admin access):

```bash
python manage.py createsuperuser
```

6. Start the development server:

```bash
python manage.py runserver
```

7. Open the application in your browser:

```text
http://127.0.0.1:8000/
```

## Default Usage

- Visit the homepage to access the main navigation.
- Register an employee through the employee creation flow.
- Log in using the employee email and password.
- Use the dashboard to mark attendance, request leave, view announcements, and review payroll data.
- Access the Django admin panel at:

```text
http://127.0.0.1:8000/admin/
```

## Database

This project uses SQLite by default, which is configured in `EMS/settings.py`.

## Contributing

Contributions are welcome. If you want to improve the project:

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Open a pull request

## License

This project is intended for educational and internal business use. Add your preferred license before publishing publicly.

## Note

This is a practical Django project designed for learning and small-scale employee management workflows. It is suitable as a foundation for expanding into a full HR system.
