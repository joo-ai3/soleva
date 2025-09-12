# Manual Installation Guide for Soleva Platform

## Overview
This guide provides steps to deploy Soleva without Docker, in case of Docker registry connectivity issues.

## Prerequisites
- Windows Server or Windows 10/11
- Administrator access
- Internet connectivity (for downloading packages)

## Step 1: Install PostgreSQL

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install with these settings:
   - Port: 5432
   - Database: soleva_db
   - Username: soleva_user
   - Password: Soleva@2025

## Step 2: Install Redis

1. Download Redis for Windows from https://github.com/microsoftarchive/redis/releases
2. Install and configure:
   - Port: 6379
   - Password: Redis@2025

## Step 3: Install Python 3.11

1. Download Python 3.11 from https://www.python.org/downloads/
2. Install with "Add to PATH" option
3. Verify: `python --version`

## Step 4: Install Node.js

1. Download Node.js LTS from https://nodejs.org/
2. Install with default settings
3. Verify: `node --version` and `npm --version`

## Step 5: Deploy Backend

```bash
cd "soleva back end"
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

## Step 6: Deploy Frontend

```bash
cd "soleva front end"
npm install
npm run build
# Serve the build folder using a web server like nginx or IIS
```

## Step 7: Install and Configure Nginx

1. Download nginx for Windows from http://nginx.org/en/download.html
2. Extract to C:\nginx
3. Copy our nginx configuration files
4. Start nginx: `nginx.exe`

## Step 8: Configure SSL Certificates

1. Download certbot for Windows
2. Run: `certbot certonly --webroot --webroot-path=C:\nginx\html --email support@solevaeg.com -d solevaeg.com -d www.solevaeg.com`
3. Configure nginx with SSL certificates

## Environment Configuration

Create `.env` file in backend directory:
```
SECRET_KEY=django-insecure-change-this-in-production-soleva-production-key-2025
DEBUG=False
ALLOWED_HOSTS=solevaeg.com,www.solevaeg.com,localhost,127.0.0.1
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=Soleva@2025
DB_HOST=localhost
DB_PORT=5432
REDIS_PASSWORD=Redis@2025
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@solevaeg.com
EMAIL_HOST_PASSWORD=?3aeeSjqq
```

## Services Management

Create Windows services for:
1. PostgreSQL (usually auto-installed)
2. Redis
3. Django backend (using gunicorn or similar)
4. Celery worker
5. Celery beat
6. Nginx

## Firewall Configuration

Open ports:
- 80 (HTTP)
- 443 (HTTPS)
- 5432 (PostgreSQL) - internal only
- 6379 (Redis) - internal only
- 8000 (Django) - internal only

## Monitoring and Logs

- Backend logs: Check Django logs
- Frontend logs: Check nginx access/error logs
- Database logs: Check PostgreSQL logs
- Redis logs: Check Redis logs

## Troubleshooting

1. **Database Connection Issues**: Check PostgreSQL service and credentials
2. **Redis Connection Issues**: Check Redis service and password
3. **Static Files**: Ensure collectstatic is run and nginx can serve files
4. **SSL Issues**: Verify certificate paths and permissions
5. **Port Conflicts**: Check that required ports are not in use

## Backup Strategy

1. Database: Use pg_dump for PostgreSQL backups
2. Media files: Regular file system backups
3. Configuration: Backup nginx and application configs

## Performance Optimization

1. Use gunicorn for Django in production
2. Configure nginx caching
3. Optimize database queries
4. Use Redis for caching
5. Enable gzip compression

This manual approach gives you full control over the deployment but requires more system administration knowledge.
