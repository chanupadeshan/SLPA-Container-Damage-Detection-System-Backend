# SLPA Container Damage Detection System - Backend

## 🚀 Quick Start

### Run in Terminal:

**Terminal 1 - Start Django:**
```bash
venv\Scripts\activate    
python manage.py runserver 0.0.0.0:9000
```

**Terminal 2 - Start phpMyAdmin:**
```bash
php -S localhost:8080 -t /opt/homebrew/share/phpmyadmin
```

### Access in Browser:

- **Django API**: http://localhost:8000
- **Database (phpMyAdmin)**: http://localhost:8080
  - Username: `root`
  - Password: (leave empty)
  - Database: `slpa_container_detection`

---

## 📋 System Overview

Django REST framework backend for Container Damage Detection using YOLO and MySQL database.

## ⚙️ Tech Stack

- **Framework**: Django 4.2.7 + Django REST Framework
- **Database**: MySQL 9.6.0
- **AI/ML**: PyTorch, Ultralytics YOLO, OpenCV
- **Python**: 3.9+

## Project Structure
```
SLPA-Container-Damage-Detection-System-Backend/
├── core_api/              # Django configuration
│   ├── settings.py        # MySQL database config
│   └── urls.py            # URL routing
├── damage_detection/      # Damage detection app
│   ├── views.py           # API endpoints
│   ├── urls.py           
│   └── utils/
│       ├── pipeline.py    # Detection pipeline
│       └── yolo_damage.py # YOLO model
├── .env                   # Database credentials
├── manage.py              # Django management
└── requirements.txt       # Python dependencies
```

## 🗄️ Database

**MySQL Database**: `slpa_container_detection`

**View in Terminal:**
```bash
mysql -u root slpa_container_detection
```

**View in Browser:**
```bash
# Access phpMyAdmin at: http://localhost:8080
```

## 🛑 Stop Servers

Press `Ctrl + C` in both terminal windows

---

## 📚 Documentation

- **[SIMPLE_START.md](SIMPLE_START.md)** - Quick start guide (recommended)
- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Detailed instructions
- [WINDOWS_SETUP.md](WINDOWS_SETUP.md) - Windows setup guide
- [DATABASE_ACCESS_GUIDE.md](DATABASE_ACCESS_GUIDE.md) - Database access methods

---

**That's all you need to get started!** 🎉
When ready to use MySQL:
1. Install: `pip install mysqlclient`
2. Update `DATABASES` in `core_api/settings.py` with MySQL credentials
3. Run migrations