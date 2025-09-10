# Soleva E-commerce Platform - Complete Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the Soleva e-commerce platform with the new domain structure and payment proof system.

## Domain Configuration

### Primary Domain: solevaeg.com
- **Frontend**: https://solevaeg.com
- **Backend API**: https://solevaeg.com/api
- **Admin Panel**: https://solevaeg.com/admin

### Redirect Domains
All the following domains should redirect to https://solevaeg.com:
- soleva.shop → https://solevaeg.com
- soleva.vip → https://solevaeg.com
- sole-va.com → https://solevaeg.com
- www.solevaeg.com → https://solevaeg.com

## Server Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 20.04+ or CentOS 8+

### Recommended for Production
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Bandwidth**: Unmetered

## 1. Server Setup and Dependencies

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Required Packages
```bash
# Essential packages
sudo apt install -y nginx postgresql postgresql-contrib redis-server python3-pip python3-venv nodejs npm git certbot python3-certbot-nginx

# Install Node.js 18 (for better frontend performance)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 2. Database Setup

### PostgreSQL Configuration
```bash
# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE soleva_db;
CREATE USER soleva_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE soleva_db TO soleva_user;
ALTER USER soleva_user CREATEDB;
\q
```

### Redis Configuration
```bash
# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
```

## 3. Backend Deployment

### Clone Repository
```bash
cd /var/www
sudo git clone https://github.com/your-repo/soleva-platform.git
sudo chown -R $USER:$USER /var/www/soleva-platform
cd /var/www/soleva-platform/soleva\ back\ end
```

### Python Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Create production environment file
cp env.example .env
nano .env
```

Update the following values in `.env`:
```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,solevaeg.com,www.solevaeg.com,soleva.shop,soleva.vip,sole-va.com

# Database Configuration
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Email Configuration (Update with your SMTP settings)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@solevaeg.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@solevaeg.com

# Payment Configuration
PAYMOB_API_KEY=your-paymob-api-key
PAYMOB_SECRET_KEY=your-paymob-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_SECRET_KEY=your-stripe-secret-key

# Firebase Configuration (for notifications)
FIREBASE_CREDENTIALS=/var/www/soleva-platform/firebase-credentials.json

# Analytics & Tracking
FACEBOOK_PIXEL_ID=your-facebook-pixel-id
GOOGLE_ANALYTICS_ID=your-google-analytics-id
TIKTOK_PIXEL_ID=your-tiktok-pixel-id
SNAPCHAT_PIXEL_ID=your-snapchat-pixel-id
```

### Database Migration
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### Gunicorn Setup
```bash
# Test Gunicorn
gunicorn --bind 0.0.0.0:8000 soleva_backend.wsgi:application

# Create Gunicorn service
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following content:
```ini
[Unit]
Description=gunicorn daemon for Soleva Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/soleva-platform/soleva back end
ExecStart=/var/www/soleva-platform/soleva back end/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/var/www/soleva-platform/soleva back end/soleva_backend.sock \
          soleva_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Start and enable Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

### Celery Setup (for async tasks)
```bash
# Create Celery service
sudo nano /etc/systemd/system/celery.service
```

Add the following content:
```ini
[Unit]
Description=Celery Service for Soleva
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/soleva-platform/soleva back end
ExecStart=/var/www/soleva-platform/soleva back end/venv/bin/celery multi start worker1 \
          -A soleva_backend --pidfile=/var/run/celery/%n.pid \
          --logfile=/var/log/celery/%n%I.log --loglevel=INFO
ExecStop=/var/www/soleva-platform/soleva back end/venv/bin/celery multi stopwait worker1 \
         --pidfile=/var/run/celery/%n.pid
ExecReload=/var/www/soleva-platform/soleva back end/venv/bin/celery multi restart worker1 \
           -A soleva_backend --pidfile=/var/run/celery/%n.pid \
           --logfile=/var/log/celery/%n%I.log --loglevel=INFO

[Install]
WantedBy=multi-user.target
```

```bash
# Create directories for Celery
sudo mkdir /var/run/celery /var/log/celery
sudo chown www-data:www-data /var/run/celery /var/log/celery

# Start and enable Celery
sudo systemctl start celery
sudo systemctl enable celery
```

## 4. Frontend Deployment

### Navigate to Frontend Directory
```bash
cd /var/www/soleva-platform/soleva\ front\ end
```

### Environment Configuration
```bash
cp env.example .env.production
nano .env.production
```

