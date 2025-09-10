# 🐳 Docker Setup Guide for Soleva Platform

Complete Docker containerization setup for production deployment.

## 📋 Overview

This setup includes:
- **Backend**: Django REST API with Gunicorn
- **Frontend**: React SPA with Nginx
- **Database**: PostgreSQL with persistence
- **Cache/Queue**: Redis for caching and Celery
- **Reverse Proxy**: Nginx with SSL termination
- **SSL**: Let's Encrypt certificates with auto-renewal
- **Monitoring**: Health checks and logging
- **Backup**: Automated backup system

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Environment Setup
```bash
# Copy environment template
cp docker.env.example .env

# Edit with your configuration
nano .env
```

### 3. Deploy Platform
```bash
# Make scripts executable (Linux/Mac)
chmod +x scripts/*.sh

# Deploy everything
./scripts/deploy.sh
```

## 🗂️ Docker Architecture

### Services Overview

| Service | Purpose | Port | Health Check |
|---------|---------|------|--------------|
| `postgres` | Database | 5432 | `pg_isready` |
| `redis` | Cache/Queue | 6379 | `redis-cli ping` |
| `backend` | Django API | 8000 | `/api/health/` |
| `celery` | Background tasks | - | `celery inspect` |
| `celery-beat` | Task scheduler | - | - |
| `frontend` | React app | 80 | `/health` |
| `nginx` | Reverse proxy | 80/443 | `/health` |
| `certbot` | SSL management | - | - |

### Volume Mapping

| Volume | Purpose | Backup | Retention |
|--------|---------|--------|-----------|
| `postgres_data` | Database storage | ✅ | Persistent |
| `redis_data` | Cache storage | ❌ | Persistent |
| `static_volume` | Django static files | ❌ | Persistent |
| `media_volume` | User uploads | ✅ | Persistent |
| `letsencrypt_certs` | SSL certificates | ✅ | Persistent |
| `nginx_logs` | Web server logs | ❌ | Rotated |

## ⚙️ Configuration Files

### 1. Backend Configuration

**`soleva back end/Dockerfile`**
- Multi-stage build for optimization
- Security: Non-root user
- Health checks for monitoring
- Production-ready Gunicorn setup

**`soleva back end/docker-entrypoint.sh`**
- Database migration automation
- Static file collection
- Superuser creation
- Gunicorn with optimal settings

**`soleva back end/requirements.txt`**
- All Python dependencies
- Production versions pinned
- Security-focused packages

### 2. Frontend Configuration

**`soleva front end/Dockerfile`**
- Multi-stage build (Node.js + Nginx)
- Optimized asset serving
- Security headers
- Gzip compression

**`soleva front end/nginx.conf`**
- SPA routing support
- Asset caching strategies
- Security headers
- Health check endpoint

### 3. Nginx Reverse Proxy

**`nginx/nginx.conf`**
- Global Nginx configuration
- Performance optimizations
- Security settings
- Rate limiting

**`nginx/conf.d/soleva.conf`**
- Site-specific configuration
- SSL termination
- Domain redirects (301)
- API/Frontend routing

**`nginx/conf.d/ssl.conf`**
- SSL security settings
- Modern cipher suites
- OCSP stapling
- HSTS headers

### 4. Docker Compose

**`docker-compose.yml`**
- Complete service orchestration
- Health checks for all services
- Named volumes for persistence
- Environment variable injection
- Service dependencies

## 🔐 SSL Certificate Management

### Automatic Certificate Obtaining
```bash
# Included in deployment script
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email admin@solevaeg.com \
  --agree-tos \
  --no-eff-email \
  -d solevaeg.com \
  -d www.solevaeg.com
```

### Manual Certificate Renewal
```bash
# Test renewal
docker-compose run --rm certbot renew --dry-run

# Force renewal
docker-compose run --rm certbot renew --force-renewal

# Reload Nginx
docker-compose exec nginx nginx -s reload
```

### Auto-Renewal Setup
```bash
# Add to crontab
echo "0 2 * * * /var/www/soleva-platform/scripts/ssl-renew.sh" | crontab -
```

## 📊 Monitoring and Health Checks

### Health Check Endpoints

**Backend Health Check**
```bash
curl -f http://localhost:8000/api/health/
# Returns: {"status": "healthy", "checks": {...}}
```

**Frontend Health Check**
```bash
curl -f http://localhost/health
# Returns: "healthy"
```

**Service Status**
```bash
docker-compose ps
# Shows all service statuses
```

### Log Management

**View Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 nginx
```

**Log Rotation**
```bash
# Add to crontab for log rotation
echo "0 1 * * * docker run --rm -v soleva_nginx_logs:/logs alpine find /logs -name '*.log' -type f -mtime +7 -delete" | crontab -
```

## 🔄 Deployment Commands

### Initial Deployment
```bash
./scripts/deploy.sh
```

### Update Deployment
```bash
./scripts/deploy.sh update
```

### Service Management
```bash
# Restart specific service
docker-compose restart backend

