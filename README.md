# Backend - Django REST API

## Overview
Django REST framework backend for the Truck Container Damage Detection System. Handles damage detection processing and API endpoints.

## Prerequisites
- Python 3.10+
- pip/conda package manager

## Installation

### 1. Install Dependencies
```bash
pip install django djangorestframework django-cors-headers
```

### 2. Database Setup (SQLite - Default)
The project uses SQLite for development. No additional setup needed.

### 3. Migrations (Optional)
```bash
python manage.py makemigrations
python manage.py migrate
```

## Running the Server

Start the development server on port 9000:
```bash
python manage.py runserver 9000
```

The API will be available at: `http://localhost:9000`

## Project Structure
```
Backend/
├── core_api/           # Main Django configuration
│   ├── settings.py     # Settings & database config
│   ├── urls.py         # Main URL routing
│   └── wsgi.py         # WSGI application
├── damage_detection/   # Damage detection app
│   ├── views.py        # API endpoints
│   ├── urls.py         # App routing
│   └── utils/          # ML pipeline utilities
│       ├── yolo_damage.py
│       └── pipeline.py
└── manage.py           # Django management script
```

## API Endpoints
- Coming soon - see `damage_detection/views.py`

## Configuration
Edit `core_api/settings.py` to:
- Change database (currently SQLite)
- Add/remove installed apps
- Configure CORS origins (default: localhost:5173)

## Future: MySQL Setup
When ready to use MySQL:
1. Install: `pip install mysqlclient`
2. Update `DATABASES` in `core_api/settings.py` with MySQL credentials
3. Run migrations