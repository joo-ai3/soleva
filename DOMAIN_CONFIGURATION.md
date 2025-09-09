# Domain Configuration Guide for Soleva Platform

## Overview
This guide covers the complete domain setup for the Soleva e-commerce platform with `thesoleva.com` as the primary domain and proper redirects from all alternate domains.

## Domain Structure

### Primary Domain
- **thesoleva.com** - Main website
  - Frontend: `https://thesoleva.com`
  - Backend API: `https://thesoleva.com/api`
  - Admin Panel: `https://thesoleva.com/admin`

### Redirect Domains (301 Redirects to Primary)
- `www.thesoleva.com` → `https://thesoleva.com`
- `soleva.shop` → `https://thesoleva.com`
- `soleva.vip` → `https://thesoleva.com`
- `sole-va.com` → `https://thesoleva.com`

## DNS Configuration

### 1. Primary Domain (thesoleva.com)

#### A Records
```
Type: A
Name: @
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300

Type: A
Name: www
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300
```

#### CNAME Records (if using CDN)
```
Type: CNAME
Name: www
Value: thesoleva.com
TTL: 300
```

#### MX Records (for email)
```
Type: MX
Name: @
Value: mail.thesoleva.com
Priority: 10
TTL: 300
```

#### TXT Records (for verification and security)
```
# SPF Record
Type: TXT
Name: @
Value: "v=spf1 include:_spf.google.com ~all"
TTL: 300

# DMARC Record
Type: TXT
Name: _dmarc
Value: "v=DMARC1; p=quarantine; rua=mailto:dmarc@thesoleva.com"
TTL: 300

# Google Site Verification
Type: TXT
Name: @
Value: "google-site-verification=YOUR_VERIFICATION_CODE"
TTL: 300

# Facebook Domain Verification
Type: TXT
Name: @
Value: "facebook-domain-verification=YOUR_FB_VERIFICATION_CODE"
TTL: 300
```

### 2. Redirect Domains Configuration

For each redirect domain (`soleva.shop`, `soleva.vip`, `sole-va.com`):

#### A Records
```
Type: A
Name: @
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300

Type: A
Name: www
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300
```

## SSL Certificate Setup

### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificates for all domains
sudo certbot certonly --nginx -d thesoleva.com -d www.thesoleva.com -d soleva.shop -d www.soleva.shop -d soleva.vip -d www.soleva.vip -d sole-va.com -d www.sole-va.com

# Set up automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

### Certificate Paths
```
Certificate: /etc/letsencrypt/live/thesoleva.com/fullchain.pem
Private Key: /etc/letsencrypt/live/thesoleva.com/privkey.pem
```

## Nginx Configuration

### Complete Nginx Configuration
Create `/etc/nginx/sites-available/thesoleva.com`:

