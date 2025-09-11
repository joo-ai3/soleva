# 🔐 SSL Configuration Guide for solevaeg.com

This guide provides complete instructions for configuring SSL certificates and HTTPS for the Soleva platform using Docker and Let's Encrypt.

## 📋 Overview

The SSL setup includes:
- Automatic SSL certificate generation using Let's Encrypt
- HTTPS configuration with proper redirects
- Certificate auto-renewal every 12 hours
- Security headers and best practices
- Support for both `solevaeg.com` and `www.solevaeg.com`

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Domain `solevaeg.com` pointing to your server IP
- Ports 80 and 443 open on your server
- Email address for SSL certificate notifications

### One-Command Deployment
```bash
# Linux/macOS
./deploy-with-ssl.sh

# Windows PowerShell
.\deploy-with-ssl.ps1
```

This will:
1. Build and start all services
2. Obtain SSL certificates from Let's Encrypt
3. Configure nginx with HTTPS
4. Set up automatic certificate renewal

## 📁 File Structure

```
ssl/
├── certbot/
│   ├── conf/           # Let's Encrypt configuration and certificates
│   └── www/            # Webroot challenge directory
├── init-ssl.sh         # Certificate initialization script (Linux)
├── init-ssl.ps1        # Certificate initialization script (Windows)
├── renew-ssl.sh        # Certificate renewal script (Linux)
└── renew-ssl.ps1       # Certificate renewal script (Windows)

nginx/
├── nginx.conf          # Main nginx configuration
└── conf.d/
    ├── soleva.conf     # Main site configuration with SSL
    └── ssl.conf        # SSL security settings

docker-compose.production.yml  # Production compose with certbot
docker.env                     # Environment variables
```

## ⚙️ Configuration Files

### Environment Variables (`docker.env`)
```env
# Domain Configuration
DOMAIN=solevaeg.com
SSL_EMAIL=support@solevaeg.com

# SSL Configuration
SSL_CERT_PATH=/etc/letsencrypt/live/${DOMAIN}/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/${DOMAIN}/privkey.pem
SSL_DH_PARAM_PATH=/etc/letsencrypt/ssl-dhparams.pem
```

### Nginx SSL Configuration (`nginx/conf.d/ssl.conf`)
- TLS 1.2/1.3 only
- Strong cipher suites
- OCSP stapling enabled
- HSTS headers
- Session resumption

## 🔧 Manual Setup Steps

### 1. DNS Configuration
Update your DNS A records:
```
solevaeg.com    A    [YOUR_SERVER_IP]
www.solevaeg.com A   [YOUR_SERVER_IP]
```

### 2. Certificate Initialization
```bash
# Linux/macOS
./ssl/init-ssl.sh

# Windows PowerShell
.\ssl\init-ssl.ps1
```

### 3. Deploy Services
```bash
# Start all services including certbot
docker-compose -f docker-compose.production.yml up -d

# Or use the deployment script
./deploy-with-ssl.sh
```

### 4. Verify Setup
```bash
# Linux/macOS
./test-ssl-setup.sh

# Windows PowerShell
.\test-ssl-setup.ps1
```

## 🔍 Verification Checklist

### Certificate Status
- [ ] Certificates exist in `ssl/certbot/conf/live/solevaeg.com/`
- [ ] `fullchain.pem` and `privkey.pem` files present
- [ ] DH parameters file exists

### DNS Resolution
- [ ] `solevaeg.com` resolves to your server IP
- [ ] `www.solevaeg.com` resolves to your server IP
- [ ] Both domains return the same IP

### HTTPS Functionality
- [ ] `https://solevaeg.com` loads correctly
- [ ] `https://www.solevaeg.com` loads correctly
- [ ] `http://solevaeg.com` redirects to HTTPS
- [ ] `http://www.solevaeg.com` redirects to HTTPS

### SSL Certificate
- [ ] Certificate is valid and not expired
- [ ] Certificate covers both domains
- [ ] SSL Labs test shows A+ rating

## 🔄 Certificate Management