Update with production values:
```bash
VITE_API_BASE_URL=https://solevaeg.com/api
VITE_APP_NAME=Soleva
VITE_NODE_ENV=production

# Analytics & Tracking (Update with real IDs)
VITE_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
VITE_FACEBOOK_PIXEL_ID=123456789
VITE_TIKTOK_PIXEL_ID=XXXXXXXXXX
VITE_SNAPCHAT_PIXEL_ID=XXXXXXXXXX

# Payment Keys
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_XXXXXXXXXX
VITE_PAYMOB_API_KEY=XXXXXXXXXX

# Feature Flags
VITE_ENABLE_GUEST_CHECKOUT=true
VITE_ENABLE_SOCIAL_LOGIN=true
VITE_ENABLE_WISHLIST=true
VITE_ENABLE_REVIEWS=true
VITE_ENABLE_PWA=true
```

### Build Frontend
```bash
# Install dependencies
npm install

# Build for production
npm run build
```

## 5. Nginx Configuration

### Main Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/solevaeg.com
```

Add the following configuration:
```nginx
# Redirect all HTTP to HTTPS
server {
    listen 80;
    server_name solevaeg.com www.solevaeg.com soleva.shop soleva.vip sole-va.com;
    return 301 https://solevaeg.com$request_uri;
}

# Redirect alternate domains to primary domain
server {
    listen 443 ssl http2;
    server_name www.solevaeg.com soleva.shop soleva.vip sole-va.com;
    
    ssl_certificate /etc/letsencrypt/live/solevaeg.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/solevaeg.com/privkey.pem;
    
    return 301 https://solevaeg.com$request_uri;
}

