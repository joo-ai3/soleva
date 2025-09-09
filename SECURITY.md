# Security Guide - Soleva E-commerce Platform

## Overview

This document outlines the security measures implemented in the Soleva e-commerce platform and provides guidelines for maintaining security in production.

## Backend Security Features

### 1. Authentication & Authorization

#### JWT Token Security
- **Access Token Lifetime**: 60 minutes (configurable)
- **Refresh Token Lifetime**: 7 days (configurable)
- **Token Rotation**: Refresh tokens are rotated on use
- **Token Blacklisting**: Tokens are blacklisted after logout
- **Secure Headers**: Tokens sent via Authorization header only

#### Password Security
- **Validation**: Django's built-in password validators
- **Hashing**: PBKDF2 with SHA256 (Django default)
- **Minimum Requirements**: 8 characters, mixed case, numbers
- **Password Reset**: Secure 6-digit code with expiration

#### User Account Security
- **Email Verification**: Required for new accounts
- **Account Lockout**: Can be implemented with django-axes
- **Two-Factor Authentication**: Ready for implementation
- **Session Management**: Tracked user sessions with IP logging

### 2. API Security

#### Input Validation
```python
# All API endpoints use DRF serializers for validation
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField()  # Built-in email validation
```

#### Rate Limiting
```python
# Can be implemented with django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def login_view(request):
    # Login logic
```

#### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
CORS_ALLOW_CREDENTIALS = True
```

### 3. Database Security

#### Query Protection
- **ORM Usage**: Django ORM prevents SQL injection
- **Parameterized Queries**: All queries use parameters
- **Permission System**: Database user with minimal privileges

#### Data Encryption
```python
# Sensitive data encryption (can be added)
from django.contrib.auth.hashers import make_password, check_password

# Credit card data should never be stored
# Use payment gateway tokens instead
```

### 4. File Upload Security

#### Image Upload Validation
```python
def validate_image(image):
    # File type validation
    if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        raise ValidationError("Only image files are allowed")
    
    # File size validation (5MB max)
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("File size cannot exceed 5MB")
```

#### File Storage
- **Separate Media Directory**: Media files stored separately
- **No Executable Permissions**: Media directory has no execute permissions
- **CDN Integration**: Use CDN for production file serving

### 5. Environment Security

#### Environment Variables
```bash
# Never commit these to version control
SECRET_KEY=your-very-secure-secret-key-here
DB_PASSWORD=your-secure-database-password
STRIPE_SECRET_KEY=sk_live_your-stripe-secret
```

#### Debug Settings
```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True  # HTTPS only
```

## Frontend Security Features

### 1. Authentication

#### Token Management
```typescript
// Secure token storage
const token = localStorage.getItem(API_CONFIG.AUTH_TOKEN_KEY);

// Automatic token refresh
const refreshToken = useCallback(async (): Promise<boolean> => {
  // Token refresh logic with error handling
}, []);
```

#### Protected Routes
```typescript
// Route protection
<ProtectedRoute>
  <AccountPage />
</ProtectedRoute>
```

### 2. Input Validation

#### Form Validation
```typescript
// Client-side validation
const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Server-side validation is always performed
```

#### XSS Prevention
```typescript
// Sanitize user input (if displaying HTML)
import DOMPurify from 'dompurify';

const sanitizedHTML = DOMPurify.sanitize(userInput);
```

### 3. API Communication

#### HTTPS Only
```typescript
// API configuration
export const API_CONFIG = {
  BASE_URL: 'https://yourdomain.com/api', // HTTPS only in production
  TIMEOUT: 30000,
};
```

#### Request Headers
```typescript
// Secure headers
const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem(API_CONFIG.AUTH_TOKEN_KEY);
  return token 
    ? { 
        ...API_CONFIG.DEFAULT_HEADERS, 
        Authorization: `Bearer ${token}`,
        'X-Requested-With': 'XMLHttpRequest'
      }
    : API_CONFIG.DEFAULT_HEADERS;
};
```

## Production Security Checklist

### Server Configuration

#### Nginx Security Headers
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Hide server version
server_tokens off;
```

#### SSL/TLS Configuration
```nginx
# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
```

### Database Security

#### PostgreSQL Configuration
```sql
-- Create dedicated database user
CREATE USER soleva_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE soleva_db TO soleva_user;
GRANT USAGE ON SCHEMA public TO soleva_user;
GRANT CREATE ON SCHEMA public TO soleva_user;

-- Limit permissions
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM soleva_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO soleva_user;
```

#### Database Connection
```python
# Use connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',  # Require SSL
        },
        'CONN_MAX_AGE': 60,  # Connection pooling
    }
}
```

### Monitoring & Logging

#### Security Logging
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'security': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/soleva/security.log',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security'],
            'level': 'INFO',
        },
    },
}
```

#### Failed Login Attempts
```python
# Track failed login attempts
class LoginAttempt(models.Model):
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=150)
    success = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Backup & Recovery

#### Automated Backups
```bash
#!/bin/bash
# Daily backup script
pg_dump -h localhost -U soleva_user soleva_db | gzip > /backup/db_$(date +%Y%m%d).sql.gz

# Encrypt sensitive backups
gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 \
    --s2k-digest-algo SHA512 --s2k-count 65536 --symmetric \
    --output backup_encrypted.gpg backup.sql
```

## Security Best Practices

### Development

1. **Never commit secrets** to version control
2. **Use environment variables** for configuration
3. **Validate all inputs** on both client and server
4. **Use HTTPS** for all communications
5. **Implement proper error handling** without exposing internals
6. **Keep dependencies updated** regularly
7. **Use security linters** (bandit for Python, ESLint for JS)

### Production

1. **Regular security updates** for OS and packages
2. **Monitor logs** for suspicious activities
3. **Implement rate limiting** on API endpoints
4. **Use Web Application Firewall** (WAF)
5. **Regular security audits** and penetration testing
6. **Backup strategy** with encryption
7. **Incident response plan**

### Code Review Security Checklist

- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user inputs
- [ ] Proper error handling without information disclosure
- [ ] Authentication required for sensitive endpoints
- [ ] Authorization checks for data access
- [ ] SQL injection prevention (use ORM)
- [ ] XSS prevention in templates
- [ ] CSRF protection enabled
- [ ] Secure HTTP headers configured
- [ ] File upload restrictions implemented

## Incident Response

### Security Incident Procedure

1. **Identify** the security incident
2. **Contain** the threat immediately
3. **Assess** the scope and impact
4. **Eradicate** the threat
5. **Recover** systems and data
6. **Learn** and improve security measures

### Contact Information

- **Security Team**: security@yourdomain.com
- **Emergency Contact**: +20-XXX-XXX-XXXX
- **External Security Consultant**: [Contact Details]

## Compliance

### Data Protection (GDPR/Local Laws)

- **Data Minimization**: Collect only necessary data
- **User Consent**: Clear consent for data collection
- **Right to Delete**: Users can delete their accounts
- **Data Export**: Users can export their data
- **Privacy Policy**: Clear privacy policy
- **Data Encryption**: Sensitive data encrypted

### PCI DSS (Payment Card Industry)

- **No Card Data Storage**: Use payment gateway tokens
- **Secure Transmission**: HTTPS for all payment data
- **Access Control**: Restrict access to payment systems
- **Regular Testing**: Security testing for payment flows
- **Network Segmentation**: Isolate payment processing

This security guide should be reviewed regularly and updated as new threats emerge or as the application evolves.
