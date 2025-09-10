# 🐳 Soleva Environment Setup Guide

## 📋 Overview

This guide helps you set up a local development environment for the Soleva project using Docker. The setup includes PostgreSQL, Redis, Django Backend, React Frontend, and supporting services.

## 🔧 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository
- **At least 4GB RAM** available for Docker

## 🚀 Quick Start

### Step 1: Create Environment File

Choose the method that matches your operating system:

#### 🪟 Windows
```bash
# Run the setup script
setup-env.bat
```

#### 🐧 Linux/Mac
```bash
# Make script executable and run
chmod +x setup-env.sh
./setup-env.sh
```

### Step 2: Start Services

```bash
# Start all services in detached mode
docker compose up -d

# Or start specific services
docker compose up -d postgres redis backend
```

### Step 3: Verify Setup

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f

# Check specific service logs
docker compose logs -f backend
```

## 📁 Environment Variables

The `.env` file contains all necessary configuration:

### 🗄️ Database (PostgreSQL)
```env
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=Soleva@2025
DB_HOST=postgres
DB_PORT=5432
```

### 🔄 Redis
```env
REDIS_PASSWORD=Redis@2025
```

### 🔧 Backend (Django)
```env
SECRET_KEY=dev-django-secret-key-for-local-development-min-50-chars-recommended-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*
```

### 📧 Email (Development)
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@localhost
EMAIL_HOST_PASSWORD=dev-email-password
DEFAULT_FROM_EMAIL=noreply@localhost
```

## 🔌 Service Ports

| Service    | Internal Port | External Port | Description              |
|------------|---------------|---------------|--------------------------|
| PostgreSQL | 5432         | 5432         | Database                |
| Redis      | 6379         | 6379         | Cache/Message Broker    |
| Backend    | 8000         | -            | Django API              |
| Frontend   | 80           | -            | React App              |
| Nginx      | 80/443       | 80/443       | Reverse Proxy           |

## 🛠️ Useful Commands

### Docker Compose Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Rebuild and restart
docker compose up -d --build

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend

# Execute commands in containers
docker compose exec backend python manage.py shell
docker compose exec postgres psql -U soleva_user -d soleva_db
```

### Database Management

```bash
# Access PostgreSQL
docker compose exec postgres psql -U soleva_user -d soleva_db

# Create Django migrations
docker compose exec backend python manage.py makemigrations

# Run Django migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

### Frontend Development

```bash
# Access frontend container
docker compose exec frontend sh

# Install new dependencies
docker compose exec frontend npm install <package-name>

# Run frontend build
docker compose exec frontend npm run build
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :5432  # Windows
lsof -i :5432                 # Linux/Mac

# Stop conflicting service or change port in docker-compose.yml
```

#### 2. Database Connection Failed
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres

# Reset database (⚠️ This will delete all data)
docker compose down -v
docker compose up -d postgres
```

#### 3. Redis Connection Failed
```bash
# Check Redis logs
docker compose logs redis

# Test Redis connection
docker compose exec redis redis-cli -a Redis@2025 ping
```

#### 4. Backend Not Starting
```bash
# Check backend logs
docker compose logs backend

# Check if database is ready
docker compose exec postgres pg_isready -U soleva_user -d soleva_db

# Run database migrations
docker compose exec backend python manage.py migrate
```

### Service Health Checks

```bash
# Check all service health
docker compose ps

# Check specific service health
docker compose exec backend curl -f http://localhost:8000/health/
```

## 🔒 Security Notes

- **Never commit** the `.env` file to version control
- The `.env` file is automatically added to `.gitignore`
- Use strong passwords in production
- Rotate secrets regularly
- Use environment-specific configurations

## 📊 Monitoring

### View Service Status
```bash
docker compose ps
```

### Resource Usage
```bash
docker stats
```

### Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

## 🧹 Cleanup

### Stop and Remove Everything
```bash
# Stop services
docker compose down

# Remove volumes (⚠️ This deletes all data)
docker compose down -v

# Remove images
docker compose down --rmi all

# Complete cleanup
docker system prune -a --volumes
```

## 📞 Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review service logs: `docker compose logs -f`
3. Verify environment variables in `.env`
4. Ensure Docker has sufficient resources
5. Check firewall settings for required ports

## 🎯 Next Steps

After successful setup:

1. Access the application at `http://localhost`
2. Create a Django superuser for admin access
3. Configure your IDE for development
4. Set up database backups
5. Review security configurations for production

---

**Happy coding! 🚀**