# Main server configuration
server {
    listen 443 ssl http2;
    server_name solevaeg.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/solevaeg.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/solevaeg.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

    # Frontend (React app)
    location / {
        root /var/www/soleva-platform/soleva front end/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/soleva-platform/soleva back end/soleva_backend.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting for API
        limit_req zone=api burst=20 nodelay;
        
        # Specific rate limiting for auth endpoints
        location /api/auth/login/ {
            limit_req zone=login burst=5 nodelay;
            include proxy_params;
            proxy_pass http://unix:/var/www/soleva-platform/soleva back end/soleva_backend.sock;
        }
    }

    # Django Admin
    location /admin/ {
        include proxy_params;
        proxy_pass http://unix:/var/www/soleva-platform/soleva back end/soleva_backend.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (Django)
    location /static/ {
        alias /var/www/soleva-platform/soleva back end/staticfiles/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Media files (uploads)
    location /media/ {
        alias /var/www/soleva-platform/soleva back end/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Robots.txt
    location = /robots.txt {
        alias /var/www/soleva-platform/soleva front end/dist/robots.txt;
    }

    # Sitemap
    location = /sitemap.xml {
        alias /var/www/soleva-platform/soleva front end/dist/sitemap.xml;
    }
}
```

### Enable Site and Test Configuration
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/solevaeg.com /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 6. SSL Certificate Setup

### Obtain SSL Certificates
```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificates for all domains
sudo certbot certonly --standalone -d solevaeg.com -d www.solevaeg.com -d soleva.shop -d soleva.vip -d sole-va.com

# Start Nginx
sudo systemctl start nginx

# Set up automatic renewal
sudo crontab -e
```

Add the following line for automatic renewal:
```bash
0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

## 7. SEO Configuration

### Create robots.txt
```bash
nano /var/www/soleva-platform/soleva\ front\ end/dist/robots.txt
```

```
User-agent: *
Allow: /

# Sitemap
Sitemap: https://solevaeg.com/sitemap.xml

# Disallow admin and API
Disallow: /admin/
Disallow: /api/
```

### Create sitemap.xml
```bash
nano /var/www/soleva-platform/soleva\ front\ end/dist/sitemap.xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://solevaeg.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://solevaeg.com/products</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>https://solevaeg.com/collections</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://solevaeg.com/about</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://solevaeg.com/contact</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>
```

### Update Frontend for Canonical URLs
Update the main index.html to include canonical links:
```html
<link rel="canonical" href="https://solevaeg.com" />
```

## 8. Monitoring and Logging

### Set up Log Rotation
```bash
sudo nano /etc/logrotate.d/soleva
```

```
/var/log/nginx/solevaeg.com.access.log
/var/log/nginx/solevaeg.com.error.log
/var/log/celery/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
```

### Setup System Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Create monitoring script
sudo nano /usr/local/bin/soleva-health-check.sh
```

```bash
#!/bin/bash
# Soleva Health Check Script

# Check services
services=("nginx" "postgresql" "redis-server" "gunicorn" "celery")

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo "✓ $service is running"
    else
        echo "✗ $service is not running"
        systemctl restart $service
    fi
done

# Check disk space
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "Warning: Disk usage is ${disk_usage}%"
fi

# Check memory usage
memory_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
echo "Memory usage: ${memory_usage}%"
```

```bash
chmod +x /usr/local/bin/soleva-health-check.sh

# Add to crontab for regular checks
sudo crontab -e
```

Add:
```bash
*/5 * * * * /usr/local/bin/soleva-health-check.sh >> /var/log/soleva-health.log 2>&1
```

## 9. Security Configuration

### Firewall Setup
```bash
# Install and configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Additional Security Measures
```bash
# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh

# Install fail2ban
sudo apt install -y fail2ban

# Configure fail2ban for Nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
findtime = 600
bantime = 7200
maxretry = 10
```

```bash
sudo systemctl restart fail2ban
```

## 10. Performance Optimization

### Database Optimization
```sql
-- Connect to PostgreSQL and run these optimizations
\c soleva_db

-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_orders_user_created ON orders_order(user_id, created_at);
CREATE INDEX CONCURRENTLY idx_orders_payment_status ON orders_order(payment_status);
CREATE INDEX CONCURRENTLY idx_products_active ON products_product(is_active);
CREATE INDEX CONCURRENTLY idx_products_category ON products_product(category_id);
CREATE INDEX CONCURRENTLY idx_payment_proofs_verification ON order_payment_proofs(verification_status);

-- Update table statistics
ANALYZE;
```

### Redis Optimization
```bash
sudo nano /etc/redis/redis.conf
```

Update these settings:
```
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

```bash
sudo systemctl restart redis-server
```

## 11. Backup Strategy

### Database Backup Script
```bash
sudo nano /usr/local/bin/backup-soleva.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/soleva"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U soleva_user -h localhost soleva_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /var/www/soleva-platform/soleva\ back\ end/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x /usr/local/bin/backup-soleva.sh

# Schedule daily backups
sudo crontab -e
```

Add:
```bash
0 2 * * * /usr/local/bin/backup-soleva.sh >> /var/log/soleva-backup.log 2>&1
```

## 12. Post-Deployment Checklist

### Verify All Services
- [ ] Nginx is running and accessible
- [ ] PostgreSQL is running
- [ ] Redis is running
- [ ] Gunicorn is running
- [ ] Celery is running
- [ ] SSL certificates are installed
- [ ] All domains redirect correctly

### Test Website Functionality
- [ ] Homepage loads correctly
- [ ] Product pages display properly
- [ ] User registration works
- [ ] User login works
- [ ] Cart functionality works
- [ ] Checkout process works
- [ ] Payment proof upload works
- [ ] Admin panel is accessible
- [ ] API endpoints respond correctly

### Analytics and Tracking
- [ ] Google Analytics is tracking
- [ ] Facebook Pixel is firing
- [ ] TikTok Pixel is working
- [ ] Snapchat Pixel is working

### SEO Configuration
- [ ] Canonical URLs are set
- [ ] robots.txt is accessible
- [ ] sitemap.xml is accessible
- [ ] Meta tags are properly set

## 13. Maintenance Commands

### Update Application
```bash
# Update backend
cd /var/www/soleva-platform/soleva\ back\ end
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn celery

# Update frontend
cd /var/www/soleva-platform/soleva\ front\ end
git pull origin main
npm install
npm run build
sudo systemctl reload nginx
```

### Monitor Logs
```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django logs
sudo tail -f /var/www/soleva-platform/soleva\ back\ end/logs/django.log

# Celery logs
sudo tail -f /var/log/celery/worker1.log
```

## 14. Troubleshooting

### Common Issues and Solutions

1. **502 Bad Gateway**
   ```bash
   sudo systemctl status gunicorn
   sudo systemctl restart gunicorn
   ```

2. **SSL Certificate Issues**
   ```bash
   sudo certbot renew --dry-run
   sudo nginx -t
   ```

3. **Database Connection Issues**
   ```bash
   sudo systemctl status postgresql
   sudo -u postgres psql -c "\l"
   ```

4. **Redis Connection Issues**
   ```bash
   redis-cli ping
   sudo systemctl restart redis-server
   ```

5. **High Memory Usage**
   ```bash
   # Check processes
   htop
   
   # Restart services if needed
   sudo systemctl restart gunicorn celery
   ```

## Support and Updates

For ongoing support and updates, maintain regular monitoring and follow the maintenance procedures outlined above. Keep all system packages and dependencies updated regularly for security and performance.

Remember to update this documentation as new features are added or configuration changes are made.