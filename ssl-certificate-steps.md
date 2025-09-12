# SSL Certificate Setup Steps for Soleva Platform

## Current Status
- ✅ Domain DNS configured: solevaeg.com → 213.130.147.41
- ✅ HTTP-only nginx configuration prepared
- ✅ HTTPS configuration ready to enable
- ⚠️ Need to obtain SSL certificates

## Step 1: Prepare HTTP Server for Certificate Validation

### Option A: Using existing nginx configuration
```bash
# The temp-http-only.conf is already configured for ACME challenge
# Location block: /.well-known/acme-challenge/
# Root: /var/www/certbot
```

### Option B: Simple HTTP server (if nginx unavailable)
```bash
# Create webroot directory
mkdir webroot

# Start simple HTTP server on port 80
python -m http.server 80 --directory webroot
```

## Step 2: Obtain SSL Certificates

### Method 1: Using Certbot (Recommended)
```bash
# Install Certbot (if not installed)
# Windows: Download from https://certbot.eff.org/instructions?ws=nginx&os=windows

# Generate certificates
certbot certonly \
  --webroot \
  --webroot-path=./webroot \
  --email support@solevaeg.com \
  --agree-tos \
  --no-eff-email \
  --non-interactive \
  -d solevaeg.com \
  -d www.solevaeg.com
```

### Method 2: Using Docker Certbot (if Docker works)
```bash
docker run --rm \
  -v "$(pwd)/letsencrypt:/etc/letsencrypt" \
  -v "$(pwd)/webroot:/var/www/certbot" \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email support@solevaeg.com \
  --agree-tos \
  --no-eff-email \
  --non-interactive \
  -d solevaeg.com \
  -d www.solevaeg.com
```

### Method 3: Manual Certificate (Alternative)
If automatic generation fails, you can:
1. Use a different ACME client
2. Use CloudFlare SSL (if using CloudFlare)
3. Purchase SSL certificate from a CA
4. Use self-signed certificates for testing

## Step 3: Verify Certificate Generation

Certificates should be generated at:
```
/etc/letsencrypt/live/solevaeg.com/fullchain.pem
/etc/letsencrypt/live/solevaeg.com/privkey.pem
```

Or in local directory:
```
./letsencrypt/live/solevaeg.com/fullchain.pem
./letsencrypt/live/solevaeg.com/privkey.pem
```

## Step 4: Enable HTTPS Configuration

### 4.1 Restore nginx HTTPS configuration
```bash
# Restore the HTTPS configuration
mv nginx/conf.d/soleva.conf.disabled nginx/conf.d/soleva.conf

# Remove temporary HTTP-only config
rm nginx/conf.d/temp-http-only.conf
```

### 4.2 Update docker-compose.yml
```bash
# Re-enable SSL port in docker-compose.yml
# Uncomment: - "443:443"

# Re-enable certbot service
# Uncomment the certbot section
```

### 4.3 Update nginx.conf
```bash
# Re-enable HTTPS server block in nginx.conf
# Uncomment the SSL server configuration
```

## Step 5: Start HTTPS Services

### Using Docker (if connectivity resolved)
```bash
docker compose down
docker compose up -d
```

### Using local services with nginx
```bash
# Start nginx with HTTPS configuration
nginx -s reload

# Start backend
cd "soleva back end"
python manage.py runserver 0.0.0.0:8000

# Start frontend  
cd "soleva front end"
npx serve -s build -p 3000
```

## Step 6: Test HTTPS Access

```bash
# Test HTTPS access
curl -I https://solevaeg.com

# Test HTTP redirect
curl -I http://solevaeg.com
```

## Verification Checklist

- [ ] Domain resolves to correct IP
- [ ] Port 80 accessible from internet
- [ ] HTTP server responds to ACME challenges
- [ ] SSL certificates generated successfully
- [ ] HTTPS configuration enabled
- [ ] Services restarted with SSL
- [ ] HTTPS site accessible
- [ ] HTTP redirects to HTTPS

## Troubleshooting

### Common Issues:
1. **Port 80 blocked**: Check firewall settings
2. **DNS not propagated**: Wait for DNS propagation
3. **ACME challenge fails**: Verify webroot path
4. **Certificate path wrong**: Check certificate locations
5. **Nginx config error**: Test config with `nginx -t`

### Alternative Solutions:
1. Use CloudFlare SSL (proxy mode)
2. Use reverse proxy with SSL termination
3. Deploy on cloud platform with automatic SSL
4. Use load balancer with SSL certificates
