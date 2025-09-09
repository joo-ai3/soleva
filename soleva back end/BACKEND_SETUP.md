# 🐍 Soleva Django Backend Setup Guide

This is a **Django (Python)** backend, not a Node.js project. Follow these steps to set up and run the backend server.

## 📋 Prerequisites

- **Python 3.11+** installed
- **PostgreSQL** database server
- **Redis** server (for caching and Celery)

## 🚀 Quick Setup

### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Update database credentials, Redis URL, etc.
```

### 4. Database Setup
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
# Start Django development server
python manage.py runserver

# Server will be available at: http://localhost:8000
# Admin panel: http://localhost:8000/admin
# API: http://localhost:8000/api
```

## 🔧 Development Commands

### Database Operations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (DANGER: deletes all data)
python manage.py flush
```

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword <username>
```

### Static Files
```bash
# Collect static files for production
python manage.py collectstatic
```

### Shell Access
```bash
# Django shell
python manage.py shell

# Database shell
python manage.py dbshell
```

## 🐘 PostgreSQL Setup

### Install PostgreSQL
```bash
# Windows: Download from postgresql.org
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql
```

### Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database and user
CREATE DATABASE soleva_db;
CREATE USER soleva_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE soleva_db TO soleva_user;
```

## 🔴 Redis Setup

### Install Redis
```bash
# Windows: Download from redis.io
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis
```

### Start Redis
```bash
# Linux/Mac
redis-server

# Windows: Run redis-server.exe
```

## 🌲 Celery (Background Tasks)

### Start Celery Worker
```bash
# In a new terminal (with venv activated)
celery -A soleva_backend worker -l info
```

### Start Celery Beat (Scheduler)
```bash
# In another terminal (with venv activated)
celery -A soleva_backend beat -l info
```

## 📁 Project Structure

```
soleva back end/
├── soleva_backend/          # Main Django project
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI config
│   └── asgi.py              # ASGI config
├── users/                   # User management app
├── products/                # Product catalog app
├── orders/                  # Order management app
├── cart/                    # Shopping cart app
├── coupons/                 # Discount coupons app
├── notifications/           # Notification system app
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── Dockerfile               # Docker configuration
└── README.md                # Project documentation
```

## 🔧 Environment Variables (.env)

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,thesoleva.com

# Database
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@thesoleva.com

# Payment Gateways
PAYMOB_API_KEY=your-paymob-api-key
PAYMOB_SECRET_KEY=your-paymob-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_SECRET_KEY=sk_test_your-stripe-key

# Analytics
FACEBOOK_PIXEL_ID=your-pixel-id
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
TIKTOK_PIXEL_ID=your-tiktok-pixel
SNAPCHAT_PIXEL_ID=your-snapchat-pixel
```

## 🔗 API Endpoints

Once the server is running, you can access:

- **API Root**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/api/health/
- **Authentication**: http://localhost:8000/api/auth/
- **Products**: http://localhost:8000/api/products/
- **Orders**: http://localhost:8000/api/orders/
- **Cart**: http://localhost:8000/api/cart/

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test orders

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t soleva-backend .
docker run -p 8000:8000 soleva-backend
```

## 🚨 Troubleshooting

### Common Issues

1. **"No module named 'django'"**
   ```bash
   # Activate virtual environment first
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Database connection errors**
   ```bash
   # Check PostgreSQL is running
   psql -U postgres -l
   
   # Verify database credentials in .env
   ```

3. **Redis connection errors**
   ```bash
   # Check Redis is running
   redis-cli ping
   # Should return PONG
   ```

4. **Migration errors**
   ```bash
   # Reset migrations (DANGER: loses data)
   python manage.py migrate --fake-initial
   
   # Or delete migration files and recreate
   rm */migrations/0*.py
   python manage.py makemigrations
   python manage.py migrate
   ```

## 📚 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## ⚡ Quick Start Summary

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

Your Django backend will be running at **http://localhost:8000** 🎉

**Note**: This is a Python/Django project, not Node.js, so you use `pip` and `python manage.py` commands instead of `npm`.
