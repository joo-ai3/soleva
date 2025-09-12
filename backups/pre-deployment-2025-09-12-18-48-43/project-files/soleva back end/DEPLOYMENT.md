# 🚀 Soleva E-commerce Backend - Deployment Guide

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js (for frontend integration)

## 🔧 Environment Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd soleva-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**

```env
# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=soleva_production
DB_USER=soleva_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payments
PAYMOB_API_KEY=your-paymob-api-key
PAYMOB_SECRET_KEY=your-paymob-secret
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Analytics
FACEBOOK_PIXEL_ID=your-pixel-id
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb soleva_production

# Run migrations
python manage.py migrate

# Run setup script
python scripts/setup.py
```

### 4. Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Create media directories
mkdir -p media/products media/categories media/brands
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python scripts/setup.py
```

### Production Docker Setup

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: soleva_production
      POSTGRES_USER: soleva_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 soleva_backend.wsgi:application
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    environment:
      - DEBUG=0
      - DATABASE_URL=postgres://soleva_user:${DB_PASSWORD}@db:5432/soleva_production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    restart: unless-stopped

  celery:
    build: .
    command: celery -A soleva_backend worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A soleva_backend beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

## 🌐 Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:8000;
    }

    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;

        location / {
            proxy_pass http://app;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $host;
            proxy_redirect off;
        }

        location /static/ {
            alias /var/www/static/;
        }

        location /media/ {
            alias /var/www/media/;
        }

        client_max_body_size 100M;
    }
}
```

## 🔐 SSL/HTTPS Setup

### Using Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 2. Health Checks

```bash
# Health check endpoint
curl http://your-domain.com/api/auth/health/

# Database check
python manage.py check --database default

# Redis check
redis-cli ping
```

## 🔄 Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump soleva_production > backups/db_backup_$DATE.sql

# Keep only last 7 days
find backups/ -name "db_backup_*.sql" -mtime +7 -delete
```

### Media Files Backup

```bash
# Sync media files to S3
aws s3 sync media/ s3://your-bucket/media/

# Or use rsync for local backup
rsync -av media/ /backup/media/
```

## 🚀 Deployment Checklist

### Pre-deployment

- [ ] Update environment variables
- [ ] Run tests: `python manage.py test`
- [ ] Check migrations: `python manage.py showmigrations`
- [ ] Backup database
- [ ] Update requirements.txt if needed

### Deployment Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Install/update dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart nginx

# 6. Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### Post-deployment

- [ ] Check application health
- [ ] Verify API endpoints
- [ ] Test payment integration
- [ ] Monitor error logs
- [ ] Update DNS if needed

## 🔧 Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX CONCURRENTLY idx_orders_created_at ON orders(created_at);
CREATE INDEX CONCURRENTLY idx_products_category ON products(category_id);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

### 2. Redis Configuration

```redis
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
```

## 🛡️ Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Set secure headers
- [ ] Configure CORS properly
- [ ] Use strong passwords
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup encryption

## 📱 API Documentation

The API documentation is available at:
- Swagger UI: `http://your-domain.com/swagger/`
- ReDoc: `http://your-domain.com/redoc/`

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -U soleva_user -d soleva_production
   ```

2. **Redis Connection Error**
   ```bash
   # Check Redis status
   sudo systemctl status redis
   
   # Test connection
   redis-cli ping
   ```

3. **Static Files Not Loading**
   ```bash
   # Recollect static files
   python manage.py collectstatic --clear --noinput
   
   # Check nginx configuration
   sudo nginx -t
   ```

4. **Celery Workers Not Processing**
   ```bash
   # Check worker status
   celery -A soleva_backend inspect active
   
   # Restart workers
   sudo systemctl restart celery
   ```

### Logs Location

- Application: `/app/logs/django.log`
- Nginx: `/var/log/nginx/access.log`
- PostgreSQL: `/var/log/postgresql/`
- Redis: `/var/log/redis/`

## 📞 Support

For deployment support:
- Documentation: [Link to docs]
- Issues: [Link to issue tracker]
- Email: tech@soleva.com

---

**Note**: Always test deployments in a staging environment before production!
