# Backend - Django REST API

## Overview
Django REST framework backend for the Truck Container Damage Detection System. Handles damage detection processing and API endpoints.

## Prerequisites
- Python 3.10+
- pip/conda package manager

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

For local development you can keep:

```env
DEBUG=True
```

For production, set strong values:

```env
DEBUG=False
SECRET_KEY=<long-random-django-secret>
API_KEY=<long-random-api-key>
ALLOWED_HOSTS=your-domain.example.com
CORS_ALLOWED_ORIGINS=https://your-frontend.example.com
SECURE_SSL_REDIRECT=True
```

The expensive ML/OCR endpoints require the `X-API-Key` header when `API_KEY` is set. The frontend can send this by setting:

```env
VITE_API_KEY=<same-api-key>
```

### 3. Database Setup (SQLite - Default)
The project uses SQLite for development. No additional setup needed.

### 4. Migrations (Optional)
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
Use `.env` to configure:

- `DEBUG`
- `SECRET_KEY`
- `API_KEY`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `MAX_IMAGE_UPLOAD_BYTES`
- `MAX_IMAGE_PIXELS`
- `MAX_IMAGE_WIDTH`
- `MAX_IMAGE_HEIGHT`
- `DETECT_THROTTLE_RATE`
- `OCR_THROTTLE_RATE`

Security defaults include:

- API-key protection for `/api/detect/` and `/api/ocr-container/`
- request throttling for ML/OCR endpoints
- upload size, MIME type, and image dimension validation
- production startup failure when required secrets are missing
- safer security headers and cookie flags

## Future: MySQL Setup
When ready to use MySQL:
1. Install: `pip install mysqlclient`
2. Update `DATABASES` in `core_api/settings.py` with MySQL credentials
3. Run migrations
