# Soleva E-commerce Backend

A premium E-commerce platform backend built with Django REST Framework, designed for fashion & lifestyle products with full coverage for Egypt and expansion-ready for international markets.

## 🚀 Features

### Core Features
- **User Management**: Registration, authentication, profile management with JWT
- **Product Catalog**: Categories, brands, variants, attributes with multi-language support
- **Shopping Cart**: Persistent cart, wishlist functionality
- **Order Management**: Complete order lifecycle with status tracking
- **Payment Integration**: Paymob (Egypt), Stripe (International), Cash on Delivery
- **Shipping System**: Full Egypt coverage (27 governorates), dynamic pricing
- **Notifications**: Email, SMS, Push notifications with templates
- **Admin Panel**: Comprehensive management interface
- **Analytics**: Facebook Pixel, Google Analytics, TikTok, Snapchat integration
- **Caching**: Redis for performance optimization

### Security Features
- JWT authentication with refresh tokens
- Input sanitization and validation
- Rate limiting and brute force protection
- HTTPS enforcement
- Role-based access control
- Audit logging

## 🛠 Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT (Simple JWT)
- **Storage**: Django Storages with AWS S3 support
- **Notifications**: Firebase Cloud Messaging
- **Payments**: Paymob, Stripe
- **Search**: Fuzzy search with typo tolerance

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js (for frontend integration)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd soleva-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb soleva_db
   
   # Run migrations
   python manage.py migrate
   
   # Load initial data
   python manage.py load_egypt_locations
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis server**
   ```bash
   redis-server
   ```

8. **Start Celery worker** (in separate terminal)
   ```bash
   celery -A soleva_backend worker -l info
   ```

9. **Start Celery beat** (in separate terminal)
   ```bash
   celery -A soleva_backend beat -l info
   ```

10. **Run development server**
    ```bash
    python manage.py runserver
    ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=soleva_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payment Gateways
PAYMOB_API_KEY=your-paymob-key
STRIPE_SECRET_KEY=your-stripe-key

# Analytics
FACEBOOK_PIXEL_ID=your-pixel-id
GOOGLE_ANALYTICS_ID=your-ga-id
```

## 🔗 API Endpoints

### Authentication
```
POST /api/auth/register/          # User registration
POST /api/auth/login/             # User login
POST /api/auth/logout/            # User logout
POST /api/auth/token/             # Get JWT token
POST /api/auth/token/refresh/     # Refresh JWT token
POST /api/auth/password/reset/    # Request password reset
POST /api/auth/verify/email/      # Verify email
```

### User Management
```
GET  /api/user/profile/           # Get user profile
PUT  /api/user/profile/           # Update user profile
GET  /api/user/dashboard/         # User dashboard data
GET  /api/user/addresses/         # List user addresses
POST /api/user/addresses/         # Create address
```

### Products
```
GET  /api/products/               # List products
GET  /api/products/{id}/          # Product details
GET  /api/products/categories/    # List categories
GET  /api/products/search/        # Search products
```

### Cart & Orders
```
GET  /api/cart/                   # Get cart
POST /api/cart/add/               # Add to cart
POST /api/orders/                 # Create order
GET  /api/orders/                 # List user orders
GET  /api/orders/{id}/            # Order details
```

### Shipping
```
GET  /api/shipping/rates/         # Get shipping rates
GET  /api/shipping/governorates/  # List governorates
GET  /api/shipping/cities/        # List cities
```

## 🏗️ Project Structure

```
soleva_backend/
├── authentication/          # JWT authentication
├── users/                  # User management
├── products/               # Product catalog
├── orders/                 # Order management
├── cart/                   # Shopping cart
├── shipping/               # Shipping system
├── coupons/                # Discount coupons
├── notifications/          # Email/SMS/Push notifications
├── tracking/               # Analytics & tracking
├── admin_panel/            # Admin interface
├── soleva_backend/         # Project settings
├── static/                 # Static files
├── media/                  # Media files
├── templates/              # Email templates
└── requirements.txt        # Dependencies
```

## 🗄️ Database Models

### Key Models
- **User**: Extended user model with profile fields
- **Product**: Product catalog with variants and attributes
- **Order**: Complete order management
- **Address**: Egypt-specific address system
- **Cart**: Shopping cart functionality
- **Coupon**: Discount system
- **Notification**: Multi-channel notifications

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment
1. Configure production settings
2. Set up PostgreSQL and Redis
3. Configure web server (Nginx)
4. Set up SSL certificates
5. Configure monitoring and logging

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Monitoring

- **Health Check**: `/api/auth/health/`
- **Admin Interface**: `/admin/`
- **API Documentation**: Available via DRF browsable API

## 🔒 Security Considerations

- Change default SECRET_KEY in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Configure proper CORS settings
- Set up rate limiting
- Regular security updates

## 🌍 Internationalization

The system supports:
- Arabic (ar)
- English (en)

All models include multilingual fields for product names, descriptions, and categories.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 📞 Support

For support and questions:
- Email: support@soleva.com
- Documentation: [Link to docs]
- Issue Tracker: [Link to issues]

## 🗺️ Roadmap

- [ ] Mobile app API enhancements
- [ ] Multi-currency support
- [ ] Advanced analytics dashboard
- [ ] Machine learning recommendations
- [ ] International shipping expansion
- [ ] Multi-vendor marketplace features
