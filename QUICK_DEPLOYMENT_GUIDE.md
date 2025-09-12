# 🚀 Quick Deployment Guide - Soleva Website

## 📋 Pre-Requirements Checklist

- [ ] Docker Desktop is installed and running
- [ ] Domain `solevaeg.com` DNS A record points to your server IP
- [ ] Port 80 and 443 are open on your server
- [ ] `docker.env` file exists with proper configuration

## 🛠️ Step-by-Step Deployment

### Step 1: Verify Environment
```bash
# Check Docker is running
docker --version
docker info

# Check environment file exists
ls docker.env
```

### Step 2: Start Services (Manual Method)
```bash
# Clean start
docker-compose down --remove-orphans

# Start database services
docker-compose up -d postgres redis

# Wait 10 seconds, then start backend
docker-compose up -d backend

# Wait 15 seconds, then start frontend  
docker-compose up -d frontend

# Wait 10 seconds, then start nginx
docker-compose up -d nginx
```

### Step 3: Check Service Status
```bash
# Check all services are running
docker-compose ps

# Check logs if any service is failing
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

### Step 4: Test Basic Connectivity
```bash
# Test health endpoint
curl http://localhost/health

# Test with domain (if DNS configured)
curl http://solevaeg.com/health
```

### Step 5: Generate SSL Certificate (Optional)
**Only if domain DNS is properly configured:**
```bash
# Generate SSL certificate
docker-compose run --rm certbot

# Restart nginx to enable SSL
docker-compose restart nginx
```

### Step 6: Final Testing
```bash
# Test HTTPS (if SSL enabled)
curl -I https://solevaeg.com

# Test website pages
curl -I http://solevaeg.com
curl -I http://solevaeg.com/api/
```

## 🌐 Access URLs

After successful deployment:

- **Website**: http://solevaeg.com (or https:// if SSL enabled)
- **API**: http://solevaeg.com/api/
- **Admin Panel**: http://solevaeg.com/admin/
- **Health Check**: http://solevaeg.com/health

## 🔍 Troubleshooting

### If containers won't start:
```bash
# Check Docker resources
docker system df
docker system prune

# Pull images manually
docker pull postgres:latest
docker pull redis:latest
docker pull nginx:alpine
```

### If domain doesn't resolve:
1. Check DNS propagation: `nslookup solevaeg.com`
2. Verify A record points to correct IP
3. Test with server IP directly

### If SSL fails:
1. Ensure domain is accessible via HTTP first
2. Check port 80 is open for Let's Encrypt validation
3. Verify email in docker.env is valid

## ✅ Success Indicators

You'll know deployment is successful when:

- [ ] All containers show "Up" status in `docker-compose ps`
- [ ] Health endpoint returns "healthy" response
- [ ] Website loads at your domain
- [ ] Admin panel is accessible
- [ ] SSL certificate is active (if configured)

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs [service-name]`
2. Verify environment variables in `docker.env`
3. Ensure Docker has sufficient resources (4GB+ RAM recommended)
4. Check firewall settings for ports 80/443

The website has a **professional, production-ready design** and will look excellent once deployed successfully.