```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;

# Upstream for backend
upstream backend {
    server unix:/var/www/soleva-platform/soleva\ back\ end/soleva_backend.sock fail_timeout=0;
}

# HTTP to HTTPS redirect for all domains
server {
    listen 80;
    listen [::]:80;
    server_name thesoleva.com www.thesoleva.com soleva.shop www.soleva.shop soleva.vip www.soleva.vip sole-va.com www.sole-va.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect everything else to HTTPS
    location / {
        return 301 https://thesoleva.com$request_uri;
    }
}

# HTTPS redirects for alternate domains
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.thesoleva.com soleva.shop www.soleva.shop soleva.vip www.soleva.vip sole-va.com www.sole-va.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/thesoleva.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/thesoleva.com/privkey.pem;
    
    # Include SSL settings
    include /etc/nginx/snippets/ssl-params.conf;
    
    # 301 redirect to primary domain
    return 301 https://thesoleva.com$request_uri;
}

# Main server configuration for thesoleva.com
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name thesoleva.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/thesoleva.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/thesoleva.com/privkey.pem;
    
    # Include SSL settings
    include /etc/nginx/snippets/ssl-params.conf;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google-analytics.com https://connect.facebook.net https://analytics.tiktok.com https://sc-static.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://api.thesoleva.com https://www.google-analytics.com https://analytics.tiktok.com; frame-src 'none';" always;
    
    # Root directory
    root /var/www/soleva-platform/soleva\ front\ end/dist;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;
    
    # Brotli compression (if available)
    # brotli on;
    # brotli_comp_level 6;
    # brotli_types text/xml image/svg+xml application/x-font-ttf image/vnd.microsoft.icon application/x-font-opentype application/json font/eot application/vnd.ms-fontobject application/javascript font/otf application/xml application/xhtml+xml text/javascript  application/x-javascript text/plain application/x-font-truetype application/xml+rss image/x-icon font/opentype text/css image/x-win-bitmap;
    
    # Rate limiting
    limit_req zone=general burst=20 nodelay;
    
    # Frontend (React app)
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache control for HTML files
        location ~* \.html$ {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
        }
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary "Accept-Encoding";
            
            # Enable CORS for fonts
            location ~* \.(woff|woff2|ttf|eot)$ {
                add_header Access-Control-Allow-Origin "*";
            }
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate limiting for API
        limit_req zone=api burst=50 nodelay;
        
        # Specific rate limiting for auth endpoints
        location /api/auth/ {
            limit_req zone=login burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # File upload size
        client_max_body_size 50M;
    }
    
    # Django Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Additional security for admin
        limit_req zone=login burst=5 nodelay;
        
        # Optional: IP whitelist for admin access
        # allow YOUR_ADMIN_IP;
        # deny all;
    }
    
    # Static files (Django)
    location /static/ {
        alias /var/www/soleva-platform/soleva\ back\ end/staticfiles/;
        expires 1y;
        add_header Cache-Control "public";
        
        # Security headers for static files
        add_header X-Content-Type-Options nosniff;
    }
    
    # Media files (uploads)
    location /media/ {
        alias /var/www/soleva-platform/soleva\ back\ end/media/;
        expires 1y;
        add_header Cache-Control "public";
        
        # Security for uploaded files
        add_header X-Content-Type-Options nosniff;
        
        # Prevent PHP execution in media directory
        location ~* \.php$ {
            deny all;
        }
    }
    
    # Security.txt
    location /.well-known/security.txt {
        alias /var/www/soleva-platform/security.txt;
    }
    
    # Robots.txt
    location = /robots.txt {
        alias /var/www/soleva-platform/soleva\ front\ end/dist/robots.txt;
        expires 1d;
    }
    
    # Sitemap
    location = /sitemap.xml {
        alias /var/www/soleva-platform/soleva\ front\ end/dist/sitemap.xml;
        expires 1d;
    }
    
    # Favicon
    location = /favicon.ico {
        alias /var/www/soleva-platform/soleva\ front\ end/dist/favicon.ico;
        expires 1y;
    }
    
    # Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Block access to version control
    location ~ /\.git {
        deny all;
    }
    
    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /404.html {
        root /var/www/soleva-platform/soleva\ front\ end/dist;
        internal;
    }
    
    location = /50x.html {
        root /var/www/soleva-platform/soleva\ front\ end/dist;
        internal;
    }
}
```

### SSL Parameters Configuration
Create `/etc/nginx/snippets/ssl-params.conf`:

```nginx
# SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# DH parameters
ssl_dhparam /etc/nginx/dhparam.pem;
```

### Generate DH Parameters
```bash
sudo openssl dhparam -out /etc/nginx/dhparam.pem 2048
```

## Testing Domain Configuration

### 1. DNS Propagation Check
```bash
# Check DNS resolution
nslookup thesoleva.com
dig thesoleva.com

# Check from multiple locations
# Use online tools like:
# - whatsmydns.net
# - dnschecker.org
```

### 2. SSL Certificate Verification
```bash
# Check SSL certificate
openssl s_client -connect thesoleva.com:443 -servername thesoleva.com

# Online SSL checker
# Use: ssllabs.com/ssltest/
```

### 3. Redirect Testing
```bash
# Test HTTP to HTTPS redirect
curl -I http://thesoleva.com

# Test alternate domain redirects
curl -I https://www.thesoleva.com
curl -I https://soleva.shop
curl -I https://soleva.vip
curl -I https://sole-va.com

# Should all return 301 redirects to https://thesoleva.com
```

