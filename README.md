# Soleva E-commerce Platform

A complete full-stack e-commerce platform built with Django REST Framework and React, designed for the Egyptian market with bilingual support (Arabic/English).

## 🚀 Features

- **Full E-commerce Functionality**: Product catalog, shopping cart, checkout, order management
- **Multi-Payment Support**: Cash on Delivery, Bank Wallet, E-Wallet, Paymob, Stripe
- **Payment Proof System**: Upload and verification system for bank/e-wallet payments
- **Bilingual Support**: Complete Arabic and English localization
- **Admin Dashboard**: Comprehensive order and payment management
- **Mobile Responsive**: Optimized for all devices
- **SEO Optimized**: Meta tags, structured data, sitemap
- **Analytics Integration**: Google Analytics, Facebook Pixel, TikTok, Snapchat
- **Real-time Notifications**: Order status updates and payment notifications

## 🏗️ Architecture

### Backend (Django REST Framework)
- **API**: RESTful APIs for all frontend interactions
- **Database**: PostgreSQL for data persistence
- **Cache**: Redis for caching and session storage
- **Queue**: Celery for background tasks
- **File Storage**: Local storage with S3 compatibility
- **Authentication**: JWT-based authentication system

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: React hooks and context
- **Routing**: React Router for SPA navigation
- **Build Tool**: Vite for fast development and building

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Reverse Proxy**: Nginx with SSL termination
- **SSL**: Let's Encrypt certificates with auto-renewal
- **Monitoring**: Health checks and logging
- **Backup**: Automated database and media backups

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Domain name pointed to your server

### One-Command Deployment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd soleva-platform
   ```

2. **Configure environment**:
   ```bash
   cp docker.env.example .env
   # Edit .env with your configuration
   nano .env
   ```

3. **Deploy**:
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

That's it! Your platform will be available at:
- **Frontend**: https://thesoleva.com
- **API**: https://thesoleva.com/api
- **Admin**: https://thesoleva.com/admin

## 📋 Environment Configuration

Copy `docker.env.example` to `.env` and configure:

```bash
# Domain Configuration
DOMAIN=thesoleva.com
SSL_EMAIL=admin@thesoleva.com

# Database
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=your-secure-password

# Django
SECRET_KEY=your-50-character-secret-key
ADMIN_PASSWORD=your-admin-password

# Payment Gateways
PAYMOB_API_KEY=your-paymob-key
STRIPE_SECRET_KEY=sk_live_your-stripe-key

# Email
EMAIL_HOST_USER=noreply@thesoleva.com
EMAIL_HOST_PASSWORD=your-email-password

# Analytics
FACEBOOK_PIXEL_ID=your-pixel-id
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

## 🛠️ Management Commands

### Deployment Commands
```bash
# Full deployment
./scripts/deploy.sh

# Update deployment
./scripts/deploy.sh update

# View status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs [service_name]

# Restart services
./scripts/deploy.sh restart [service_name]

# Stop all services
./scripts/deploy.sh stop
```

### Docker Compose Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]

# Rebuild and restart
docker-compose up -d --build
```

### Backup and Maintenance
```bash
# Create backup
./scripts/backup.sh

# Renew SSL certificates
./scripts/ssl-renew.sh

# Clean up old Docker resources
docker system prune -f
```

## 🔧 Development Setup

### Local Development

1. **Backend Development**:
   ```bash
   cd "soleva back end"
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend Development**:
   ```bash
   cd "soleva front end"
   npm install
   npm run dev
   ```

### Development with Docker
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Watch logs
docker-compose -f docker-compose.dev.yml logs -f
```

## 📁 Project Structure

```
soleva-platform/
├── soleva back end/          # Django backend
│   ├── soleva_backend/       # Main Django project
│   ├── orders/               # Orders and payments app
│   ├── products/             # Products catalog app
│   ├── users/                # User management app
│   ├── cart/                 # Shopping cart app
│   ├── coupons/              # Discount coupons app
│   ├── notifications/        # Notification system
│   ├── Dockerfile            # Backend Docker configuration
│   └── requirements.txt      # Python dependencies
├── soleva front end/         # React frontend
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   ├── Dockerfile            # Frontend Docker configuration
│   └── package.json          # Node.js dependencies
├── nginx/                    # Nginx configuration
│   ├── nginx.conf            # Main Nginx config
│   └── conf.d/               # Site-specific configs
├── scripts/                  # Deployment scripts
│   ├── deploy.sh             # Main deployment script
│   ├── backup.sh             # Backup script
│   └── ssl-renew.sh          # SSL renewal script
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # This file
```

## 🌐 Domain Configuration

The platform supports multiple domains with automatic redirects:

- **Primary Domain**: `thesoleva.com`
- **Redirect Domains**: `soleva.shop`, `soleva.vip`, `sole-va.com`

All traffic is automatically redirected to `https://hetsoleva.com` with proper SEO handling.

