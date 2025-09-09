# 🌐 Nginx Configuration Guide for Soleva

## 📋 **Configuration Files Created/Updated**

### **1. Primary Configuration: `nginx/nginx-optimized.conf`**
- **Complete standalone configuration** for production use
- **Optimized for Docker containers** with React frontend and Django backend
- **All requirements implemented** as requested

### **2. Updated Configuration: `nginx/conf.d/soleva.conf`**
- **Updated existing configuration** with correct domain (`solevaeg.com`)
- **Maintains existing structure** while fixing domain references

---

## ✅ **All Requirements Implemented**

### **✅ 1. Frontend Serving**
- **React/SPA routing support** with catch-all location `/`
- **Proper WebSocket support** for development (HMR)
- **Static asset optimization** with aggressive caching

### **✅ 2. API Proxying**
- **All `/api/` requests** proxied to backend container
- **Enhanced proxy settings** with proper headers and buffering
- **Connection keepalive** for better performance

### **✅ 3. HTTPS Redirection**
- **Force HTTPS** for all requests (HTTP → HTTPS redirect)
- **www subdomain** redirects to primary domain
- **Let's Encrypt** certificate support

### **✅ 4. Static File Caching**
- **Aggressive caching** for CSS, JS, images (1 year)
- **Immutable cache headers** for versioned assets
- **Proper cache control** for HTML files (no-cache)

### **✅ 5. Gzip Compression**
- **Enhanced gzip** with optimal compression levels
- **Comprehensive file types** covered
- **Brotli support** ready (commented, enable if available)

### **✅ 6. Docker Optimization**
- **Service names** for backend/frontend communication
- **Health checks** and monitoring endpoints
- **Proper logging** and error handling

---

## 🚀 **Performance Optimizations**

### **Connection & Buffer Optimization**
```nginx
worker_connections 2048;
keepalive 32;
proxy_buffering on;
proxy_buffer_size 128k;
```

### **Advanced Caching Strategy**
```nginx
# Static assets: 1 year
expires 1y;
add_header Cache-Control "public, immutable";

# HTML files: no-cache
add_header Cache-Control "no-cache, no-store, must-revalidate";
```

### **Rate Limiting**
```nginx
# API: 100 requests/minute
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

# Auth: 5 requests/minute  
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
```

---

## 🔒 **Security Features**

### **Security Headers**
- **HSTS** (Strict-Transport-Security)
- **CSP** (Content-Security-Policy) optimized for Soleva
- **X-Frame-Options**, **X-Content-Type-Options**
- **XSS Protection**, **Referrer-Policy**

### **Access Control**
- **Block sensitive files** (`.git`, `.htaccess`, etc.)
- **Prevent PHP execution** in upload directories
- **IP-based rate limiting**
- **Admin panel protection** (optional IP whitelist)

### **SSL Configuration**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:...;
ssl_stapling on;
ssl_session_cache shared:SSL:10m;
```

---

## 📁 **File Structure**

```
nginx/
├── nginx-optimized.conf          # New optimized standalone config
├── nginx.conf                    # Original main config
└── conf.d/
    ├── soleva.conf               # Updated with correct domain
    └── ssl.conf                  # SSL settings (if exists)
```

---

## 🐳 **Docker Integration**

### **Volume Mounts Required**
```yaml
volumes:
  - ./nginx/nginx-optimized.conf:/etc/nginx/nginx.conf:ro
  - static_volume:/var/www/static:ro
  - media_volume:/var/www/media:ro
  - letsencrypt_certs:/etc/letsencrypt:ro
  - certbot_webroot:/var/www/certbot:ro
```

### **Service Dependencies**
```yaml
depends_on:
  backend:
    condition: service_healthy
  frontend:
    condition: service_healthy
```

---

## 🧪 **Testing Instructions**

### **1. Local Testing**
```bash
# Test nginx configuration syntax
docker-compose exec nginx nginx -t

# Reload nginx configuration
docker-compose exec nginx nginx -s reload

# Check nginx status
docker-compose exec nginx nginx -V
```

### **2. Performance Testing**
```bash
# Test gzip compression
curl -H "Accept-Encoding: gzip" -I https://solevaeg.com

# Test static file caching
curl -I https://solevaeg.com/static/css/main.css

# Test API proxy
curl -I https://solevaeg.com/api/health/
```

### **3. Security Testing**
```bash
# Test HTTPS redirect
curl -I http://solevaeg.com

# Test security headers
curl -I https://solevaeg.com

# Test rate limiting
for i in {1..10}; do curl -I https://solevaeg.com/api/auth/; done
```

---

## 🔧 **Configuration Options**

### **Switch to Optimized Config**
To use the new optimized configuration:

1. **Update docker-compose.yml**:
```yaml
nginx:
  volumes:
    - ./nginx/nginx-optimized.conf:/etc/nginx/nginx.conf:ro
    # Remove the conf.d mount if using standalone config
```

2. **Or keep modular approach**:
```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./nginx/conf.d:/etc/nginx/conf.d:ro
```

### **SSL Certificate Paths**
Update certificate paths for your domain:
```nginx
ssl_certificate /etc/letsencrypt/live/solevaeg.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/solevaeg.com/privkey.pem;
```

---

## 📊 **Monitoring & Logging**

### **Log Locations**
```
/var/log/nginx/access.log  # Access logs with timing info
/var/log/nginx/error.log   # Error logs
```

### **Health Check Endpoint**
```
GET /health
Returns: 200 "healthy"
```

### **Metrics Available**
- Request timing (`$request_time`)
- Upstream timing (`$upstream_response_time`)
- Cache hit/miss status
- Rate limiting status

---

## 🚀 **Deployment Steps**

### **1. Update Docker Compose**
Choose your preferred configuration approach and update volume mounts.

### **2. Generate SSL Certificates**
```bash
# Initial certificate generation
docker-compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email info@solevaeg.com \
  --agree-tos --no-eff-email \
  -d solevaeg.com -d www.solevaeg.com
```

### **3. Start Services**
```bash
docker-compose up -d nginx
docker-compose logs -f nginx
```

### **4. Verify Configuration**
```bash
# Test all endpoints
curl -I https://solevaeg.com          # Frontend
curl -I https://solevaeg.com/api/     # API
curl -I https://solevaeg.com/admin/   # Admin
curl -I https://solevaeg.com/static/  # Static files
```

---

## 🎯 **Expected Results**

After deployment, you should see:

- ✅ **HTTP → HTTPS redirect** working
- ✅ **Frontend served** at `https://solevaeg.com`
- ✅ **API accessible** at `https://solevaeg.com/api/`
- ✅ **Static files cached** with proper headers
- ✅ **Gzip compression** active
- ✅ **Security headers** present
- ✅ **Rate limiting** functional

---

## 📞 **Support & Troubleshooting**

### **Common Issues**
1. **SSL Certificate errors**: Check certificate paths and permissions
2. **502 Bad Gateway**: Verify backend/frontend containers are running
3. **Rate limiting**: Adjust zones and limits as needed
4. **CORS issues**: Update allowed origins for your domain

### **Debug Commands**
```bash
# Check nginx processes
docker-compose exec nginx ps aux

# Test configuration
docker-compose exec nginx nginx -t

# View real-time logs
docker-compose logs -f nginx

# Check upstream status
docker-compose exec nginx curl -I http://backend:8000/api/health/
```

---

**✅ Your nginx configuration is now production-ready with all requested features implemented!**
