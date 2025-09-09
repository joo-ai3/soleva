# 🌐 Domain Configuration Guide - solevaeg.com

## Primary Domain Configuration

### ✅ **Main Domain**: `solevaeg.com`
This is the **only** domain that should be used for the Soleva website.

---

## 🔧 **Required Configuration Steps**

### 1. **DNS Configuration**
```dns
# A Records
solevaeg.com.           A    [Your Server IP]
www.solevaeg.com.       A    [Your Server IP]

# CNAME Records (if using CDN)
www.solevaeg.com.       CNAME    solevaeg.com.

# MX Records (for emails)
solevaeg.com.           MX    10    mail.solevaeg.com.
```

### 2. **SSL Certificate**
- Install SSL certificate for `solevaeg.com` and `www.solevaeg.com`
- Ensure HTTPS redirect is enabled
- Configure HSTS headers for security

### 3. **Web Server Configuration**

#### **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name solevaeg.com www.solevaeg.com;
    return 301 https://solevaeg.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.solevaeg.com;
    return 301 https://solevaeg.com$request_uri;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
}

server {
    listen 443 ssl http2;
    server_name solevaeg.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # Your main site configuration
    location / {
        # Frontend serving or proxy to backend
    }
}
```

#### **Apache Configuration**
```apache
<VirtualHost *:80>
    ServerName solevaeg.com
    ServerAlias www.solevaeg.com
    Redirect permanent / https://solevaeg.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName www.solevaeg.com
    Redirect permanent / https://solevaeg.com/
    
    SSLEngine on
    SSLCertificateFile /path/to/ssl/cert.pem
    SSLCertificateKeyFile /path/to/ssl/private.key
</VirtualHost>

<VirtualHost *:443>
    ServerName solevaeg.com
    
    SSLEngine on
    SSLCertificateFile /path/to/ssl/cert.pem
    SSLCertificateKeyFile /path/to/ssl/private.key
    
    # Your main site configuration
</VirtualHost>
```

---

## 🚫 **Remove Old Domain Configurations**

### **Check and Remove:**
1. **Environment Variables**: Remove any references to old domains
2. **Config Files**: Clean up any hardcoded old domain references
3. **Database Records**: Remove old domain entries
4. **CDN Settings**: Update CDN to only serve solevaeg.com
5. **Analytics**: Update Google Analytics, Facebook Pixel with new domain

### **Files to Check:**
```bash
# Backend configuration
soleva back end/soleva_backend/settings.py
soleva back end/.env
soleva back end/docker.env.example

# Frontend configuration
soleva front end/.env
soleva front end/src/config/api.ts

# Docker configurations
docker-compose.yml
docker-compose.production.yml

# Nginx configuration
nginx/conf.d/soleva.conf
```

---

## ⚙️ **Application Configuration**

### **Backend Settings** (`settings.py`)
```python
# Update allowed hosts
ALLOWED_HOSTS = [
    'solevaeg.com',
    'www.solevaeg.com',
    'localhost',  # for development only
    '127.0.0.1',  # for development only
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://solevaeg.com",
]

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "https://solevaeg.com",
]

# Site URL
SITE_URL = "https://solevaeg.com"
```

### **Frontend Configuration**
```typescript
// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: 'https://solevaeg.com/api',
  SITE_URL: 'https://solevaeg.com',
  // ... other config
};
```

### **Environment Variables**
```env
# Backend .env
SITE_URL=https://solevaeg.com
FRONTEND_URL=https://solevaeg.com
ALLOWED_HOSTS=solevaeg.com,www.solevaeg.com

# Frontend .env
VITE_API_BASE_URL=https://solevaeg.com/api
VITE_SITE_URL=https://solevaeg.com
```

---

## 🔍 **SEO Configuration**

### **Meta Tags Update**
```html
<!-- Update all meta tags to use solevaeg.com -->
<meta property="og:url" content="https://solevaeg.com" />
<link rel="canonical" href="https://solevaeg.com" />
```

### **Sitemap Configuration**
```xml
<!-- sitemap.xml -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://solevaeg.com/</loc>
        <lastmod>2024-01-01</lastmod>
        <priority>1.0</priority>
    </url>
    <!-- ... other URLs -->
</urlset>
```

### **Robots.txt**
```txt
User-agent: *
Allow: /
Sitemap: https://solevaeg.com/sitemap.xml
```

---

## 📧 **Email Configuration**

### **Email Domains**
All email addresses should use `@solevaeg.com`:
- `info@solevaeg.com`
- `support@solevaeg.com`
- `sales@solevaeg.com`
- `business@solevaeg.com`

### **SMTP Configuration**
```python
# Django email settings
EMAIL_HOST = 'mail.solevaeg.com'  # or your email provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'info@solevaeg.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'Soleva <info@solevaeg.com>'
```

---

## 🧪 **Testing Checklist**

### **Domain Testing**
- [ ] `https://solevaeg.com` loads correctly
- [ ] `https://www.solevaeg.com` redirects to `https://solevaeg.com`
- [ ] `http://solevaeg.com` redirects to `https://solevaeg.com`
- [ ] `http://www.solevaeg.com` redirects to `https://solevaeg.com`
- [ ] SSL certificate is valid and secure
- [ ] No mixed content warnings
- [ ] All internal links use the correct domain

### **Email Testing**
- [ ] All email addresses (`@solevaeg.com`) are working
- [ ] Contact forms send to correct addresses
- [ ] Email templates use correct sender addresses
- [ ] Email deliverability is working

### **SEO Testing**
- [ ] Google Search Console configured for `solevaeg.com`
- [ ] Analytics tracking updated
- [ ] Social media links updated
- [ ] Sitemap accessible at `https://solevaeg.com/sitemap.xml`

---

## 🚨 **Important Notes**

1. **Single Domain Policy**: Only use `solevaeg.com` - no other domains or subdomains
2. **HTTPS Only**: Always redirect HTTP to HTTPS
3. **WWW Redirect**: Always redirect `www.solevaeg.com` to `solevaeg.com`
4. **Email Consistency**: All emails must use `@solevaeg.com`
5. **Update External Services**: Update all external services (Google Analytics, Facebook, etc.) to use the new domain

---

## 📞 **Support**

If you encounter any issues with domain configuration:
1. Check DNS propagation (can take up to 48 hours)
2. Verify SSL certificate installation
3. Test from multiple locations/devices
4. Check server logs for any errors

---

*This guide ensures that solevaeg.com is properly configured as the single, official domain for the Soleva website.*