### Automatic Renewal
Certificates are automatically renewed every 12 hours by the certbot container. No manual intervention required.

### Manual Renewal
```bash
# Linux/macOS
./ssl/renew-ssl.sh

# Windows PowerShell
.\ssl\renew-ssl.ps1
```

### Certificate Information
```bash
# View certificate details
openssl x509 -in ssl/certbot/conf/live/solevaeg.com/fullchain.pem -text -noout

# Check expiry date
openssl x509 -in ssl/certbot/conf/live/solevaeg.com/fullchain.pem -enddate -noout
```

## 🛠️ Troubleshooting

### Common Issues

#### Certificate Not Obtained
```
Error: Failed to obtain SSL certificates
```
**Solution:**
1. Check DNS propagation: `dig solevaeg.com`
2. Ensure ports 80/443 are open
3. Verify nginx is running and accessible
4. Check certbot logs: `docker logs soleva_nginx`

#### HTTP Not Redirecting to HTTPS
```
HTTP redirect test failed
```
**Solution:**
1. Check nginx configuration in `nginx/conf.d/soleva.conf`
2. Verify certificates are properly mounted
3. Restart nginx: `docker restart soleva_nginx`
4. Check nginx logs: `docker logs soleva_nginx`

#### Mixed Content Warnings
```
Mixed content: page was loaded over HTTPS but requested an insecure resource
```
**Solution:**
1. Update all asset URLs to use HTTPS
2. Check API calls in frontend use HTTPS
3. Verify backend serves content over HTTPS

### Log Files
```bash
# Nginx logs
docker-compose -f docker-compose.production.yml logs nginx

# Certbot logs
docker-compose -f docker-compose.production.yml logs certbot

# Application logs
docker-compose -f docker-compose.production.yml logs backend frontend
```

### Emergency Commands
```bash
# Stop all services
docker-compose -f docker-compose.production.yml down

# Start without SSL (temporary)
docker-compose -f docker-compose.production.yml up -d postgres redis backend frontend nginx

# Force certificate renewal
docker run --rm -v "$(pwd)/ssl/certbot/conf:/etc/letsencrypt" certbot/certbot renew --force-renewal
```

## 🔒 Security Features

### SSL/TLS Configuration
- TLS 1.2 and 1.3 only
- Strong cipher suites (ECDHE with AES-256-GCM)
- Perfect Forward Secrecy (PFS)
- OCSP stapling enabled
- HSTS (HTTP Strict Transport Security)

### Security Headers
```nginx
# Applied to all HTTPS responses
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Rate Limiting
- General: 10 requests/second
- Login endpoints: 5 requests/minute
- API endpoints: 100 requests/minute

## 📊 Monitoring

### Certificate Expiry
Monitor certificate expiry dates:
```bash
# Check expiry
openssl x509 -in ssl/certbot/conf/live/solevaeg.com/fullchain.pem -enddate -noout

# Alert if expiring within 30 days
openssl x509 -checkend $((30*24*3600)) -in ssl/certbot/conf/live/solevaeg.com/fullchain.pem
```

### SSL Labs Rating
Test your SSL configuration: https://www.ssllabs.com/ssltest/

### Uptime Monitoring
- Monitor `https://solevaeg.com/health`
- Check certificate validity
- Verify HTTPS redirects

## 📞 Support

### Getting Help
1. Run the test script: `./test-ssl-setup.sh`
2. Check logs: `docker-compose -f docker-compose.production.yml logs`
3. Verify DNS: `dig solevaeg.com`
4. Test SSL: `openssl s_client -connect solevaeg.com:443`

### Emergency Contacts
- SSL Certificate Issues: Check Let's Encrypt status
- DNS Issues: Contact your DNS provider
- Server Issues: Check server firewall and ports

## 📝 Changelog

### v1.0.0
- Initial SSL setup implementation
- Let's Encrypt integration
- Automatic certificate renewal
- HTTPS redirect configuration
- Security headers and best practices

---

*This SSL setup ensures your Soleva platform is secure and uses industry best practices for HTTPS configuration.*
