# Soleva Unified Docker Deployment Guide

## 🚀 Quick Start

### Production Deployment
```bash
# 1. Clone and setup environment
git clone <repository-url>
cd soleva
cp .env.example .env
# Edit .env with your production values

# 2. Start all services
docker compose up -d

# 3. Initialize SSL certificates
docker compose run --rm certbot

# 4. Verify deployment
docker compose ps
curl -f http://your-domain.com/health
```

### Development Setup
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with development values (or use docker.env)

# 2. Start development environment
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 3. Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

## 📋 Architecture Overview

### Unified Services
- **PostgreSQL**: Database with persistent storage
- **Redis**: Cache and message broker for Celery
- **Django Backend**: API server with health checks
- **Celery Worker**: Background task processing
- **Celery Beat**: Scheduled task management
- **React Frontend**: Vite-built SPA with Nginx
- **Nginx**: Unified reverse proxy with SSL termination
- **Certbot**: Automated SSL certificate management

### Network Architecture
```
Internet → Nginx (80/443) → Backend (8000) | Frontend (80)
                          ↓
                    PostgreSQL (5432) + Redis (6379)
                          ↓
                    Celery Worker + Beat
```

## 🔧 Configuration Management

### Environment Variables
All configuration is centralized in `.env` file:

```bash
# Domain & SSL
DOMAIN=your-domain.com
SSL_EMAIL=admin@your-domain.com

# Database
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=secure-password

# Redis
REDIS_PASSWORD=secure-redis-password

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### SSL Certificate Setup

#### Initial Certificate Generation
```bash
# Make sure Nginx is running first
docker compose up -d nginx

# Generate certificates
docker compose run --rm certbot
```

#### Automatic Renewal
```bash
# Make renewal script executable
chmod +x scripts/ssl-renew.sh

# Add to crontab for automatic renewal
crontab -e
# Add: 0 3 * * 0 /path/to/soleva/scripts/ssl-renew.sh
```

#### Manual Renewal
```bash
# Renew certificates manually
./scripts/ssl-renew.sh

# Or using Docker Compose
docker compose --profile renewal run --rm certbot-renew
docker compose exec nginx nginx -s reload
```

## 🛠 Management Commands

### Service Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart backend

# View logs
docker compose logs -f backend
docker compose logs -f nginx

# Check service status
docker compose ps
```

### Database Management
```bash
# Run Django migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Collect static files
docker compose exec backend python manage.py collectstatic --noinput

# Database backup
docker compose exec postgres pg_dump -U $DB_USER $DB_NAME > backup.sql
```

### Development Workflow
```bash
# Start development environment
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Access development services
# Frontend with HMR: http://localhost:5173
# Backend API: http://localhost:8000/api
# Django Admin: http://localhost:8000/admin

# View development logs
docker compose logs -f frontend
docker compose logs -f backend
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoints
- **Overall Health**: `https://your-domain.com/health`
- **Backend API**: `https://your-domain.com/api/health/`
- **Frontend**: `https://your-domain.com/` (React app)

### Service Status
```bash
# Check all services
docker compose ps

# Check specific service health
docker compose exec backend curl -f http://localhost:8000/api/health/
docker compose exec frontend curl -f http://localhost/health
```

### Log Monitoring
```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f celery

# View last 100 lines
docker compose logs --tail=100 backend
```

## 🚨 Troubleshooting

### Common Issues

#### SSL Certificate Problems
```bash
# Check certificate status
docker compose exec nginx openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -text -noout

# Regenerate certificates
docker compose run --rm certbot --force-renewal

# Check Nginx configuration
docker compose exec nginx nginx -t
```

#### Database Connection Issues
```bash
# Check database connectivity
docker compose exec backend python manage.py dbshell

# Check PostgreSQL logs
docker compose logs postgres

# Reset database (CAUTION: Data loss!)
docker compose down
docker volume rm soleva_postgres_data
docker compose up -d
```

#### Service Communication Issues
```bash
# Check network connectivity
docker compose exec backend ping postgres
docker compose exec backend ping redis

# Check port bindings
docker compose ps
netstat -tlnp | grep :80
netstat -tlnp | grep :443
```

### Performance Optimization

#### Database Optimization
```bash
# Run database maintenance
docker compose exec backend python manage.py optimize_db

# Check database performance
docker compose exec postgres psql -U $DB_USER -d $DB_NAME -c "SELECT * FROM pg_stat_activity;"
```

#### Cache Management
```bash
# Clear Redis cache
docker compose exec redis redis-cli FLUSHALL

# Check Redis memory usage
docker compose exec redis redis-cli INFO memory
```

## 🔒 Security Considerations

### SSL/TLS Configuration
- Automatic HTTPS redirects
- HSTS headers enabled
- Modern TLS configuration
- Automatic certificate renewal

### Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: enabled
- Content Security Policy configured

### Access Control
- Rate limiting on API endpoints
- Admin interface protection
- CORS properly configured
- Static file security

## 📊 Backup & Recovery

### Database Backup
```bash
# Create backup
docker compose exec postgres pg_dump -U $DB_USER $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker compose exec -T postgres psql -U $DB_USER -d $DB_NAME < backup.sql
```

### Volume Backup
```bash
# Backup all volumes
docker run --rm -v soleva_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
docker run --rm -v soleva_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

## 🎯 Best Practices

1. **Environment Management**: Always use `.env` files, never commit secrets
2. **SSL Certificates**: Monitor expiration, test renewal process
3. **Database**: Regular backups, monitor performance
4. **Logs**: Implement log rotation, monitor for errors
5. **Updates**: Test in development before production deployment
6. **Security**: Regular security updates, monitor access logs

## 📞 Support

For issues or questions:
1. Check logs: `docker compose logs -f`
2. Verify configuration: `docker compose config`
3. Check service health: `docker compose ps`
4. Review this guide for troubleshooting steps

---

**Note**: This unified setup eliminates the need for separate Docker configurations and provides a single command deployment experience: `docker compose up -d`