## 🔒 SSL Certificate Management

SSL certificates are automatically obtained and renewed using Let's Encrypt:

- **Initial Setup**: Certificates are obtained during first deployment
- **Auto-Renewal**: Automated via cron job running `ssl-renew.sh`
- **Manual Renewal**: Run `./scripts/ssl-renew.sh`

### Setup Auto-Renewal Cron Job
```bash
# Add to crontab (runs every day at 2 AM)
0 2 * * * /var/www/soleva-platform/scripts/ssl-renew.sh
```

## 📊 Backup Strategy

Automated backups include:
- **Database**: PostgreSQL dump (compressed)
- **Media Files**: User uploads and payment proofs
- **Configuration**: Environment and Docker configs
- **SSL Certificates**: Let's Encrypt certificates

### Backup Schedule
```bash
# Add to crontab (runs every day at 3 AM)
0 3 * * * /var/www/soleva-platform/scripts/backup.sh
```

### Restore from Backup
```bash
# Extract backup
tar -xzf soleva_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore database
gunzip -c database.sql.gz | docker-compose exec -T postgres psql -U soleva_user soleva_db

# Restore media files
docker cp media/ soleva_backend:/app/
```

## 🔍 Monitoring and Health Checks

### Health Check Endpoints
- **Frontend**: `https://thesoleva.com/health`
- **Backend**: `https://thesoleva.com/api/health/`

### Service Monitoring
```bash
# Check all services status
docker-compose ps

# View service logs
docker-compose logs -f [service_name]

# Check resource usage
docker stats
```

### Log Locations
- **Nginx**: `nginx_logs` volume
- **Backend**: `backend_logs` volume
- **Celery**: `celery_logs` volume
- **SSL Renewal**: `/var/log/soleva-ssl-renewal.log`
- **Backup**: `/var/log/soleva-backup.log`

## 🚨 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**:
   ```bash
   # Check certificate status
   openssl x509 -in letsencrypt/live/thesoleva.com/cert.pem -text -noout
   
   # Force certificate renewal
   docker-compose run --rm certbot certonly --force-renewal
   ```

2. **Database Connection Issues**:
   ```bash
   # Check database status
   docker-compose exec postgres pg_isready -U soleva_user
   
   # View database logs
   docker-compose logs postgres
   ```

3. **Service Not Starting**:
   ```bash
   # Check service logs
   docker-compose logs [service_name]
   
   # Restart service
   docker-compose restart [service_name]
   ```

4. **Performance Issues**:
   ```bash
   # Check resource usage
   docker stats
   
   # Scale services
   docker-compose up -d --scale backend=2
   ```

### Support

For technical support or questions:
- Check logs: `docker-compose logs -f`
- Review configuration: Verify `.env` file settings
- Test connectivity: Use health check endpoints
- Monitor resources: Check disk space and memory usage

## 🔄 Updates and Maintenance

### Updating the Platform
```bash
# Pull latest changes
git pull origin main

# Update and restart
./scripts/deploy.sh update
```

### Adding New Domains
1. Update DNS records to point to your server
2. Add domain to `.env` file in `ALLOWED_HOSTS`
3. Update Nginx configuration in `nginx/conf.d/soleva.conf`
4. Restart services: `docker-compose restart`

### Scaling Services
```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Scale Celery workers
docker-compose up -d --scale celery=2
```

## 📈 Performance Optimization

### Production Optimizations Included
- **Nginx Gzip Compression**: Reduces bandwidth usage
- **Static File Caching**: Browser caching for static assets
- **Database Connection Pooling**: Efficient database connections
- **Redis Caching**: Session and query result caching
- **CDN Ready**: Configured for CDN integration
- **Image Optimization**: Automatic image compression

### Monitoring Performance
- Use health check endpoints to monitor response times
- Monitor Docker resource usage with `docker stats`
- Check Nginx access logs for traffic patterns
- Use database query analysis for optimization

---

## 🎉 Deployment Success

After successful deployment, your Soleva e-commerce platform will be:

✅ **Fully Functional**: Complete e-commerce experience  
✅ **Secure**: HTTPS everywhere with security headers  
✅ **Scalable**: Docker-based architecture  
✅ **Monitored**: Health checks and logging  
✅ **Backed Up**: Automated backup system  
✅ **SEO Ready**: Optimized for search engines  
✅ **Analytics Enabled**: Tracking pixels configured  
✅ **Mobile Optimized**: Responsive design  
✅ **Bilingual**: Arabic and English support  

Welcome to your new e-commerce platform! 🚀