### 4. Performance Testing
```bash
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s "https://thesoleva.com"

# Create curl-format.txt:
echo "
     time_namelookup:  %{time_namelookup}s
        time_connect:  %{time_connect}s
     time_appconnect:  %{time_appconnect}s
    time_pretransfer:  %{time_pretransfer}s
       time_redirect:  %{time_redirect}s
  time_starttransfer:  %{time_starttransfer}s
                     ----------
          time_total:  %{time_total}s
" > curl-format.txt
```

## Monitoring and Alerts

### 1. Domain Monitoring Script
Create `/usr/local/bin/domain-monitor.sh`:

```bash
#!/bin/bash

DOMAINS=("thesoleva.com" "www.thesoleva.com" "soleva.shop" "soleva.vip" "sole-va.com")
LOG_FILE="/var/log/domain-monitor.log"

for domain in "${DOMAINS[@]}"; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain" --max-time 10)
    
    if [[ "$response" == "200" ]] || [[ "$response" == "301" ]]; then
        echo "$(date): ✅ $domain - OK ($response)" >> "$LOG_FILE"
    else
        echo "$(date): ❌ $domain - FAILED ($response)" >> "$LOG_FILE"
        # Send alert (email, Slack, etc.)
        # mail -s "Domain Alert: $domain DOWN" admin@thesoleva.com < /dev/null
    fi
done
```

### 2. SSL Certificate Monitoring
Create `/usr/local/bin/ssl-monitor.sh`:

```bash
#!/bin/bash

DOMAIN="thesoleva.com"
THRESHOLD=30  # Days before expiration to alert

# Get certificate expiration date
expiry_date=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)

# Convert to Unix timestamp
expiry_timestamp=$(date -d "$expiry_date" +%s)
current_timestamp=$(date +%s)

# Calculate days until expiration
days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))

if [[ $days_until_expiry -lt $THRESHOLD ]]; then
    echo "$(date): ⚠️ SSL certificate for $DOMAIN expires in $days_until_expiry days"
    # Send alert
    # mail -s "SSL Certificate Alert: $DOMAIN" admin@thesoleva.com
else
    echo "$(date): ✅ SSL certificate for $DOMAIN is valid for $days_until_expiry more days"
fi
```

### 3. Cron Jobs for Monitoring
```bash
# Add to crontab
sudo crontab -e

# Check domains every 5 minutes
*/5 * * * * /usr/local/bin/domain-monitor.sh

# Check SSL certificate daily at 9 AM
0 9 * * * /usr/local/bin/ssl-monitor.sh
```

## Troubleshooting

### Common Issues

1. **DNS Not Resolving**
   - Check DNS provider settings
   - Verify A records point to correct IP
   - Wait for DNS propagation (up to 48 hours)

2. **SSL Certificate Issues**
   ```bash
   # Renew certificate manually
   sudo certbot renew --force-renewal
   
   # Check certificate status
   sudo certbot certificates
   ```

3. **Redirect Loops**
   - Check Nginx configuration
   - Verify no conflicting redirects
   - Clear browser cache

4. **Performance Issues**
   - Enable Gzip compression
   - Optimize static file caching
   - Use CDN for static assets

### Log Locations
```bash
# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log

# SSL renewal logs
/var/log/letsencrypt/letsencrypt.log

# Custom monitoring logs
/var/log/domain-monitor.log
```

## Best Practices

1. **Security**
   - Use strong SSL configuration
   - Enable HSTS headers
   - Regular security updates
   - Monitor failed login attempts

2. **Performance**
   - Enable compression
   - Use browser caching
   - Optimize images
   - Monitor response times

3. **SEO**
   - Consistent use of primary domain
   - Proper 301 redirects
   - Updated sitemap
   - Canonical URLs

4. **Monitoring**
   - Regular uptime checks
   - SSL certificate monitoring
   - Performance monitoring
   - Error log monitoring

This configuration ensures that thesoleva.com serves as the primary domain with proper redirects from all alternate domains, maintains security best practices, and provides optimal performance for users.