# Scale services
docker-compose up -d --scale backend=2

# View resource usage
docker stats

# Stop all services
docker-compose down
```

## 💾 Backup and Recovery

### Automated Backup
```bash
# Manual backup
./scripts/backup.sh

# Schedule daily backups (3 AM)
echo "0 3 * * * /var/www/soleva-platform/scripts/backup.sh" | crontab -
```

### Backup Contents
- Database dump (compressed)
- Media files (payment proofs, product images)
- Configuration files
- SSL certificates

### Recovery Process
```bash
# Extract backup
tar -xzf soleva_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore database
gunzip -c database.sql.gz | docker-compose exec -T postgres psql -U soleva_user soleva_db

# Restore media files
docker cp media/ soleva_backend:/app/
```

## 🔧 Development vs Production

### Development Setup
```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up -d

# Enable debug mode
echo "DEBUG=True" >> .env
```

### Production Optimizations
- Debug mode disabled
- Static file serving optimized
- Database connection pooling
- Redis caching enabled
- Gunicorn with multiple workers
- Nginx gzip compression
- Security headers enabled

## 🌐 Domain Configuration

### Primary Domain Setup
1. Point DNS A record: `solevaeg.com` → Your server IP
2. Point DNS A record: `www.solevaeg.com` → Your server IP

### Redirect Domains
All alternate domains redirect to primary:
- `soleva.shop` → `https://solevaeg.com`
- `soleva.vip` → `https://solevaeg.com`
- `sole-va.com` → `https://solevaeg.com`

### DNS Configuration Example
```
A     solevaeg.com         YOUR_SERVER_IP
A     www.solevaeg.com     YOUR_SERVER_IP
A     soleva.shop           YOUR_SERVER_IP
A     www.soleva.shop       YOUR_SERVER_IP
A     soleva.vip            YOUR_SERVER_IP
A     www.soleva.vip        YOUR_SERVER_IP
A     sole-va.com           YOUR_SERVER_IP
A     www.sole-va.com       YOUR_SERVER_IP
```

## 🚨 Troubleshooting

### Common Issues

**1. SSL Certificate Fails**
```bash
# Check DNS propagation
dig solevaeg.com

# Test port 80 accessibility
curl -I http://solevaeg.com/.well-known/acme-challenge/test

# View certbot logs
docker-compose logs certbot
```

**2. Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U soleva_user

# View database logs
docker-compose logs postgres

# Reset database (⚠️ Data loss)
docker-compose down -v
docker-compose up -d postgres
```

**3. Service Won't Start**
```bash
# Check service logs
docker-compose logs [service_name]

# Rebuild service
docker-compose build --no-cache [service_name]

# Check resource usage
docker system df
```

**4. Performance Issues**
```bash
# Monitor resource usage
docker stats

# Check disk space
df -h

# Clean up Docker resources
docker system prune -f
```

## 📈 Performance Tuning

### Database Optimization
```sql
-- Monitor query performance
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- Optimize frequently used queries
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### Nginx Optimization
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
client_max_body_size 50M;
```

### Redis Optimization
```bash
# Monitor Redis performance
docker-compose exec redis redis-cli INFO stats

# Set memory limit
docker-compose exec redis redis-cli CONFIG SET maxmemory 512mb
```

## 🔒 Security Considerations

### Network Security
- Services communicate via internal Docker network
- Only necessary ports exposed (80, 443)
- Rate limiting configured in Nginx
- SQL injection protection via ORM

### Application Security
- CSRF protection enabled
- XSS protection headers
- Secure cookie settings
- JWT token expiration
- Input validation and sanitization

### Infrastructure Security
- Non-root containers
- Read-only file systems where possible
- Secret management via environment variables
- Regular security updates

### Security Headers
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

## 📋 Maintenance Tasks

### Daily
- Check service health (`docker-compose ps`)
- Monitor disk space (`df -h`)
- Review error logs

### Weekly
- Clean up Docker resources (`docker system prune`)
- Check backup integrity
- Update security patches

### Monthly
- Update Docker images
- Review performance metrics
- Test disaster recovery procedures
- Security audit

---

## ✅ Production Checklist

Before going live, ensure:

- [ ] Environment variables configured
- [ ] SSL certificates obtained and valid
- [ ] Backup system tested and working
- [ ] Health checks responding
- [ ] Domain redirects working
- [ ] Analytics tracking configured
- [ ] Payment gateways tested
- [ ] Email delivery working
- [ ] Error monitoring setup
- [ ] Performance benchmarks established

---

Your Soleva platform is now ready for production deployment! 🚀

The Docker setup provides a robust, scalable, and secure foundation for your e-commerce platform with automated deployments, SSL management, and comprehensive monitoring.
